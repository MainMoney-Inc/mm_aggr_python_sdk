"""Client auth, envelope, and resource request coverage."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta

import pytest
from tests.mock_http_client import MockHttpClient

from mm_aggr import Client
from mm_aggr.exceptions import ApiException, AuthenticationException
from mm_aggr.http.http_response import HttpResponse


def _client_with_mock(responses: list[HttpResponse]) -> tuple[Client, MockHttpClient]:
    mock = MockHttpClient()
    mock.enqueue(*responses)
    client = Client(
        client_id="client-id",
        secret="secret",
        base_uri="https://example.test/api/v1/",
        http_client=mock,
    )
    return client, mock


def _token_response(token: str = "tok_1") -> HttpResponse:
    expires_at = (datetime.now(UTC) + timedelta(hours=1)).isoformat()
    return HttpResponse(
        200,
        json.dumps(
            {
                "access_token": token,
                "token_type": "Bearer",
                "expires_in": 3600,
                "expires_at": expires_at,
            }
        ),
    )


def test_token_exchange_then_bearer_on_follow_up() -> None:
    client, mock = _client_with_mock(
        [
            _token_response(),
            HttpResponse(
                200,
                json.dumps(
                    {
                        "success": True,
                        "response_code": 202,
                        "response_data": {"status": "PENDING", "merchant_reference": "ORDER-1"},
                        "message": "ok",
                    }
                ),
            ),
        ]
    )

    result = client.deposits.create(
        {
            "provider_code": "VODACOM_MPESA_COD",
            "reference": "ORDER-1",
            "amount": "100.00",
            "currency": "USD",
            "customer_phone": "243820000000",
        }
    )

    assert result["status"] == "PENDING"
    assert len(mock.history) == 2

    exchange = mock.history[0]
    assert exchange["method"] == "POST"
    assert "/auth/tokens/exchange/" in exchange["uri"]
    assert "Authorization" not in (exchange["options"].get("headers") or {})
    assert exchange["options"]["json"]["client_id"] == "client-id"
    assert exchange["options"]["json"]["secret"] == "secret"

    deposit = mock.history[1]
    assert deposit["options"]["headers"]["Authorization"] == "Bearer tok_1"
    assert "X-API-KEY" not in deposit["options"]["headers"]
    assert "Idempotency-Key" not in deposit["options"]["headers"]
    assert deposit["options"]["json"]["reference"] == "ORDER-1"
    assert deposit["options"]["json"]["amount"] == "100.00"
    assert deposit["options"]["json"]["currency"] == "USD"
    assert deposit["options"]["json"]["provider_code"] == "VODACOM_MPESA_COD"
    assert deposit["options"]["json"]["customer_phone"] == "243820000000"


def test_token_is_cached_across_calls() -> None:
    client, mock = _client_with_mock(
        [
            _token_response(),
            HttpResponse(200, json.dumps({"count": 1, "next": None, "previous": None, "results": []})),
            HttpResponse(200, json.dumps({"count": 0, "next": None, "previous": None, "results": []})),
        ]
    )

    client.countries.list()
    client.wallets.list()

    assert len(mock.history) == 3
    assert "/auth/tokens/exchange/" in mock.history[0]["uri"]
    assert "/manage/general/countries/" in mock.history[1]["uri"]
    assert "/manage/merchant-admin/wallets/" in mock.history[2]["uri"]


def test_unauthorized_retries_once_after_reexchange() -> None:
    client, mock = _client_with_mock(
        [
            _token_response("tok_old"),
            HttpResponse(401, json.dumps({"detail": "Token expired"})),
            _token_response("tok_new"),
            HttpResponse(
                200,
                json.dumps(
                    {
                        "success": True,
                        "response_data": {"status": "SUCCESS"},
                        "message": "ok",
                    }
                ),
            ),
        ]
    )

    result = client.status.check("deposit", "ORDER-1")
    assert result["status"] == "SUCCESS"
    assert len(mock.history) == 4
    assert mock.history[3]["options"]["headers"]["Authorization"] == "Bearer tok_new"


def test_second_unauthorized_fails() -> None:
    client, mock = _client_with_mock(
        [
            _token_response("tok_old"),
            HttpResponse(401, "{}"),
            _token_response("tok_new"),
            HttpResponse(401, "{}"),
        ]
    )

    with pytest.raises(AuthenticationException):
        client.countries.list()
    assert mock.history  # exchanged then retried


def test_paginated_list_is_not_unwrapped() -> None:
    client, _mock = _client_with_mock(
        [
            _token_response(),
            HttpResponse(
                200,
                json.dumps(
                    {
                        "count": 1,
                        "next": None,
                        "previous": None,
                        "results": [{"code": "KE"}],
                    }
                ),
            ),
        ]
    )

    page = client.countries.list()
    assert page["count"] == 1
    assert page["results"] == [{"code": "KE"}]


def test_idempotency_key_sent_only_when_provided() -> None:
    client, mock = _client_with_mock(
        [
            _token_response(),
            HttpResponse(
                200,
                json.dumps(
                    {
                        "success": True,
                        "response_data": {"status": "PENDING"},
                        "message": "ok",
                    }
                ),
            ),
        ]
    )

    client.payouts.create(
        {
            "provider_code": "MPESA_KE",
            "reference": "PAY-1",
            "amount": "50.00",
            "currency": "KES",
            "destination_account": "254700000000",
        },
        idempotency_key="PAY-1",
    )

    payout = mock.history[1]
    assert payout["options"]["headers"]["Idempotency-Key"] == "PAY-1"
    assert "X-API-KEY" not in payout["options"]["headers"]


def test_envelope_error_surfaces_message() -> None:
    client, _mock = _client_with_mock(
        [
            _token_response(),
            HttpResponse(
                400,
                json.dumps(
                    {
                        "success": False,
                        "response_code": 400,
                        "response_data": {"errors": {"reference": ["already exists"]}},
                        "message": "Duplicate reference",
                    }
                ),
            ),
        ]
    )

    with pytest.raises(ApiException) as caught:
        client.deposits.create(
            {
                "provider_code": "MPESA_KE",
                "reference": "DUP",
                "amount": "1.00",
                "currency": "KES",
                "customer_phone": "+254700000000",
            }
        )

    exception = caught.value
    assert exception.args[0] == "Duplicate reference"
    assert exception.status_code == 400
    assert exception.errors == {"reference": ["already exists"]}


def test_default_base_uri_is_production() -> None:
    client = Client(client_id="client-id", secret="secret", http_client=MockHttpClient())
    assert client.base_uri == Client.PRODUCTION_BASE_URI


def test_test_flag_uses_test_aggregator() -> None:
    client = Client(client_id="client-id", secret="secret", test=True, http_client=MockHttpClient())
    assert client.base_uri == Client.TEST_BASE_URI


def test_custom_host_without_api_prefix_is_normalized() -> None:
    client = Client(
        client_id="client-id",
        secret="secret",
        base_uri="https://aggregator.mainmoney.net",
        http_client=MockHttpClient(),
    )
    assert client.base_uri == Client.PRODUCTION_BASE_URI


def test_checkout_preferences_get() -> None:
    client, mock = _client_with_mock(
        [
            _token_response(),
            HttpResponse(
                200,
                json.dumps(
                    {
                        "success": True,
                        "response_data": {
                            "primary_color": "#ff3366",
                            "secondary_color": "#5f5e5e",
                            "accent_color": "#b90040",
                            "background_color": "#f8f9fb",
                            "locale": "en",
                            "logo": None,
                        },
                        "message": "ok",
                    }
                ),
            ),
        ]
    )

    prefs = client.checkout_preferences.get()
    assert prefs["primary_color"] == "#ff3366"
    assert prefs["locale"] == "en"
    assert "/manage/general/checkout-preferences/" in mock.history[1]["uri"]
