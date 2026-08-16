"""Injectable HTTP client protocol."""

from __future__ import annotations

from typing import Any, Protocol

from mm_aggr.http.http_response import HttpResponse

RequestOptions = dict[str, Any]


class HttpClient(Protocol):
    def request(self, method: str, uri: str, options: RequestOptions | None = None) -> HttpResponse:
        """Send an HTTP request and return the raw response."""
