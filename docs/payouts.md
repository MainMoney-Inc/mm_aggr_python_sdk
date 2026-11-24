# Payouts (send money out)

**Purpose.** Pay a beneficiary from your wallet.

**Prerequisites.** Token; enough wallet balance (checked before processing; HTTP 400 otherwise); for the business
variants the API key needs the `BUSINESS_PAYOUT` scope.

| Method | Endpoint | Use |
| --- | --- | --- |
| `payouts.create` | `POST /transactions/payouts/` | standard payout |
| `payouts.create_business` | `POST /transactions/payouts/business/` | business (B2C) to a beneficiary phone number; `purpose` mandatory |
| `payouts.create_business_merchant_account` | `POST /transactions/payouts/business/merchant-account/` | business (B2B) to a provider merchant shortcode, not a phone; `purpose` mandatory |
| `payouts.create_card_business_merchant_account` | `POST /transactions/card-payouts/business/merchant-account/` | same B2B payout on the card-payouts path |

All take `(payload, idempotency_key=None)`; the first three also take `merchant_account=` (see
[mainmoney-rails.md](mainmoney-rails.md)). The contract lists no `Idempotency-Key` or `X-Merchant-Account` on the
card-payouts path.

Body (`PayoutRequest`): required `provider_code`, `reference`, `amount`, `currency`, `destination_account`;
optional `destination_name`, `purpose`, `purpose_code`, `callback_url`, `fee_bearer`, `application_fee`,
`application_fee_percent`, `metadata`. Payouts never accept `fees`.

```python
payout = client.payouts.create(
    {
        "provider_code": "VODACOM_MPESA_COD",
        "reference": "PAYOUT-77",
        "amount": "25.00",
        "currency": "USD",
        "destination_account": "243820000000",
        "destination_name": "Jane Doe",
    },
    idempotency_key="PAYOUT-77",
)

client.payouts.create_business_merchant_account(
    {
        "provider_code": "VODACOM_MPESA_COD",
        "reference": "B2B-1",
        "amount": "500.00",
        "currency": "USD",
        "destination_account": "<provider merchant shortcode>",
        "purpose": "Supplier invoice 42",
    },
)
```

Response (HTTP 201): same fields as deposits (`status`, `transaction_id`, `internal_reference`,
`merchant_reference`, ...). Wallet timing: your wallet is debited before the provider call. A provider failure is
reported as `PENDING` (HTTP 202) until a [status check](status-and-polling.md) or webhook settles it; a confirmed
failed payout returns the debit and fees together, a payout the provider actually paid keeps both.

Errors: 400 (validation or insufficient balance), 401, 403, 409. See [errors.md](errors.md).

## Minimal example

```python
p = client.payouts.create(
    {
        "provider_code": "VODACOM_MPESA_COD",
        "reference": "P-1",
        "amount": "5.00",
        "currency": "USD",
        "destination_account": "243820000000",
    },
    idempotency_key="P-1",
)
print(p["status"])
```
