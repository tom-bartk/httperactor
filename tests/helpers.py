from contextlib import contextmanager

import pytest


@contextmanager
def not_raises(exc_type):
    try:
        yield
    except exc_type as e:
        raise pytest.fail(f"Did raise {exc_type} - {e!r}")  # noqa: TRY200,TRY003
