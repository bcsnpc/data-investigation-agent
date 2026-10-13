"""Add checked-upload receipts to an owner cleanup plan without inventing readback."""
import json
from pathlib import Path
from investigator.artifact_store import ArtifactError,canonical,digest
from investigator.archive_migration import verify_local,protected_path
from prepare_verified_cleanup import verify_remote as verify_historical

METHOD='SERVER_VALIDATED_BLOCK_MD5_ORDERED_COMMIT_AND_STORED_MD5_PROPERTY'


def pinned(record):
    raw=Path(record['path']).read_bytes()
    if digest(raw)!=record['sha256']:raise ArtifactError('CLEANUP_PROOF_PIN_DIFFERS')
    return raw


def append_checksum(plan, manifest_pin, receipt_pin, journal_pin, bundle_pin, *, protected_parents):
    manifest=json.loads(pinned(manifest_pin));receipt=json.loads(pinned(receipt_pin))
    bundle=json.loads(pinned(bundle_pin))
    envelopes=[json.loads(x) for x in pinned(journal_pin).splitlines() if x]
    journal=[];tail='0'*64
    for envelope in envelopes:
        identity=envelope.pop('record_sha256')
        scope=envelope.get('scope',{})
        if (envelope.get('previous_sha256')!=tail or digest(canonical(envelope))!=identity or
            scope.get('manifest_sha256')!=bundle_pin['sha256'] or scope.get('container')!='archive' or
            scope.get('account_url')!=plan['account_url']):raise ArtifactError('CLEANUP_JOURNAL_CHAIN')
        tail=identity;journal.append(envelope['event'])
    if bundle.get('source_manifest_sha256')!=manifest_pin['sha256'] or bundle.get('member_proof')!=receipt.get('member_proof'):
        raise ArtifactError('CLEANUP_MEMBER_PROOF_DIFFERS')
    if receipt.get('version')!='checksum-archive-receipt-v1' or receipt.get('manifest_sha256')!=manifest_pin['sha256']:
        raise ArtifactError('CLEANUP_CHECKSUM_MANIFEST_DIFFERS')
    if Path(manifest['workspace']).resolve()!=Path(plan['workspace']).resolve():raise ArtifactError('CLEANUP_WORKSPACE_DIFFERS')
    expected={e['path']:e for e in manifest['entries']}
    if len(expected)!=len(manifest['entries']) or len(receipt['objects'])!=len(expected):raise ArtifactError('CLEANUP_CHECKSUM_CONSERVATION')
    proof=receipt['integrity'];blob=proof['blob']
    if proof.get('integrity_method')!=METHOD or proof.get('download_performed') is not False or proof.get('server_computed_sha256') is not False:
        raise ArtifactError('CLEANUP_CHECKSUM_METHOD')
    phases=[e for e in journal if e.get('blob')==blob]
    verified=[e for e in phases if e.get('phase')=='CHECKSUM_VERIFIED']
    archived=[e for e in phases if e.get('phase')=='ARCHIVED_CHECKSUM']
    fields=('etag','stored_bytes','stored_md5','stored_sha256','integrity_method')
    if not verified or not archived or any(proof.get(k)!=verified[-1].get(k) or proof.get(k)!=archived[-1].get(k) for k in fields):
        raise ArtifactError('CLEANUP_CHECKSUM_JOURNAL_REQUIRED')
    blocks={}
    for e in phases:
        if e.get('phase')!='BLOCK_CHECKSUM_VALIDATED':continue
        row={k:e[k] for k in ('index','block_id','bytes','sha256','md5')}
        if row['index'] in blocks and blocks[row['index']]!=row:raise ArtifactError('CLEANUP_CHECKSUM_BLOCK_CONFLICT')
        blocks[row['index']]=row
    if not blocks or sorted(blocks)!=list(range(len(blocks))):raise ArtifactError('CLEANUP_CHECKSUM_BLOCKS_MISSING')
    ordered=[(blocks[i]['block_id'],blocks[i]['bytes']) for i in range(len(blocks))]
    intents=[e for e in phases if e.get('phase')=='ORDERED_COMMIT_INTENT']
    if (not intents or intents[-1].get('blocks_sha256')!=digest(canonical(ordered)) or
        intents[-1].get('stored_md5')!=proof['stored_md5'] or sum(x[1] for x in ordered)!=proof['stored_bytes']):
        raise ArtifactError('CLEANUP_CHECKSUM_COMMIT_DIFFERS')
    if receipt.get('member_proof',{}).get('source_manifest_sha256')!=manifest_pin['sha256']:
        raise ArtifactError('CLEANUP_MEMBER_PROOF_DIFFERS')
    result=json.loads(json.dumps(plan)); seen=set()
    for previous in result['files']:
        relative=Path(previous['path']).relative_to(Path(plan['workspace'])).as_posix()
        previous['runtime_protected']=bool(previous.get('runtime_protected')) or protected_path(relative,protected_parents)
    existing={str(Path(e['path'])).casefold() for e in result['files']}
    for row in receipt['objects']:
        e=expected.get(row['path'])
        if not e or e['path'] in seen or any(row.get(k)!=e[k] for k in ('sha256','bytes')):
            raise ArtifactError('CLEANUP_MEMBER_PROOF_DIFFERS')
        if row.get('blob')!=blob or row.get('bundle_sha256')!=receipt['member_proof']['bundle_sha256'] or row.get('tier')!='Archive' or any(row.get(k)!=proof[k] for k in fields):
            raise ArtifactError('CLEANUP_MEMBER_PROOF_DIFFERS')
        seen.add(e['path']);path=verify_local(manifest,e)
        if str(path).casefold() in existing:raise ArtifactError('CLEANUP_DUPLICATE_PATH')
        result['files'].append({'path':str(path),'bytes':e['bytes'],'sha256':e['sha256'],'blob':blob,
                               'runtime_protected':protected_path(e['path'],protected_parents)})
    if seen!=set(expected):raise ArtifactError('CLEANUP_CHECKSUM_CONSERVATION')
    result['blobs'].append({'blob':blob,'etag':proof['etag'],'stored_bytes':proof['stored_bytes'],
                           'stored_md5':proof['stored_md5'],'stored_sha256':proof['stored_sha256'],
                           'tier':'Archive','proof_class':'CHECKED_BLOCKS_STORED_MD5_NO_DOWNLOAD',
                           'proof_pins':[manifest_pin,receipt_pin,journal_pin,bundle_pin]})
    result['version']=2;result['protected_parents']=list(protected_parents)
    return result


