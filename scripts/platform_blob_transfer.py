"""Identity-only replacement for retired owner bootstrap Blob key scripts.

No listKeys, SAS, credential chains, public access or identity/role changes.
The operator supplies an existing gateway policy granting the exact URL.
"""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

from investigator.artifact_store import ArtifactError
from investigator.archive_migration import sha_file


MAX_BYTES = 512 * 1024 * 1024


def transfer(action, url, path, sha256, *, credential, gateway, channel, controls, max_bytes=MAX_BYTES):
    from azure.storage.blob import BlobClient
    from investigator.adapters.guarded_transport import GuardedTransport
    if not callable(getattr(credential, 'get_token', None)):
        raise ArtifactError('PLATFORM_TOKEN_CREDENTIAL_REQUIRED')
    parsed = urlsplit(url)
    if parsed.scheme != 'https' or parsed.query or parsed.fragment or not parsed.hostname.endswith('.blob.core.windows.net'):
        raise ArtifactError('PLATFORM_BLOB_EXACT_PRIVATE_URL_REQUIRED')
    if type(max_bytes) is not int or not 0 < max_bytes <= MAX_BYTES:
        raise ArtifactError('PLATFORM_TRANSFER_BOUND')
    method = {'get': 'GET', 'put': 'PUT'}.get(action)
    if method is None:
        raise ArtifactError('PLATFORM_TRANSFER_OPERATION')
    gateway.http(channel, method, url)
    client = BlobClient.from_blob_url(url, credential=credential, retry_total=0,
             transport=GuardedTransport(gateway, channel, receipts=controls),
             max_single_put_size=MAX_BYTES, max_single_get_size=MAX_BYTES)
    path = Path(path)
    if action == 'put':
        if not path.is_file() or path.stat().st_size > max_bytes or sha_file(path) != sha256:
            raise ArtifactError('PLATFORM_UPLOAD_INPUT_HASH_OR_BOUND')
        # Single immutable PUT; SDK must not invent a block URL outside policy.
        with path.open('rb') as stream:
            client.upload_blob(stream, length=path.stat().st_size, overwrite=False, max_concurrency=1)
    else:
        if path.exists():
            raise ArtifactError('PLATFORM_LOCAL_OUTPUT_EXISTS')
        partial = path.with_name(path.name + '.partial')
        whole, count = hashlib.sha256(), 0
        with partial.open('xb') as output:
            for block in client.download_blob(max_concurrency=1).chunks():
                count += len(block)
                if count > max_bytes:
                    raise ArtifactError('PLATFORM_DOWNLOAD_BOUND')
                whole.update(block)
                output.write(block)
        if whole.hexdigest() != sha256:
            raise ArtifactError('PLATFORM_DOWNLOAD_SHA_DIFFERS')
        # Partial failure stays local, never promoted as a verified result.
        partial.rename(path)
    return {'action': action, 'url': url, 'bytes': path.stat().st_size, 'sha256': sha_file(path),
            'credential_type': type(credential).__name__, 'shared_key_used': False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['get', 'put'])
    parser.add_argument('--url', required=True)
    parser.add_argument('--file', required=True, type=Path)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--tenant', required=True)
    parser.add_argument('--subscription', required=True)
    parser.add_argument('--azure-cli-python', type=Path)
    parser.add_argument('--gateway-channel', required=True)
    parser.add_argument('--controls', required=True, type=Path)
    parser.add_argument('--receipt', required=True, type=Path)
    args = parser.parse_args(argv)
    if args.receipt.exists():
        raise ArtifactError('PLATFORM_RECEIPT_EXISTS')
    from azure.identity import AzureCliCredential
    from investigator.live_gateway import current
    from investigator.adapters.platform_credentials import OwnerCliCredential
    credential=(OwnerCliCredential(args.azure_cli_python,args.tenant,args.subscription) if args.azure_cli_python else
                AzureCliCredential(tenant_id=args.tenant, subscription=args.subscription))
    result = transfer(args.action, args.url, args.file, args.sha256, credential=credential,
             gateway=current(), channel=args.gateway_channel, controls=args.controls)
    with args.receipt.open('x', encoding='utf-8') as output:
        json.dump(result, output, indent=2)
    print(json.dumps(result))


if __name__ == '__main__':
    main()
