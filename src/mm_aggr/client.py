"""Merchant API client facade."""

from __future__ import annotations

from mm_aggr.auth.token_store import TokenStore
from mm_aggr.http.http_client import HttpClient
from mm_aggr.http.transport import Transport
from mm_aggr.http.urllib_client import UrllibHttpClient
from mm_aggr.resources.amount_limits import AmountLimits
from mm_aggr.resources.countries import Countries
from mm_aggr.resources.customers import Customers
from mm_aggr.resources.deposits import Deposits
from mm_aggr.resources.fees import Fees
from mm_aggr.resources.payouts import Payouts
from mm_aggr.resources.providers import Providers
from mm_aggr.resources.refunds import Refunds
from mm_aggr.resources.remittances import Remittances
from mm_aggr.resources.status import Status
from mm_aggr.resources.transactions import Transactions
from mm_aggr.resources.wallets import Wallets
from mm_aggr.webhook.verifier import WebhookVerifier


class Client:
    PRODUCTION_BASE_URI = "https://aggregator.mainmoney.net/api/v1/"
    TEST_BASE_URI = "https://testaggregator.mainmoney.net/api/v1/"

    def __init__(
        self,
        client_id: str,
        secret: str,
        base_uri: str | None = None,
        *,
        test: bool = False,
        http_client: HttpClient | None = None,
        timeout: float = 30.0,
        token_expires_in: int | None = None,
    ) -> None:
        self._base_uri = self.normalize_base_uri(
            base_uri if base_uri is not None else (self.TEST_BASE_URI if test else self.PRODUCTION_BASE_URI)
        )
        http = http_client if http_client is not None else UrllibHttpClient(timeout)
        tokens = TokenStore(http, self._base_uri, client_id, secret, token_expires_in)
        transport = Transport(http, self._base_uri, tokens)

        self.deposits = Deposits(transport)
        self.payouts = Payouts(transport)
        self.remittances = Remittances(transport)
        self.refunds = Refunds(transport)
        self.status = Status(transport)
        self.customers = Customers(transport)
        self.wallets = Wallets(transport)
        self.transactions = Transactions(transport)
        self.countries = Countries(transport)
        self.providers = Providers(transport)
        self.fees = Fees(transport)
        self.amount_limits = AmountLimits(transport)
        self.webhooks = WebhookVerifier()

    @property
    def base_uri(self) -> str:
        return self._base_uri

    @staticmethod
    def normalize_base_uri(base_uri: str) -> str:
        normalized = base_uri.strip().rstrip("/")
        if not normalized.lower().endswith("/api/v1"):
            normalized += "/api/v1"
        return normalized + "/"
