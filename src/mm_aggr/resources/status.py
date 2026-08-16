"""Transaction status checks."""

from __future__ import annotations

from mm_aggr.http.transport import JsonValue
from mm_aggr.resources.resource import Resource


class Status(Resource):
    def check(self, operation_type: str, reference: str) -> JsonValue:
        return self._transport.post(
            f"transactions/status/check/{operation_type}/",
            {"reference": reference},
        )
