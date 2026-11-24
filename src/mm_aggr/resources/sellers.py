"""MainMoney Rails: sellers (sub-merchants) of a platform, and their KYB verification."""

from __future__ import annotations

from typing import Any

from mm_aggr.http.transport import JsonValue
from mm_aggr.resources.resource import Resource


class Sellers(Resource):
    def list(self) -> JsonValue:
        return self._transport.get("sellers/")

    def create(self, payload: dict[str, Any]) -> JsonValue:
        return self._transport.post("sellers/", payload)

    def countries(self) -> JsonValue:
        return self._transport.get("sellers/countries/")

    def get(self, id: str) -> JsonValue:  # noqa: A002
        return self._transport.get(f"sellers/{id}/")

    def update(self, id: str, payload: dict[str, Any]) -> JsonValue:  # noqa: A002
        return self._transport.patch(f"sellers/{id}/", payload)

    def get_kyb(self, id: str) -> JsonValue:  # noqa: A002
        return self._transport.get(f"sellers/{id}/kyb/")

    def update_kyb(self, id: str, payload: dict[str, Any]) -> JsonValue:  # noqa: A002
        return self._transport.patch(f"sellers/{id}/kyb/", payload)

    def start_kyb(self, id: str) -> JsonValue:  # noqa: A002
        return self._transport.post(f"sellers/{id}/kyb/start/", {})

    def submit_kyb(self, id: str) -> JsonValue:  # noqa: A002
        return self._transport.post(f"sellers/{id}/kyb/submit/", {})

    def create_onboarding_link(self, id: str) -> JsonValue:  # noqa: A002
        return self._transport.post(f"sellers/{id}/onboarding-link/", {})

    def revoke_onboarding_link(self, id: str) -> JsonValue:  # noqa: A002
        return self._transport.delete(f"sellers/{id}/onboarding-link/")
