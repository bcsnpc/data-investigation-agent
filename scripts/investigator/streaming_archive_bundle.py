"""Deterministic, lossless archive bundles with no on-disk body staging."""
import hashlib
import io
from pathlib import Path
import tarfile

from .archive_migration import verify_local, privacy_approved, encoded_stream
from .artifact_store import ArtifactError, canonical, digest
from .resumable_archive import publish_resumable


class _Reader(io.RawIOBase):
    def __init__(self, chunks):
        self.chunks=iter(chunks)
        self.pending=b''
    def readable(self):return True
    def read(self,size=-1):
        if size<0:raise ArtifactError('ARCHIVE_STREAM_UNBOUNDED_READ')
        result=bytearray()
        while len(result)<size:
            if not self.pending:
                self.pending=next(self.chunks,b'')
                if not self.pending:break
            take=min(size-len(result),len(self.pending))
            result.extend(self.pending[:take]);self.pending=self.pending[take:]
        return bytes(result)
    def close(self):
        self.chunks.close()
        super().close()


class _Source:
    def __init__(self,manifest,paths):
        self.manifest=manifest
        self.paths=paths
    def open(self,mode):
        if mode!='rb':raise ArtifactError('ARCHIVE_STREAM_READ_ONLY')
        return _Reader(self.chunks())
    def chunks(self):
        offset=0
        metadata=canonical(self.manifest)
        info=tarfile.TarInfo('manifest.json');info.size=len(metadata)
        header=info.tobuf(format=tarfile.PAX_FORMAT)
        yield header;yield metadata
        padding=(-len(metadata))%512
        if padding:yield bytes(padding)
        offset+=len(header)+len(metadata)+padding
        seen=set()
        for entry,path in zip(self.manifest['entries'],self.paths):
            if entry['sha256'] in seen:continue
            seen.add(entry['sha256'])
            info=tarfile.TarInfo('objects/'+entry['sha256']);info.size=entry['bytes']
            header=info.tobuf(format=tarfile.PAX_FORMAT)
            yield header;offset+=len(header)
            whole=hashlib.sha256();size=0
            with path.open('rb') as stream:
                for block in iter(lambda:stream.read(1024*1024),b''):
                    size+=len(block)
                    if size>entry['bytes']:raise ArtifactError('ARCHIVE_STREAM_SOURCE_CHANGED')
                    whole.update(block);yield block
            if size!=entry['bytes'] or whole.hexdigest()!=entry['sha256']:
                raise ArtifactError('ARCHIVE_STREAM_SOURCE_CHANGED')
            padding=(-size)%512
            if padding:yield bytes(padding)
            offset+=size+padding
        yield bytes(1024);offset+=1024
        padding=(-offset)%tarfile.RECORDSIZE
        if padding:yield bytes(padding)


def prepare(manifest,manifest_sha):
    if digest(canonical(manifest))!=manifest_sha:
        raise ArtifactError('ARCHIVE_MANIFEST_SHA_DIFFERS')
    paths=[verify_local(manifest,entry) for entry in manifest['entries']]
    source=_Source(manifest,paths)
    whole=hashlib.sha256();size=0
    for block in source.chunks():whole.update(block);size+=len(block)
    unique={entry['sha256']:entry['bytes'] for entry in manifest['entries']}
    proof={'source_manifest_sha256':manifest_sha,'bundle_sha256':whole.hexdigest(),
           'bundle_bytes':size,'original_paths':len(manifest['entries']),
           'unique_objects':len(unique),'unique_original_bytes':sum(unique.values())}
    return {'version':'streamed-source-bundle-v1','storage_encoding':'gzip',
            'source_manifest_sha256':manifest_sha,'member_proof':proof,
            'entries':[{'path':'bundle.tar','sha256':whole.hexdigest(),'bytes':size}]},source


def publish(plan,plan_sha,manifest,manifest_sha,review,client,journal,*,max_stored_bytes):
    privacy_approved(review,manifest_sha)
    if digest(canonical(plan))!=plan_sha:raise ArtifactError('ARCHIVE_BUNDLE_PLAN_SHA_DIFFERS')
    current,source=prepare(manifest,manifest_sha)
    if current!=plan:raise ArtifactError('ARCHIVE_STREAM_PLAN_CHANGED')
    def verified_source(actual,entry):
        if actual!=plan or entry!=plan['entries'][0]:
            raise ArtifactError('ARCHIVE_STREAM_ENTRY_CHANGED')
        return source
    bundle_review={**review,'manifest_sha256':plan_sha,'source_manifest_sha256':manifest_sha}
    def encode(current,encoding,stats):
        with current.open('rb') as stream:
            yield from encoded_stream(stream,encoding,stats)
    remote=publish_resumable(plan,plan_sha,bundle_review,client,journal,
                             source_verifier=verified_source,max_stored_bytes=max_stored_bytes,
                             source_encoder=encode)
    archived=remote['objects'][0]
    objects=[]
    for entry in manifest['entries']:
        verify_local(manifest,entry)
        objects.append({**entry,'blob':archived['blob'],'etag':archived['etag'],'tier':'Archive',
                        'download_verified_sha256':entry['sha256'],'original_bytes':entry['bytes'],
                        'stored_bytes':archived['stored_bytes'],'stored_sha256':archived['stored_sha256'],
                        'stored_bytes_scope':'WHOLE_BUNDLE_NOT_MEMBER','storage_encoding':'gzip',
                        'member':'objects/'+entry['sha256'],'bundle_sha256':plan['member_proof']['bundle_sha256'],
                        'verified_at':archived['verified_at']})
    return {'version':'verified-archive-receipt-v1','manifest_sha256':manifest_sha,'privacy_review':review,
            'objects':objects,'bundle_receipt':remote,'member_proof':plan['member_proof'],
            'original_bytes':sum(entry['bytes'] for entry in manifest['entries']),
            'stored_bytes':archived['stored_bytes'],'local_deletion_performed':False,
            'mode':'STREAMED_BUNDLE_NO_BODY_STAGING','max_stored_bytes':max_stored_bytes}
