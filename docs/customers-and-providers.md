# Countries, providers, provider matching and customer lookup

**Purpose.** Discover where and through whom you can transact, find the provider behind a phone/account number, and
look up the account holder before paying out.

**Prerequisites.** A valid token ([authentication.md](authentication.md)). The contract does not name scopes for
these read operations.

## Countries and providers

`GET /manage/general/countries/` returns the effective allow-list for your account (only countries with at least one
active provider). Send transactions only for these codes. Items: `code`, `name`, `iso3_code`, `phone_code`, `flag`
(URL or null). Paginated (`count`, `next`, `previous`, `results`); query `page`, `page_size`, `search`, `ordering`.

`GET /manage/general/financial-entities/` returns providers filtered to those countries. Query: `country`,
`entity_type`, `operation_type` (when set, only providers you can run that operation on), plus the pagination keys.
Items: `code` (the `provider_code` you send on transactions), `name`, `entity_type`, `country_code`, `currency_code`,
`accepted_currencies`, `logo`, `is_active`.

```python
countries = client.countries.list()
providers = client.providers.list({"country": "CD", "operation_type": "deposit"})
for p in providers["results"]:
    print(p["code"], p["accepted_currencies"])
```

Countries and providers are read-only; allowing a country is a back-office action. The contract suggests caching
countries, providers, limits and checkout preferences (for example 24 hours).

## Match a provider from a number

`GET /transactions/customers/match-provider/`: `account_number` (required), `get_lookup` (boolean, also return
account information when the provider supports it), `operation_type` (optional).

```python
match = client.customers.match_provider("243840000000", get_lookup=True, operation_type="payout")
```

Response (`CustomerLookupResponse`): `account_number`, `is_active`, `name`, `account_type`, `additional_info`. The
contract does not document which key carries the matched provider code; inspect the live response.

## Customer lookup and KYC

```python
info = client.customers.lookup({"provider_code": "VODACOM_MPESA_COD", "account_number": "243820000000"})
kyc = client.customers.kyc({"provider_code": "VODACOM_MPESA_COD", "account_number": "243820000000"})
```

Lookup body: `provider_code`, `account_number` (required), `account_type` (`bank`, `mobile_money`, optional). Lookup
answers `account_number`, `is_active`, `name`, `account_type`, `additional_info`. KYC answers the same plus
`first_name`, `last_name`, `dob`, `id_number`, `nationality`, `grade`, `barred`, `lookup_supported`, `error_code`,
`message`. KYC uses the `USER_KYC` adapter routing when configured; the contract does not say what happens otherwise.

Errors: 400 validation, 401 credentials (see [errors.md](errors.md)).

## Minimal example

```python
match = client.customers.match_provider("243820000000", get_lookup=True)
if not match.get("is_active"):
    raise SystemExit("Account cannot receive funds")
```
