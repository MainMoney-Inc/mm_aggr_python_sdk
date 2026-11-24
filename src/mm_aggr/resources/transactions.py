"""Merchant transaction lists."""

from __future__ import annotations

from typing import Any

from mm_aggr.http.transport import JsonValue
from mm_aggr.resources.resource import Resource


class Transactions(Resource):
    def list(
        self,
        operation_type: str,
        query: dict[str, Any] | None = None,
        merchant_account: str | None = None,
    ) -> JsonValue:
        return self._transport.get(
            f"manage/merchant-admin/transactions/{operation_type}/",
            query or {},
            self._account_headers(merchant_account),
        )
