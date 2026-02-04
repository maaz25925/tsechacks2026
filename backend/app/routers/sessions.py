from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter

from app.config import get_settings
from app.errors import http_error
from app.schemas import SessionEndBreakdown, SessionEndRequest, SessionStartRequest, SessionStartResponse
from app.services.finternet import get_finternet
from app.services.metering import compute_charge_amount, compute_completion_percentage
from app.supabase_client import get_supabase, utc_now_iso

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/start", response_model=SessionStartResponse)
def start(req: SessionStartRequest) -> SessionStartResponse:
    """
    Session start:
    - Ensure student + listing exist
    - Ensure student wallet is connected + sufficient balance
    - Create session (active) + lock funds via Finternet (mock)
    """
    sb = get_supabase()
    s = get_settings()

    student = sb.maybe_single("users", "*", id=req.student_id)
    if not student or student.get("role") != "student":
        raise http_error(404, "Student not found", code="STUDENT_NOT_FOUND")

    listing = sb.maybe_single("listings", "*", id=req.listing_id)
    if not listing or listing.get("status") != "published":
        raise http_error(404, "Listing not found", code="LISTING_NOT_FOUND")

    wallet_address = student.get("wallet_address")
    if not wallet_address:
        raise http_error(400, "Wallet not connected", code="WALLET_NOT_CONNECTED")

    reserve_amount = float(
        req.reserve_amount
        if req.reserve_amount is not None
        else listing.get("reserve_amount") or s.default_reserve_amount
    )
    reserve_amount = max(1.0, round(reserve_amount, 2))

    gw = get_finternet()
    balance = gw.get_balance(wallet_address=wallet_address)
    if balance < reserve_amount:
        raise http_error(402, "Insufficient balance", code="INSUFFICIENT_BALANCE")

    lock_tx = gw.lock_funds(wallet_address=wallet_address, amount=reserve_amount)

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
        # convenience field (not in the requested schema, but handy if table includes it)
        "reserve_amount": reserve_amount,
    }

    # If your Supabase table doesn't have reserve_amount column, remove the key above.
    try:
        sb.insert("sessions", session_row)
    except Exception:
        session_row.pop("reserve_amount", None)
        sb.insert("sessions", session_row)

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

    return SessionStartResponse(
        session_id=session_id,
        status="active",
        reserve_amount=reserve_amount,
        transaction_id=lock_tx.finternet_tx_id,
    )


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
        float(session.get("reserve_amount"))
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

