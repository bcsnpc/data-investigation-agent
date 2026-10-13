"""Prepare an owner-run cleanup script; never remove files from this command."""
import argparse
import json
from pathlib import Path
from investigator.artifact_store import ArtifactError, canonical, digest


def build(checkpoint, receipts_root, workspace, *, protected_parents):
    workspace = Path(workspace).resolve(strict=True)
    files = {}; blobs = {}
    for batch in checkpoint['batches']:
        raw = (Path(receipts_root) / batch['batch'] / 'receipt.json').read_bytes()
        if digest(raw) != batch['receipt_sha256']:
            raise ArtifactError('CLEANUP_RECEIPT_SHA_DIFFERS')
        receipt = json.loads(raw)
        if len(receipt['objects']) != batch['files']:
            raise ArtifactError('CLEANUP_MEMBER_COUNT_DIFFERS')
        for row in receipt['objects']:
            if row['sha256'] != row['download_verified_sha256'] or row['tier'] != 'Archive':
                raise ArtifactError('CLEANUP_READBACK_PROOF_REQUIRED')
            path = (workspace / row['path']).absolute()
            if not path.is_relative_to(workspace / '.local') or '..' in Path(row['path']).parts:
                raise ArtifactError('CLEANUP_PATH_OUTSIDE_LOCAL')
            relative=path.relative_to(workspace).as_posix()
            protected=any(relative==parent or relative.startswith(parent.rstrip('/')+'/') for parent in protected_parents)
            entry = {'path': str(path), 'bytes': row['bytes'], 'sha256': row['sha256'], 'blob': row['blob'],
                     'runtime_protected':protected}
            if str(path).lower() in files and files[str(path).lower()] != entry:
                raise ArtifactError('CLEANUP_DUPLICATE_PATH_DIFFERS')
            files[str(path).lower()] = entry
            blob = {'blob': row['blob'], 'etag': row['etag'], 'stored_bytes': row['stored_bytes'],
                    'readback_sha256': row.get('bundle_sha256', row['sha256']), 'tier': 'Archive'}
            if row['blob'] in blobs and blobs[row['blob']] != blob:
                raise ArtifactError('CLEANUP_BLOB_PROOF_DIFFERS')
            blobs[row['blob']] = blob
    if len(files) != checkpoint['original_paths']:
        raise ArtifactError('CLEANUP_CHECKPOINT_COUNT_DIFFERS')
    return {'version': 1, 'workspace': str(workspace), 'files': list(files.values()), 'blobs': list(blobs.values()),
            'protected_parents':list(protected_parents)}


def verify_remote(plan, client):
    """An unchanged ETag binds the prior full readback to the current cold blob."""
    for expected in plan['blobs']:
        response = client.request(expected['blob'], 'HEAD', absent=True)
        if response is None:
            raise ArtifactError('CLEANUP_REMOTE_MISSING')
        try:
            headers = {k.lower(): v for k, v in response.headers.items()}
            if (headers.get('etag') != expected['etag'] or headers.get('x-ms-access-tier') != 'Archive'
                    or int(headers.get('content-length', -1)) != expected['stored_bytes']):
                raise ArtifactError('CLEANUP_REMOTE_CHANGED')
        finally:
            client.close(response)
    return {'status': 'UNCHANGED_ARCHIVED_READBACK', 'blobs': len(plan['blobs'])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify-plan', type=Path, required=True)
    parser.add_argument('--plan-sha256', required=True)
    args = parser.parse_args()
    raw = args.verify_plan.read_bytes()
    if digest(raw) != args.plan_sha256:
        raise ArtifactError('CLEANUP_PLAN_SHA_DIFFERS')
    plan = json.loads(raw)
    from investigator.adapters.platform_credentials import OwnerCliCredential
    from investigator.adapters.platform_archive_client import IdentityArchiveClient
    from investigator.live_gateway import current
    credential = OwnerCliCredential(Path(plan['azure_cli_python']), plan['tenant'], plan['subscription'])
    client = IdentityArchiveClient(plan['account_url'], credential, current(), plan['gateway_channel'],
                                  max_requests=len(plan['blobs']) * 3, receipts=plan['control_receipts'])
    print(json.dumps(verify_remote(plan, client)))


if __name__ == '__main__':
    main()
