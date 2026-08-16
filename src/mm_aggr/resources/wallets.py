"""Merchant wallet balances."""

from __future__ import annotations

from typing import Any

from mm_aggr.http.transport import JsonValue
from mm_aggr.resources.resource import Resource


class Wallets(Resource):
    def list(self, query: dict[str, Any] | None = None) -> JsonValue:
        return self._transport.get("manage/merchant-admin/wallets/", query or {})
