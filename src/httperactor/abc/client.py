from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from .auth_middleware import AuthMiddleware
from .request import Request

__all__ = ["HttpClientBase"]


TResponse = TypeVar("TResponse")
"""Invariant type variable for a generic response."""


TSubRequest = TypeVar("TSubRequest")
"""Invariant type variable for a generic request."""


class HttpClientBase(Generic[TSubRequest], ABC):
    """Base class for a service that sends HTTP requests."""

    __slots__ = ()

    @abstractmethod
    async def send(
        self, request: Request[TResponse], auth: AuthMiddleware[TSubRequest] | None = None
    ) -> TResponse | None:
        """Send a request.

        Args:
            request (Request[TResponse]): The request to send.
            auth (AuthMiddleware[TSubRequest] | None): Optional auth middleware.
                Defaults to `None`.

        Returns:
            The parsed response if the request is successful; `None` otherwise.
        """
