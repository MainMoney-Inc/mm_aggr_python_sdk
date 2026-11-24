# Python SDK docs

User install guide: [../README.md](../README.md).
Contributor setup: [../CONTRIBUTING.md](../CONTRIBUTING.md).

## Payment links

`client.payment_links` wraps `/api/v1/payment-links/` (API key scope `PAYMENT_LINK`). See the
"Payment links" section of [../README.md](../README.md) for create, list, get, cancel, `url`, `expires_at`,
`single_use`, `redirect_url`, errors (`400`, `409`), acting on behalf of a seller (`merchant_account`), and how to
learn a link was paid.

| Method | Endpoint |
| --- | --- |
| `create(payload, idempotency_key=None, merchant_account=None)` | `POST /payment-links/` |
| `list(query=None, merchant_account=None)` | `GET /payment-links/` (optional `status`) |
| `get(id, merchant_account=None)` | `GET /payment-links/{id}/` |
| `cancel(id, merchant_account=None)` | `POST /payment-links/{id}/cancel/` |
