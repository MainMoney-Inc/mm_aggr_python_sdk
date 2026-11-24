"""Merchant pricing per operation type."""

from __future__ import annotations

from typing import Any

from mm_aggr.http.transport import JsonValue
from mm_aggr.resources.resource import Resource


class Pricing(Resource):
    def get(self, query: dict[str, Any] | None = None) -> JsonValue:
        """``GET /manage/general/pricing/``; optional ``financial_entity_code`` and ``operation_type``."""
        return self._transport.get("manage/general/pricing/", query or {})
