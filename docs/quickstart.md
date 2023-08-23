## Define the State, an Action and a Reducer

Httperactor is designed to work with the Unidirectional Data Flow pattern implemented by the [`pydepot`](https://pydepot.tombartk.com) package. For detailed guide on how to set up `pydepot`, visit its [quickstart](https://pydepot.tombartk.com/quickstart/).

Following example defines a simple state and an action that sets a list of books:

```python3
from collections.abc import Sequence
from typing import NamedTuple

import pydepot


class Book(NamedTuple):
    title: str
    author: str


class State(NamedTuple):
    books: tuple[Book, ...]


class SetBooksAction(pydepot.Action):
    def __init__(self, books: Sequence[Book]):
        self.books: Sequence[Book] = books


class SetBooksReducer(pydepot.Reducer[SetBooksAction, State]):
    @property
    def action_type(self) -> type[SetBooksAction]:
        return SetBooksAction

    def apply(self, action: SetBooksAction, state: State) -> State:
        return State(books=tuple(action.books))
```

## Define a Request

A [`Request`](/api/request/#httperactor.abc.Request) is an object describing an HTTP request. It is also used to transform the response text to a python object. 

Following example defines a GET request that fetches a list of books:

```python3
import json

import httperactor

...

class GetBooksRequest(httperactor.Request[Sequence[Book]]):
    @property
    def path(self) -> str:
        return "/books"

    def map_response(self, response: str) -> Sequence[Book]:
        return json.loads(response, object_hook=lambda res: Book(**res))
```
## Create an Interactor

An [`Interactor`](/api/interactor/#httperactor.HttpInteractor) is an object that "interacts" with some HTTP service. Usually, it is positioned below the layer responsible for capturing the user input.

The [`HttpInteractor`](/api/interactor/#httperactor.HttpInteractor) is designed as a [Template Method](https://refactoring.guru/design-patterns/template-method), which makes creating subclasses easy and flexible.

Basic usage consists of implementing the [`request`](/api/interactor/#httperactor.interactor.HttpInteractor.request) property, which returns the [`Request`](/api/request/#httperactor.abc.Request) to send, and the [`actions`](/api/interactor/#httperactor.interactor.HttpInteractor.actions) method, which returns a list of `pydepot.Action` that will be dispatched to the store.

Following example defines an interactor that will send the `GetBooksRequest`, and dispatch a single `SetBooksAction` on successful response:

```python3
import httpx

import httperactor

...

class GetBooksInteractor(httperactor.HttpInteractor[httpx.Request, Sequence[Book], State]):
    @property
    def request(self) -> httperactor.Request[Sequence[Book]]:
        return GetBooksRequest()

    def actions(self, response: Sequence[Book]) -> Sequence[pydepot.Action]:
        return [SetBooksAction(books=response)]
```

## Send the Request

Before sending the request, let's create a `StoreSubscriber` that will print any changes to the `State` - this will help in veryfing that the interactor is doing its job:

```python3
...

class StateSubscriber:
    def on_state(self, state: State) -> None:
        print(f"[StoreSubscriber] on_state called with {state}")
```

The endpoint of `GetBooksRequest` - `GET /books` - returns the following json document:

```sh
$ curl localhost:5000/books

[
  {
    "author": "Alice",
    "title": "foo"
  },
  {
    "author": "Bob",
    "title": "bar"
  },
  {
    "author": "Charlie",
    "title": "baz"
  }
]
```

Following example sets up the store, creates the interactor and sends a request by awaiting the [`execute`](/api/interactor/#httperactor.interactor.HttpInteractor.execute) coroutine:

```python3
import asyncio

...

async def main() -> None:
    store = pydepot.Store(initial_state=State(books=()))
    store.register(SetBooksReducer())

    subscriber = StateSubscriber()
    store.subscribe(subscriber)

    interactor = GetBooksInteractor(
        http_client=HttpClient(httpx.AsyncClient(base_url="http://localhost:5000")),
        store=store,
    )

    await interactor.execute()


if __name__ == "__main__":
    asyncio.run(main())
```

Running the script will result in the following output:

```sh
$ python3 main.py

[StoreSubscriber] on_state called with:
    State(
        books=(
            Book(title='foo', author='Alice'),
            Book(title='bar', author='Bob'),
            Book(title='baz', author='Charlie')
        )
    )
```

## Next steps

To see more in-depth examples, see the [Advanced Usage](/advanced/).

To see all available properties and methods, see the [API Documentation](/api/interactor/).
<br/>
