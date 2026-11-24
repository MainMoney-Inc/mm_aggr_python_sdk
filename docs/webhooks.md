# Webhooks

**Purpose.** Get notified when a transaction changes state.

**Prerequisites.** A public HTTPS URL and a webhook secret, configured in the aggregator admin
(`Merchant.webhook_url`, optional `WebhookRule`). There is no merchant REST endpoint to register or verify
webhooks. Verify on your server, never in the browser.

## Request you receive

`POST` to your URL, `Content-Type: application/json`, `User-Agent: MM-Aggregator-Webhook/1.0`.

| Header | Meaning |
| --- | --- |
| `X-Webhook-Event-ID` | event UUID |
| `X-Webhook-Provider` | provider (financial entity) code |
| `X-Webhook-Type` | `DEPOSIT`, `PAYOUT`, `REMITTANCE`, `REFUND`, `STATUS_UPDATE`, `DIRECT_DEBIT`, `DEPOSIT_PROFILE`, `SETTLEMENT` |
| `X-Webhook-Timestamp` | ISO-8601 |
| `X-Webhook-Signature` | hex HMAC-SHA256 (present when a secret is set) |

There is no HTTP Basic auth and no `X-Callback-Signature`. Body:

```json
{"webhook_event_id": "uuid", "type": "DEPOSIT", "provider_code": "MPESA_KE", "transaction_id": "...",
 "provider_transaction_id": "...", "timestamp": "...", "status": "SUCCESS", "amount": "100.00", "currency": "KES",
 "merchant_reference": "ORDER-12345", "internal_reference": "...", "metadata": {}, "error_message": null}
```

With `payment_currency`, payloads report the charged `amount`/`currency` plus `original_amount` and
`original_currency`.

## Verify the signature

The signature is HMAC-SHA256 (hex) of the **raw request body** (canonical JSON, keys sorted, no spaces) with your
webhook secret. Verify the bytes you received; do not parse and re-serialize.

```python
client.webhooks.verify(raw_body, signature, secret) -> bool          # constant-time compare
client.webhooks.verify_or_fail(raw_body, signature, secret) -> None  # raises WebhookSignatureException
```

An empty signature or secret verifies as `False`.

```python
import os
from fastapi import FastAPI, HTTPException, Request
from mm_aggr.exceptions import WebhookSignatureException

app = FastAPI()


@app.post("/webhooks/mainmoney")
async def webhook(request: Request) -> dict[str, bool]:
    raw = (await request.body()).decode("utf-8")
    try:
        client.webhooks.verify_or_fail(
            raw, request.headers.get("X-Webhook-Signature", ""), os.environ["MM_WEBHOOK_SECRET"]
        )
    except WebhookSignatureException:
        raise HTTPException(status_code=401, detail="invalid signature")
    event = await request.json()
    # Idempotent: dedupe on event["webhook_event_id"] / merchant_reference
    return {"ok": True}
```

Flask: `raw = request.get_data(as_text=True)`. Django: `request.body.decode()`.

## Delivery

Answer HTTP 2xx quickly. Retries follow the matching webhook rule (`max_retries`, `retry_delay_seconds`); the
contract gives no default. Because an event can be delivered more than once, make the handler idempotent on
`webhook_event_id` or `merchant_reference`, and confirm the final state with a [status check](status-and-polling.md)
if in doubt. Errors in your handler (non-2xx) trigger the retries.
