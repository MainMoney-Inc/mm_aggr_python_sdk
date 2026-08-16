"""HTTP response value object."""

from __future__ import annotations


class HttpResponse:
    def __init__(
        self,
        status_code: int,
        body: str,
        headers: dict[str, list[str]] | None = None,
    ) -> None:
        self.status_code = status_code
        self.body = body
        self.headers: dict[str, list[str]] = headers if headers is not None else {}
