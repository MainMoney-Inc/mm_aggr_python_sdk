"""Framework-neutral merchant-backend proxy for the JS checkout widget.

The browser widget (``@mainmoneyapp/js-*``) never holds API credentials: it calls routes on *your* backend, and
those routes forward to the aggregator through :class:`mm_aggr.Client`. :func:`dispatch` implements every route the
JS SDK's ``DEFAULT_PATHS`` uses, so a framework adapter only has to parse the request and call it.

Security: ``deposits``/``payouts`` bodies come from the browser. ``payment_currency`` is passed through unchanged
(it is the currency the customer chose to pay in, quoted server-side), but the merchant must force ``reference``,
``amount`` and ``currency`` from its own order, via ``overrides``, never trust the browser.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from mm_aggr.client import Client
from mm_aggr.exceptions import AggregatorException, ApiException

#: ``(HTTP method, route)`` pairs handled by :func:`dispatch` (routes have no leading/trailing slash).
CHECKOUT_ROUTES: tuple[tuple[str, str], ...] = (
    ("GET", "countries"),
    ("GET", "providers"),
    ("GET", "match-provider"),
    ("GET", "amount-limits"),
    ("POST", "fees/simulate"),
    ("GET", "checkout-preferences"),
    ("POST", "deposits"),
    ("POST", "deposits/validate"),
    ("POST", "payouts"),
    ("GET", "status"),
)

_TRUTHY = {"1", "true", "yes"}


def dispatch(
    client: Client,
    method: str,
    route: str,
    query: Mapping[str, Any] | None = None,
    body: Mapping[str, Any] | None = None,
    *,
    reference: str | None = None,
    idempotency_key: str | None = None,
    overrides: Mapping[str, Any] | None = None,
    operation: str = "deposit",
) -> Any:
    """Run one checkout route and return the aggregator payload.

    ``overrides`` are merged over deposit/payout bodies (e.g. ``{"amount": "10.00", "currency": "USD"}`` from the
    merchant's order). ``reference`` is the merchant's reference for the order; it overrides any browser value and is
    the default for ``status``. ``idempotency_key`` is forwarded on deposits (payouts use ``reference``).
    ``operation`` is the default ``status`` operation. Raises :class:`ValueError` for an unknown route.
    """
    verb = method.upper()
    path = route.strip("/")
    params = dict(query or {})
    payload = dict(body or {})

    if verb == "GET" and path == "countries":
        return client.countries.list()
    if verb == "GET" and path == "providers":
        return client.providers.list(_scalar_query(params))
    if verb == "GET" and path == "match-provider":
        return client.customers.match_provider(
            str(params.get("account_number") or ""),
            str(params.get("get_lookup") or "").lower() in _TRUTHY,
            str(params.get("operation_type") or "") or None,
        )
    if verb == "GET" and path == "amount-limits":
        return client.amount_limits.list(_scalar_query(params))
    if verb == "POST" and path == "fees/simulate":
        return client.fees.simulate(payload)
    if verb == "GET" and path == "checkout-preferences":
        return client.checkout_preferences.get()
    if verb == "POST" and path == "deposits":
        return client.deposits.create(_forced(payload, reference, overrides), idempotency_key)
    if verb == "POST" and path == "deposits/validate":
        return client.deposits.validate_payment(payload)
    if verb == "POST" and path == "payouts":
        forced = _forced(payload, reference, overrides)
        return client.payouts.create(forced, str(forced.get("reference") or "") or None)
    if verb == "GET" and path == "status":
        return client.status.check(
            str(params.get("operation") or operation),
            str(params.get("reference") or reference or ""),
        )
    raise ValueError("Unknown merchant backend path")


def handle(
    client: Client,
    method: str,
    route: str,
    query: Mapping[str, Any] | None = None,
    body: Mapping[str, Any] | None = None,
    **options: Any,
) -> tuple[int, Any]:
    """Like :func:`dispatch` but returns ``(http_status, json_payload)`` and never raises for API errors."""
    try:
        return 200, dispatch(client, method, route, query, body, **options)
    except ApiException as exc:
        status = int(getattr(exc, "status_code", 400) or 400)
        return (status if status >= 400 else 400), {"message": str(exc), "errors": getattr(exc, "errors", {})}
    except AggregatorException as exc:
        return 400, {"message": str(exc)}
    except ValueError:
        return 404, {"message": "Unknown merchant backend path"}


def _forced(
    payload: dict[str, Any],
    reference: str | None,
    overrides: Mapping[str, Any] | None,
) -> dict[str, Any]:
    merged = dict(payload)
    if reference is not None:
        merged["reference"] = reference
    if overrides:
        merged.update(overrides)
    return merged


def _scalar_query(query: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in query.items() if isinstance(value, (str, int, float, bool)) or value is None}
