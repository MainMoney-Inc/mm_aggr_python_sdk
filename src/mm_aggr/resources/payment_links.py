"""Payment link operations (API key scope ``PAYMENT_LINK``)."""

from __future__ import annotations

from typing import Any

from mm_aggr.http.transport import JsonValue
from mm_aggr.resources.resource import Resource


class PaymentLinks(Resource):
    """Hosted payment links. Pass ``merchant_account`` to act on behalf of one of your sellers.

    ``merchant_account`` is sent as the ``X-Merchant-Account`` header (MainMoney Rails only).
    """

    def create(
        self,
        payload: dict[str, Any],
        idempotency_key: str | None = None,
        merchant_account: str | None = None,
    ) -> JsonValue:
        return self._transport.post(
            "payment-links/",
            payload,
            {**self._idempotency_headers(idempotency_key), **self._account_headers(merchant_account)},
        )

    def list(self, query: dict[str, Any] | None = None, merchant_account: str | None = None) -> JsonValue:
        return self._transport.get("payment-links/", query or {}, self._account_headers(merchant_account))

    def get(self, id: str, merchant_account: str | None = None) -> JsonValue:  # noqa: A002
        return self._transport.get(f"payment-links/{id}/", None, self._account_headers(merchant_account))

    def cancel(self, id: str, merchant_account: str | None = None) -> JsonValue:  # noqa: A002
        return self._transport.post(f"payment-links/{id}/cancel/", {}, self._account_headers(merchant_account))

    @staticmethod
    def _account_headers(merchant_account: str | None) -> dict[str, str]:
        if merchant_account is None or merchant_account == "":
            return {}
        return {"X-Merchant-Account": merchant_account}
