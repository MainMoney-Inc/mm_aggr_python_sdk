"""Merchant-backend proxy matching JS SDK DEFAULT_PATHS."""

from __future__ import annotations

from typing import Any

from client import get_client
from db import Order, SessionLocal, Transfer
from sessions import CheckoutSession


def handle_proxy(
    method: str,
    route: str,
    query: dict[str, Any],
    body: dict[str, Any],
    session: CheckoutSession,
) -> tuple[int, Any]:
    try:
        from mm_aggr.exceptions import AggregatorException, ApiException
    except ImportError:
        AggregatorException = Exception  # type: ignore[misc,assignment]
        ApiException = Exception  # type: ignore[misc,assignment]

    try:
        payload = _dispatch(method.upper(), route.strip("/"), query, body, session)
        return 200, payload
    except ApiException as exc:
        status = int(getattr(exc, "status_code", 400) or 400)
        if status < 400:
            status = 400
        return status, {"message": str(exc), "errors": getattr(exc, "errors", {})}
    except AggregatorException as exc:
        return 400, {"message": str(exc)}
    except ValueError as exc:
        return 400, {"message": str(exc)}


def _dispatch(
    method: str,
    route: str,
    query: dict[str, Any],
    body: dict[str, Any],
    session: CheckoutSession,
) -> Any:
    client = get_client()
    if method == "GET" and route == "countries":
        return client.countries.list()
    if method == "GET" and route == "providers":
        return client.providers.list(_scalar_query(query))
    if method == "GET" and route == "match-provider":
        account = str(query.get("account_number") or "")
        lookup = str(query.get("get_lookup") or "").lower() in {"1", "true", "yes"}
        return client.customers.match_provider(account, lookup)
    if method == "GET" and route == "amount-limits":
        return client.amount_limits.list(_scalar_query(query))
    if method == "POST" and route == "fees/simulate":
        return client.fees.simulate(body)
    if method == "GET" and route == "checkout-preferences":
        return client.checkout_preferences.get()
    if method == "POST" and route == "deposits":
        payload = dict(body)
        payload["reference"] = session.reference
        if session.lock_amount and session.amount is not None:
            payload["amount"] = session.amount
        result = client.deposits.create(payload, session.reference)
        _mark_order(session, "pending")
        return result
    if method == "POST" and route == "payouts":
        payload = dict(body)
        payload["reference"] = session.reference
        if session.lock_amount and session.amount is not None:
            payload["amount"] = session.amount
        destination = str(payload.get("customer_phone") or payload.get("destination_account") or "")
        result = client.payouts.create(payload, session.reference)
        _mark_transfer(session, "pending", destination)
        return result
    if method == "GET" and route == "status":
        reference = str(query.get("reference") or session.reference)
        operation = str(query.get("operation") or session.operation or "deposit")
        result = client.status.check(operation, reference)
        status = _extract_status(result)
        if operation == "payout":
            _mark_transfer(session, status)
        else:
            _mark_order(session, status)
        return result
    raise ValueError("Unknown merchant backend path")


def _scalar_query(query: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in query.items() if isinstance(value, (str, int, float, bool)) or value is None}


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
