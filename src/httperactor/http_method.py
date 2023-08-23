from enum import StrEnum

__all__ = ["HttpMethod"]


class HttpMethod(StrEnum):
    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"
    PATCH = "PATCH"
    PUT = "PUT"
