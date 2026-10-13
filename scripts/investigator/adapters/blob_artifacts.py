"""Private platform object transport; credentials stay with the selected identity."""
import re
from ..artifact_store import ArtifactError, equivalent


def validate_account_url(value):
    if not isinstance(value, str) or not re.fullmatch(r'https://[a-z0-9]{3,24}\.blob\.core\.windows\.net', value):
        raise ArtifactError('SLIM_PLATFORM_BLOB_URL_REQUIRED')
    return value


def recording_stores(config):
    """The platform adapter owns its endpoint, token audience and SDK classes."""
    import base64
    import json
    from .managed_identity import Tokens
    from ..artifact_store import Files
    from ..live_gateway import current
    validate_account_url(config['account_url'])
    tokens = Tokens(config['identity'])
    class BoundCredential:
        def get_token(self, *scopes, **kwargs):
            if scopes != ('https://storage.azure.com/.default',):
                raise ArtifactError('SLIM_AUTH_SCOPE')
            from azure.core.credentials import AccessToken
            token = tokens.get_token(scopes[0])
            part = token.split('.')[1]
            claims = json.loads(base64.urlsafe_b64decode(part + '=' * (-len(part) % 4)))
            return AccessToken(token, int(claims['exp']))
    credential = BoundCredential(); gateway = current()
    return (Files(BlobObjects(config['account_url'], 'snapshots', credential, channel=config['snapshot_channel'], gateway=gateway)),
            Files(BlobObjects(config['account_url'], 'tapes', credential, channel=config['tape_channel'], gateway=gateway)))


class BlobObjects:
    """Private platform artifacts. SDK requests are checked before transport.

    The operator supplies an exact platform-channel allowlist. Estate/model
    callers cannot select this channel. Authentication uses only the explicit
    managed identity; owner migration can pass its existing credential in memory.
    """
    def __init__(self, account_url, container, credential, *, channel, gateway):
        from azure.core.pipeline.policies import SansIOHTTPPolicy
        from azure.storage.blob import ContainerClient
        if container not in {'snapshots', 'tapes', 'captures', 'screenshots'}:
            raise ArtifactError('ARTIFACT_CONTAINER_NOT_ALLOWED')
        class Guard(SansIOHTTPPolicy):
            def on_request(self, request):
                http = request.http_request
                gateway.http(channel, http.method, http.url)
        self.client = ContainerClient(account_url, container, credential=credential,
                                      per_call_policies=[Guard()], retry_total=0)

    @staticmethod
    def key(key):
        if not re.fullmatch(r'(chunks|files)/[0-9a-f]{64}', key):
            raise ArtifactError('INVALID_OBJECT_KEY')
        return key

    def put(self, key, data):
        from azure.core.exceptions import ResourceExistsError
        blob = self.client.get_blob_client(self.key(key))
        try:
            blob.upload_blob(data, overwrite=False, validate_content=True)
        except ResourceExistsError:
            if not equivalent(key, blob.download_blob().readall(), data):
                raise ArtifactError('IMMUTABLE_OBJECT_CONFLICT')

    def get(self, key):
        return self.client.get_blob_client(self.key(key)).download_blob().readall()

