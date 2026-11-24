# Status check and polling

**Purpose.** Learn the final state of a deposit, payout, refund or remittance.

**Prerequisites.** Token.

`client.status.check(operation_type, reference, merchant_account=None)` calls
`POST /transactions/status/check/{deposit|payout|refund|remittance}/` with `{"reference": "..."}`. The reference is
your `merchant_reference` or the `internal_reference`. The aggregator queries the provider, updates the local
transaction and returns it (same fields as the create responses: `status`, `transaction_id`, `internal_reference`,
`external_reference`, `merchant_reference`, `timestamp`, `message`, `error_code`, `error_message`, `data`, ...).

Statuses: the contract names `SUCCESS`, `PENDING`, `FAILED` and says "etc."; treat `PENDING` as not final and any
other value as unknown until you have read it in your own logs. Errors: 400, 401, 404 (transaction not found).

Prefer [webhooks](webhooks.md) and use polling as a fallback or to settle an `PENDING` answer.

```python
import time
from mm_aggr.exceptions import ApiException


def wait_final(client, operation: str, reference: str, attempts: int = 10, delay: float = 3.0) -> dict:
    for _ in range(attempts):
        try:
            tx = client.status.check(operation, reference)
        except ApiException as exc:
            if exc.status_code == 404:  # not visible yet
                time.sleep(delay)
                continue
            raise
        if tx["status"] != "PENDING":
            return tx
        time.sleep(delay)
    raise TimeoutError(f"{reference} still pending")
```

The contract gives no recommended poll interval or rate limit.
