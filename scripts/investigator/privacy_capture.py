"""One projected installation capture boundary for stores, sidecars and tape.

All raw material is staged in memory. Finalization discovers typed values
across the whole capture before projecting dependent identities and writing.
This module never loads raw legacy databases into a projected installation.
"""
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
import hashlib
from .privacy_projection import ProjectionError,canonical
from .privacy_identities import Identities,active as identity_active
from .privacy_storage import EvidenceStore
from .provider_tape_contract import parse

ACTIVE=ContextVar('privacy_capture',default=None)


def input_characters(value):
    """Replay the actual capture cost, not the longer projected spelling.

    The source size is metering evidence. Replay first byte-matches the sealed
    projected payload before returning its recorded size; live admission always
    uses the actual producer input length.
    """
    from .onboarding import encoded
    from .process_tape import ACTIVE as TAPE
    tape=TAPE.get()
    actual=len(encoded(value))
    if tape is None or tape.tape_class!='PRIVACY_PROJECTED':return actual
    if tape.replaying:
        saved=parse(tape.take('INPUT_SIZE'))
        if canonical(tape.projection.project(value))!=canonical(saved['payload']):
            raise ProjectionError('PRIVACY_METERED_PAYLOAD_DIFFERS')
        if type(saved['characters']) is not int or saved['characters']<0:
            raise ProjectionError('PRIVACY_METERED_SIZE_INVALID')
        return saved['characters']
    tape.event('INPUT_SIZE',canonical({'payload':value,'characters':actual}))
    return actual


class Capture:
    def __init__(self,projection,paths):
        self.projection=projection;self.identities=Identities(projection)
        self.stores=[];self.sidecars=[];self.ledgers={};self.running=False
        try:
            for path in paths:self.stores.append(EvidenceStore(path,projection))
        except BaseException:
            self.close();raise

    @contextmanager
    def active(self):
        if ACTIVE.get() not in (None,self):raise ProjectionError('PRIVACY_CAPTURE_CLASSES_CANNOT_MIX')
        token=ACTIVE.set(self)
        with identity_active(self.identities):
            try:yield self
            finally:ACTIVE.reset(token)

    def sidecar(self,record,name,data):
        # Validate before staging; arbitrary raw bytes are never a fallback.
        body=parse(data)
        self.projection.discover(body)
        self.sidecars.append((record,name,body))

    def ledger_rows(self,path):
        path=Path(path).resolve()
        if path not in self.ledgers:
            rows=[]
            if path.exists():
                import hmac
                value=parse(path.read_bytes())
                if set(value)!={'version','projection','rows','seal'} or value['version']!='privacy-projected-ledger-v1':
                    raise ProjectionError('PRIVACY_RAW_LEDGER_REFUSED')
                self.projection.require_descriptor(value['projection'])
                if not hmac.compare_digest(value['seal'],self.projection.sign({k:v for k,v in value.items() if k!='seal'})):
                    raise ProjectionError('PRIVACY_LEDGER_SEAL')
                self.projection.trust_sealed_tokens(value);rows=value['rows']
            self.ledgers[path]=rows
        return self.ledgers[path]

    def ledger_append(self,path,row):
        self.projection.discover(row)
        self.ledger_rows(path).append(row)

    def prepare(self,tape=None,final=None):
        images=[store.prepare() for store in self.stores]
        for _,_,body in self.sidecars:self.projection.discover(body)
        for rows in self.ledgers.values():self.projection.discover(rows)
        if tape is not None:
            import base64
            for event in tape.events:
                self.projection.discover(parse(base64.b64decode(event['body']) if tape.replaying else event['body']))
        if final is not None:self.projection.discover(final)
        self.identities.prepare();self.projection.prepare_spans();self.identities.rekey()
        self.projection.prepare_spans()
        return images

    def finish(self,tape,final):
        images=self.prepare(tape,final)
        # Preflight every durable value before opening any output file.
        projected=self.projection.project(final)
        for image in images:self.projection.project(image)
        if tape.replaying:
            tape.finish(projected)
            return projected
        owners={record for record,_,_ in self.sidecars}
        for record in owners:
            if sum(owner is record and name=='manifest.json' for owner,name,_ in self.sidecars)!=1:
                raise ProjectionError('PRIVACY_SIDECAR_MANIFEST_REQUIRED')
        ledgers=[]
        for path,rows in self.ledgers.items():
            value={'version':'privacy-projected-ledger-v1','projection':self.projection.descriptor(),
                   'rows':self.projection.project(rows)}
            value['seal']=self.projection.sign(value)
            from .planner_recording import _safe
            data=canonical(value);_safe(data);ledgers.append((path,data))
        projected_sidecars=[]
        for record,name,body in self.sidecars:
            data=canonical(self.projection.project(body))
            from .planner_recording import _safe
            _safe(data)
            projected_sidecars.append((record,name,data))
        for store,image in zip(self.stores,images):store.persist(image)
        for path,data in ledgers:
            from secrets import token_hex
            path.parent.mkdir(parents=True,exist_ok=True)
            history=path.with_name(path.name+'.history');history.mkdir(exist_ok=True)
            sealed=history/(hashlib.sha256(data).hexdigest()+'.json')
            if not sealed.exists():
                with sealed.open('xb') as stream:stream.write(data)
            temporary=path.with_name(path.name+'.projected-'+token_hex(16)+'.tmp')
            with temporary.open('xb') as stream:stream.write(data)
            temporary.replace(path)
        records={}
        for record,name,data in projected_sidecars:
            # Recompute metadata from projected bytes, never copy raw byte
            # counts or unkeyed raw-body seals into the manifest.
            if name=='manifest.json':continue
            record.path.mkdir(parents=True,exist_ok=True)
            with (record.path/name).open('xb') as stream:stream.write(data)
            records.setdefault(record,{})[name]={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
        for record,files in records.items():
            manifests=[body for owner,name,body in self.sidecars if owner is record and name=='manifest.json']
            if len(manifests)!=1:raise ProjectionError('PRIVACY_SIDECAR_MANIFEST_REQUIRED')
            manifest=self.projection.project(manifests[0]);manifest['files']=files
            manifest['tape_class']='PRIVACY_PROJECTED'
            manifest['projection']=self.projection.descriptor()
            manifest['seal']=self.projection.sign(manifest)
            with (record.path/'manifest.json').open('xb') as stream:stream.write(canonical(manifest))
            record.bodies=files
        tape.finish(projected)
        self.sidecars=[]
        return projected

    def close(self):
        for store in self.stores:store.close()
