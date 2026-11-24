"""Coverage for every contract operation and the X-Merchant-Account option."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

import pytest

from mm_aggr import Client
from mm_aggr.http.http_response import HttpResponse
from tests.mock_http_client import MockHttpClient
from tests.test_client import _token_response

ACCOUNT = "7f9c2b6e-1d3a-4c5b-8e7f-0a1b2c3d4e5f"


def _make(account: str | None = None) -> tuple[Client, MockHttpClient]:
    mock = MockHttpClient()
    mock.enqueue(_token_response(), *[HttpResponse(200, "{}")] * 5)
    client = Client("id", "secret", base_uri="https://example.test/api/v1/", http_client=mock, merchant_account=account)
    return client, mock


def _last(mock: MockHttpClient) -> dict[str, Any]:
    return mock.history[-1]


Call = Callable[[Client], Any]

# (call, method, path suffix, supports X-Merchant-Account)
CASES: list[tuple[Call, str, str, bool]] = [
    (lambda c: c.deposits.create({"a": 1}), "POST", "transactions/deposits/", True),
    (lambda c: c.deposits.validate_payment({}), "POST", "transactions/deposits/validate-payment/", True),
    (lambda c: c.payouts.create({"a": 1}), "POST", "transactions/payouts/", True),
    (lambda c: c.payouts.create_business({"a": 1}), "POST", "transactions/payouts/business/", True),
    (
        lambda c: c.payouts.create_business_merchant_account({"a": 1}),
        "POST",
        "transactions/payouts/business/merchant-account/",
        True,
    ),
    (lambda c: c.refunds.create({"a": 1}), "POST", "transactions/refunds/", True),
    (lambda c: c.remittances.create({"a": 1}), "POST", "transactions/remittances/", True),
    (lambda c: c.status.check("deposit", "R1"), "POST", "transactions/status/check/deposit/", True),
    (lambda c: c.wallets.list(), "GET", "manage/merchant-admin/wallets/", True),
    (lambda c: c.transactions.list("payout"), "GET", "manage/merchant-admin/transactions/payout/", True),
    (lambda c: c.reports.charts(), "GET", "manage/merchant-admin/reports/charts/", True),
    (lambda c: c.reports.summary(), "GET", "manage/merchant-admin/reports/summary/", True),
    (lambda c: c.payment_links.list(), "GET", "payment-links/", True),
    (lambda c: c.pricing.get(), "GET", "manage/general/pricing/", False),
    (lambda c: c.transfers.list(), "GET", "transactions/transfers/", False),
    (lambda c: c.transfers.create({"a": 1}), "POST", "transactions/transfers/", False),
    (lambda c: c.transfers.get("T1"), "GET", "transactions/transfers/T1/", False),
    (lambda c: c.sellers.list(), "GET", "sellers/", False),
    (lambda c: c.sellers.create({"a": 1}), "POST", "sellers/", False),
    (lambda c: c.sellers.countries(), "GET", "sellers/countries/", False),
    (lambda c: c.sellers.get("S1"), "GET", "sellers/S1/", False),
    (lambda c: c.sellers.update("S1", {"name": "n"}), "PATCH", "sellers/S1/", False),
    (lambda c: c.sellers.get_kyb("S1"), "GET", "sellers/S1/kyb/", False),
    (lambda c: c.sellers.update_kyb("S1", {"jurisdiction": "CD"}), "PATCH", "sellers/S1/kyb/", False),
    (lambda c: c.sellers.start_kyb("S1"), "POST", "sellers/S1/kyb/start/", False),
    (lambda c: c.sellers.submit_kyb("S1"), "POST", "sellers/S1/kyb/submit/", False),
    (lambda c: c.sellers.create_onboarding_link("S1"), "POST", "sellers/S1/onboarding-link/", False),
    (lambda c: c.sellers.revoke_onboarding_link("S1"), "DELETE", "sellers/S1/onboarding-link/", False),
    (lambda c: c.deposits.validate_card_payment({}), "POST", "transactions/card-deposits/validate-payment/", False),
    (
        lambda c: c.payouts.create_card_business_merchant_account({"a": 1}),
        "POST",
        "transactions/card-payouts/business/merchant-account/",
        False,
    ),
]


@pytest.mark.parametrize(("call", "method", "path", "supports_account"), CASES)
def test_operation_method_and_path(call: Call, method: str, path: str, supports_account: bool) -> None:
    client, mock = _make()
    call(client)
    request = _last(mock)
    assert request["method"] == method
    assert request["uri"] == "https://example.test/api/v1/" + path
    assert "X-Merchant-Account" not in request["options"]["headers"]


@pytest.mark.parametrize(("call", "method", "path", "supports_account"), CASES)
def test_client_wide_merchant_account(call: Call, method: str, path: str, supports_account: bool) -> None:
    client, mock = _make(ACCOUNT)
    call(client)
    headers = _last(mock)["options"]["headers"]
    if supports_account:
        assert headers["X-Merchant-Account"] == ACCOUNT
    else:
        assert "X-Merchant-Account" not in headers


def test_per_call_account_overrides_client_default() -> None:
    client, mock = _make(ACCOUNT)
    client.deposits.create({"a": 1}, "key-1", merchant_account="other")
    headers = _last(mock)["options"]["headers"]
    assert headers["X-Merchant-Account"] == "other"
    assert headers["Idempotency-Key"] == "key-1"


def test_per_call_account_without_client_default() -> None:
    client, mock = _make()
    client.status.check("payout", "R1", merchant_account=ACCOUNT)
    assert _last(mock)["options"]["headers"]["X-Merchant-Account"] == ACCOUNT
    assert _last(mock)["options"]["json"] == {"reference": "R1"}


def test_with_merchant_account_returns_scoped_client_sharing_token() -> None:
    client, mock = _make()
    scoped = client.with_merchant_account(ACCOUNT)
    scoped.wallets.list()
    client.wallets.list()
    assert scoped.merchant_account == ACCOUNT
    assert client.merchant_account is None
    assert mock.history[1]["options"]["headers"]["X-Merchant-Account"] == ACCOUNT
    assert "X-Merchant-Account" not in mock.history[2]["options"]["headers"]
    assert len([h for h in mock.history if h["uri"].endswith("auth/tokens/exchange/")]) == 1


def test_sellers_create_sends_body_and_queries_are_forwarded() -> None:
    client, mock = _make()
    body = {"sub_type": "LEGAL", "name": "Shop", "email": "a@b.co", "country": "uuid"}
    client.sellers.create(body)
    assert _last(mock)["options"]["json"] == body
    client.transfers.list({"sub_merchant_id": "S1", "reference": None})
    assert _last(mock)["options"]["query"] == {"sub_merchant_id": "S1"}
    client.reports.summary({"currency": "USD"}, merchant_account=ACCOUNT)
    assert _last(mock)["options"]["query"] == {"currency": "USD"}


def test_onboarding_revoke_returns_payload() -> None:
    mock = MockHttpClient()
    mock.enqueue(_token_response(), HttpResponse(200, json.dumps({"revoked": 1})))
    client = Client("id", "secret", base_uri="https://example.test/api/v1/", http_client=mock)
    assert client.sellers.revoke_onboarding_link("S1") == {"revoked": 1}
