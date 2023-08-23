from collections.abc import Callable
from unittest.mock import AsyncMock, Mock, PropertyMock, call, create_autospec

import httpx
import pytest

from src.httperactor.abc import AuthMiddleware, ErrorHandler, Request
from src.httperactor.client import HttpClient
from src.httperactor.http_method import HttpMethod


@pytest.fixture()
def error_handler() -> ErrorHandler:
    return create_autospec(ErrorHandler)


@pytest.fixture()
def auth_middleware() -> AuthMiddleware:
    return create_autospec(AuthMiddleware)


@pytest.fixture()
def httpx_request() -> httpx.Request:
    return create_autospec(httpx.Request)


@pytest.fixture()
def create_response() -> Callable[[str | None, int | None], httpx.Response]:
    def factory(text: str | None = None, code: int | None = None) -> httpx.Response:
        response = create_autospec(httpx.Response)
        type(response).status_code = PropertyMock(return_value=code or 200)
        type(response).text = PropertyMock(return_value=text or "")
        return response

    return factory


@pytest.fixture()
def create_httpx_client(
    create_response, httpx_request
) -> Callable[[httpx.Request | None, httpx.Response | None], httpx.AsyncClient]:
    def factory(
        will_build: httpx.Request | None = None,
        will_respond: httpx.Response | None = None,
    ) -> httpx.AsyncClient:
        client = create_autospec(httpx.AsyncClient)
        client.send = AsyncMock(return_value=will_respond or create_response())
        client.build_request = Mock(return_value=will_build or httpx_request)
        return client

    return factory


@pytest.fixture()
def create_request() -> (
    Callable[
        [
            dict | None,
            list[tuple[str, str]] | None,
            HttpMethod | None,
            Mock | None,
            str | None,
        ],
        Request,
    ]
):
    def factory(
        body: dict | None = None,
        headers: list[tuple[str, str]] | None = None,
        method: HttpMethod | None = None,
        map_response: Mock | None = None,
        path: str | None = None,
    ) -> Request:
        request = create_autospec(Request)
        if body:
            type(request).body = PropertyMock(return_value=body)
        if headers:
            type(request).headers = PropertyMock(return_value=headers)
        if method:
            type(request).method = PropertyMock(return_value=method)
        if map_response:
            request.map_response = map_response
        if path:
            type(request).path = PropertyMock(return_value=path)
        return request

    return factory


@pytest.fixture()
def create_sut(
    create_httpx_client, error_handler
) -> Callable[[httpx.AsyncClient | None], HttpClient]:
    _error_handler = error_handler

    def factory(client: httpx.AsyncClient | None = None) -> HttpClient:
        return HttpClient(
            httpx_client=client or create_httpx_client(), error_handler=error_handler
        )

    return factory


@pytest.mark.asyncio()
class TestSend:
    async def test_builds_httpx_request_using_httpx_client(
        self, create_httpx_client, create_sut, create_request
    ):
        request = create_request(
            method=HttpMethod.POST,
            path="/foo",
            headers=[("foo", "bar")],
            body={"foo": "bar"},
        )
        expected_call = call(
            method=HttpMethod.POST,
            url="/foo",
            headers=[("foo", "bar")],
            json={"foo": "bar"},
        )
        httpx_client = create_httpx_client()
        sut = create_sut(client=httpx_client)

        await sut.send(request)

        httpx_client.build_request.assert_has_calls([expected_call])

    async def test_when_auth_middleware_not_none__passes_apply_as_auth_to_httpx_client(
        self,
        auth_middleware,
        create_httpx_client,
        create_sut,
        create_request,
        httpx_request,
    ):
        httpx_client = create_httpx_client()
        sut = create_sut(client=httpx_client)

        await sut.send(create_request(), auth=auth_middleware)

        httpx_client.send.assert_awaited_once_with(
            httpx_request, auth=auth_middleware.apply
        )

    async def test_calls_raise_for_status_on_response(
        self, create_httpx_client, create_sut, create_request, create_response
    ):
        response = create_response()
        httpx_client = create_httpx_client(will_respond=response)
        sut = create_sut(client=httpx_client)

        await sut.send(create_request())

        response.raise_for_status.assert_called_once_with()

    async def test_returns_result_of_mapping_response_text(
        self, create_httpx_client, create_sut, create_request, create_response
    ):
        map_response = Mock(return_value="foo")
        response = create_response(text="bar")
        request = create_request(map_response=map_response)
        sut = create_sut(client=create_httpx_client(will_respond=response))

        result = await sut.send(request)

        assert result == "foo"
        map_response.assert_called_once_with("bar")

    async def test_when_exception_raised__calls_handle_on_error_handler(
        self, create_httpx_client, create_sut, create_request, error_handler
    ):
        expected_error = ValueError("foo")
        httpx_client = create_httpx_client()
        httpx_client.send = AsyncMock(side_effect=expected_error)
        sut = create_sut(client=httpx_client)

        await sut.send(create_request())

        error_handler.handle.assert_called_once_with(expected_error)

    async def test_when_exception_raised__returns_none(
        self, create_httpx_client, create_sut, create_request
    ):
        expected_error = ValueError("foo")
        httpx_client = create_httpx_client()
        httpx_client.send = AsyncMock(side_effect=expected_error)
        sut = create_sut(client=httpx_client)

        result = await sut.send(create_request())

        assert not result
