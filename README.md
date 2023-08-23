<div align="center">
  <a href="https://github.com/tom-bartk/httperactor">
    <img src="https://httperactor.tombartk.com/images/logo.png" alt="Logo" width="429" height="85">
  </a>

<div align="center">
<a href="https://jenkins.tombartk.com/job/httperactor/">
  <img alt="Jenkins" src="https://img.shields.io/jenkins/build?jobUrl=https%3A%2F%2Fjenkins.tombartk.com%2Fjob%2Fhttperactor">
</a>
<a href="https://jenkins.tombartk.com/job/httperactor/lastCompletedBuild/testReport/">
  <img alt="Jenkins tests" src="https://img.shields.io/jenkins/tests?jobUrl=https%3A%2F%2Fjenkins.tombartk.com%2Fjob%2Fhttperactor">
</a>
<a href="https://jenkins.tombartk.com/job/httperactor/lastCompletedBuild/coverage/">
  <img alt="Jenkins Coverage" src="https://img.shields.io/jenkins/coverage/apiv4?jobUrl=https%3A%2F%2Fjenkins.tombartk.com%2Fjob%2Fhttperactor%2F">
</a>
<a href="https://www.gnu.org/licenses/agpl-3.0.en.html">
  <img alt="PyPI - License" src="https://img.shields.io/pypi/l/httperactor">
</a>
<a href="https://pypi.org/project/httperactor/">
  <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/httperactor">
</a>
<a href="https://pypi.org/project/httperactor/">
  <img alt="PyPI - Version" src="https://img.shields.io/pypi/v/httperactor">
</a>
<a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff" style="max-width:100%;"></a>
</div>

  <p align="center">
    Async interactor for HTTP requests using a template method.
    <br />
    <a href="https://httperactor.tombartk.com"><strong>Documentation</strong></a>
  </p>
</div>

## Simple example

```python3
# main.py

import asyncio
import json
from collections.abc import Sequence
from typing import NamedTuple

import httpx
import pydepot

from httperactor import HttpClient, HttpInteractor, Request


class Book(NamedTuple):
    title: str
    author: str


class State(NamedTuple):
    books: tuple[Book, ...]


class StateSubscriber:
    def on_state(self, state: State) -> None:
        print(f"[StoreSubscriber] on_state called with {state}")


class SetBooksAction(pydepot.Action):
    def __init__(self, books: Sequence[Book]):
        self.books: Sequence[Book] = books


class SetBooksReducer(pydepot.Reducer[SetBooksAction, State]):
    @property
    def action_type(self) -> type[SetBooksAction]:
        return SetBooksAction

    def apply(self, action: SetBooksAction, state: State) -> State:
        return State(books=tuple(action.books))


class GetBooksRequest(Request[Sequence[Book]]):
    @property
    def path(self) -> str:
        return "/books"

    def map_response(self, response: str) -> Sequence[Book]:
        return json.loads(response, object_hook=lambda res: Book(**res))


class GetBooksInteractor(HttpInteractor[httpx.Request, Sequence[Book], State]):
    @property
    def request(self) -> Request[Sequence[Book]]:
        return GetBooksRequest()

    def actions(self, response: Sequence[Book]) -> Sequence[pydepot.Action]:
        return [SetBooksAction(books=response)]


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

## Installation

Httperactor is available as [`httperactor`](https://pypi.org/project/httperactor/) on PyPI:

```shell
pip install httperactor
```

## Usage

For detailed quickstart and API reference, visit the [Documentation](https://httperactor.tombartk.com/quickstart/).


## License
![AGPLv3](https://www.gnu.org/graphics/agplv3-with-text-162x68.png)
```monospace
Copyright (C) 2023 tombartk 

This program is free software: you can redistribute it and/or modify it under the terms
of the GNU Affero General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this program.
If not, see https://www.gnu.org/licenses/.
```
