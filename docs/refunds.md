# Refunds

**Purpose.** Reverse a previous deposit.

**Prerequisites.** Token; the original transaction's merchant reference. The contract names no refund scope.

`client.refunds.create(payload, idempotency_key=None, merchant_account=None)` calls `POST /transactions/refunds/`.

Required: `provider_code`, `reference` (unique), `original_transaction_id` (the **merchant reference** of the
original transaction), `amount`, `currency`, `customer_phone`, `reason`. Optional: `reason_code`, `callback_url`,
`metadata`.

```python
refund = client.refunds.create(
    {
        "provider_code": "VODACOM_MPESA_COD",
        "reference": "REFUND-ORDER-123",
        "original_transaction_id": "ORDER-123",
        "amount": "100.00",
        "currency": "USD",
        "customer_phone": "243820000000",
        "reason": "Customer cancelled",
    },
    idempotency_key="REFUND-ORDER-123",
)
```

Response (HTTP 201): standard transaction fields (`status`, `internal_reference`, `merchant_reference`, ...). Settle
with `client.status.check("refund", "REFUND-ORDER-123")`.

Errors: 400, 401, 403, 409. The contract is silent on partial refunds and refund time limits.
