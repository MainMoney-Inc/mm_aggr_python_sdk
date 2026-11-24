# MainMoney Python SDK

[![PyPI](https://img.shields.io/pypi/v/mm-aggr-sdk)](https://pypi.org/project/mm-aggr-sdk/) [![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Python client for the MainMoney aggregator merchant API. Install this package
in your Python application (Django, FastAPI, Flask, or scripts).

The [JS/TS frontend SDK](https://github.com/MainMoney-Inc/mm_aggr_js_sdk) can
be used in the browser only if this SDK (or the PHP or Node SDK) runs on your
server. Never put merchant API keys in frontend code.

## Requirements

- Python 3.11 or later (3.13 or 3.14 recommended)
- A merchant application on MM Aggregator

## Install

With uv (recommended):

```bash
uv add mm-aggr-sdk
```

With pip:

```bash
pip install mm-aggr-sdk
```

With Poetry:

```bash
poetry add mm-aggr-sdk
```

## Quick start

```python
import os

from mm_aggr import Client

client = Client(
    client_id=os.environ["MM_CLIENT_ID"],
    secret=os.environ["MM_API_SECRET"],
    test=True,  # https://testaggregator.mainmoney.net — omit for production
)

deposit = client.deposits.create(
    {
        "provider_code": "VODACOM_MPESA_COD",
        "reference": "ORDER-123",
        "amount": "100.00",
        "currency": "USD",
        "customer_phone": "243820000000",
    },
    idempotency_key="ORDER-123",
)
```

Defaults: production `https://aggregator.mainmoney.net/api/v1/`, test
`https://testaggregator.mainmoney.net/api/v1/`. Pass `base_uri` only to override.
Configure credentials from your environment. Merchant API docs:
`/api/v1/docs/merchants/` on the aggregator host.

Exchange `client_id` and `secret` for a Bearer access token is handled by the
SDK. There is no `X-API-KEY` header. Resend the same `reference` and
`Idempotency-Key` only when retrying the *same* create (same body). When the body
changes (new phone number, new currency) use a new `Idempotency-Key`; after a
failed deposit also use a new `reference`, because a failed one stays reserved.
Derive the key from your checkout session, not from the cart or order. Amounts are
decimal strings; do not mix currencies.

Verify inbound webhooks with
`client.webhooks.verify(raw_body, signature, secret)`.

Do not send merchant API keys to the browser.

## Checkout proxy

The JS checkout widget calls routes on **your** backend, which forward to the aggregator with this SDK.
`mm_aggr.checkout_proxy` implements all of them, framework-neutral, so none gets forgotten:

| Method | Route | Aggregator call |
| --- | --- | --- |
| GET | `/countries` | `client.countries.list()` |
| GET | `/providers` | `client.providers.list(query)` |
| GET | `/match-provider` | `client.customers.match_provider(...)` |
| GET | `/amount-limits` | `client.amount_limits.list(query)` |
| POST | `/fees/simulate` | `client.fees.simulate(body)` |
| GET | `/checkout-preferences` | `client.checkout_preferences.get()` |
| POST | `/deposits` | `client.deposits.create(body, idempotency_key)` |
| POST | `/deposits/validate` | `client.deposits.validate_payment(body)` |
| POST | `/payouts` | `client.payouts.create(body, reference)` |
| GET | `/status` | `client.status.check(operation, reference)` |

```python
from mm_aggr.checkout_proxy import handle

status, payload = handle(
    client,
    request.method,
    route,
    query,
    body,
    reference=order.reference,  # forced over any browser value
    idempotency_key=session_key,  # one per checkout session
    overrides={"amount": order.amount, "currency": order.currency},
)
return JsonResponse(payload, status=status)
```

`dispatch(...)` raises instead of returning a status tuple. The test suite fails if a path in the JS SDK's
`DEFAULT_PATHS` has no Python route.

**Never trust the browser for the order.** Deposit and payout bodies come from the customer's browser. Force
`reference`, `amount` and `currency` from your own order through `reference=` and `overrides=`. `payment_currency`
(the currency the customer pays in, chosen through a fee quote) is passed through unchanged.

## Payment links

A payment link is a hosted payment page for one amount. You create it, give the returned `url` to your customer
(email, chat, QR code), and the customer pays there with card or mobile money; no checkout code on your side.
The API key needs the `PAYMENT_LINK` scope.

```python
link = client.payment_links.create(
    {
        "reference": "INV-2026-001",  # your unique reference, max 100 chars
        "amount": "25.00",
        "currency": "USD",
        "title": "Invoice 2026-001",
        "description": "Consulting, March",
        "methods": ["card", "mobile_money"],  # empty or omitted: every method available to you
        "expires_at": "2026-12-31T23:59:59Z",  # optional; the link stops accepting payments after this
        "single_use": True,  # default: closes after the first successful payment
        "redirect_url": "https://shop.example.com/thanks",  # where the customer lands after paying
        "customer_name": "Jane Doe",
        "customer_email": "jane@example.com",
        "customer_phone": "243820000000",
        "metadata": {"order_id": 42},
    },
    idempotency_key="INV-2026-001",
)
print(link["url"])  # public URL the customer pays at

page = client.payment_links.list({"status": "ACTIVE"})  # status: ACTIVE, PAID, EXPIRED, CANCELLED; newest first
link = client.payment_links.get(link["id"])
link = client.payment_links.cancel(link["id"])  # only active links; a paid link cannot be cancelled
```

- Only `reference`, `amount` and `currency` are required. The amount is a decimal string and is fixed by you; the
  customer cannot change it.
- `status` is `ACTIVE`, `PAID`, `EXPIRED` or `CANCELLED`; `paid_at` is set once paid.
- Errors raise `ApiException`: `400` for invalid input, `409` when the request conflicts with the link's state (for
  example cancelling a link that is already paid). Read `exc.status_code` and `exc.message`.
- **On behalf of a seller (MainMoney Rails):** pass `merchant_account="<seller account id>"` to any payment link
  method. It is sent as `X-Merchant-Account`; the link is created for and attributed to that seller (`account_id`),
  and the API answers `403` when the seller is unknown, not yours or not active.
- **Knowing it was paid:** poll `client.payment_links.get(id)` until `status` is `PAID`, and verify any webhook with
  `client.webhooks.verify(...)` before trusting it. Reconcile on your own `reference`.

## License

Copyright (c) 2026 MainMoney SARL. Licensed under the MIT License. See [LICENSE](LICENSE).

## Examples

Runnable mini-shops live in [examples/](examples/). Each folder has its own
README (Django REST Framework, FastAPI, Flask). Pair them with a
[JS/TS frontend example](https://github.com/MainMoney-Inc/mm_aggr_js_sdk/tree/main/examples).

Want to contribute? See [CONTRIBUTING.md](CONTRIBUTING.md).
