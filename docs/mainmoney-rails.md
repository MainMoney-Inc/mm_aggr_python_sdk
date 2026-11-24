# MainMoney Rails: sellers, KYB, acting on behalf, transfers

**Purpose.** For platforms that onboard sellers (sub-merchants), act for them, and move funds between wallets.

**Prerequisites.** A platform account with MainMoney Rails enabled. The contract names no scope for these
endpoints and is silent on what an account without Rails receives.

## 1. Create a seller

```python
countries = client.sellers.countries()  # GET /sellers/countries/ -> [{"id", "code", "name"}]
seller = client.sellers.create(
    {  # POST /sellers/
        "sub_type": "LEGAL",  # LEGAL = verified business, LOGIC = wallets only
        "name": "Mama Shop",
        "email": "owner@mamashop.example",
        "country": countries[0]["id"],  # the country *id*
        "legal_name": "Mama Shop SARL",  # optional: legal_name, phone_number, registration_number, tax_id
    }
)
seller_id = seller["id"]  # use it as X-Merchant-Account
```

`LOGIC` sellers can transact immediately; `LEGAL` sellers once the KYB case is `APPROVED`. The seller gets a wallet
for each market of your account in its country. Seller fields: `id`, `name`, `legal_name`, `email`,
`sub_merchant_type`, `kyb_status`, `is_operational`, `created_at`.

Other calls: `sellers.list()` (`GET /sellers/`), `sellers.get(id)` (adds `country`, `notification_email`,
`phone_number`, `registration_number`, `tax_id`, `kyb`), `sellers.update(id, {...})` (`PATCH /sellers/{id}/`; name,
legal_name, email, notification_email, phone_number, registration_number, tax_id; the country cannot change).

## 2. Verify a business (KYB)

Option A, collect it yourself:

```python
client.sellers.update_kyb(
    seller_id,
    {  # PATCH /sellers/{id}/kyb/ while DRAFT
        "jurisdiction": "CD",
        "ubos": [{"name": "Jane Doe", "ownership_pct": "100", "nationality": "CD", "date_of_birth": "1985-04-02"}],
        # or "no_ubo_reason": "..." when there are no beneficial owners
    },
)
start = client.sellers.start_kyb(seller_id)  # POST .../kyb/start/ -> freezes the data
token = start["capture_token"]  # {"token", "expires_at", "upload_url"} or None
```

Upload the documents yourself: `POST` each as `multipart/form-data` to `capture_token.upload_url` with header
`X-Capture-Token: <token>` (outside this SDK). Calling `start_kyb` again returns a fresh token for the same session.
Then:

```python
client.sellers.submit_kyb(seller_id)  # POST .../kyb/submit/ -> HTTP 202, status IN_REVIEW
client.sellers.get_kyb(seller_id)["status"]  # poll: APPROVED, REJECTED or EXPIRED
```

Submit is refused, naming the missing documents, while one is missing. `status` values: `DRAFT`, `IN_REVIEW`,
`APPROVED` (can transact), `REJECTED`, `EXPIRED` (correct the data with `update_kyb` and start again), or null for a
seller without verification. The contract does not list the required documents.

Option B, hosted page:

```python
link = client.sellers.create_onboarding_link(seller_id)  # POST .../onboarding-link/ -> {"url", "token", "expires_at"}
client.sellers.revoke_onboarding_link(seller_id)  # DELETE -> {"revoked": <count>}
```

Send `link["url"]` to the business (shown once); a new link replaces the previous one.

## 3. Act on behalf of a seller (`X-Merchant-Account`)

The header makes the request run as that seller: its wallets, fees and limits apply and the record is attributed to
it. HTTP 403 when the seller is unknown, not yours or not active. Supported by deposits, deposit validate-payment,
payouts (standard, business, business merchant-account), refunds, remittances, status check, payment links,
wallets, merchant-admin transactions and reports.

```python
# whole client
seller_client = client.with_merchant_account(seller_id)  # shares the HTTP client and token cache
seller_client.deposits.create({...}, idempotency_key="k1")

# or the whole constructor: Client(..., merchant_account=seller_id)
# or one call (wins over the client-wide value):
client.deposits.create({...}, idempotency_key="k1", merchant_account=seller_id)
client.wallets.list(merchant_account=seller_id)
```

Resources without the header in the contract (countries, providers, fees, pricing, customers, transfers, sellers,
card-deposit/card-payout paths) never send it, even from a scoped client. Deposits and payouts may also carry
`application_fee` or `application_fee_percent` (not together) to take a platform fee from the seller.

## 4. Transfers between wallets

```python
t = client.transfers.create(
    {  # POST /transactions/transfers/
        "reference": "TOPUP-1",  # unique per platform; same details again is a replay
        "direction": "TO_SUB_MERCHANT",  # or FROM_SUB_MERCHANT (sweep back)
        "sub_merchant_id": seller_id,
        "amount": "50.00",
        "currency": "USD",
        "description": "Float top-up",  # optional
    }
)
client.transfers.get(t["id"])  # GET /transactions/transfers/{id}/
client.transfers.list({"sub_merchant_id": seller_id})  # also filter: reference
```

Transfer fields: `id`, `reference`, `direction`, `platform_merchant_id`, `sub_merchant_id`, `amount`, `currency`,
`description`, `channel` (`API`, `BACKOFFICE`), `created_at`. The create answers 201 (new) or 200 (replay). The
contract documents no error bodies for transfers (insufficient balance, wrong currency): handle `ApiException`.

## Minimal example

```python
seller = client.sellers.create(
    {"sub_type": "LOGIC", "name": "Kiosk", "email": "k@example.com", "country": countries[0]["id"]}
)
scoped = client.with_merchant_account(seller["id"])
print(scoped.wallets.list())
```
