"""Private exact-class metadata capture; authentication is outside call packets.

Projected discovery is explicitly unavailable: Inventory writes have not been
wired to the memory-only projected capture contract. Never downgrade its class.
"""
import base64,hashlib,json,sqlite3,subprocess
from contextlib import closing,contextmanager
from pathlib import Path
from datetime import datetime,timezone
from types import SimpleNamespace
from urllib.error import HTTPError
from metadata_auth import MetadataHttp
from investigator import process_tape as journal
from investigator.planner_recording import _safe,RecordingError
from investigator.privacy_projection import declaration


def safe(value):
    _safe(journal.bytes_of(value))
    if isinstance(value,dict):
        for key,item in value.items():
            if key.lower() in ('authorization','proxy-authorization','set-cookie','cookie'):
                raise RecordingError('METADATA_CAPTURE_AUTH_HEADER')
            # Native definition payloads are encoded; audit their decoded contents.
            if key=='payload' and isinstance(item,str):
                try:decoded=base64.b64decode(item,validate=True)
                except ValueError:pass
                else:_safe(decoded)
            safe(item)
    elif isinstance(value,list):
        for item in value:safe(item)


class CapturedHttp(MetadataHttp):
    def _send(self,request):
        # Request (including Authorization) never crosses the tape boundary.
        try:
            with self.opener.open(request,timeout=90) as response:
                body=response.read()
                result={'status_code':response.status,'headers':dict(response.headers),
                        'text':json.loads(body) if body else {}}
        except HTTPError as exc:
            body=exc.read()
            result={'status_code':exc.code,'headers':dict(exc.headers),
                    'text':json.loads(body) if body else {}}
        safe(result)
        return result


def snapshot(source,destination):
    # Audit before creating any durable artifact. Backup includes committed state.
    source=Path(source);destination=Path(destination)
    if not source.exists():return None
    with closing(sqlite3.connect(source.resolve().as_uri()+'?mode=ro',uri=True)) as db:
        db.execute('BEGIN')
        tables=[r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        for table in tables:
            quoted='"'+table.replace('"','""')+'"'
            for row in db.execute('SELECT * FROM '+quoted):
                for value in row:
                    if isinstance(value,str):
                        try:safe(json.loads(value))
                        except json.JSONDecodeError:_safe(value.encode())
                    elif isinstance(value,bytes):_safe(value)
        # Backup a separate read connection: the validated snapshot stays stable.
        with closing(sqlite3.connect(destination)) as output:db.backup(output)
        db.rollback()
    return hashlib.sha256(destination.read_bytes()).hexdigest()


@contextmanager
def deterministic_metadata():
    # Scoped adapter seams, serial collection only; never patch stdlib globals.
    from investigator import enterprise_discovery,onboarding
    import metadata_inventory
    before=(enterprise_discovery.utc,metadata_inventory.utc,metadata_inventory.uuid,onboarding.datetime)
    class RecordedDateTime(datetime):
        @classmethod
        def now(cls,tz=None):
            return datetime.fromtimestamp(journal.clock('metadata_store_event'),tz or timezone.utc)
    enterprise_discovery.utc=lambda:datetime.fromtimestamp(journal.clock('metadata_discovery_utc'),timezone.utc).isoformat()
    metadata_inventory.utc=lambda:datetime.fromtimestamp(journal.clock('metadata_inventory_utc'),timezone.utc).isoformat()
    metadata_inventory.uuid=SimpleNamespace(uuid4=journal.uuid4)
    onboarding.datetime=RecordedDateTime
    try:yield
    finally:enterprise_discovery.utc,metadata_inventory.utc,metadata_inventory.uuid,onboarding.datetime=before


class Capture:
    def __init__(self,root,manifest,config,policy,catalog,inventory,engine_hash):
        if declaration(manifest.get('recording',{'tape_class':'EXACT'}))!={'tape_class':'EXACT'}:
            raise RecordingError('PROJECTED_DISCOVERY_CAPTURE_UNIMPLEMENTED')
        safe(manifest);safe(config);safe(policy)
        self.root=Path(root);self.root.mkdir(parents=True,exist_ok=False)
        self.catalog=Path(catalog);self.inventory=Path(inventory)
        support={}
        for name in ('metadata_capture.py','replay_metadata.py'):
            source=Path(__file__).parent/name;content=source.read_bytes();_safe(content)
            (self.root/name).write_bytes(content);support[name]=hashlib.sha256(content).hexdigest()
        revision=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
        artifacts={name:snapshot(source,self.root/name) for name,source in
                   [('catalog.sqlite',self.catalog),('inventory.sqlite',self.inventory)]}
        bootstrap={'entry_point':'billing_metadata_collection',
            'context_identity':'catalog-sha256:'+artifacts['catalog.sqlite'],
            'config':config,'profile':{'capture':'NATIVE_METADATA','tape_class':'EXACT'},
            'usage_policy':policy,'engine_hash':engine_hash,
            'state':{'environment':manifest['environment'],'manifest':manifest,'artifacts':artifacts,'engine_revision':revision,'capture_support':support}}
        if policy is not None:bootstrap['state']['budget_checkpoint']='DELTA_V2'
        self.tape=journal.Tape(self.root/'tape.json',bootstrap)
        if policy is not None:
            from investigator.budget_checkpoint import prepare
            prepare(self.tape,self.root/'catalog.sqlite',manifest['environment'])
        self.scope=journal.active(self.tape);self.scope.__enter__()
        self.metadata_scope=deterministic_metadata();self.metadata_scope.__enter__()
    def call(self,name,request,producer):
        safe(request)
        def checked():
            try:response=producer();safe(response);return response
            except Exception as exc:
                # Do not tape arbitrary error messages/attributes from auth/SDKs.
                raise RuntimeError('METADATA_READ_FAILED:'+type(exc).__name__) from None
        return journal.bounded_call(name,request,checked)
    def finish(self,result):
        try:
            safe(result)
            final=dict(result,artifacts={name:snapshot(source,self.root/name) for name,source in
                [('catalog-after.sqlite',self.catalog),('inventory-after.sqlite',self.inventory)]})
            self.tape.finish(final)
            return {'path':str(self.tape.path),'sha256':hashlib.sha256(self.tape.path.read_bytes()).hexdigest(),
                    'tape_class':'EXACT','artifacts':final['artifacts']}
        finally:
            self.metadata_scope.__exit__(None,None,None)
            self.scope.__exit__(None,None,None)
