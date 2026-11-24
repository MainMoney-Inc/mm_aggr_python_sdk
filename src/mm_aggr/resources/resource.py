"""Base merchant API resource."""

from __future__ import annotations

from mm_aggr.http.transport import Transport

MERCHANT_ACCOUNT_HEADER = "X-Merchant-Account"


class Resource:
    """Base class. ``merchant_account`` is the client-wide default for ``X-Merchant-Account`` (MainMoney Rails)."""

    def __init__(self, transport: Transport, merchant_account: str | None = None) -> None:
        self._transport = transport
        self._merchant_account = merchant_account

    def _idempotency_headers(self, idempotency_key: str | None) -> dict[str, str]:
        if idempotency_key is None or idempotency_key == "":
            return {}
        return {"Idempotency-Key": idempotency_key}

    def _account_headers(self, merchant_account: str | None = None) -> dict[str, str]:
        """``X-Merchant-Account``: the per-call value wins over the client-wide default; none sends no header."""
        account = merchant_account if merchant_account else self._merchant_account
        if not account:
            return {}
        return {MERCHANT_ACCOUNT_HEADER: account}

    def _headers(
        self,
        idempotency_key: str | None = None,
        merchant_account: str | None = None,
    ) -> dict[str, str]:
        return {**self._idempotency_headers(idempotency_key), **self._account_headers(merchant_account)}
