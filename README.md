# MainMoney Python SDK

Python client for the MainMoney aggregator merchant API. Install this package
in your Python application (Django, FastAPI, Flask, or scripts).

The [JS/TS frontend SDK](https://github.com/MainMoney-Inc/mm_aggr_js_sdk) can
be used in the browser only if this SDK (or the PHP or Node SDK) runs on your
server. Never put merchant API keys in frontend code.

## Requirements

- Python 3.11 or later (3.13 or 3.14 recommended)
- A merchant application on MM Aggregator

## Install

With uv (recommended):

```bash
uv add mm-aggr
```

With pip:

```bash
pip install mm-aggr
```

With Poetry:

```bash
poetry add mm-aggr
```

## Quick start

```python
from mm_aggr import Client

client = Client(
    base_uri="https://your-aggregator.example/api/v1/",
    api_key="your-api-key",
)
```

See merchant API docs at `/api/v1/docs/merchants/` on your aggregator host.
Payment methods will be added in a later release.

## License

Copyright (c) 2026 MainMoney SARL. Licensed under the PolyForm Noncommercial
License 1.0.0. Non-commercial use is allowed. Commercial use requires
permission from MainMoney SARL. See [LICENSE](LICENSE).

Want to contribute? See [CONTRIBUTING.md](CONTRIBUTING.md).
