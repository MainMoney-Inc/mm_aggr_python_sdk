# MainMoney Python SDK

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
uv add mm-aggr
```

With pip:

```bash
pip install mm-aggr
```

With Poetry:

```bash
poetry add mm-aggr
```

Until the package is on PyPI, install from GitHub:

```bash
pip install git+https://github.com/MainMoney-Inc/mm_aggr_python_sdk.git
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
SDK. There is no `X-API-KEY` header. Reuse the same `reference` and optional
`Idempotency-Key` when retrying a create. Amounts are decimal strings; do not
mix currencies.

Verify inbound webhooks with
`client.webhooks.verify(raw_body, signature, secret)`.

Do not send merchant API keys to the browser.

## License

Copyright (c) 2026 MainMoney SARL. Licensed under the PolyForm Noncommercial
License 1.0.0. Non-commercial use is allowed. Commercial use requires
permission from MainMoney SARL. See [LICENSE](LICENSE).

## Examples

Runnable mini-shops live in [examples/](examples/). Each folder has its own
README (Django REST Framework, FastAPI, Flask). Pair them with a
[JS/TS frontend example](https://github.com/MainMoney-Inc/mm_aggr_js_sdk/tree/main/examples).

Want to contribute? See [CONTRIBUTING.md](CONTRIBUTING.md).
