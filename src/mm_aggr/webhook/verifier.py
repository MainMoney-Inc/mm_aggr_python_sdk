"""Verify inbound aggregator webhooks."""

from __future__ import annotations

import hashlib
import hmac

from mm_aggr.exceptions import WebhookSignatureException


class WebhookVerifier:
    def verify(self, raw_body: str, signature: str, secret: str) -> bool:
        if signature == "" or secret == "":
            return False
        expected = hmac.new(
            key=secret.encode("utf-8"),
            msg=raw_body.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature.lower())

    def verify_or_fail(self, raw_body: str, signature: str, secret: str) -> None:
        if not self.verify(raw_body, signature, secret):
            raise WebhookSignatureException("Invalid X-Webhook-Signature")
