"""Deposit operations."""

from __future__ import annotations

from typing import Any

from mm_aggr.http.transport import JsonValue
from mm_aggr.resources.resource import Resource


class Deposits(Resource):
    def create(
        self,
        payload: dict[str, Any],
        idempotency_key: str | None = None,
        merchant_account: str | None = None,
    ) -> JsonValue:
        return self._transport.post("transactions/deposits/", payload, self._headers(idempotency_key, merchant_account))

    def validate_payment(
        self,
        payload: dict[str, Any] | None = None,
        merchant_account: str | None = None,
    ) -> JsonValue:
        return self._transport.post(
            "transactions/deposits/validate-payment/", payload or {}, self._headers(None, merchant_account)
        )

    def validate_card_payment(self, payload: dict[str, Any] | None = None) -> JsonValue:
        """``POST /transactions/card-deposits/validate-payment/`` (no ``X-Merchant-Account`` in the contract)."""
        return self._transport.post("transactions/card-deposits/validate-payment/", payload or {})
