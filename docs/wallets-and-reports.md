# Wallets, transactions and reports

**Purpose.** Read balances, list your transactions, and get volume reports.

**Prerequisites.** Token. All four calls accept `merchant_account=` to read a seller's data
([mainmoney-rails.md](mainmoney-rails.md)).

## Wallets

`client.wallets.list(query=None, merchant_account=None)` -> `GET /manage/merchant-admin/wallets/`. Query: `country`,
`currency`, `status`, `page`, `page_size`, `search`, `ordering`. Items: `id`, `merchant_id`, `merchant_name`,
`currency`, `country`, `is_active`, `balance`, `reserved_balance`, `available_balance`, `created_at`, `updated_at`.
One wallet per currency: never add balances across currencies.

```python
for w in client.wallets.list({"currency": "USD"})["results"]:
    print(w["currency"], w["available_balance"])
```

## Transactions

`client.transactions.list(operation_type, query=None, merchant_account=None)` -> 
`GET /manage/merchant-admin/transactions/{deposit|payout|refund|remittance|settlement}/`. Filters: `amount_min`,
`amount_max`, `country`, `currency`, `date_from`, `date_to`, `internal_reference`, `merchant_reference`,
`provider_code`, `status`, plus pagination, `search`, `ordering`. The contract does not state the date format.
Items: `id`, `operation_type`, `internal_reference`, `merchant_reference`, `external_reference`,
`provider_transaction_id`, `amount`, `currency`, `provider_code`, `country`, `status`, `status_reason`,
`created_at`, `completed_at`.

```python
page = client.transactions.list("deposit", {"status": "SUCCESS", "currency": "USD", "page_size": 50})
```

## Reports

Filters for both: `currency`, `date_from`, `date_to`, `operation_type`, `provider_code`.

```python
charts = client.reports.charts(
    {"currency": "USD"}
)  # {"volume_by_day": [{"date", "currency", "count", "total_amount"}]}
summary = client.reports.summary({"currency": "USD"})  # {"totals_by_provider": [...], "top_transactions": [...]}
```

`totals_by_provider` items: `provider_code`, `currency`, `count`, `total_amount`, `success_count`.
`top_transactions` items: `operation_type`, `amount`, `currency`, `provider_code`, `merchant_reference`,
`internal_reference`, `created_at`. Totals are per currency.
