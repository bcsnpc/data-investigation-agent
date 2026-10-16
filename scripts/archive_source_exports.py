"""Build or publish one hash-verified legacy export bundle; never deletes files."""
import argparse
import json
from pathlib import Path
from investigator.archive_migration import load_pinned
from investigator.artifact_store import canonical, digest, ArtifactError
from investigator.source_export_archive import build, bundle_manifest, publish_bundle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build', 'publish'])
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--manifest-sha256', required=True)
    parser.add_argument('--bundle', required=True, type=Path)
    parser.add_argument('--bundle-plan', required=True, type=Path)
    parser.add_argument('--bundle-plan-sha256')
    parser.add_argument('--bundle-compression',choices=['identity','gzip'],default='identity')
    parser.add_argument('--max-staging-bytes',type=int,default=512*1024*1024)
    parser.add_argument('--privacy-review', type=Path)
    parser.add_argument('--account-url')
    parser.add_argument('--tenant')
    parser.add_argument('--subscription')
    parser.add_argument('--azure-cli-python', type=Path)
    parser.add_argument('--gateway-channel')
    parser.add_argument('--max-control-requests', type=int)
    parser.add_argument('--max-stored-bytes', type=int,help='Required for new publications; actual compressed measurement before network')
    parser.add_argument('--journal', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    manifest = load_pinned(args.manifest, args.manifest_sha256)
    if args.action == 'build':
        if args.bundle_plan.exists(): raise ArtifactError('BUNDLE_PLAN_EXISTS')
        proof = build(manifest, args.manifest_sha256, args.bundle,compression=args.bundle_compression,
                      max_staging_bytes=args.max_staging_bytes)
        plan = bundle_manifest(args.bundle, manifest, args.manifest_sha256, proof)
        with args.bundle_plan.open('xb') as output: output.write(canonical(plan))
        print(json.dumps({**proof, 'bundle_plan_sha256': digest(canonical(plan))}))
        return
    required = ['bundle_plan_sha256', 'privacy_review', 'account_url', 'tenant', 'subscription',
                'gateway_channel', 'max_control_requests', 'max_stored_bytes', 'journal', 'output']
    if any(getattr(args, key) is None for key in required): raise ArtifactError('BUNDLE_PUBLICATION_ARGUMENTS')
    if args.output.exists(): raise ArtifactError('BUNDLE_RECEIPT_EXISTS')
    raw = args.bundle_plan.read_bytes()
    if digest(raw) != args.bundle_plan_sha256: raise ArtifactError('BUNDLE_PLAN_SHA_DIFFERS')
    plan = json.loads(raw)
    if Path(plan['workspace']) / plan['entries'][0]['path'] != args.bundle.resolve(strict=True):
        raise ArtifactError('BUNDLE_PATH_DIFFERS')
    from investigator.live_gateway import current
    from investigator.resumable_archive import IdentityArchiveClient, Journal
    from investigator.adapters.platform_credentials import OwnerCliCredential
    if args.azure_cli_python:
        credential = OwnerCliCredential(args.azure_cli_python,args.tenant,args.subscription)
    else:
        from azure.identity import AzureCliCredential
        credential = AzureCliCredential(tenant_id=args.tenant, subscription=args.subscription)
    client = IdentityArchiveClient(args.account_url, credential, current(), args.gateway_channel,
                   max_requests=args.max_control_requests, receipts=str(args.journal) + '.controls.jsonl')
    result = publish_bundle(plan, args.bundle_plan_sha256, manifest, args.manifest_sha256,
                json.loads(args.privacy_review.read_bytes()), client,
                Journal(args.journal, args.bundle_plan_sha256, args.account_url),max_stored_bytes=args.max_stored_bytes)
    with args.output.open('xb') as output: output.write(canonical(result))
    print(json.dumps({'receipt_sha256': digest(canonical(result)), 'original_bytes': result['original_bytes'],
                      'stored_bytes': result['stored_bytes'], 'local_deletion_performed': False,
                      'controls_used': args.max_control_requests - client.remaining}))


if __name__ == '__main__': main()
