from typing import TypeVar

import httpx

from .abc import AuthMiddleware, HttpClientBase, Request
from .error_handler import ErrorHandler, StderrErrorHandler

__all__ = ["HttpClient"]


TResponse = TypeVar("TResponse")
"""Invariant type variable for a generic response."""


class HttpClient(HttpClientBase[httpx.Request]):
    """An HTTP client wrapping an `httpx.AsyncClient`."""

    __slots__ = ("_client", "_error_handler")

    def __init__(
        self, httpx_client: httpx.AsyncClient, error_handler: ErrorHandler | None = None
    ):
        """Initialize new instance with a httpx client and an optional error handler.

        Args:
            httpx_client (httpx.AsyncClient): The `httpx` async client.
            error_handler (ErrorHandler | None): An optional error handler.
                Defaults to `StderrErrorHandler`.
        """
        self._client: httpx.AsyncClient = httpx_client
        self._error_handler: ErrorHandler = error_handler or StderrErrorHandler()

    async def send(
        self,
        request: Request[TResponse],
        auth: AuthMiddleware[httpx.Request] | None = None,
    ) -> TResponse | None:
        """Send a request.

        Creates an `httpx.Request` based on the `request`, and if provided,
        authenticates it using the auth strategy.

        Returns the result of mapping the response text using the `request.map_response`.
        If an exception is thrown at any stage, it's caught and handled
        by the error handler.

        Args:
            request (Request[TResponse]): The request to send.
            auth (AuthMiddleware[httpx.Request] | None): Optional auth middleware.
                Defaults to `None`.

        Returns:
            The parsed response if the request is successful; `None` otherwise.
        """
        try:
            httpx_req = self._client.build_request(
                method=request.method,
                url=request.path,
                headers=request.headers,
                json=request.body,
            )

            res = await self._client.send(httpx_req, auth=auth.apply if auth else None)
            res.raise_for_status()

            return request.map_response(res.text)
        except Exception as error:
            await self._error_handler.handle(error)
            return None
