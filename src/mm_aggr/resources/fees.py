"""Fee listing and simulation."""

from __future__ import annotations

from typing import Any

from mm_aggr.http.transport import JsonValue
from mm_aggr.resources.resource import Resource


class Fees(Resource):
    def list(self, query: dict[str, Any] | None = None) -> JsonValue:
        return self._transport.get("manage/general/fees/", query or {})

    def simulate(self, payload: dict[str, Any]) -> JsonValue:
        return self._transport.post("manage/general/fees/simulate/", payload)
