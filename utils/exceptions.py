from fastapi import HTTPException


class NotFound(Exception):
    pass


class HTTPError(HTTPException):
    pass


