"""MainMoney aggregator Python SDK."""

from mm_aggr.client import Client
from mm_aggr.exceptions import (
    AggregatorException,
    ApiException,
    AuthenticationException,
    WebhookSignatureException,
)

__version__ = "0.1.0"

__all__ = [
    "AggregatorException",
    "ApiException",
    "AuthenticationException",
    "Client",
    "WebhookSignatureException",
    "__version__",
]
