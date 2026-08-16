"""Webhook HMAC verification."""

from __future__ import annotations

import hashlib
import hmac
import json

import pytest

from mm_aggr.exceptions import WebhookSignatureException
from mm_aggr.webhook.verifier import WebhookVerifier


def test_accepts_python_canonical_json_hmac() -> None:
    payload = {
        "amount": "100.00",
        "currency": "KES",
        "merchant_reference": "ORDER-123",
        "type": "DEPOSIT",
    }
    raw_body = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    secret = "whsec_test"
    signature = hmac.new(secret.encode("utf-8"), raw_body.encode("utf-8"), hashlib.sha256).hexdigest()

    verifier = WebhookVerifier()
    assert verifier.verify(raw_body, signature, secret)


def test_rejects_tampered_body() -> None:
    raw_body = '{"amount":"100.00","currency":"KES"}'
    secret = "whsec_test"
    signature = hmac.new(secret.encode("utf-8"), raw_body.encode("utf-8"), hashlib.sha256).hexdigest()

    verifier = WebhookVerifier()
    assert not verifier.verify('{"amount":"999.00","currency":"KES"}', signature, secret)


def test_verify_or_fail_throws() -> None:
    with pytest.raises(WebhookSignatureException):
        WebhookVerifier().verify_or_fail("{}", "deadbeef", "secret")
