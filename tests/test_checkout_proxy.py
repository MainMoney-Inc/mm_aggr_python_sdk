"""Checkout proxy dispatch and JS SDK route parity."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

from mm_aggr import Client
from mm_aggr.checkout_proxy import CHECKOUT_ROUTES, dispatch, handle
from mm_aggr.http.http_response import HttpResponse
from tests.mock_http_client import MockHttpClient

JS_PATHS = Path(__file__).resolve().parents[2] / "javascript" / "packages" / "core" / "src" / "paths.ts"


def _envelope(data: Any, code: int = 200) -> HttpResponse:
    body = {"success": code < 400, "response_code": code, "response_data": data, "message": "ok"}
    return HttpResponse(code, json.dumps(body))


def _client(*responses: HttpResponse) -> tuple[Client, MockHttpClient]:
    mock = MockHttpClient()
    expires_at = (datetime.now(UTC) + timedelta(hours=1)).isoformat()
    token = {"access_token": "tok", "token_type": "Bearer", "expires_in": 3600, "expires_at": expires_at}
    mock.enqueue(HttpResponse(200, json.dumps(token)), *responses)
    client = Client("id", "secret", base_uri="https://example.test/api/v1/", http_client=mock)
    return client, mock


@pytest.mark.parametrize(
    ("method", "route", "uri_part"),
    [
        ("GET", "countries", "/countries"),
        ("GET", "providers", "financial-entities"),
        ("GET", "match-provider", "match-provider"),
        ("GET", "amount-limits", "amount-limits"),
        ("POST", "fees/simulate", "fee"),
        ("GET", "checkout-preferences", "checkout-preferences"),
        ("POST", "deposits", "deposits"),
        ("POST", "deposits/validate", "validate-payment"),
        ("POST", "payouts", "payouts"),
        ("GET", "status", "status/check"),
    ],
)
def test_every_route_reaches_the_aggregator(method: str, route: str, uri_part: str) -> None:
    client, mock = _client(_envelope({"ok": True}))
    result = dispatch(client, method, f"/{route}/", {"account_number": "1"}, {}, reference="R1")
    assert result == {"ok": True}
    assert uri_part in mock.history[-1]["uri"]


def test_routes_table_covers_every_dispatch_route() -> None:
    assert {route for _, route in CHECKOUT_ROUTES} >= {
        "countries",
        "providers",
        "match-provider",
        "amount-limits",
        "fees/simulate",
        "checkout-preferences",
        "deposits",
        "deposits/validate",
        "payouts",
        "status",
    }


def test_deposit_passes_payment_currency_unchanged_and_overrides_win() -> None:
    client, mock = _client(_envelope({"status": "PENDING"}))
    body = {
        "provider_code": "P",
        "reference": "browser-ref",
        "amount": "1.00",
        "currency": "EUR",
        "payment_currency": "CDF",
        "customer_phone": "243987805910",
    }
    dispatch(
        client,
        "POST",
        "deposits",
        body=body,
        reference="ORDER-1",
        idempotency_key="key-1",
        overrides={"amount": "10.00", "currency": "USD"},
    )
    request = mock.history[-1]["options"]
    assert request["json"]["payment_currency"] == "CDF"
    assert request["json"]["reference"] == "ORDER-1"
    assert request["json"]["amount"] == "10.00"
    assert request["json"]["currency"] == "USD"
    assert request["headers"]["Idempotency-Key"] == "key-1"


def test_match_provider_forwards_e164_account_and_lookup_flag() -> None:
    client, mock = _client(_envelope({"entity": "MTN"}))
    dispatch(client, "GET", "match-provider", {"account_number": "243987805910", "get_lookup": "true"})
    params = mock.history[-1]["options"]["query"]
    assert params["account_number"] == "243987805910"
    assert params["get_lookup"] == "true"


def test_unknown_route_is_rejected() -> None:
    client, _ = _client()
    with pytest.raises(ValueError):
        dispatch(client, "GET", "nope")
    assert handle(client, "GET", "nope") == (404, {"message": "Unknown merchant backend path"})


def test_handle_maps_api_errors() -> None:
    client, _ = _client(_envelope({"errors": {"amount": ["bad"]}}, 400))
    status, payload = handle(client, "POST", "deposits", body={})
    assert status == 400
    assert "message" in payload


def test_python_covers_every_js_default_path() -> None:
    if not JS_PATHS.exists():
        pytest.skip("JS SDK checkout not next to the Python SDK (standalone checkout)")
    paths = re.findall(r':\s*"(/[^"]*)"', JS_PATHS.read_text().split("DEFAULT_PATHS", 1)[1])
    assert paths, "could not parse DEFAULT_PATHS"
    python_routes = {route for _, route in CHECKOUT_ROUTES}
    missing = [path for path in paths if path.strip("/") not in python_routes]
    assert missing == [], f"JS DEFAULT_PATHS without a Python route: {missing}"
