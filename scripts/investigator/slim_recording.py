"""Opt-in CAS publication of newly created exact recordings, never old tapes."""
from contextlib import contextmanager
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import stat
from uuid import UUID

from .artifact_store import ArtifactError, BlobObjects, Files, canonical, digest
from . import tape_bundle

VERSION='slim-recording-v1'
CONFIG_ENV='DIA_SLIM_RECORDING_CONFIG'


def validate(value):
    fields={'version','account_url','identity','snapshot_channel','tape_channel','tape_class'}
    if not isinstance(value,dict) or set(value)!=fields or value['version']!=VERSION:
        raise ArtifactError('SLIM_RECORDING_CONFIGURATION')
    if value['tape_class']!='EXACT':raise ArtifactError('SLIM_PROJECTED_CAPTURE_NOT_IMPLEMENTED')
    if not isinstance(value['account_url'],str) or not re.fullmatch(r'https://[a-z0-9]{3,24}\.blob\.core\.windows\.net',value['account_url']):
        raise ArtifactError('SLIM_PLATFORM_BLOB_URL_REQUIRED')
    from .adapters.managed_identity import validate as validate_identity
    validate_identity(value['identity'])
    if any(not isinstance(value[k],str) or not re.fullmatch(r'[A-Za-z0-9_.-]{1,80}',value[k])
           for k in ('snapshot_channel','tape_channel')):
        raise ArtifactError('SLIM_PLATFORM_CHANNEL_REQUIRED')
    return json.loads(canonical(value))


def configuration(agent):
    path=os.environ.get(CONFIG_ENV)
    if not path:return None
    config=validate(json.loads(Path(path).read_bytes()))
    if agent.config.get('_estate',{}).get('recording',{}).get('tape_class','EXACT')!='EXACT':
        raise ArtifactError('SLIM_PROJECTED_CAPTURE_NOT_IMPLEMENTED')
    return config


def stores(config):
    validate(config)
    from .adapters.managed_identity import Tokens
    from .live_gateway import current
    from azure.core.credentials import AccessToken
    tokens=Tokens(config['identity'])
    class BoundCredential:
        def get_token(self,*scopes,**kwargs):
            if scopes!=('https://storage.azure.com/.default',):raise ArtifactError('SLIM_AUTH_SCOPE')
            token=tokens.get_token(scopes[0])
            part=token.split('.')[1]
            claims=json.loads(base64.urlsafe_b64decode(part+'='*(-len(part)%4)))
            return AccessToken(token,int(claims['exp']))
    credential=BoundCredential();gateway=current()
    return (Files(BlobObjects(config['account_url'],'snapshots',credential,channel=config['snapshot_channel'],gateway=gateway)),
            Files(BlobObjects(config['account_url'],'tapes',credential,channel=config['tape_channel'],gateway=gateway)))


def _exclusive(path,value):
    with Path(path).open('xb') as stream:
        stream.write(canonical(value));stream.flush();os.fsync(stream.fileno())


def file_hash(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def publish_sealed(agent,tape):
    config=getattr(tape,'_slim_configuration',None)
    if config is None or getattr(tape,'_slim_published',False):return None
    if not tape.finished or tape.replaying:raise ArtifactError('SLIM_REQUIRES_NEW_SEALED_RECORDING')
    root=tape.path.parent.resolve(strict=True)
    if root!=getattr(tape,'_slim_owned_root',None) or root.name!=str(UUID(root.name)):
        raise ArtifactError('SLIM_PRIVATE_DIRECTORY_OWNERSHIP_REQUIRED')
    from .run_recording import backup
    final_files={}
    # Independent snapshots, never a rename/unlink of the store or shared ledger.
    for name,source in [('catalog.sqlite',agent.store.database),('inventory.sqlite',agent.store.inventory)]:
        path=root/('final-'+name)
        if path.exists():raise ArtifactError('SLIM_FINAL_SNAPSHOT_ALREADY_EXISTS')
        backup(source,path)
        if name=='catalog.sqlite' and getattr(agent.store,'shared_accounting',None):
            from .shared_accounting import materialize
            materialize(path,agent.store.shared_accounting)
        final_files[name]=path
    snapshots,envelopes=stores(config)
    bundle=tape_bundle.pack(root,snapshots,tape_class='EXACT',final_files=final_files)
    # Read back every original and final object before making any local copy disposable.
    with tape_bundle.materialize(bundle,snapshots):pass
    for ref in bundle['final_state'].values():snapshots.verify(ref['sha256'])
    envelope=root/'snapshot-bundle.json'
    _exclusive(envelope,bundle)
    published=envelopes.capture(envelope);envelopes.verify(published['sha256'])
    receipt={'version':VERSION,'configuration':config,'bundle':published,'bundle_seal':bundle['seal'],
             'source_seal':bundle['source_seal'],'restoration_verified':True,'engine_replay':'NOT_RUN',
             'retired_private_files':[]}
    # Pin remote envelope before retirement; partial cleanup remains recoverable.
    pointer=root/'slim-recording.json'
    _exclusive(pointer,receipt)
    candidates=[(root/name,ref) for name,ref in bundle['files'].items() if name.endswith('.sqlite')]
    candidates += [(final_files[name],ref) for name,ref in bundle['final_state'].items()]
    for path,ref in candidates:
        info=path.lstat()
        if (path.parent.resolve()!=root or stat.S_ISLNK(info.st_mode) or
            getattr(info,'st_file_attributes',0)&0x400 or info.st_nlink!=1 or
            info.st_size!=ref['bytes'] or file_hash(path)!=ref['sha256']):
            raise ArtifactError('SLIM_RETIREMENT_LOCAL_COPY_CHANGED')
    for path,ref in candidates:
        path.unlink()
        receipt['retired_private_files'].append({'name':path.name,**ref})
        with (root/'slim-retirements.jsonl').open('ab') as log:
            log.write(canonical(receipt['retired_private_files'][-1])+b'\n');log.flush();os.fsync(log.fileno())
    tape._slim_published=True
    return receipt


@contextmanager
def materialize(path, *, storage=None):
    """Restore an exact tape to disposable job scratch for existing replay APIs."""
    path=Path(path)
    pointer=path if path.name=='slim-recording.json' else path.parent/'slim-recording.json'
    if not pointer.exists():
        yield path;return
    receipt=json.loads(pointer.read_bytes())
    if receipt.get('version')!=VERSION or receipt.get('restoration_verified') is not True:
        raise ArtifactError('SLIM_POINTER_INVALID')
    config=validate(receipt['configuration'])
    snapshots,envelopes=storage or stores(config)
    import tempfile
    with tempfile.TemporaryDirectory(prefix='slim-envelope-') as temporary:
        envelope=envelopes.restore(receipt['bundle']['sha256'],Path(temporary)/'bundle.json')
        bundle=tape_bundle.validate(json.loads(envelope.read_bytes()))
        if bundle['seal']!=receipt['bundle_seal'] or bundle['source_seal']!=receipt['source_seal']:
            raise ArtifactError('SLIM_POINTER_SEAL_DIFFERS')
        with tape_bundle.materialize(bundle,snapshots) as restored:
            if path.name!='slim-recording.json' and path.exists() and file_hash(path)!=file_hash(restored):
                raise ArtifactError('SLIM_LOCAL_TAPE_DIFFERS')
            yield restored
