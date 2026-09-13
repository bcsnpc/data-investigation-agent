"""Service response handling independent of authentication and storage."""
import base64
import time
from urllib.parse import quote, urlsplit

def relative(endpoint, audience='fabric'):
    """Only follow pagination URLs on the original service, never arbitrary hosts."""
    if '://' not in endpoint:
        return endpoint
    url = urlsplit(endpoint)
    host, prefix = ('api.fabric.microsoft.com', '/v1/') if audience == 'fabric' else ('api.powerbi.com', '/v1.0/myorg/')
    if url.scheme != 'https' or url.netloc != host or not url.path.startswith(prefix):
        raise ValueError('Unexpected continuation origin')
    return url.path[len(prefix):] + ('?' + url.query if url.query else '')


def pages(endpoint, call, audience='fabric', key='value'):
    result, seen = [], set()
    base = endpoint
    while endpoint:
        if endpoint in seen:
            raise ValueError('Repeated continuation')
        seen.add(endpoint)
        body = call(endpoint, audience=audience)['text']
        result.extend(body[key])
        next_url = body.get('continuationUri') or body.get('@odata.nextLink')
        token = body.get('continuationToken')
        endpoint = relative(next_url, audience) if next_url else (base + ('&' if '?' in base else '?') + 'continuationToken=' + quote(token, safe='') if token else None)
    return result


def definition(endpoint, call, sleep=time.sleep):
    response = call(endpoint, 'post')
    if response['status_code'] == 202:
        headers = {k.lower(): v for k, v in response.get('headers', {}).items()}
        operation = headers.get('x-ms-operation-id')
        if not operation:
            raise ValueError('Definition operation ID missing')
        for _ in range(30):
            status = call(f'operations/{operation}')['text']['status']
            if status in ('Succeeded', 'Completed'):
                response = call(f'operations/{operation}/result')
                break
            if status in ('Failed', 'Cancelled'):
                raise RuntimeError('Definition operation failed')
            sleep(min(30, max(1, int(headers.get('retry-after', 5)))))
        else:
            raise TimeoutError('Definition operation timed out')
    parts = {}
    for part in response['text']['definition']['parts']:
        if part['payloadType'] != 'InlineBase64':
            raise ValueError('Unsupported definition payload')
        if part['path'] in parts:
            raise ValueError('Duplicate definition part')
        parts[part['path']] = base64.b64decode(part['payload'], validate=True).decode('utf-8-sig')
    return parts


