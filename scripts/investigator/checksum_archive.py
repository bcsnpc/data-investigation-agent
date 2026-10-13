"""Explicit upload-integrity proof; no download/readback claim and no deletion."""
import base64
from datetime import datetime,timezone
import hashlib
from .artifact_store import ArtifactError,canonical,digest
from .archive_migration import privacy_approved,encoded_stream,verify_unchanged_local
from .streaming_archive_bundle import prepare
from .resumable_archive import fixed_blocks,block_id


def encoded(source):
    with source.open('rb') as stream:yield from encoded_stream(stream,'gzip',{})


def block_proof(index,data):
    return {'index':index,'block_id':block_id(index,data),'bytes':len(data),
            'sha256':digest(data),'md5':base64.b64encode(hashlib.md5(data).digest()).decode()}


def measure(source,max_stored_bytes):
    blocks=[];whole=hashlib.sha256();md5=hashlib.md5();size=0
    for index,data in enumerate(fixed_blocks(encoded(source))):
        size+=len(data)
        if size>max_stored_bytes:raise ArtifactError('ARCHIVE_TRANSFER_BYTE_CAP')
        whole.update(data);md5.update(data);blocks.append(block_proof(index,data))
    return {'stored_bytes':size,'stored_sha256':whole.hexdigest(),
            'stored_md5':base64.b64encode(md5.digest()).decode(),'blocks':blocks}


def publish(plan,plan_sha,manifest,manifest_sha,review,client,journal,*,max_stored_bytes):
    privacy_approved(review,manifest_sha)
    if digest(canonical(plan))!=plan_sha:raise ArtifactError('ARCHIVE_BUNDLE_PLAN_SHA_DIFFERS')
    current,source=prepare(manifest,manifest_sha)
    if current!=plan:raise ArtifactError('ARCHIVE_STREAM_PLAN_CHANGED')
    if journal.scope!={'manifest_sha256':plan_sha,'account_url':client.account_url,'container':'archive'}:
        raise ArtifactError('ARCHIVE_JOURNAL_SCOPE')
    measured=measure(source,max_stored_bytes)
    key='originals/'+plan['entries'][0]['sha256']+'/'+digest(b'block-checksum-v1:bundle.tar')+'.gz'
    prior=client.checksum_properties(key)
    verified=journal.last(key,'CHECKSUM_VERIFIED')
    if prior and prior['tier']=='Archive':
        if not verified or any(prior[k]!=verified[k] for k in ('etag','stored_bytes','stored_md5')):
            raise ArtifactError('ARCHIVE_COLD_OBJECT_WITHOUT_MATCHING_VERIFICATION')
        if any(measured[k]!=verified[k] for k in ('stored_bytes','stored_md5','stored_sha256')):
            raise ArtifactError('ARCHIVE_RECORDED_SOURCE_DIFFERS')
    else:
        if prior and prior['tier']!='Cool':raise ArtifactError('ARCHIVE_EXPECTED_COOL')
        remote=client.checksum_blocks(key)
        expected=[(b['block_id'],b['bytes']) for b in measured['blocks']]
        if prior:
            # A claimed MD5 property alone cannot prove the blob. Require every
            # successful server-checked block receipt and committed block order.
            for b in measured['blocks']:
                if not any(e.get('phase')=='BLOCK_CHECKSUM_VALIDATED' and e.get('blob')==key and
                           all(e.get(k)==v for k,v in b.items()) for e in journal.rows):
                    raise ArtifactError('ARCHIVE_EXISTING_BLOB_WITHOUT_BLOCK_PROOFS')
            if remote['committed']!=expected:raise ArtifactError('ARCHIVE_COMMITTED_BLOCKS_DIFFER')
        else:
            seen=[]
            for index,data in enumerate(fixed_blocks(encoded(source))):
                b=block_proof(index,data)
                if index>=len(measured['blocks']) or b!=measured['blocks'][index]:raise ArtifactError('ARCHIVE_STREAM_SOURCE_CHANGED')
                seen.append(b)
                checked=any(e.get('phase')=='BLOCK_CHECKSUM_VALIDATED' and e.get('blob')==key and
                            all(e.get(k)==v for k,v in b.items()) for e in journal.rows)
                if not checked or remote['uncommitted'].get(b['block_id'])!=b['bytes']:
                    client.stage_checked(key,b['block_id'],data)
                    journal.append({'phase':'BLOCK_CHECKSUM_VALIDATED','blob':key,**b})
            if seen!=measured['blocks']:raise ArtifactError('ARCHIVE_STREAM_SOURCE_CHANGED')
            # A compressor may have consumed a source before the first remote
            # block is sent. Recheck current original hashes before commit too.
            for entry in manifest['entries']:verify_unchanged_local(manifest,entry)
            journal.append({'phase':'ORDERED_COMMIT_INTENT','blob':key,'blocks_sha256':digest(canonical(expected)),
                            'stored_md5':measured['stored_md5']})
            client.commit_cool(key,[b['block_id'] for b in measured['blocks']],measured['stored_md5'])
            remote=client.checksum_blocks(key)
            if remote['committed']!=expected:raise ArtifactError('ARCHIVE_COMMITTED_BLOCKS_DIFFER')
        prior=client.checksum_properties(key)
        if not prior or prior['tier']!='Cool' or any(prior[k]!=measured[k] for k in ('stored_bytes','stored_md5')):
            raise ArtifactError('ARCHIVE_CONTENT_MD5_OR_LENGTH_DIFFERS')
        verified={'phase':'CHECKSUM_VERIFIED','blob':key,**prior,**{k:v for k,v in measured.items() if k!='blocks'},
                  'integrity_method':'SERVER_VALIDATED_BLOCK_MD5_ORDERED_COMMIT_AND_STORED_MD5_PROPERTY',
                  'download_performed':False,'server_computed_sha256':False,
                  'verified_at':datetime.now(timezone.utc).isoformat()}
        journal.append(verified)
        client.archive(key,prior['etag'])
        archived=client.checksum_properties(key)
        if not archived or archived['tier']!='Archive' or any(archived[k]!=prior[k] for k in ('etag','stored_bytes','stored_md5')):
            raise ArtifactError('ARCHIVE_TIER_PROOF_DIFFERS')
        journal.append({**verified,'phase':'ARCHIVED_CHECKSUM','tier':'Archive'})
    objects=[]
    for e in manifest['entries']:
        verify_unchanged_local(manifest,e)
        objects.append({**e,'blob':key,'etag':verified['etag'],'tier':'Archive','stored_bytes':measured['stored_bytes'],
                        'stored_bytes_scope':'WHOLE_BUNDLE_NOT_MEMBER','stored_sha256':measured['stored_sha256'],
                        'stored_md5':measured['stored_md5'],'bundle_sha256':plan['entries'][0]['sha256'],
                        'integrity_method':verified['integrity_method'],'download_performed':False})
    return {'version':'checksum-archive-receipt-v1','manifest_sha256':manifest_sha,'objects':objects,
            'original_bytes':sum(e['bytes'] for e in manifest['entries']),'stored_bytes':measured['stored_bytes'],
            'member_proof':plan['member_proof'],'integrity':verified,'local_deletion_performed':False}
