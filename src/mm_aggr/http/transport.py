"""Authenticated JSON transport for the merchant API."""

from __future__ import annotations

import json
from typing import Any

from mm_aggr.auth.token_store import TokenStore
from mm_aggr.exceptions import ApiException, AuthenticationException
from mm_aggr.http.http_client import HttpClient
from mm_aggr.http.http_response import HttpResponse

JsonValue = dict[str, Any] | list[Any]


class Transport:
    def __init__(self, http: HttpClient, base_uri: str, tokens: TokenStore) -> None:
        self._http = http
        self._base_uri = base_uri
        self._tokens = tokens

    def post(
        self,
        path: str,
        body: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> JsonValue:
        return self._request("POST", path, body if body is not None else {}, {}, headers or {})

    def get(
        self,
        path: str,
        query: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> JsonValue:
        return self._request("GET", path, None, query or {}, headers or {})

    def _request(
        self,
        method: str,
        path: str,
        body: dict[str, Any] | None,
        query: dict[str, Any],
        headers: dict[str, str],
        retried: bool = False,
    ) -> JsonValue:
        headers = dict(headers)
        headers["Authorization"] = f"Bearer {self._tokens.get_access_token()}"
        try:
            response = self._send(method, path, body, query, headers)
        except AuthenticationException:
            if retried:
                raise
            self._tokens.invalidate()
            headers.pop("Authorization", None)
            return self._request(method, path, body, query, headers, True)
        return self._decode(response)

    def _send(
        self,
        method: str,
        path: str,
        body: dict[str, Any] | None,
        query: dict[str, Any],
        headers: dict[str, str],
    ) -> HttpResponse:
        options: dict[str, Any] = {"headers": headers}
        if body is not None:
            options["json"] = body
        filtered_query = {key: value for key, value in query.items() if value is not None and value != ""}
        if filtered_query:
            options["query"] = filtered_query
        response = self._http.request(method, self._url(path), options)
        if response.status_code == 401:
            raise AuthenticationException("Authentication failed")
        return response

    def _decode(self, response: HttpResponse) -> JsonValue:
        status = response.status_code
        raw = response.body
        parsed: Any = [] if raw == "" else _json_object(raw)
        decoded: JsonValue = parsed if isinstance(parsed, (dict, list)) else []

        if status >= 400:
            if isinstance(decoded, dict) and decoded.get("success") is False:
                raise ApiException.from_envelope(decoded, status)
            detail = None
            if isinstance(decoded, dict):
                detail = decoded.get("detail", decoded.get("message", raw))
            message = detail if isinstance(detail, str) else "Aggregator request failed"
            raise ApiException(message, status, decoded if isinstance(decoded, dict) else {}, decoded)

        if isinstance(decoded, dict) and "success" in decoded:
            if decoded["success"] is False:
                raise ApiException.from_envelope(decoded, status)
            data = decoded.get("response_data") or []
            return data if isinstance(data, (dict, list)) else []

        return decoded

    def _url(self, path: str) -> str:
        return self._base_uri.rstrip("/") + "/" + path.lstrip("/")


def _json_object(raw: str) -> Any:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return []
