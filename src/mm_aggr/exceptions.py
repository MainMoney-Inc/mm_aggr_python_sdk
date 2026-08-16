"""Exceptions raised by the MainMoney aggregator SDK."""

from __future__ import annotations

from typing import Any


class AggregatorException(Exception):
    """Base exception for all SDK errors."""


class AuthenticationException(AggregatorException):
    """Token exchange failed or the API returned HTTP 401."""


class WebhookSignatureException(AggregatorException):
    """Inbound webhook HMAC verification failed."""


class ApiException(AggregatorException):
    """Aggregator request failed with an HTTP or envelope error."""

    def __init__(
        self,
        message: str,
        status_code: int,
        errors: dict[str, Any] | None = None,
        response_body: Any = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.errors: dict[str, Any] = errors if errors is not None else {}
        self.response_body = response_body

    @classmethod
    def from_envelope(cls, envelope: dict[str, Any], status_code: int) -> ApiException:
        message = envelope.get("message")
        if not isinstance(message, str):
            message = "Aggregator request failed"
        response_data = envelope.get("response_data") or {}
        errors: dict[str, Any] = {}
        if isinstance(response_data, dict):
            raw_errors = response_data.get("errors")
            if isinstance(raw_errors, dict):
                errors = raw_errors
        return cls(message, status_code, errors, envelope)
