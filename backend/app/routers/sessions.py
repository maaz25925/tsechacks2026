from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter

from app.config import get_settings
from app.errors import http_error
from app.schemas import SessionEndBreakdown, SessionEndRequest, SessionStartRequest, SessionStartResponse
from app.services.finternet import get_finternet
from app.services.metering import compute_charge_amount, compute_completion_percentage
from app.supabase_client import get_supabase, utc_now_iso

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/start", response_model=SessionStartResponse)
def start(req: SessionStartRequest) -> SessionStartResponse:
    """
    Session start:
    - Ensure student + listing exist
    - Ensure student wallet is connected + sufficient balance
    - Create session (active) + lock funds via Finternet (mock)
    - Create escrow for milestone-based payouts
    """
    try:
        logger.info(f"Session start request received: student_id={req.student_id}, listing_id={req.listing_id}, reserve_amount={req.reserve_amount}")
        
        sb = get_supabase()
        s = get_settings()

        student = sb.maybe_single("users", "*", id=req.student_id)
        if not student or student.get("role") != "student":
            logger.warning(f"Student not found or invalid role: {req.student_id}")
            raise http_error(404, "Student not found", code="STUDENT_NOT_FOUND")

        listing = sb.maybe_single("listings", "*", id=req.listing_id)
        if not listing or listing.get("status") != "published":
            logger.warning(f"Listing not found or not published: {req.listing_id}")
            raise http_error(404, "Listing not found", code="LISTING_NOT_FOUND")

        wallet_address = student.get("wallet_address")
        if not wallet_address:
            # For MVP: auto-generate mock wallet if not set
            logger.info(f"Wallet not connected, generating mock wallet for {req.student_id}")
            wallet_address = f"0x{uuid4().hex[:40]}"
            # Update student record with wallet
            try:
                sb.update("users", {"wallet_address": wallet_address}, match={"id": req.student_id})
                logger.info(f"Mock wallet assigned: {wallet_address}")
            except Exception as e:
                logger.warning(f"Could not update wallet: {e}")
                # Continue with generated wallet anyway


        reserve_amount = float(
            req.reserve_amount
            if req.reserve_amount is not None
            else listing.get("reserve_amount") or s.default_reserve_amount
        )
        reserve_amount = max(1.0, round(reserve_amount, 2))
        logger.info(f"Reserve amount: ${reserve_amount}")

        gw = get_finternet()
        balance = gw.get_balance(wallet_address=wallet_address)
        logger.info(f"Student balance: ${balance}")
        
        if balance < reserve_amount:
            logger.warning(f"❌ Insufficient balance: ${balance} < ${reserve_amount}")
            raise http_error(402, "Insufficient balance", code="INSUFFICIENT_BALANCE")

        lock_tx = gw.lock_funds(wallet_address=wallet_address, amount=reserve_amount)
        logger.info(f"✅ Funds locked: {lock_tx.finternet_tx_id}")

        session_id = f"sess_{uuid4().hex}"
        now = datetime.now(timezone.utc).isoformat()
        session_row = {
            "id": session_id,
            "student_id": req.student_id,
            "teacher_id": listing["teacher_id"],
            "listing_id": req.listing_id,
            "status": "active",
            "start_time": now,
            "end_time": None,
            "duration_min": None,
            "completion_percentage": None,
            "engagement_metrics": None,
            "final_amount_charged": None,
            "refund_amount": None,
            "transaction_id": lock_tx.finternet_tx_id,
            "created_at": utc_now_iso(),
        }

        sb.insert("sessions", session_row)
        logger.info(f"Session created: {session_id}")

        # Store payment record
        sb.insert(
            "payments",
            {
                "id": f"pay_{uuid4().hex}",
                "session_id": session_id,
                "type": "lock",
                "amount": reserve_amount,
                "status": "success",
                "finternet_tx_id": lock_tx.finternet_tx_id,
                "created_at": utc_now_iso(),
            },
        )

        # Create escrow for milestone-based payouts
        try:
            print(f"\n🔵 CALLING create_payment_intent from sessions.py")
            print(f"Amount: {reserve_amount}, Session: {session_id}")
            
            payment_intent = gw.create_payment_intent(
                amount=reserve_amount,
                currency="USD",
                description=f"Escrow for session {session_id} - {listing['title']}",
                metadata={
                    "releaseType": "MILESTONE_LOCKED",
                    "session_id": session_id,
                    "student_id": req.student_id,
                    "teacher_id": listing["teacher_id"],
                },
            )
            
            print(f"✅ Got payment_intent response: {payment_intent}")
            logger.info(f"Payment intent response: {payment_intent}")
            
            escrow_id = f"escrow_{uuid4().hex}"
            escrow_row = {
                "id": escrow_id,
                "session_id": session_id,
                "finternet_intent_id": payment_intent.get("id", ""),
                "total_amount": reserve_amount,
                "locked_amount": reserve_amount,
                "status": "active",
                "created_at": utc_now_iso(),
            }
            sb.insert("escrows", escrow_row)
            logger.info(f"✅ Created escrow {escrow_id} for session {session_id}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to create escrow for session {session_id}: {str(e)}")
            # Continue anyway; escrow is optional for MVP

        logger.info(f"Session start successful: {session_id}")
        return SessionStartResponse(
            session_id=session_id,
            status="active",
            reserve_amount=reserve_amount,
            transaction_id=lock_tx.finternet_tx_id,
        )
    except Exception as exc:
        logger.error(f"Error in session start: {str(exc)}", exc_info=True)
        # Re-raise if it's already an HTTPException
        if hasattr(exc, 'status_code'):
            raise
        # Otherwise wrap it
        raise http_error(400, f"Session start failed: {str(exc)}", code="SESSION_START_ERROR")


