"""MainMoney aggregator Python SDK."""

__version__ = "0.1.0"


class Client:
    def __init__(self, base_uri: str, api_key: str) -> None:
        self.base_uri = base_uri
        self.api_key = api_key


__all__ = ["Client", "__version__"]
