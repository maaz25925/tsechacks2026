from __future__ import annotations

import logging
from uuid import uuid4

from fastapi import APIRouter

from app.errors import http_error
from app.schemas import (
    EscrowResponse,
    MilestoneCompleteResponse,
    MilestoneCreateRequest,
    MilestoneListResponse,
    MilestoneResponse,
    PaymentIntentRequest,
    ProofSubmitRequest,
)
from app.services.finternet import get_finternet
from app.supabase_client import get_supabase, utc_now_iso

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/milestones", tags=["milestones"])


@router.post("/intent", response_model=dict)
def create_payment_intent(req: PaymentIntentRequest) -> dict:
    """
    Create a payment intent for milestone-based payouts.
    Returns: { intent_id, escrow_id, status, total_amount }
    """
    print(f"\n{'='*60}")
    print(f"🔵 /milestones/intent ENDPOINT HIT!")
    print(f"{'='*60}")
    print(f"Request Data: amount={req.amount}, currency={req.currency}, description={req.description}")
    print(f"Metadata: {req.metadata}")
    print(f"{'='*60}\n")
    
    logger.info(f"🔵 Creating payment intent: amount={req.amount}, currency={req.currency}")
    
    gw = get_finternet()
    sb = get_supabase()
    
    # session_id must be provided in metadata for escrow tracking
    session_id = None
    if req.metadata:
        session_id = req.metadata.get("session_id")
    
    if not session_id:
        raise http_error(400, "session_id is required in metadata", code="INVALID_METADATA")
    
    try:
        result = gw.create_payment_intent(
            amount=req.amount,
            currency=req.currency,
            description=req.description,
            metadata=req.metadata,
        )
        
        logger.info(f"💰 Payment intent response from Finternet: {result}")
        
        # Extract critical fields from Finternet response
        intent_id = result.get("id") or result.get("intent_id")
        payment_url = result.get("paymentUrl") or result.get("payment_url")
        status = result.get("status", "INITIATED")
        intent_amount = result.get("amount", str(req.amount))
        intent_currency = result.get("currency", req.currency)
        
        logger.info(f"📋 Extracted: intent_id={intent_id}, paymentUrl={payment_url}, amount={intent_amount}")
        
        # Store escrow in database for later milestone creation
        try:
            escrow_id = f"escrow_{uuid4().hex[:12]}"
            amount_value = float(intent_amount) if intent_amount else float(req.amount)
            
            escrow_row = {
                "id": escrow_id,
                "finternet_intent_id": intent_id or "",
                "session_id": session_id,
                "total_amount": amount_value,
                "locked_amount": amount_value,
                "status": "active",
                "created_at": utc_now_iso(),
            }
            sb.insert("escrows", escrow_row)
            logger.info(f"✅ Stored escrow {escrow_id} with session {session_id}")
        except Exception as db_error:
            logger.error(f"❌ Failed to store escrow in database: {str(db_error)}")
            # Don't fail completely - still return the payment URL to frontend!
            logger.warning(f"⚠️ Escrow storage failed but returning payment intent anyway")
        
        # Return response with paymentUrl for frontend navigation
        return {
            "id": intent_id or f"intent_{uuid4().hex[:12]}",
            "escrow_id": escrow_id if 'escrow_id' in locals() else f"escrow_{uuid4().hex[:12]}",
            "paymentUrl": payment_url,  # CRITICAL: This is what frontend needs
            "status": status,
            "amount": intent_amount,
            "currency": intent_currency,
        }
    except Exception as e:
        logger.error(f"❌ Failed to create payment intent: {str(e)}", exc_info=True)
        raise http_error(500, f"Failed to create payment intent: {str(e)}", code="INTENT_FAILED")
        raise http_error(500, f"Failed to create payment intent: {str(e)}", code="INTENT_FAILED")


