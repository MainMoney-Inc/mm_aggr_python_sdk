"""Customer lookup, KYC, and provider match."""

from __future__ import annotations

from typing import Any

from mm_aggr.http.transport import JsonValue
from mm_aggr.resources.resource import Resource


class Customers(Resource):
    def lookup(self, payload: dict[str, Any]) -> JsonValue:
        return self._transport.post("transactions/customers/lookup/", payload)

    def kyc(self, payload: dict[str, Any]) -> JsonValue:
        return self._transport.post("transactions/customers/kyc/", payload)

    def match_provider(self, account_number: str, get_lookup: bool = False) -> JsonValue:
        return self._transport.get(
            "transactions/customers/match-provider/",
            {
                "account_number": account_number,
                "get_lookup": "true" if get_lookup else None,
            },
        )
