# FastAPI mini-shop

Standalone example that installs [`mm-aggr`](https://github.com/MainMoney-Inc/mm_aggr_python_sdk)
as a package. Same shop API as the Django and Flask examples.

Default port: **8001**.

## Setup

```bash
cp .env.example .env
# set MM_CLIENT_ID, MM_API_SECRET, and MM_WEBHOOK_SECRET
uv sync
./scripts/reset-db
```

Until PyPI lists `mm-aggr`, `uv sync` installs it from GitHub (see `pyproject.toml`).

```bash
./scripts/seed
```

Update `data/initial.sqlite3` only when the schema or catalog changes:

```bash
./scripts/seed
./scripts/export-initial-db
```

Do not commit `db.sqlite3`.

## Run

```bash
uv run uvicorn app:app --host 127.0.0.1 --port 8001
```

Then start a JS frontend example:

```
VITE_MERCHANT_BACKEND_URL=http://127.0.0.1:8001
```

Aggregator webhooks cannot reach `localhost`. Use a tunnel for `POST /webhooks`.
Status polling works without a public URL.
