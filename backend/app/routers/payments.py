from __future__ import annotations

import logging
from fastapi import APIRouter

from app.errors import http_error
from app.supabase_client import get_supabase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("/by_session")
def payments_by_session(session_id: str) -> dict:
    """
    Convenience endpoint for frontend: retrieve lock/settle/refund records.
    """
    sb = get_supabase()
    session = sb.maybe_single("sessions", "id", id=session_id)
    if not session:
        raise http_error(404, "Session not found", code="SESSION_NOT_FOUND")
    rows = (
        sb.client.table("payments")
        .select("id,session_id,type,amount,status,finternet_tx_id,created_at")
        .eq("session_id", session_id)
        .order("created_at", desc=False)
        .execute()
        .data
        or []
    )
    return {"session_id": session_id, "payments": rows}

