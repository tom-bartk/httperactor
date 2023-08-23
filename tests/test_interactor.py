from collections.abc import Callable, Sequence
from typing import Any
from unittest.mock import AsyncMock, Mock, call, create_autospec

import pytest
from pydepot import Action, Store

from src.httperactor.abc import AuthMiddleware, HttpClientBase, Request
from src.httperactor.interactor import HttpInteractor
from tests.helpers import not_raises


class DefaultHttpInteractor(HttpInteractor):
    @property
    def request(self) -> Request:
        return Mock()


class MockHttpInteractor(HttpInteractor):
    def __init__(self, *args: Any, **kwargs: Any):
        self.mock_actions: Mock = Mock(return_value=[])
        self.mock_auth: Mock = Mock()
        self.mock_request: Mock = Mock()
        self.mock_side_effects: Mock = Mock()
        super().__init__(*args, **kwargs)

    @property
    def auth(self) -> AuthMiddleware:
        return self.mock_auth

    @property
    def request(self) -> Request:
        return self.mock_request

    def actions(self, response) -> Sequence[Action]:
        return self.mock_actions(response)

    async def side_effects(self, response) -> None:
        self.mock_side_effects(response)


@pytest.fixture()
def response() -> Mock:
    return Mock()


@pytest.fixture()
def create_http_client(response) -> Callable[[Any | None], HttpClientBase]:
    def factory(will_respond: Any | None = None) -> HttpClientBase:
        client = create_autospec(HttpClientBase)
        client.send = AsyncMock(return_value=will_respond or response)
        return client

    return factory


@pytest.fixture()
def store() -> Store:
    return create_autospec(Store)


@pytest.fixture()
def default_sut(create_http_client, store) -> HttpInteractor:
    return DefaultHttpInteractor(http_client=create_http_client(), store=store)


@pytest.fixture()
def create_sut(
    create_http_client, store
) -> Callable[[HttpClientBase | None], HttpInteractor]:
    def factory(http_client: HttpClientBase | None = None) -> MockHttpInteractor:
        return MockHttpInteractor(
            http_client=http_client or create_http_client(), store=store
        )

    return factory


class TestDefaults:
    def test_actions__returns_empty_list(self, default_sut):
        assert default_sut.actions(Mock()) == []

    @pytest.mark.asyncio()
    async def test_side_effects__does_not_raise(self, default_sut):
        with not_raises(Exception):
            await default_sut.side_effects(Mock())

    def test_auth__returns_none(self, default_sut):
        assert not default_sut.auth


@pytest.mark.asyncio()
class TestExecute:
    async def test_sends_request_returned_by_request(
        self, create_sut, create_http_client
    ):
        http_client = create_http_client()
        sut = create_sut(http_client)

        await sut.execute()

        http_client.send.assert_awaited_once_with(sut.mock_request, auth=sut.mock_auth)

    async def test_when_response_not_none__performs_side_effects_with_response(
        self, create_sut, response
    ):
        sut = create_sut()

        await sut.execute()

        sut.mock_side_effects.assert_called_once_with(response)

    async def test_when_response_not_none__dispatches_actions_from_response_to_store(
        self, create_sut, response
    ):
        action_1 = Mock()
        action_2 = Mock()
        sut = create_sut()
        sut.mock_actions = Mock(return_value=[action_1, action_2])
        expected_calls = [call(action_1), call(action_2)]

        await sut.execute()

        sut.mock_actions.assert_called_once_with(response)
        sut.store.dispatch.assert_has_calls(expected_calls)
