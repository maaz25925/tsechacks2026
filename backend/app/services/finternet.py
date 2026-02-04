from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class FinternetTx:
    finternet_tx_id: str
    status: str = "success"


class FinternetGateway:
    """
    Mocked Finternet payment gateway.

    Swap these methods to real `httpx` calls once sandbox docs are available.
    Keep the interface stable so the rest of the code doesn't change.
    """

    def connect_wallet(self, *, user_id: str) -> tuple[str, float]:
        # TODO: Replace with wallet connection flow (OAuth / signature / etc.)
        wallet_address = f"0x{random.getrandbits(160):040x}"
        balance = float(50 + random.randint(0, 200))  # fake USD balance
        return wallet_address, balance

    def get_balance(self, *, wallet_address: str) -> float:
        # TODO: Replace with Finternet balance API call via httpx.
        return float(50 + random.randint(0, 200))

    def lock_funds(self, *, wallet_address: str, amount: float) -> FinternetTx:
        # TODO: Replace with Finternet "lock/reserve" API.
        return FinternetTx(finternet_tx_id=f"ft_lock_{random.randint(100000, 999999)}")

    def settle(self, *, wallet_address: str, amount: float) -> FinternetTx:
        # TODO: Replace with Finternet settlement API.
        return FinternetTx(finternet_tx_id=f"ft_settle_{random.randint(100000, 999999)}")

    def refund(self, *, wallet_address: str, amount: float) -> FinternetTx:
        # TODO: Replace with Finternet refund API.
        return FinternetTx(finternet_tx_id=f"ft_refund_{random.randint(100000, 999999)}")


_gw: FinternetGateway | None = None


def get_finternet() -> FinternetGateway:
    global _gw
    if _gw is None:
        _gw = FinternetGateway()
    return _gw

