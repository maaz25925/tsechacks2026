from __future__ import annotations

from fastapi import APIRouter

from app.errors import http_error
from app.schemas import WalletBalanceResponse, WalletConnectRequest, WalletConnectResponse
from app.services.finternet import get_finternet
from app.supabase_client import get_supabase

router = APIRouter(prefix="/wallet", tags=["wallet"])


@router.post("/connect", response_model=WalletConnectResponse)
def connect(req: WalletConnectRequest) -> WalletConnectResponse:
    sb = get_supabase()
    user = sb.maybe_single("users", "*", id=req.user_id)
    if not user:
        raise http_error(404, "User not found", code="USER_NOT_FOUND")

    gw = get_finternet()
    wallet_address, balance = gw.connect_wallet(user_id=req.user_id)

    sb.update("users", {"wallet_address": wallet_address}, match={"id": req.user_id})
    return WalletConnectResponse(wallet_address=wallet_address, balance=balance)


@router.get("/balance", response_model=WalletBalanceResponse)
def balance(user_id: str) -> WalletBalanceResponse:
    sb = get_supabase()
    user = sb.maybe_single("users", "*", id=user_id)
    if not user:
        raise http_error(404, "User not found", code="USER_NOT_FOUND")

    wallet_address = user.get("wallet_address")
    if not wallet_address:
        # Frontend can call /wallet/connect first.
        raise http_error(400, "Wallet not connected", code="WALLET_NOT_CONNECTED")

    gw = get_finternet()
    bal = gw.get_balance(wallet_address=wallet_address)
    return WalletBalanceResponse(
        user_id=user_id,
        wallet_address=wallet_address,
        balance=bal,
    )

