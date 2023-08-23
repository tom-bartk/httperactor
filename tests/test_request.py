import pytest

from src.httperactor import HttpMethod, Request


class DefaultRequest(Request[str]):
    @property
    def path(self) -> str:
        return "/foo"

    def map_response(self, response: str) -> str:
        return "bar"


@pytest.fixture()
def sut() -> Request[str]:
    return DefaultRequest()


class TestDefaults:
    def test_body__returns_none(self, sut):
        assert not sut.body

    def test_headers__returns_empty_list(self, sut):
        assert sut.headers == []

    def test_method__returns_get(self, sut):
        assert sut.method == HttpMethod.GET
