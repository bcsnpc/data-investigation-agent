"""Plan, privacy-review-bound archive publication, or generate cleanup (never run it)."""
import argparse
import json
import os
from pathlib import Path

from investigator.archive_migration import (plan, load_pinned, publish, cleanup_script,
    privacy_approved, verify_local, convert_tape, encoded_chunks)
from investigator.artifact_store import ArtifactError, Files, LocalObjects, canonical, digest


class ArchiveClient:
    def __init__(self, account_url, identity, channel):
        from investigator.adapters.guarded_transport import GuardedTransport
        from azure.identity import ManagedIdentityCredential
        from azure.storage.blob import ContainerClient
        from investigator.live_gateway import current
        gateway=current()
        self.client=ContainerClient(account_url,'archive',credential=ManagedIdentityCredential(client_id=identity),
                                    transport=GuardedTransport(gateway,channel),retry_total=0)

    def upload_hot(self,key,path,encoding='identity'):
        from azure.storage.blob import StandardBlobTier
        from azure.core.exceptions import ResourceExistsError
        stats={}
        try:
            self.client.get_blob_client(key).upload_blob(encoded_chunks(path,encoding,stats),overwrite=False,
                        validate_content=True,max_concurrency=1,standard_blob_tier=StandardBlobTier.Hot)
        except ResourceExistsError:
            # A previous failed response may have left the immutable object Hot.
            # Existing bytes are NOT accepted here: publish must download and
            # verify original size/hash, stable ETag and Hot tier before archiving.
            return None
        return stats

    def download_chunks(self,key):
        yield from self.client.get_blob_client(key).download_blob().chunks()

    def properties(self,key):
        result=self.client.get_blob_client(key).get_blob_properties()
        return {'tier':result.blob_tier,'etag':result.etag}

    def archive(self,key,etag):
        from azure.core import MatchConditions
        from azure.storage.blob import StandardBlobTier
        self.client.get_blob_client(key).set_standard_blob_tier(StandardBlobTier.Archive,
                                                               etag=etag,match_condition=MatchConditions.IfNotModified)


def write_new(path,value):
    raw=canonical(value)
    with Path(path).open('xb') as output:output.write(raw)
    return digest(raw)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest='command',required=True)
    prepare=commands.add_parser('plan')
    prepare.add_argument('--workspace',required=True,type=Path)
    prepare.add_argument('--files',required=True,type=Path,help='JSON array of explicit relative file paths; no glob')
    prepare.add_argument('--protected-paths',required=True,type=Path,help='JSON array including current shared catalogs/ledgers')
    prepare.add_argument('--finished-statement',required=True)
    prepare.add_argument('--storage-encoding',choices=('identity','gzip'),default='identity')
    prepare.add_argument('--output',required=True,type=Path)
    for action in ('upload','cleanup-script','convert'):
        sub=commands.add_parser(action)
        sub.add_argument('--manifest',required=True,type=Path)
        sub.add_argument('--manifest-sha256',required=True)
        sub.add_argument('--output',required=True,type=Path)
        if action=='cleanup-script':
            sub.add_argument('--receipt',required=True,type=Path)
            sub.add_argument('--receipt-sha256',required=True)
        else:sub.add_argument('--privacy-review',required=True,type=Path)
        if action=='upload':
            sub.add_argument('--account-url',required=True)
            sub.add_argument('--managed-client-id',required=True)
            sub.add_argument('--gateway-channel',required=True)
        if action=='convert':
            sub.add_argument('--tape-directory',required=True,type=Path)
            sub.add_argument('--local-cas',required=True,type=Path)
    args=parser.parse_args(argv)
    if args.command=='plan':
        value=plan(args.workspace,json.loads(args.files.read_bytes()),
                   protected=json.loads(args.protected_paths.read_bytes()),finished_statement=args.finished_statement,
                   storage_encoding=args.storage_encoding)
        identity=write_new(args.output,value)
        print(json.dumps({'manifest_sha256':identity,'eligible_files':len(value['entries']),
                          'excluded_files':len(value['excluded']),'privacy_status':value['privacy_status'],
                          'original_bytes':sum(entry['bytes'] for entry in value['entries']),
                          'storage_encoding':value.get('storage_encoding','identity')}))
        return 0
    value=load_pinned(args.manifest,args.manifest_sha256)
    if args.command=='cleanup-script':
        raw=args.receipt.read_bytes()
        if digest(raw)!=args.receipt_sha256:raise ArtifactError('ARCHIVE_RECEIPT_SHA_DIFFERS')
        text=cleanup_script(value,args.manifest_sha256,json.loads(raw))
        with args.output.open('x',encoding='utf-8') as target:target.write(text)
        print(json.dumps({'script':str(args.output),'executed':False}));return 0
    review=json.loads(args.privacy_review.read_bytes())
    privacy_approved(review,args.manifest_sha256)
    if args.command=='upload':
        def checkpoint(row):
            progress=Path(str(args.output)+'.progress.jsonl')
            record={'manifest_sha256':args.manifest_sha256,'privacy_review':review,'object':row}
            with progress.open('a',encoding='utf-8') as stream:
                stream.write(json.dumps(record,sort_keys=True)+'\n');stream.flush();os.fsync(stream.fileno())
        result=publish(value,args.manifest_sha256,review,ArchiveClient(args.account_url,args.managed_client_id,args.gateway_channel),
                       on_verified=checkpoint)
    else:
        directory=args.tape_directory.resolve(strict=True)
        workspace=Path(value['workspace']).resolve(strict=True)
        if not directory.is_relative_to(workspace):raise ArtifactError('CONVERSION_OUTSIDE_MANIFEST')
        selected={entry['path']:entry for entry in value['entries']}
        for name in ('tape.json','tape.events.jsonl','catalog.sqlite','inventory.sqlite'):
            target=directory/name
            if target.exists():
                relative=target.relative_to(workspace).as_posix()
                if relative not in selected:raise ArtifactError('CONVERSION_FILE_NOT_IN_MANIFEST')
                verify_local(value,selected[relative])
        result=convert_tape(directory,Files(LocalObjects(args.local_cas)))
        result['manifest_sha256']=args.manifest_sha256
    identity=write_new(args.output,result)
    print(json.dumps({'output_sha256':identity,'local_deletion_performed':False,
                      **{key:result[key] for key in ('original_bytes','stored_bytes') if key in result}}))
    return 0


if __name__=='__main__':raise SystemExit(main())
