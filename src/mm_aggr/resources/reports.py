"""Merchant reports (charts and summary)."""

from __future__ import annotations

from typing import Any

from mm_aggr.http.transport import JsonValue
from mm_aggr.resources.resource import Resource


class Reports(Resource):
    def charts(self, query: dict[str, Any] | None = None, merchant_account: str | None = None) -> JsonValue:
        """``GET /manage/merchant-admin/reports/charts/``: daily volume series (``volume_by_day``)."""
        return self._transport.get(
            "manage/merchant-admin/reports/charts/", query or {}, self._account_headers(merchant_account)
        )

    def summary(self, query: dict[str, Any] | None = None, merchant_account: str | None = None) -> JsonValue:
        """``GET /manage/merchant-admin/reports/summary/``: ``totals_by_provider`` and ``top_transactions``."""
        return self._transport.get(
            "manage/merchant-admin/reports/summary/", query or {}, self._account_headers(merchant_account)
        )
