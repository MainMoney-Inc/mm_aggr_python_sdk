"""Exchange client_id/secret for a Bearer token and cache it."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from typing import Any

from mm_aggr.auth.access_token import AccessToken
from mm_aggr.exceptions import AuthenticationException
from mm_aggr.http.http_client import HttpClient


class TokenStore:
    def __init__(
        self,
        http: HttpClient,
        base_uri: str,
        client_id: str,
        secret: str,
        expires_in: int | None = None,
    ) -> None:
        self._http = http
        self._base_uri = base_uri
        self._client_id = client_id
        self._secret = secret
        self._expires_in = expires_in
        self._current: AccessToken | None = None

    def get_access_token(self) -> str:
        if self._current is None or self._current.is_expiring():
            self._current = self._exchange()
        return self._current.access_token

    def invalidate(self) -> None:
        self._current = None

    def _exchange(self) -> AccessToken:
        body: dict[str, Any] = {
            "client_id": self._client_id,
            "secret": self._secret,
        }
        if self._expires_in is not None:
            body["expires_in"] = self._expires_in

        url = self._base_uri.rstrip("/") + "/auth/tokens/exchange/"
        response = self._http.request(
            "POST",
            url,
            {
                "headers": {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                "json": body,
            },
        )
        try:
            decoded = json.loads(response.body) if response.body else None
        except json.JSONDecodeError:
            decoded = None
        access_token = decoded.get("access_token") if isinstance(decoded, dict) else None
        if response.status_code >= 400 or not isinstance(access_token, str):
            raise AuthenticationException("Token exchange failed")

        expires_at_raw = decoded.get("expires_at") if isinstance(decoded, dict) else None
        expires_at = (
            _parse_expires_at(expires_at_raw)
            if isinstance(expires_at_raw, str)
            else datetime.now(UTC) + timedelta(hours=1)
        )
        token_type = decoded.get("token_type") if isinstance(decoded, dict) else None
        expires_in_raw = decoded.get("expires_in") if isinstance(decoded, dict) else None
        expires_in = int(expires_in_raw) if isinstance(expires_in_raw, (int, float, str)) else 3600

        return AccessToken(
            access_token=access_token,
            token_type=token_type if isinstance(token_type, str) else "Bearer",
            expires_in=expires_in,
            expires_at=expires_at,
        )


def _parse_expires_at(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00") if value.endswith("Z") else value
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed
