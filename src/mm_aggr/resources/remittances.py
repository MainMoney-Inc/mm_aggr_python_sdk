"""Remittance operations."""

from __future__ import annotations

from typing import Any

from mm_aggr.http.transport import JsonValue
from mm_aggr.resources.resource import Resource


class Remittances(Resource):
    def create(self, payload: dict[str, Any], idempotency_key: str | None = None) -> JsonValue:
        return self._transport.post(
            "transactions/remittances/",
            payload,
            self._idempotency_headers(idempotency_key),
        )
