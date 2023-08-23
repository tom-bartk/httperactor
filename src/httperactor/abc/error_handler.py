from abc import ABC, abstractmethod

__all__ = ["ErrorHandler"]


class ErrorHandler(ABC):
    """Base class for an error handler."""

    __slots__ = ()

    @abstractmethod
    async def handle(self, error: Exception) -> None:
        """Handle error.

        Args:
            error (Exception): The error to handle.
        """
