"""Prepare or publish a pinned lossless archive bundle without body staging."""
import argparse
import json
from pathlib import Path
import shutil

from investigator.archive_migration import load_pinned
from investigator.artifact_store import ArtifactError,canonical,digest
from investigator.streaming_archive_bundle import prepare,publish


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['prepare','publish'])
    parser.add_argument('--manifest',required=True,type=Path)
    parser.add_argument('--manifest-sha256',required=True)
    parser.add_argument('--bundle-plan',required=True,type=Path)
    parser.add_argument('--bundle-plan-sha256')
    parser.add_argument('--privacy-review',type=Path)
    parser.add_argument('--account-url')
    parser.add_argument('--gateway-channel')
    parser.add_argument('--tenant')
    parser.add_argument('--subscription')
    identity=parser.add_mutually_exclusive_group()
    identity.add_argument('--managed-client-id')
    identity.add_argument('--azure-cli-python',type=Path)
    parser.add_argument('--max-control-requests',type=int)
    parser.add_argument('--max-stored-bytes',type=int)
    parser.add_argument('--journal',type=Path)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    manifest=load_pinned(args.manifest,args.manifest_sha256)
    if args.action=='prepare':
        if args.bundle_plan.exists():raise ArtifactError('ARCHIVE_BUNDLE_PLAN_EXISTS')
        prepared,_=prepare(manifest,args.manifest_sha256)
        with args.bundle_plan.open('xb') as stream:stream.write(canonical(prepared))
        print(json.dumps({'bundle_plan_sha256':digest(canonical(prepared)),**prepared['member_proof']}))
        return
    required=['bundle_plan_sha256','privacy_review','account_url','gateway_channel','max_control_requests',
              'max_stored_bytes','journal','output']
    if any(getattr(args,key) is None for key in required):raise ArtifactError('ARCHIVE_ARGUMENTS_REQUIRED')
    if not args.managed_client_id and not (args.azure_cli_python and args.tenant and args.subscription):
        raise ArtifactError('ARCHIVE_EXPLICIT_IDENTITY_REQUIRED')
    if args.output.exists():raise ArtifactError('ARCHIVE_RECEIPT_EXISTS')
    if shutil.disk_usage(manifest['workspace']).free<10*1024**3:raise ArtifactError('ARCHIVE_DISK_FLOOR')
    raw=args.bundle_plan.read_bytes()
    if digest(raw)!=args.bundle_plan_sha256:raise ArtifactError('ARCHIVE_BUNDLE_PLAN_SHA_DIFFERS')
    from investigator.adapters.platform_archive_client import IdentityArchiveClient
    from investigator.resumable_archive import Journal
    from investigator.live_gateway import current
    if args.managed_client_id:
        from azure.identity import ManagedIdentityCredential
        credential=ManagedIdentityCredential(client_id=args.managed_client_id)
    else:
        from investigator.adapters.platform_credentials import OwnerCliCredential
        credential=OwnerCliCredential(args.azure_cli_python,args.tenant,args.subscription)
    client=IdentityArchiveClient(args.account_url,credential,current(),args.gateway_channel,
                                max_requests=args.max_control_requests,receipts=str(args.journal)+'.controls.jsonl')
    result=publish(json.loads(raw),args.bundle_plan_sha256,manifest,args.manifest_sha256,
                   json.loads(args.privacy_review.read_bytes()),client,
                   Journal(args.journal,args.bundle_plan_sha256,args.account_url),max_stored_bytes=args.max_stored_bytes)
    with args.output.open('xb') as stream:stream.write(canonical(result))
    print(json.dumps({'receipt_sha256':digest(canonical(result)),'original_bytes':result['original_bytes'],
                      'stored_bytes':result['stored_bytes'],'controls_used':args.max_control_requests-client.remaining,
                      'body_staging':False,'local_deletion':False}))


if __name__=='__main__':main()
