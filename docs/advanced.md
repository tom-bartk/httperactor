## Authenticate a Request

Use the [`AuthMiddleware`](/api/auth/#httperactor.abc.AuthMiddleware) to provide required authentication to the outgoing request.

Httperactor has a concept of a `SubRequest`, which represents a request type used by the module that connects to the HTTP server. Httperactor uses the [`httpx`](https://wwww.python-httpx.org) package as the default HTTP client, so the `SubRequest` becomes the [`httpx.Request`](https://www.python-httpx.org/api/#request).

Following example defines an [`AuthMiddleware`](/api/auth/#httperactor.abc.AuthMiddleware) that adds an `Authorization` header to the `httpx.Request`:

```python3
import httpx

import httperactor


class BearerTokenAuthMiddleware(httperactor.AuthMiddleware[httpx.Request]):
    def __init__(self, token: str):
        self._token: str = token

    def apply(self, request: httpx.Request) -> httpx.Request:
        request.headers["Authorization"] = f"Bearer {self._token}"
        return request
```

To have the interactor use the middleware, override the [`auth`](/api/interactor/#httperactor.interactor.HttpInteractor.auth) property:
```python3

import httpx

import httperactor

...

class GetBooksInteractor(httperactor.HttpInteractor[httpx.Request, Sequence[Book], State]):
    @property
    def request(self) -> httperactor.Request[Sequence[Book]]:
        return GetBooksRequest()

    @property
    def auth(self) -> httperactor.AuthMiddleware[httpx.Request] | None:
        return BearerTokenAuthMiddleware(token="MY_SECRET_TOKEN")
```

## Use a custom HttpClient

Httperactor ships with a [`HttpClient`](/api/client/#httperactor.HttpClient) that uses the [`httpx`](https://www.python-httpx.org) package for sending the HTTP requests.

You can provide your own client by subclassing the [`HttpClientBase`](/api/client/#httperactor.abc.HttpClientBase). 

Following example defines a simple client using the [`tornado`](https://www.tornadoweb.org/en/stable/index.html) package:

```python3
from typing import TypeVar

import tornado.httpclient as tornado

from httperactor import AuthMiddleware, HttpClientBase, Request

TResponse = TypeVar("TResponse")


class TornadoHttpClient(HttpClientBase[tornado.HTTPRequest]):
    async def send(
        self,
        request: Request[TResponse],
        auth: AuthMiddleware[tornado.HTTPRequest] | None = None,
    ) -> TResponse | None:
        tornado_request = tornado.HTTPRequest(
            url=f"http://localhost:5000{request.path}",
            method=request.method,
        )
        http_client = tornado.AsyncHTTPClient()

        response = await http_client.fetch(tornado_request)

        return request.map_response(response.body.decode())
```