@router.post("/end", response_model=SessionEndBreakdown)
def end(req: SessionEndRequest) -> SessionEndBreakdown:
    """
    Session end:
    - Compute duration from start_time to now
    - Compute completion percentage (from request or from chunk metrics)
    - Compute final charged (capped by reserve) and refund
    - Settle to teacher + refund student (mock)
    - Update session + create payments rows
    """
    sb = get_supabase()

    session = sb.maybe_single("sessions", "*", id=req.session_id)
    if not session:
        raise http_error(404, "Session not found", code="SESSION_NOT_FOUND")
    if session.get("status") != "active":
        raise http_error(400, "Session is not active", code="SESSION_NOT_ACTIVE")

    listing = sb.maybe_single("listings", "*", id=session["listing_id"])
    if not listing:
        raise http_error(404, "Listing not found", code="LISTING_NOT_FOUND")

    student = sb.maybe_single("users", "*", id=session["student_id"])
    teacher = sb.maybe_single("users", "*", id=session["teacher_id"])
    if not student or not teacher:
        raise http_error(500, "Session user records missing", code="DATA_INTEGRITY")

    wallet_address = student.get("wallet_address")
    if not wallet_address:
        raise http_error(400, "Wallet not connected", code="WALLET_NOT_CONNECTED")

    start_raw = session.get("start_time")
    if not start_raw:
        raise http_error(500, "Session start_time missing", code="DATA_INTEGRITY")
    start_dt = datetime.fromisoformat(start_raw.replace("Z", "+00:00"))
    end_dt = datetime.now(timezone.utc)
    duration_min = max(0.0, (end_dt - start_dt).total_seconds() / 60.0)

    engagement = req.engagement_metrics or session.get("engagement_metrics") or {}
    if req.completion_percentage is not None:
        completion = float(req.completion_percentage)
    else:
        completion = compute_completion_percentage(listing, engagement)

    # determine reserve amount
    reserve_amount = (
        float(session.get("reserve_amount") or 0.0)
        if session.get("reserve_amount") is not None
        else float(listing.get("reserve_amount") or get_settings().default_reserve_amount)
    )

    final_charge, refund = compute_charge_amount(
        duration_min=duration_min,
        completion_percentage=completion,
        price_per_min=float(listing.get("price_per_min") or 0.0),
        total_duration_min=float(listing.get("total_duration_min") or 0.0),
        reserve_amount=reserve_amount,
    )

    gw = get_finternet()
    settle_tx = gw.settle(wallet_address=wallet_address, amount=final_charge)
    refund_tx = gw.refund(wallet_address=wallet_address, amount=refund)

    # Update session
    updates = {
        "status": "ended",
        "end_time": end_dt.isoformat(),
        "duration_min": round(duration_min, 2),
        "completion_percentage": round(completion, 2),
        "engagement_metrics": engagement,
        "final_amount_charged": final_charge,
        "refund_amount": refund,
        "transaction_id": session.get("transaction_id") or settle_tx.finternet_tx_id,
    }
    sb.update("sessions", updates, match={"id": req.session_id})

    # Payments
    sb.insert(
        "payments",
        {
            "id": f"pay_{uuid4().hex}",
            "session_id": req.session_id,
            "type": "settle",
            "amount": final_charge,
            "status": "success",
            "finternet_tx_id": settle_tx.finternet_tx_id,
            "created_at": utc_now_iso(),
        },
    )
    sb.insert(
        "payments",
        {
            "id": f"pay_{uuid4().hex}",
            "session_id": req.session_id,
            "type": "refund",
            "amount": refund,
            "status": "success",
            "finternet_tx_id": refund_tx.finternet_tx_id,
            "created_at": utc_now_iso(),
        },
    )

    return SessionEndBreakdown(
        session_id=req.session_id,
        listing_id=session["listing_id"],
        teacher_id=session["teacher_id"],
        student_id=session["student_id"],
        start_time=start_dt,
        end_time=end_dt,
        duration_min=round(duration_min, 2),
        completion_percentage=round(completion, 2),
        reserve_amount=reserve_amount,
        final_amount_charged=final_charge,
        refund_amount=refund,
        settle_transaction_id=settle_tx.finternet_tx_id,
        refund_transaction_id=refund_tx.finternet_tx_id,
    )


