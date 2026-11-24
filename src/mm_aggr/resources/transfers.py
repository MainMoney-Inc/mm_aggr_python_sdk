"""MainMoney Rails: transfers between a platform and its sub-merchants (sellers)."""

from __future__ import annotations

from typing import Any

from mm_aggr.http.transport import JsonValue
from mm_aggr.resources.resource import Resource


class Transfers(Resource):
    def list(self, query: dict[str, Any] | None = None) -> JsonValue:
        """``GET /transactions/transfers/``; optional ``reference`` and ``sub_merchant_id`` filters."""
        return self._transport.get("transactions/transfers/", query or {})

    def create(self, payload: dict[str, Any]) -> JsonValue:
        """``POST /transactions/transfers/`` (``reference``, ``direction``, ``sub_merchant_id``, ``amount``, ...)."""
        return self._transport.post("transactions/transfers/", payload)

    def get(self, id: str) -> JsonValue:  # noqa: A002
        return self._transport.get(f"transactions/transfers/{id}/")
