"""Default HTTP client using requests."""

from __future__ import annotations

from typing import Any

import requests

from mm_aggr.exceptions import ApiException
from mm_aggr.http.http_response import HttpResponse


class RequestsHttpClient:
    def __init__(self, timeout: float = 30.0) -> None:
        self._timeout = timeout
        self._session = requests.Session()

    def request(self, method: str, uri: str, options: dict[str, Any] | None = None) -> HttpResponse:
        opts = options or {}
        headers = _string_headers(opts.get("headers"))
        json_body = opts.get("json")
        if json_body is not None:
            if not isinstance(json_body, dict):
                raise ApiException("JSON body must be an object", 0)
            headers.setdefault("Accept", "application/json")
            headers.setdefault("Content-Type", "application/json")

        query = opts.get("query")
        params = query if isinstance(query, dict) else None
        try:
            response = self._session.request(
                method,
                uri,
                headers=headers,
                json=json_body if isinstance(json_body, dict) else None,
                params=params,
                timeout=self._timeout,
            )
        except requests.RequestException as error:
            raise ApiException(f"HTTP request failed: {uri}", 0) from error

        return HttpResponse(
            status_code=int(response.status_code),
            body=response.text,
            headers=_multi_headers(response.headers.items()),
        )


def _string_headers(header_bag: Any) -> dict[str, str]:
    if not isinstance(header_bag, dict):
        return {}
    headers: dict[str, str] = {}
    for name, value in header_bag.items():
        if isinstance(name, str) and isinstance(value, (str, int, float)):
            headers[name] = str(value)
    return headers


def _multi_headers(items: Any) -> dict[str, list[str]]:
    headers: dict[str, list[str]] = {}
    for name, value in items:
        key = str(name).lower()
        headers.setdefault(key, []).append(str(value))
    return headers
