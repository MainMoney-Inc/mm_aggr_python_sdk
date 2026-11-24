# Idempotency

**Purpose.** Retry creates safely.

- `reference` (the `merchant_reference`) is unique per application; a duplicate is a validation error.
- Optional header `Idempotency-Key` (max 255 chars) on creates (deposits, payouts incl. business, refunds,
  remittances, payment links): same key and same body replays the first status and body and does not call the
  provider; same key with another body is HTTP 409; same key while the first is in flight is HTTP 409.
- No key on GETs, token exchange, status checks, lookups or fee simulation.

```python
client.deposits.create(body, idempotency_key="checkout-session-8f2a")
```

Rules: reuse the same key only to retry the *same* request. Whenever the body changes (new phone, new currency) use
a new key. A failed deposit keeps its `reference`, so a retry needs a new `reference` (for example `ORDER-123-r1`)
and a new key. For checkouts derive the key from the checkout session, not from the order. Make webhook handlers
idempotent too ([webhooks.md](webhooks.md)).

```python
from mm_aggr.exceptions import ApiException

try:
    client.deposits.create(body, idempotency_key=key)
except ApiException as exc:
    if exc.status_code == 409:
        ...  # key reused with a different body, or the first request is still running
```
