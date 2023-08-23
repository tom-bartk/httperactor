from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Generic, TypeVar

from pydepot import Action, Store

from .abc import AuthMiddleware, HttpClientBase, Request

__all__ = ["HttpInteractor"]


TSubRequest = TypeVar("TSubRequest")
"""Invariant type variable for a generic request."""

TResponse = TypeVar("TResponse")
"""Invariant type variable for a generic response."""

TState = TypeVar("TState")
"""Invariant type variable for a generic state."""


class HttpInteractor(Generic[TSubRequest, TResponse, TState], ABC):
    """An interactor using a template method for sending HTTP requests."""

    __slots__ = ("_http_client", "_store")

    @property
    @abstractmethod
    def request(self) -> Request[TResponse]:
        """The request to send."""

    @property
    def auth(self) -> AuthMiddleware[TSubRequest] | None:
        """An optional authentication middleware.

        Defaults to `None`.
        """
        return None

    @property
    def store(self) -> Store[TState]:
        """The store to send actions to."""
        return self._store

    def __init__(self, http_client: HttpClientBase[TSubRequest], store: Store[TState]):
        """Initialize new interactor with an HTTP client and the store.

        Args:
            http_client (HttpClientBase[TSubRequest]): The HTTP client to use for sending
                requests.
            store (Store[TState]): The store to dispatch actions to.
        """
        self._http_client: HttpClientBase[TSubRequest] = http_client
        self._store: Store[TState] = store

    async def side_effects(self, response: TResponse) -> None:
        """Perform side effects after receiving the response.

        Defaults to doing nothing.

        Args:
            response (TResponse): The response.
        """

    def actions(self, response: TResponse) -> Sequence[Action]:
        """Actions to dispatch to the store created from the response.

        Defaults to empty list.

        Args:
            response (TResponse): The response.

        Returns:
            The actions to dispatch.
        """
        return []

    async def execute(self) -> None:
        """The template method performing the request.

        First, it sends the `request`, with the optional authentication middleware,
        using the provided `HttpClientBase`.

        If the response is not empty, the `side_effects` are performed.
        After that, the `actions` are dispatched to the `store`.
        """
        response = await self._http_client.send(self.request, auth=self.auth)
        if response:
            await self.side_effects(response)

            for action in self.actions(response):
                self._store.dispatch(action)
