"""MainMoney aggregator Python SDK."""

from mm_aggr.checkout_proxy import CHECKOUT_ROUTES, dispatch, handle
from mm_aggr.client import Client
from mm_aggr.exceptions import (
    AggregatorException,
    ApiException,
    AuthenticationException,
    WebhookSignatureException,
)

__version__ = "0.1.3"

__all__ = [
    "CHECKOUT_ROUTES",
    "AggregatorException",
    "ApiException",
    "AuthenticationException",
    "Client",
    "WebhookSignatureException",
    "__version__",
    "dispatch",
    "handle",
]
