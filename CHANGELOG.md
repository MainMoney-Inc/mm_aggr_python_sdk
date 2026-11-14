# Changelog

## Unreleased

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
