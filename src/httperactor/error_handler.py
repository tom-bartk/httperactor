import sys

from .abc import ErrorHandler


class StderrErrorHandler(ErrorHandler):
    """Error handler that writes errors to `sys.stderr`."""

    async def handle(self, error: Exception) -> None:
        """Handle error.

        Prints the string representation of the `error` to `sys.stderr`.

        Args:
            error (Exception): The error to handle.
        """
        print(repr(error), file=sys.stderr)
