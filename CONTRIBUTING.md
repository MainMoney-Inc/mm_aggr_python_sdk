# Contributing

This document is for people who change **this repository**. To install the
package into an application, see [README.md](README.md).

## Legal

Pull requests require agreement to [CLA.md](CLA.md). Contributions are owned
by MainMoney SARL.

## Clone

```bash
git clone git@github.com:MainMoney-Inc/mm_aggr_python_sdk.git
```

## Setup

```bash
uv sync --all-extras
# or: poetry install
uv run pytest
uv run mypy src
uv run ruff check .
uv run ruff format --check .
```

## PyPI

The package name is `mm-aggr`. First publish is a one-time project create on
[PyPI](https://pypi.org/project/mm-aggr/) (Trusted Publisher to this GitHub
repo, or an API token). After that, release with:

```bash
uv build
uv publish
```

Release by pushing an annotated tag (`v0.1.0`, then semver). Do not commit
PyPI tokens.

## Branches and commits

- `feature/<name>`, `bugfix/<name>`, `hotfix/<issue>`, `refactor/<description>`
- Conventional commits: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## Pull requests

- Include tests for behavior changes.
- Do not invent merchant API endpoints. Implement from the pinned OpenAPI in
  the contrib hub (`contract/openapi/merchants.openapi.yaml`, checkout path
  `contrib/contract/` from `mm_aggregator`). Cross-check live
  `/api/v1/schema/merchants/` if the pin may be behind.
- Do not commit secrets.
- Local demos live under `examples/`. Working SQLite (`db.sqlite3`) is gitignored;
  commit `data/initial.sqlite3` only when the mini-shop schema or catalog changes.
