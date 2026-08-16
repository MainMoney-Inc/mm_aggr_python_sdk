"""Base merchant API resource."""

from __future__ import annotations

from mm_aggr.http.transport import Transport


class Resource:
    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    def _idempotency_headers(self, idempotency_key: str | None) -> dict[str, str]:
        if idempotency_key is None or idempotency_key == "":
            return {}
        return {"Idempotency-Key": idempotency_key}
