"""Build a MainMoney SDK client from the environment."""

from __future__ import annotations

import os


def get_client():
    from mm_aggr import Client

    return Client(
        client_id=os.environ.get("MM_CLIENT_ID", ""),
        secret=os.environ.get("MM_API_SECRET", ""),
        base_uri=os.environ.get("MM_BASE_URI") or None,
        test=os.environ.get("MM_TEST", "true").lower() in {"1", "true", "yes"},
    )
