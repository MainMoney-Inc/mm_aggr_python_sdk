# Authentication

**Purpose.** Exchange your application credentials for a Bearer token. The SDK does this for you.

**Prerequisites.** A merchant application with a `client_id` and an API key `secret`. Keep both on your server only.
Scopes (`allowed_scopes` on the application) gate operations; a missing scope answers HTTP 403. The contract names
the scopes `PAYMENT_LINK` (payment links) and `BUSINESS_PAYOUT` (business payouts) and is silent on the others.

## What the SDK does

`POST /auth/tokens/exchange/` with no `Authorization` header:

```json
{"client_id": "<client_id>", "secret": "<secret>", "expires_in": 3600}
```

Response: `access_token`, `token_type` (`Bearer`), `expires_in`, `expires_at`. `expires_in` is optional: default
3600, minimum 60, maximum 86400. The client caches the token, sends `Authorization: Bearer <token>` on every other
call, and on an HTTP 401 exchanges again once and retries. There is no `X-API-KEY` header.

```python
import os
from mm_aggr import Client

client = Client(
    client_id=os.environ["MM_CLIENT_ID"],
    secret=os.environ["MM_API_SECRET"],
    test=True,  # https://testaggregator.mainmoney.net/api/v1/ ; omit for production
    token_expires_in=3600,  # optional, 60..86400
    timeout=30.0,  # seconds, default HTTP client
)
```

`base_uri` overrides the host (`/api/v1/` is appended when missing). `http_client` accepts any object implementing
`mm_aggr.http.http_client.HttpClient` (useful for tests).

## Errors

| Case | Result |
| --- | --- |
| Invalid credentials | `AuthenticationException` (HTTP 401 after the retry) |
| Validation failure on exchange (for example `{"client_id": ["Invalid client_id"]}`) | `ApiException`, `status_code == 400` |
| Missing scope | `ApiException`, `status_code == 403` |

See [errors.md](errors.md).

## Minimal example

```python
client.countries.list()  # first call triggers the token exchange
```
