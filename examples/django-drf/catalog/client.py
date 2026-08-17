"""Build a MainMoney SDK client from Django settings."""

from __future__ import annotations

from django.conf import settings


def get_client():
    from mm_aggr import Client

    return Client(
        client_id=settings.MM_CLIENT_ID,
        secret=settings.MM_API_SECRET,
        base_uri=settings.MM_BASE_URI,
        test=settings.MM_TEST,
    )
