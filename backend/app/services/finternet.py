from __future__ import annotations

import logging
import random
import time
from dataclasses import dataclass
from typing import Any


logger = logging.getLogger(__name__)


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

    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def _retry_wrapper(self, func, *args, **kwargs):
        """Retry wrapper with exponential backoff."""
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Failed after {self.max_retries} attempts: {str(e)}")
                    raise
                wait_time = self.retry_delay * (2 ** attempt)
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {str(e)}")
                time.sleep(wait_time)

    def connect_wallet(self, *, user_id: str) -> tuple[str, float]:
        """TODO: Replace with wallet connection flow (OAuth / signature / etc.)"""
        def _connect():
            wallet_address = f"0x{random.getrandbits(160):040x}"
            balance = float(50 + random.randint(0, 200))
            logger.info(f"Connected wallet for user {user_id}: {wallet_address}")
            return wallet_address, balance
        return self._retry_wrapper(_connect)

    def get_balance(self, *, wallet_address: str) -> float:
        """TODO: Replace with Finternet balance API call via httpx."""
        def _get_balance():
            balance = float(50 + random.randint(0, 200))
            logger.info(f"Got balance for wallet {wallet_address}: {balance}")
            return balance
        return self._retry_wrapper(_get_balance)

    def lock_funds(self, *, wallet_address: str, amount: float) -> FinternetTx:
        """TODO: Replace with Finternet "lock/reserve" API."""
        def _lock():
            tx_id = f"ft_lock_{random.randint(100000, 999999)}"
            logger.info(f"Locked {amount} for wallet {wallet_address}: {tx_id}")
            return FinternetTx(finternet_tx_id=tx_id)
        return self._retry_wrapper(_lock)

    def settle(self, *, wallet_address: str, amount: float) -> FinternetTx:
        """TODO: Replace with Finternet settlement API."""
        def _settle():
            tx_id = f"ft_settle_{random.randint(100000, 999999)}"
            logger.info(f"Settled {amount} to wallet {wallet_address}: {tx_id}")
            return FinternetTx(finternet_tx_id=tx_id)
        return self._retry_wrapper(_settle)

    def refund(self, *, wallet_address: str, amount: float) -> FinternetTx:
        """TODO: Replace with Finternet refund API."""
        def _refund():
            tx_id = f"ft_refund_{random.randint(100000, 999999)}"
            logger.info(f"Refunded {amount} to wallet {wallet_address}: {tx_id}")
            return FinternetTx(finternet_tx_id=tx_id)
        return self._retry_wrapper(_refund)

    def create_payment_intent(self, *, amount: float, currency: str = "USD", 
                             description: str | None = None, 
                             metadata: dict[str, Any] | None = None) -> dict:
        """
        Create a payment intent for milestone-based payouts.
        TODO: Replace with real Finternet API call.
        Returns: { intent_id, escrow_id, status, total_amount }
        """
        def _create():
            intent_id = f"intent_{random.randbytes(12).hex()}"
            escrow_id = f"esc_{random.randbytes(12).hex()}"
            result = {
                "intent_id": intent_id,
                "escrow_id": escrow_id,
                "status": "pending",
                "total_amount": amount,
                "currency": currency,
                "description": description,
                "metadata": metadata or {},
            }
            logger.info(f"Created payment intent: {intent_id} for {amount} {currency}")
            return result
        return self._retry_wrapper(_create)

    def get_escrow(self, *, intent_id: str) -> dict:
        """
        Retrieve escrow details including milestones.
        TODO: Replace with real Finternet API call.
        Returns: { id, intent_id, status, total_amount, locked_amount, milestones: [...] }
        """
        def _get():
            result = {
                "id": f"esc_{random.randbytes(12).hex()}",
                "intent_id": intent_id,
                "status": "active",
                "total_amount": 100.0,
                "locked_amount": 100.0,
                "milestones": [],
            }
            logger.info(f"Retrieved escrow for intent: {intent_id}")
            return result
        return self._retry_wrapper(_get)

    def create_milestone(self, *, escrow_id: str, index: int, description: str, 
                        amount: float, percentage: float) -> dict:
        """
        Create a milestone for an escrow.
        TODO: Replace with real Finternet API call.
        Returns: { milestone_id, escrow_id, index, status, amount, percentage }
        """
        def _create():
            milestone_id = f"milestone_{random.randbytes(12).hex()}"
            result = {
                "milestone_id": milestone_id,
                "escrow_id": escrow_id,
                "index": index,
                "description": description,
                "amount": amount,
                "percentage": percentage,
                "status": "pending",
            }
            logger.info(f"Created milestone {milestone_id} for escrow {escrow_id}")
            return result
        return self._retry_wrapper(_create)

    def submit_proof(self, *, milestone_id: str, proof_data: dict[str, Any]) -> dict:
        """
        Submit proof of delivery for a milestone.
        TODO: Replace with real Finternet API call.
        Returns: { milestone_id, status, proof_hash }
        """
        def _submit():
            proof_hash = f"0x{random.randbytes(32).hex()}"
            result = {
                "milestone_id": milestone_id,
                "status": "proof_submitted",
                "proof_hash": proof_hash,
                "proof_data": proof_data,
            }
            logger.info(f"Submitted proof for milestone {milestone_id}: {proof_hash}")
            return result
        return self._retry_wrapper(_submit)

    def complete_milestone(self, *, milestone_id: str, escrow_id: str) -> dict:
        """
        Complete a milestone and release funds to teacher.
        TODO: Replace with real Finternet API call.
        Returns: { milestone_id, status, amount_released, transaction_id }
        """
        def _complete():
            tx_id = f"ft_complete_{random.randint(100000, 999999)}"
            result = {
                "milestone_id": milestone_id,
                "escrow_id": escrow_id,
                "status": "completed",
                "amount_released": 0.0,  # Would be fetched from escrow
                "transaction_id": tx_id,
            }
            logger.info(f"Completed milestone {milestone_id}, released funds via {tx_id}")
            return result
        return self._retry_wrapper(_complete)


_gw: FinternetGateway | None = None


def get_finternet() -> FinternetGateway:
    global _gw
    if _gw is None:
        _gw = FinternetGateway()
    return _gw
