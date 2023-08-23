from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

__all__ = ["AuthMiddleware"]


TSubRequest = TypeVar("TSubRequest")
"""Invariant type variable for a generic request."""


class AuthMiddleware(Generic[TSubRequest], ABC):
    """A middleware for authenticating requests."""

    __slots__ = ()

    @abstractmethod
    def apply(self, request: TSubRequest) -> TSubRequest:
        """Add authentication to a request.

        Args:
            request (TSubRequest): The request to authenticate.

        Returns:
            The authenticated request.
        """