@router.get("/escrow/{intent_id}", response_model=EscrowResponse)
def get_escrow(intent_id: str) -> EscrowResponse:
    """
    Get escrow details by intent ID.
    Returns: { id, session_id, finternet_intent_id, total_amount, locked_amount, status }
    """
    sb = get_supabase()
    gw = get_finternet()
    
    try:
        # Try to get from database first
        escrow = sb.maybe_single("escrows", "*", finternet_intent_id=intent_id)
        if escrow:
            return EscrowResponse(
                id=escrow["id"],
                session_id=escrow["session_id"],
                finternet_intent_id=escrow["finternet_intent_id"],
                total_amount=escrow["total_amount"],
                locked_amount=escrow["locked_amount"],
                status=escrow["status"],
                created_at=escrow.get("created_at"),
            )
        
        # Fallback to Finternet API
        finternet_escrow = gw.get_escrow(intent_id=intent_id)
        logger.info(f"Retrieved escrow from Finternet: {intent_id}")
        return EscrowResponse(
            id=finternet_escrow.get("id", intent_id),
            session_id="",
            finternet_intent_id=intent_id,
            total_amount=finternet_escrow.get("total_amount", 0.0),
            locked_amount=finternet_escrow.get("locked_amount", 0.0),
            status=finternet_escrow.get("status", "active"),
        )
    except Exception as e:
        logger.error(f"Failed to get escrow for intent {intent_id}: {str(e)}")
        raise http_error(500, f"Failed to get escrow: {str(e)}", code="ESCROW_FAILED")


@router.post("", response_model=MilestoneResponse)
def create_milestone(req: MilestoneCreateRequest) -> MilestoneResponse:
    """
    Create a milestone for an escrow.
    Loops based on user engagement of content.
    """
    sb = get_supabase()
    gw = get_finternet()
    
    # Verify escrow exists
    escrow = sb.maybe_single("escrows", "*", id=req.escrow_id)
    if not escrow:
        raise http_error(404, "Escrow not found", code="ESCROW_NOT_FOUND")
    
    # Verify session exists
    session = sb.maybe_single("sessions", "*", id=req.session_id)
    if not session:
        raise http_error(404, "Session not found", code="SESSION_NOT_FOUND")
    
    milestone_id = f"milestone_{uuid4().hex}"
    
    try:
        # Create in Finternet
        finternet_result = gw.create_milestone(
            escrow_id=req.escrow_id,
            index=req.index,
            description=req.description,
            amount=req.amount,
            percentage=req.percentage,
        )
        
        # Store in database
        milestone_row = {
            "id": milestone_id,
            "escrow_id": req.escrow_id,
            "session_id": req.session_id,
            "index": req.index,
            "description": req.description,
            "amount": req.amount,
            "percentage": req.percentage,
            "status": "pending",
            "proof_data": None,
            "created_at": utc_now_iso(),
        }
        sb.insert("milestones", milestone_row)
        
        logger.info(f"Created milestone {milestone_id} for escrow {req.escrow_id}")
        return MilestoneResponse(
            id=milestone_id,
            escrow_id=req.escrow_id,
            session_id=req.session_id,
            index=req.index,
            description=req.description,
            amount=req.amount,
            percentage=req.percentage,
            status="pending",
            proof_data=None,
            created_at=milestone_row["created_at"],
        )
    except Exception as e:
        logger.error(f"Failed to create milestone: {str(e)}")
        raise http_error(500, f"Failed to create milestone: {str(e)}", code="MILESTONE_FAILED")


@router.get("", response_model=MilestoneListResponse)
def list_milestones(escrow_id: str | None = None, session_id: str | None = None, 
                   limit: int = 50, offset: int = 0) -> MilestoneListResponse:
    """
    List milestones with optional filters.
    """
    sb = get_supabase()
    
    try:
        query = sb.client.table("milestones").select("*", count="exact")
        if escrow_id:
            query = query.eq("escrow_id", escrow_id)
        if session_id:
            query = query.eq("session_id", session_id)
        
        result = query.range(offset, offset + limit - 1).order("created_at", desc=True).execute()
        milestones = result.data or []
        total = result.count or 0
        
        milestone_responses = [
            MilestoneResponse(
                id=m["id"],
                escrow_id=m["escrow_id"],
                session_id=m["session_id"],
                index=m["index"],
                description=m["description"],
                amount=m["amount"],
                percentage=m["percentage"],
                status=m["status"],
                proof_data=m.get("proof_data"),
                created_at=m.get("created_at"),
            )
            for m in milestones
        ]
        
        logger.info(f"Listed {len(milestones)} milestones")
        return MilestoneListResponse(milestones=milestone_responses, total=total)
    except Exception as e:
        logger.error(f"Failed to list milestones: {str(e)}")
        raise http_error(500, f"Failed to list milestones: {str(e)}", code="LIST_FAILED")


