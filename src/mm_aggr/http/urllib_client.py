"""Default HTTP client using urllib (no runtime dependency)."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from mm_aggr.exceptions import ApiException
from mm_aggr.http.http_response import HttpResponse


class UrllibHttpClient:
    def __init__(self, timeout: float = 30.0) -> None:
        self._timeout = timeout

    def request(self, method: str, uri: str, options: dict[str, Any] | None = None) -> HttpResponse:
        opts = options or {}
        headers = _string_headers(opts.get("headers"))
        query = opts.get("query")
        if isinstance(query, dict) and query:
            uri = _append_query(uri, query)

        body = b""
        json_body = opts.get("json")
        if json_body is not None:
            if not isinstance(json_body, dict):
                raise ApiException("JSON body must be an object", 0)
            encoded = json.dumps(json_body).encode("utf-8")
            body = encoded
            headers.setdefault("Accept", "application/json")
            headers.setdefault("Content-Type", "application/json")

        request = urllib.request.Request(uri, data=body or None, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=self._timeout) as response:
                raw = response.read()
                return HttpResponse(
                    status_code=int(response.status),
                    body=raw.decode("utf-8", errors="replace"),
                    headers=_multi_headers(response.headers.items()),
                )
        except urllib.error.HTTPError as error:
            raw = error.read()
            return HttpResponse(
                status_code=int(error.code),
                body=raw.decode("utf-8", errors="replace"),
                headers=_multi_headers(error.headers.items()),
            )
        except urllib.error.URLError as error:
            raise ApiException(f"HTTP request failed: {uri}", 0) from error


def _string_headers(header_bag: Any) -> dict[str, str]:
    if not isinstance(header_bag, dict):
        return {}
    headers: dict[str, str] = {}
    for name, value in header_bag.items():
        if isinstance(name, str) and isinstance(value, (str, int, float)):
            headers[name] = str(value)
    return headers


def _append_query(uri: str, query: dict[str, Any]) -> str:
    filtered: dict[str, str] = {}
    for name, value in query.items():
        if isinstance(name, str) and isinstance(value, (str, int, float, bool)):
            filtered[name] = str(value)
    if not filtered:
        return uri
    separator = "&" if "?" in uri else "?"
    return uri + separator + urllib.parse.urlencode(filtered)


def _multi_headers(items: Any) -> dict[str, list[str]]:
    headers: dict[str, list[str]] = {}
    for name, value in items:
        key = str(name).lower()
        headers.setdefault(key, []).append(str(value))
    return headers
