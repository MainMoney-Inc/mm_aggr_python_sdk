"""Payout operations."""

from __future__ import annotations

from typing import Any

from mm_aggr.http.transport import JsonValue
from mm_aggr.resources.resource import Resource


class Payouts(Resource):
    def create(self, payload: dict[str, Any], idempotency_key: str | None = None) -> JsonValue:
        return self._transport.post(
            "transactions/payouts/",
            payload,
            self._idempotency_headers(idempotency_key),
        )

    def create_business(self, payload: dict[str, Any], idempotency_key: str | None = None) -> JsonValue:
        return self._transport.post(
            "transactions/payouts/business/",
            payload,
            self._idempotency_headers(idempotency_key),
        )

    def create_business_merchant_account(
        self,
        payload: dict[str, Any],
        idempotency_key: str | None = None,
    ) -> JsonValue:
        return self._transport.post(
            "transactions/payouts/business/merchant-account/",
            payload,
            self._idempotency_headers(idempotency_key),
        )
