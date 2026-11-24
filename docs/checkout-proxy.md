# Browser checkout widget proxy

**Purpose.** The JS checkout widget never holds API credentials: it calls routes on *your* backend.
`mm_aggr.checkout_proxy` implements all of them, framework-neutral.

**Prerequisites.** A Client on your server; the same scopes as the underlying calls.

| Method | Route | Calls |
| --- | --- | --- |
| GET | `/countries` | `countries.list()` |
| GET | `/providers` | `providers.list(query)` |
| GET | `/match-provider` | `customers.match_provider(...)` |
| GET | `/amount-limits` | `amount_limits.list(query)` |
| POST | `/fees/simulate` | `fees.simulate(body)` |
| GET | `/checkout-preferences` | `checkout_preferences.get()` |
| POST | `/deposits` | `deposits.create(body, idempotency_key)` |
| POST | `/deposits/validate` | `deposits.validate_payment(body)` |
| POST | `/payouts` | `payouts.create(body, reference)` |
| GET | `/status` | `status.check(operation, reference)` |

`handle(client, method, route, query, body, *, reference=None, idempotency_key=None, overrides=None,
operation="deposit")` returns `(http_status, payload)` and never raises for API errors (error payload:
`{"message", "errors"}`; unknown route: 404). `dispatch(...)` returns the payload and raises instead.

**Never trust the browser for the order.** Force `reference` (from your order) and `overrides={"amount": ...,
"currency": ...}`. `payment_currency` is passed through unchanged. Derive `idempotency_key` from the checkout
session. **The browser no longer sends `Idempotency-Key` by default**, so the key must come from your server.

**CORS.** If the widget is served from another origin, allow the request headers `Content-Type` and `Authorization`
(your own session/auth for your backend, not the aggregator token). `Idempotency-Key` does not need to be allowed.

## FastAPI

```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mm_aggr.checkout_proxy import handle

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://shop.example.com"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.api_route("/mm/{route:path}", methods=["GET", "POST"])
async def mm(route: str, request: Request) -> JSONResponse:
    body = await request.json() if request.method == "POST" else {}
    order = load_order(request)  # your code: authenticated, server-side order
    status, payload = handle(
        client,
        request.method,
        route,
        dict(request.query_params),
        body,
        reference=order.reference,
        idempotency_key=order.session_key,
        overrides={"amount": order.amount, "currency": order.currency},
    )
    return JSONResponse(payload, status_code=status)
```

## Flask

```python
from flask import Flask, jsonify, request
from flask_cors import CORS
from mm_aggr.checkout_proxy import handle

app = Flask(__name__)
CORS(app, origins=["https://shop.example.com"], allow_headers=["Content-Type", "Authorization"])


@app.route("/mm/<path:route>", methods=["GET", "POST"])
def mm(route: str):
    order = load_order(request)
    status, payload = handle(
        client,
        request.method,
        route,
        request.args.to_dict(),
        request.get_json(silent=True) or {},
        reference=order.reference,
        idempotency_key=order.session_key,
        overrides={"amount": order.amount, "currency": order.currency},
    )
    return jsonify(payload), status
```

## Django

```python
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt  # protect with your own auth in production
from mm_aggr.checkout_proxy import handle


@csrf_exempt
def mm(request, route):
    order = load_order(request)
    body = json.loads(request.body or b"{}") if request.method == "POST" else {}
    status, payload = handle(
        client,
        request.method,
        route,
        request.GET.dict(),
        body,
        reference=order.reference,
        idempotency_key=order.session_key,
        overrides={"amount": order.amount, "currency": order.currency},
    )
    return JsonResponse(payload, status=status, safe=False)
```

For CORS in Django use `django-cors-headers` with `CORS_ALLOW_HEADERS = ["content-type", "authorization"]`. Full
runnable shops are in [../examples/](../examples/). `load_order` stands for your own code.
