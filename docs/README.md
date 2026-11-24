# Python SDK documentation

Install and quick start: [../README.md](../README.md). Contributors: [../CONTRIBUTING.md](../CONTRIBUTING.md).
The API contract these guides follow is the pinned merchant OpenAPI in `contrib/contract/`. Where it is silent, the
guides say so.

| Guide | Covers |
| --- | --- |
| [authentication.md](authentication.md) | token exchange, client options, scopes |
| [customers-and-providers.md](customers-and-providers.md) | countries, providers, match provider, lookup, KYC |
| [amount-limits-and-fees.md](amount-limits-and-fees.md) | limits, fee structure, pricing, fee simulation, `payment_currency` |
| [deposits.md](deposits.md) | mobile money / card deposits, validate-payment |
| [payouts.md](payouts.md) | payouts, business payouts, merchant-account payouts |
| [remittances.md](remittances.md) | remittances |
| [refunds.md](refunds.md) | refunds |
| [status-and-polling.md](status-and-polling.md) | status check and polling |
| [webhooks.md](webhooks.md) | headers, payload, signature verification, retries |
| [idempotency.md](idempotency.md) | `reference` and `Idempotency-Key` |
| [payment-links.md](payment-links.md) | hosted payment links |
| [mainmoney-rails.md](mainmoney-rails.md) | sellers, KYB, onboarding link, `X-Merchant-Account`, transfers |
| [wallets-and-reports.md](wallets-and-reports.md) | wallets, transactions, reports |
| [errors.md](errors.md) | envelope, exceptions, status codes |
| [checkout-proxy.md](checkout-proxy.md) | browser widget proxy, CORS, FastAPI/Flask/Django |

## Method map

| Method | Endpoint |
| --- | --- |
| `deposits.create / validate_payment / validate_card_payment` | `POST /transactions/deposits/`, `.../deposits/validate-payment/`, `/transactions/card-deposits/validate-payment/` |
| `payouts.create / create_business / create_business_merchant_account / create_card_business_merchant_account` | `POST /transactions/payouts/`, `.../business/`, `.../business/merchant-account/`, `/transactions/card-payouts/business/merchant-account/` |
| `remittances.create`, `refunds.create` | `POST /transactions/remittances/`, `/transactions/refunds/` |
| `status.check(op, ref)` | `POST /transactions/status/check/{op}/` |
| `customers.lookup / kyc / match_provider` | `POST .../customers/lookup/`, `.../kyc/`, `GET .../match-provider/` |
| `countries.list`, `providers.list`, `checkout_preferences.get` | `GET /manage/general/countries/`, `financial-entities/`, `checkout-preferences/` |
| `fees.list / simulate`, `pricing.get`, `amount_limits.list` | `GET/POST /manage/general/fees/`, `fees/simulate/`, `pricing/`, `amount-limits/` |
| `wallets.list`, `transactions.list(op)` | `GET /manage/merchant-admin/wallets/`, `transactions/{op}/` |
| `reports.charts / summary` | `GET /manage/merchant-admin/reports/charts/`, `summary/` |
| `payment_links.create / list / get / cancel` | `/payment-links/` |
| `sellers.list / create / countries / get / update / get_kyb / update_kyb / start_kyb / submit_kyb / create_onboarding_link / revoke_onboarding_link` | `/sellers/...` |
| `transfers.list / create / get` | `/transactions/transfers/` |
| `webhooks.verify / verify_or_fail` | local HMAC check |

Every resource the contract lets act for a seller (deposits, payouts, refunds, remittances, status, payment links,
wallets, transactions, reports) takes `merchant_account=` per call, and the client takes `merchant_account=` or
`client.with_merchant_account(id)`: see [mainmoney-rails.md](mainmoney-rails.md).
