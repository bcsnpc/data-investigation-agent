"""Exact platform artifact URLs only; authentication never enters evidence."""
import re
from email.utils import formatdate
from urllib.request import Request, build_opener
from .managed_identity import Tokens, validate
from ..live_gateway import open_http


def endpoint(value):
    if not isinstance(value, str) or not re.fullmatch(
        r'https://[a-z0-9]{3,24}\.blob\.core\.windows\.net/(?:tapes|captures)/[A-Za-z0-9/_-]+\.(?:tar\.gz|json)', value
    ):
        raise ValueError('REPLAY_PLATFORM_ENDPOINT_REQUIRED')
    return value


class Transport:
    def __init__(self, identity, channel):
        self.tokens = Tokens(validate(identity))
        self.channel = channel

    def request(self, url, data=None):
        from metadata_auth import NoRedirect
        request = Request(endpoint(url), data=data, method='GET' if data is None else 'PUT', headers={
            'Authorization': 'Bearer ' + self.tokens.get_token('https://storage.azure.com/.default'),
            'x-ms-version': '2023-11-03',
            'x-ms-date': formatdate(usegmt=True),
            **({'x-ms-blob-type': 'BlockBlob', 'If-None-Match': '*', 'Content-Type': 'application/json'} if data is not None else {}),
        })
        return open_http(build_opener(NoRedirect()), request, timeout=120, identity=self.channel)
