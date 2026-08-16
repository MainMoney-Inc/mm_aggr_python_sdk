"""Cached access token from POST /auth/tokens/exchange/."""

from __future__ import annotations

from datetime import UTC, datetime


class AccessToken:
    def __init__(
        self,
        access_token: str,
        token_type: str,
        expires_in: int,
        expires_at: datetime,
    ) -> None:
        self.access_token = access_token
        self.token_type = token_type
        self.expires_in = expires_in
        self.expires_at = expires_at

    def is_expiring(self, skew_seconds: int = 60) -> bool:
        now = datetime.now(tz=self.expires_at.tzinfo or UTC)
        threshold = self.expires_at.timestamp() - skew_seconds
        return now.timestamp() >= threshold
