from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from ..http_method import HttpMethod

__all__ = ["Request"]


TResponse = TypeVar("TResponse")
TRequest = TypeVar("TRequest")


class Request(Generic[TResponse], ABC):
    """A description of an HTTP request."""

    __slots__ = ()

    @property
    @abstractmethod
    def path(self) -> str:
        """The path part of the URL."""

    @property
    def body(self) -> list | dict | None:
        """An optional body of the request.

        Defaults to `None`.
        """
        return None

    @property
    def headers(self) -> list[tuple[str, str]]:
        """HTTP headers to include in the request.

        Defaults to empty list.
        """
        return []

    @property
    def method(self) -> HttpMethod:
        """The HTTP method to use.

        Defaults to `HttpMethod.GET`.
        """
        return HttpMethod.GET

    @abstractmethod
    def map_response(self, response: str) -> TResponse:
        """Map raw response text to an object.

        Args:
            response (str): The raw response text.

        Returns:
            The mapped response object.
        """
