"""Checkout branding for the JS/TS frontend SDK."""

from __future__ import annotations

from mm_aggr.http.transport import JsonValue
from mm_aggr.resources.resource import Resource


class CheckoutPreferences(Resource):
    def get(self) -> JsonValue:
        return self._transport.get("manage/general/checkout-preferences/")