def verify_remote(plan,client):
    for blob in plan['blobs']:
        if blob.get('proof_class')!='CHECKED_BLOCKS_STORED_MD5_NO_DOWNLOAD':
            verify_historical({'blobs':[blob]},client);continue
        for pin in blob['proof_pins']:pinned(pin)
        actual=client.checksum_properties(blob['blob'])
        if not actual or any(actual.get(k)!=blob[k] for k in ('etag','tier','stored_bytes','stored_md5')):
            raise ArtifactError('CLEANUP_REMOTE_CHANGED')
    return {'status':'UNCHANGED_ARCHIVED_PROOFS','blobs':len(plan['blobs']),
            'proof_classes':sorted({b.get('proof_class','HISTORICAL_DOWNLOAD_READBACK') for b in plan['blobs']})}


def main():
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify-plan',type=Path,required=True)
    parser.add_argument('--plan-sha256',required=True)
    args=parser.parse_args();plan=json.loads(pinned({'path':str(args.verify_plan),'sha256':args.plan_sha256}))
    from investigator.adapters.platform_credentials import OwnerCliCredential
    from investigator.adapters.platform_archive_client import IdentityArchiveClient
    from investigator.live_gateway import current
    credential=OwnerCliCredential(Path(plan['azure_cli_python']),plan['tenant'],plan['subscription'])
    client=IdentityArchiveClient(plan['account_url'],credential,current(),plan['gateway_channel'],
                                max_requests=len(plan['blobs'])*3,receipts=plan['control_receipts'])
    print(json.dumps(verify_remote(plan,client)))


if __name__=='__main__':main()
