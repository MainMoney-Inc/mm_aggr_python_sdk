# Payment links

**Purpose.** A hosted payment page for one amount; no checkout code on your side.

**Prerequisites.** API key with the `PAYMENT_LINK` scope.

`client.payment_links`: `create(payload, idempotency_key=None, merchant_account=None)` `POST /payment-links/`;
`list(query=None, merchant_account=None)` `GET /payment-links/`; `get(id, ...)` `GET /payment-links/{id}/`;
`cancel(id, ...)` `POST /payment-links/{id}/cancel/`.

Create body: required `reference` (max 100 chars, unique), `amount` (decimal string), `currency`; optional `title`,
`description`, `methods` (subset of `card`, `mobile_money`; empty means every method available), `expires_at`,
`single_use` (closes after the first successful payment), `redirect_url`, `customer_name`, `customer_email`,
`customer_phone`, `metadata`.

```python
link = client.payment_links.create(
    {
        "reference": "INV-2026-001",
        "amount": "25.00",
        "currency": "USD",
        "title": "Invoice 2026-001",
        "methods": ["card", "mobile_money"],
        "single_use": True,
        "redirect_url": "https://shop.example.com/thanks",
    },
    idempotency_key="INV-2026-001",
)
print(link["url"])
```

Response (HTTP 201): `id`, `reference`, `amount`, `currency`, `title`, `description`, `status` (`ACTIVE`, `PAID`,
`EXPIRED`, `CANCELLED`), `methods`, `effective_methods`, `expires_at`, `single_use`, `redirect_url`, customer
fields, `metadata`, `paid_at`, `url`, `account_id` (seller, null for your own), `created_at`. List is paginated
(the endpoint description mentions an optional `status` filter, although its parameters list only `page`, `page_size`, `search`, `ordering`; newest first).

Cancelling a paid link, or other state conflicts, answers 409. To know a link was paid, poll
`client.payment_links.get(id)` until `status == "PAID"` and/or use verified [webhooks](webhooks.md); reconcile on your
`reference`. On behalf of a seller: [mainmoney-rails.md](mainmoney-rails.md).

## Minimal example

```python
link = client.payment_links.create({"reference": "INV-1", "amount": "25.00", "currency": "USD"})
print(link["url"], client.payment_links.get(link["id"])["status"])
```
