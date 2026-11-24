# Deposits (collect money)

**Purpose.** Charge a customer through a provider (mobile money, or card flows that need a validation step).

**Prerequisites.** Token; the `provider_code` and country must be in your allow-list
([customers-and-providers.md](customers-and-providers.md)); amount inside the limits
([amount-limits-and-fees.md](amount-limits-and-fees.md)). The contract names no deposit scope.

## Create

`POST /transactions/deposits/` (optional `Idempotency-Key`, optional `X-Merchant-Account`).

| Field | Notes |
| --- | --- |
| `provider_code`, `reference`, `amount`, `currency`, `customer_phone` | required. `reference` is unique per application; `amount` is a decimal string |
| `payment_currency` | customer pays in this currency (see fees guide) |
| `customer_name`, `customer_email` | email receives a receipt on success |
| `fees`, `fee_bearer` | your fee on top of `amount`; who pays platform fees |
| `application_fee`, `application_fee_percent` | platform fee taken from a seller when acting with `X-Merchant-Account`; not together; capped by the platform limit |
| `profile_reference` | for providers that need deposit profiles |
| `callback_url`, `metadata` | status updates URL; free object |

```python
deposit = client.deposits.create(
    {
        "provider_code": "VODACOM_MPESA_COD",
        "reference": "ORDER-123",
        "amount": "100.00",
        "currency": "USD",
        "customer_phone": "243820000000",
        "customer_email": "jane@example.com",
        "metadata": {"order_id": 123},
    },
    idempotency_key="checkout-session-8f2a",
)
```

Response (HTTP 202; the SDK returns the unwrapped `response_data`): `status`, `transaction_id`,
`internal_reference`, `external_reference`, `merchant_reference`, `timestamp`, `provider_reference`, `message`,
`error_code`, `error_message`, `data`, `processing_time_ms`.

**Final status is not guaranteed in the response.** A provider failure on a deposit answers `PENDING` (the
provider may have processed it). Settle through [status-and-polling.md](status-and-polling.md) or the
[webhook](webhooks.md). A deposit confirmed paid is credited to your wallet. Failures before the provider is called
(validation, limits) are final `FAILED`. A failed deposit keeps its `reference`; retry with a new one and a new
idempotency key ([idempotency.md](idempotency.md)).

## Validate payment (authenticator token)

For providers that ask the customer for an authenticator token (the contract names EcoBank,
`DIRECT_DEBIT_VERIFYPAYMENT`):

```python
client.deposits.validate_payment(payload)  # POST /transactions/deposits/validate-payment/ (X-Merchant-Account ok)
client.deposits.validate_card_payment(payload)  # POST /transactions/card-deposits/validate-payment/
```

The contract documents no request body for either path and answers a `DepositResponse`. Pass the fields your
provider integration gave you; this SDK does not invent them.

## Errors

400 validation (`ApiException.errors` maps field to messages), 401, 403 (unknown/not-active seller for
`X-Merchant-Account`), 409 (idempotency conflict). See [errors.md](errors.md).

## Minimal example

```python
from mm_aggr.exceptions import ApiException

try:
    d = client.deposits.create(
        {
            "provider_code": "VODACOM_MPESA_COD",
            "reference": "ORDER-1",
            "amount": "10.00",
            "currency": "USD",
            "customer_phone": "243820000000",
        },
        idempotency_key="sess-1",
    )
except ApiException as exc:
    print(exc.status_code, exc.message, exc.errors)
else:
    print(d["status"], d["internal_reference"])
```
