"""Payout operations."""

from __future__ import annotations

from typing import Any

from mm_aggr.http.transport import JsonValue
from mm_aggr.resources.resource import Resource


class Payouts(Resource):
    def create(
        self,
        payload: dict[str, Any],
        idempotency_key: str | None = None,
        merchant_account: str | None = None,
    ) -> JsonValue:
        return self._transport.post("transactions/payouts/", payload, self._headers(idempotency_key, merchant_account))

    def create_business(
        self,
        payload: dict[str, Any],
        idempotency_key: str | None = None,
        merchant_account: str | None = None,
    ) -> JsonValue:
        return self._transport.post(
            "transactions/payouts/business/", payload, self._headers(idempotency_key, merchant_account)
        )

    def create_business_merchant_account(
        self,
        payload: dict[str, Any],
        idempotency_key: str | None = None,
        merchant_account: str | None = None,
    ) -> JsonValue:
        return self._transport.post(
            "transactions/payouts/business/merchant-account/", payload, self._headers(idempotency_key, merchant_account)
        )

    def create_card_business_merchant_account(
        self,
        payload: dict[str, Any],
        idempotency_key: str | None = None,
    ) -> JsonValue:
        """``POST /transactions/card-payouts/business/merchant-account/``.

        The contract lists no ``Idempotency-Key`` or ``X-Merchant-Account`` for this path; the key is sent only
        when given.
        """
        return self._transport.post(
            "transactions/card-payouts/business/merchant-account/",
            payload,
            self._idempotency_headers(idempotency_key),
        )
