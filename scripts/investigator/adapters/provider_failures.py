"""Bounded transport retry classification shared by configured providers."""
from urllib.error import URLError
from http.client import IncompleteRead


def retryable(error):
    status=getattr(error,'http_status',getattr(error,'code',None))
    if status is not None:return status in (408,429,500,502,503,504)
    return isinstance(error,(ConnectionError,TimeoutError,IncompleteRead,URLError))
