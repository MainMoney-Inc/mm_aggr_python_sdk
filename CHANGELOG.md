# Changelog

## Unreleased

## 0.2.1

- New resources, covering the rest of the pinned contract: `client.sellers` (list, create, countries, get, update,
  KYB get/update/start/submit, onboarding link create/revoke), `client.transfers` (list, create, get),
  `client.pricing.get`, `client.reports` (`charts`, `summary`), `deposits.validate_card_payment`
  (`/transactions/card-deposits/validate-payment/`) and `payouts.create_card_business_merchant_account`
  (`/transactions/card-payouts/business/merchant-account/`). `Transport` gained `patch` and `delete`.
- `X-Merchant-Account` (act on behalf of a seller) for every resource the contract lists it on: deposits (incl.
  validate-payment), payouts (standard, business, business merchant-account), refunds, remittances, status,
  payment links, wallets, transactions and reports. Pass `merchant_account=` per call, set it client-wide with
  `Client(..., merchant_account=...)`, or use `client.with_merchant_account(id)` (shares the HTTP client and token
  cache). The per-call value wins. Existing calls are unchanged.
- Documentation: per-flow guides under `docs/`; README shortened.

## 0.2.0

- `client.payment_links` (`create`, `list`, `get`, `cancel`): hosted Payment Links API (`/payment-links/`). The
  response carries the public `url` the customer pays at. Requires an API key with the `PAYMENT_LINK` scope.
- Payment link methods accept `merchant_account` to send `X-Merchant-Account` and act on behalf of a seller.

## 0.1.5

- `checkout_proxy.handle` reads the API message from `ApiException.message` (new attribute) rather than `str(exc)`; behaviour unchanged.

## 0.1.4

- Security: `checkout_proxy.handle` logs transport/auth failures and returns a generic message instead of the raw exception text; API validation messages are unchanged.
- Security: examples no longer run Flask in debug mode by default (`FLASK_DEBUG=1` opts in).
- Security: locks updated (urllib3 2.8.0, certifi 2026.10.23, Werkzeug, Django, DRF).
- Workflows declare least-privilege `permissions: contents: read` (CodeQL).

## 0.1.3

- `mm_aggr.checkout_proxy` (`dispatch`, `handle`, `CHECKOUT_ROUTES`): framework-neutral proxy for every route the JS SDK calls
  (countries, providers, match-provider, amount-limits, fees/simulate, checkout-preferences, deposits,
  deposits/validate, payouts, status). `payment_currency` is passed through unchanged; merchants force
  `reference`/`amount`/`currency` from their own order.
- Test that fails when a JS `DEFAULT_PATHS` entry has no Python route.
- Examples use the helper. README documents every route.
- Fixed `pyproject.toml` declaring `version` both statically and dynamically (broke the build); `__version__` is the
  single source.
- README and examples: derive the `Idempotency-Key` from the checkout session, not the reference.

## 0.1.1

- Relicensed under the MIT License.
- Distribution renamed to `mm-aggr-sdk` on PyPI (the import package is still `mm_aggr`).
- First release published to PyPI.
