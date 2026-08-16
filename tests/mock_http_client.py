"""Queued HTTP test double that records requests."""

from __future__ import annotations

from typing import Any

from mm_aggr.http.http_response import HttpResponse


class MockHttpClient:
    def __init__(self) -> None:
        self._queue: list[HttpResponse] = []
        self.history: list[dict[str, Any]] = []

    def enqueue(self, *responses: HttpResponse) -> None:
        self._queue.extend(responses)

    def request(self, method: str, uri: str, options: dict[str, Any] | None = None) -> HttpResponse:
        self.history.append({"method": method, "uri": uri, "options": options or {}})
        if not self._queue:
            raise RuntimeError("MockHttpClient queue is empty")
        return self._queue.pop(0)