@router.get("/{milestone_id}", response_model=MilestoneResponse)
def get_milestone(milestone_id: str) -> MilestoneResponse:
    """
    Get a milestone by ID.
    """
    sb = get_supabase()
    
    try:
        milestone = sb.maybe_single("milestones", "*", id=milestone_id)
        if not milestone:
            raise http_error(404, "Milestone not found", code="MILESTONE_NOT_FOUND")
        
        return MilestoneResponse(
            id=milestone["id"],
            escrow_id=milestone["escrow_id"],
            session_id=milestone["session_id"],
            index=milestone["index"],
            description=milestone["description"],
            amount=milestone["amount"],
            percentage=milestone["percentage"],
            status=milestone["status"],
            proof_data=milestone.get("proof_data"),
            created_at=milestone.get("created_at"),
        )
    except Exception as e:
        logger.error(f"Failed to get milestone {milestone_id}: {str(e)}")
        raise http_error(500, f"Failed to get milestone: {str(e)}", code="GET_FAILED")


@router.post("/{milestone_id}/proof", response_model=MilestoneCompleteResponse)
def submit_proof(milestone_id: str, req: ProofSubmitRequest) -> MilestoneCompleteResponse:
    """
    Submit proof for a milestone (video URL).
    Automatically completes the milestone upon submission.
    Triggers automatic fund release to teacher.
    """
    sb = get_supabase()
    gw = get_finternet()
    
    try:
        # Get milestone
        milestone = sb.maybe_single("milestones", "*", id=milestone_id)
        if not milestone:
            raise http_error(404, "Milestone not found", code="MILESTONE_NOT_FOUND")
        
        # Get escrow for transaction details
        escrow = sb.maybe_single("escrows", "*", id=milestone["escrow_id"])
        if not escrow:
            raise http_error(404, "Escrow not found", code="ESCROW_NOT_FOUND")
        
        # Build proof data
        proof_data = {
            "video_url": req.video_url,
            "notes": req.notes,
        }
        
        # Submit proof to Finternet
        proof_result = gw.submit_proof(milestone_id=milestone_id, proof_data=proof_data)
        
        # Automatically complete milestone (auto-release on proof submission)
        completion_result = gw.complete_milestone(
            milestone_id=milestone_id, 
            escrow_id=milestone["escrow_id"]
        )
        
        # Update milestone status to completed
        sb.update(
            "milestones",
            {
                "status": "completed",
                "proof_data": proof_data,
            },
            match={"id": milestone_id}
        )
        
        logger.info(f"Submitted proof and completed milestone {milestone_id}, released {milestone['amount']}")
        
        return MilestoneCompleteResponse(
            milestone_id=milestone_id,
            status="completed",
            amount_released=milestone["amount"],
            finternet_tx_id=completion_result.get("transaction_id"),
        )
    except Exception as e:
        logger.error(f"Failed to submit proof for milestone {milestone_id}: {str(e)}")
        raise http_error(500, f"Failed to submit proof: {str(e)}", code="PROOF_FAILED")


@router.post("/{milestone_id}/complete", response_model=MilestoneCompleteResponse)
def complete_milestone_manual(milestone_id: str) -> MilestoneCompleteResponse:
    """
    Manually complete a milestone (fallback if proof not auto-triggering).
    This should rarely be used since proof submission auto-completes.
    """
    sb = get_supabase()
    gw = get_finternet()
    
    try:
        milestone = sb.maybe_single("milestones", "*", id=milestone_id)
        if not milestone:
            raise http_error(404, "Milestone not found", code="MILESTONE_NOT_FOUND")
        
        if milestone["status"] == "completed":
            raise http_error(400, "Milestone already completed", code="ALREADY_COMPLETED")
        
        # Complete in Finternet
        completion_result = gw.complete_milestone(
            milestone_id=milestone_id,
            escrow_id=milestone["escrow_id"]
        )
        
        # Update milestone status
        sb.update(
            "milestones",
            {"status": "completed"},
            match={"id": milestone_id}
        )
        
        logger.info(f"Manually completed milestone {milestone_id}")
        
        return MilestoneCompleteResponse(
            milestone_id=milestone_id,
            status="completed",
            amount_released=milestone["amount"],
            finternet_tx_id=completion_result.get("transaction_id"),
        )
    except Exception as e:
        logger.error(f"Failed to complete milestone {milestone_id}: {str(e)}")
        raise http_error(500, f"Failed to complete milestone: {str(e)}", code="COMPLETE_FAILED")
