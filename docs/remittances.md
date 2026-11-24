# Remittances

**Purpose.** Move value between two merchants, possibly across currencies. The sender wallet is debited and the
receiver wallet credited on success; balance is checked first.

**Prerequisites.** Token; sufficient balance. The contract names no scope for remittances.

`client.remittances.create(payload, idempotency_key=None, merchant_account=None)` calls
`POST /transactions/remittances/`.

Required: `provider_code`, `reference`, `receiver_merchant_id` (UUID of the receiving merchant), `source_amount`
(at most 2 decimals), `source_currency`, `destination_amount` (checked server-side against the active exchange
rate), `destination_currency`, `destination_account`. Optional: `destination_name`, `purpose`, `purpose_code`,
`callback_url`, `metadata`.

```python
r = client.remittances.create(
    {
        "provider_code": "VODACOM_MPESA_COD",
        "reference": "REM-1",
        "receiver_merchant_id": "<uuid>",
        "source_amount": "100.00",
        "source_currency": "USD",
        "destination_amount": "<amount at the active rate>",
        "destination_currency": "CDF",
        "destination_account": "243820000000",
    },
    idempotency_key="REM-1",
)
```

Response (HTTP 201): `status`, `transaction_id`, `internal_reference`, `external_reference`, `merchant_reference`,
`timestamp`, `message`, `error_code`, `error_message`, `data`, `processing_time_ms`. The contract does not say how to
obtain the exchange rate; the amounts must be consistent with the rate the server holds.

Errors: 400 (validation, insufficient balance, amount not matching the rate), 401, 403, 409.

## Minimal example

See above; poll with `client.status.check("remittance", "REM-1")`.
