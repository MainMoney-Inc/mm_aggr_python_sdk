# Amount limits, fees and pricing

**Purpose.** Check limits before a transaction, show the customer what they will pay, and read your pricing.

**Prerequisites.** A valid token. Adding your own `fees` on deposits only works when the back-office enabled
`allow_merchant_fees` on your account (otherwise HTTP 400).

## Amount limits

`GET /manage/general/amount-limits/`. Query: `currency`, `financial_entity_code`, `operation_type`, `page`,
`page_size`, `search`, `ordering`. Items: `id`, `financial_entity_code`, `operation_type`, `currency`, `amount_min`,
`amount_max`, `effective_from`, `effective_until`, `is_active`, `description`. Limits are per currency: never
compare amounts across currencies.

```python
limits = client.amount_limits.list(
    {"financial_entity_code": "VODACOM_MPESA_COD", "operation_type": "deposit", "currency": "USD"}
)
```

## Fee structure and pricing

```python
rules = client.fees.list({"currency": "USD", "financial_entity_code": "VODACOM_MPESA_COD"})  # GET /manage/general/fees/
pricing = client.pricing.get({"operation_type": "deposit"})  # GET /manage/general/pricing/
```

`fees.list` items: `id`, `scope`, `operation_type`, `fee_type`, `amount_type`, `value`, `composition_mode`,
`parent_rule_id`, `currency`, `financial_entity_code`, ... , `is_active`, `name`, `description`.

`pricing.get` (query `financial_entity_code`, `operation_type`, both optional) returns `{"items": [...]}`, one per
operation type: `operation_type`, `provider_fee`, `provider_fee_declarative`, `our_fee`, `merchant_additional_fee`,
`promotion_discount`, `total_merchant_fee`, `charged_fees`, and the rule ids. No transaction is created.

## Simulate fees

`POST /manage/general/fees/simulate/`:

| Field | Notes |
| --- | --- |
| `provider_code`, `operation_type`, `amount` | required |
| `currency` | order currency |
| `payment_currency` | currency the customer pays in; the whole answer is then in that currency, with a `quote` |
| `fees` | your own fee on top of `amount` (deposits, enabled accounts) |
| `fee_bearer` | `MERCHANT` or `CUSTOMER`, overrides the account default |

```python
sim = client.fees.simulate(
    {
        "provider_code": "VODACOM_MPESA_COD",
        "operation_type": "deposit",
        "amount": "100.00",
        "currency": "USD",
        "fees": "1.00",
        "fee_bearer": "CUSTOMER",
    }
)
print(sim["total_to_pay"], sim["merchant_receives"], sim["processing_fee"])
```

Response: `provider_fee`, `our_fee`, `merchant_additional_fee`, `promotion_discount`, `total_merchant_fee`,
`net_amount`, `fee_bearer`, `merchant_fee`, `base_amount`, `provider_fee_declarative`, `charged_fees`,
`provider_amount`, `merchant_wallet_effect` (negative for payouts), and for deposits the checkout box
`merchant_receives`, `processing_fee`, `total_to_pay`. With `payment_currency`, `quote` carries `from_currency`,
`to_currency`, `rate`, `source`, `converted_amount`.

Who pays (from the contract): amount 100, `fees` 1, platform fees 3 on 101. `CUSTOMER`: customer pays 104, merchant
nets 101. `MERCHANT`: customer pays 101, merchant nets 98. For payouts `MERCHANT` debits `amount + fees`, `CUSTOMER`
pays the recipient `amount - fees` (rejected when the fees take the whole amount); payouts never accept `fees`.

Errors: no active exchange rate for the pair answers 400 with `errors.payment_currency: ["no_quote: ..."]`; offer
payment in the order currency instead.

## Minimal example

```python
from decimal import Decimal

sim = client.fees.simulate(
    {"provider_code": "VODACOM_MPESA_COD", "operation_type": "payout", "amount": "50.00", "currency": "USD"}
)
print(Decimal(sim["merchant_wallet_effect"]))
```
