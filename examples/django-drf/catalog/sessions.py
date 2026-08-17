"""In-memory checkout sessions (TTL 30 minutes)."""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass

SESSION_TTL_SECONDS = 1800


@dataclass
class CheckoutSession:
    token: str
    reference: str
    amount: str | None
    currency: str | None
    lock_amount: bool
    operation: str
    expires_at: float
    order_id: int | None = None
    transfer_id: int | None = None


_SESSIONS: dict[str, CheckoutSession] = {}


def create_session(
    *,
    reference: str,
    amount: str | None,
    currency: str | None,
    lock_amount: bool,
    operation: str,
    order_id: int | None = None,
    transfer_id: int | None = None,
) -> CheckoutSession:
    token = secrets.token_urlsafe(24)
    session = CheckoutSession(
        token=token,
        reference=reference,
        amount=amount,
        currency=currency,
        lock_amount=lock_amount,
        operation=operation,
        expires_at=time.time() + SESSION_TTL_SECONDS,
        order_id=order_id,
        transfer_id=transfer_id,
    )
    _SESSIONS[token] = session
    return session


def get_session(token: str) -> CheckoutSession | None:
    session = _SESSIONS.get(token)
    if session is None or session.expires_at < time.time():
        _SESSIONS.pop(token, None)
        return None
    return session
