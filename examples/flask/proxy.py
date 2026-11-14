"""Merchant-backend proxy matching JS SDK DEFAULT_PATHS."""

from __future__ import annotations

import hashlib
from typing import Any

from mm_aggr.checkout_proxy import handle

from client import get_client
from db import Order, SessionLocal, Transfer
from sessions import CheckoutSession


def idempotency_key(session: CheckoutSession) -> str:
    """One key per checkout session: a refreshed page is a new attempt, a double submit replays the first answer."""
    return "mm-" + hashlib.sha256(session.token.encode()).hexdigest()[:32]


def handle_proxy(
    method: str,
    route: str,
    query: dict[str, Any],
    body: dict[str, Any],
    session: CheckoutSession,
) -> tuple[int, Any]:
    """Forward a widget request through the SDK's checkout proxy; the order is the source of truth."""
    path = route.strip("/")
    verb = method.upper()
    overrides: dict[str, Any] = {}
    if session.lock_amount and session.amount is not None:
        overrides["amount"] = session.amount
        if session.currency:
            overrides["currency"] = session.currency
    status, payload = handle(
        get_client(),
        verb,
        path,
        query,
        body,
        reference=session.reference,
        idempotency_key=idempotency_key(session),
        overrides=overrides,
        operation=session.operation or "deposit",
    )
    if status == 200:
        _record(verb, path, body, payload, session)
    return status, payload


def _record(verb: str, path: str, body: dict[str, Any], payload: Any, session: CheckoutSession) -> None:
    if verb == "POST" and path == "deposits":
        _mark_order(session, "pending")
    elif verb == "POST" and path == "payouts":
        destination = str(body.get("customer_phone") or body.get("destination_account") or "")
        _mark_transfer(session, "pending", destination)
    elif verb == "GET" and path == "status":
        status = _extract_status(payload)
        if session.operation == "payout":
            _mark_transfer(session, status)
        else:
            _mark_order(session, status)


def _extract_status(result: Any) -> str:
    if isinstance(result, dict):
        raw = result.get("status") or result.get("transaction_status") or ""
        if isinstance(raw, str) and raw:
            return raw.lower()
    return "pending"


def _map_status(status: str) -> str:
    lowered = status.lower()
    if lowered in {"success", "successful", "paid", "completed"}:
        return "paid"
    if lowered in {"failed", "error", "cancelled", "canceled"}:
        return "failed"
    if lowered == "refunded":
        return "refunded"
    return "pending"


def _mark_order(session: CheckoutSession, status: str) -> None:
    if session.order_id is None:
        return
    with SessionLocal() as db:
        order = db.get(Order, session.order_id)
        if order is not None:
            order.status = _map_status(status)
            db.commit()


def _mark_transfer(session: CheckoutSession, status: str, destination: str = "") -> None:
    if session.transfer_id is None:
        return
    with SessionLocal() as db:
        transfer = db.get(Transfer, session.transfer_id)
        if transfer is not None:
            transfer.status = _map_status(status)
            if destination:
                transfer.destination = destination
            db.commit()
