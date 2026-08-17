# Django REST Framework mini-shop

Standalone example that installs [`mm-aggr`](https://github.com/MainMoney-Inc/mm_aggr_python_sdk)
as a package and exposes the same shop API as the other SDK examples.

Pages a frontend can drive: products, pay (deposit), refund, transfer (payout).

Default port: **8000**.

## Setup

```bash
cp .env.example .env
# set MM_CLIENT_ID, MM_API_SECRET, and MM_WEBHOOK_SECRET
uv sync
./scripts/reset-db
```

Until PyPI lists `mm-aggr`, `uv sync` installs it from GitHub (see `pyproject.toml`).

If `db.sqlite3` is missing, `./scripts/reset-db` copies the committed snapshot
`data/initial.sqlite3`. To refill products after a migrate:

```bash
./scripts/seed
```

Update `data/initial.sqlite3` only when the schema or catalog changes:

```bash
uv run python manage.py migrate
./scripts/seed
./scripts/export-initial-db
```

Do not commit `db.sqlite3` (local orders and test refunds stay on your machine).

## Run

```bash
uv run python manage.py runserver 8000
```

Then start a JS frontend example and set:

```
VITE_MERCHANT_BACKEND_URL=http://127.0.0.1:8000
```

Aggregator webhooks cannot reach `localhost`. Use a tunnel if you want
`POST /webhooks` to fire. Status polling works without a public URL.

Webhook URL (after a tunnel): `https://your-host.example/webhooks`
