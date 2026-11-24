# Errors and exception handling

Most endpoints wrap bodies in an envelope. The SDK unwraps `response_data` on success and raises on failure.

```json
{"success": false, "response_code": 400, "response_data": {"errors": {"field": ["message"]}}, "message": "Summary"}
```

Paginated lists return `count`, `next`, `previous`, `results` at the top level and are returned as is. Token
exchange and some auth failures use DRF shapes (`{"client_id": ["Invalid client_id"]}`,
`{"detail": "Authentication credentials were not provided."}`).

| Exception (`mm_aggr.exceptions`) | When |
| --- | --- |
| `AggregatorException` | base class |
| `ApiException` | HTTP >= 400 or `success: false`. Attributes: `message`, `status_code`, `errors` (field to messages), `response_body` |
| `AuthenticationException` | HTTP 401 persisting after one re-exchange, or token exchange refused |
| `WebhookSignatureException` | `webhooks.verify_or_fail` failed |

| Status | Typical meaning (from the contract) |
| --- | --- |
| 400 | validation error, insufficient balance, no FX quote (`errors.payment_currency`) |
| 401 | invalid or missing credentials |
| 403 | missing scope; invalid/foreign/inactive seller in `X-Merchant-Account` |
| 404 | transaction not found (status check) |
| 409 | idempotency conflict; payment-link state conflict |

The contract defines no other error codes; do not invent them.

```python
from mm_aggr.exceptions import AggregatorException, ApiException, AuthenticationException

try:
    client.payouts.create(body, idempotency_key=key)
except ApiException as exc:
    log.warning("payout refused: %s %s", exc.status_code, exc.errors)
    show_user(exc.message)  # API text, meant for display
except AuthenticationException:
    log.error("credentials rejected")
except AggregatorException:
    log.exception("transport failure")  # do not show raw exception text to end users
```

Never return `str(exc)` of non-API exceptions in your own HTTP responses (it can leak hosts and internals).