@router.get("/student/{student_id}")
def sessions_for_student(student_id: str) -> dict:
    """
    Simple student dashboard: list recent sessions.
    """
    sb = get_supabase()
    rows = (
        sb.client.table("sessions")
        .select("*")
        .eq("student_id", student_id)
        .order("created_at", desc=True)
        .limit(50)
        .execute()
        .data
        or []
    )
    return {"student_id": student_id, "sessions": rows}


@router.get("/teacher/{teacher_id}")
def sessions_for_teacher(teacher_id: str) -> dict:
    sb = get_supabase()
    rows = (
        sb.client.table("sessions")
        .select("*")
        .eq("teacher_id", teacher_id)
        .order("created_at", desc=True)
        .limit(50)
        .execute()
        .data
        or []
    )
    return {"teacher_id": teacher_id, "sessions": rows}


@router.get("/{session_id}/videos")
def session_videos(session_id: str) -> dict:
    """
    Return listing video URLs only while session is active.

    For MVP we reuse stored public URLs. A stricter version could
    switch to short-lived signed URLs using storage paths.
    """
    sb = get_supabase()
    session = sb.maybe_single("sessions", "*", id=session_id)
    if not session:
        raise http_error(404, "Session not found", code="SESSION_NOT_FOUND")
    if session.get("status") != "active":
        raise http_error(403, "Session is not active", code="SESSION_NOT_ACTIVE")

    listing = sb.maybe_single("listings", "*", id=session["listing_id"])
    if not listing:
        raise http_error(404, "Listing not found", code="LISTING_NOT_FOUND")

    video_urls = listing.get("video_urls") or []
    if isinstance(video_urls, dict):
        # tolerate bad data shape
        video_urls = list(video_urls.values())
    return {
        "session_id": session_id,
        "listing_id": session["listing_id"],
        "video_urls": video_urls,
    }

