# Python SDK examples

Standalone mini-shops that use the `mm-aggr` package. Each folder is its own
uv project. Start **one** backend, then point a
[JS/TS frontend example](https://github.com/MainMoney-Inc/mm_aggr_js_sdk/tree/main/examples)
at it with `VITE_MERCHANT_BACKEND_URL`.

| Example | Port | Start |
| --- | --- | --- |
| [django-drf](django-drf/) | 8000 | See that folder’s README |
| [fastapi](fastapi/) | 8001 | See that folder’s README |
| [flask](flask/) | 8002 | See that folder’s README |

Same app in every example: choose a product, pay (deposit), refund, transfer (payout).
