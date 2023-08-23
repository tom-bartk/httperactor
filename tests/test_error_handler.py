import sys
from unittest.mock import patch

import pytest

from src.httperactor.error_handler import StderrErrorHandler


@pytest.mark.asyncio()
class TestStderrErrorHandler:
    @patch("builtins.print")
    async def test_handle__prints_error_to_stderr(self, patched_print):
        error = ValueError("foo")
        sut = StderrErrorHandler()

        await sut.handle(error)

        patched_print.assert_called_once_with(repr(error), file=sys.stderr)
