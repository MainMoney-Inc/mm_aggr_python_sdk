# Changelog

## Unreleased

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
