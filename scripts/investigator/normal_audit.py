"""Normal-mode audit, separately labelled from byte-exact test tapes."""
from contextlib import contextmanager
import hashlib,json,os,time
from pathlib import Path
from .process_tape import bytes_of
from .planner_recording import _safe

MODES=frozenset({'NORMAL','TEST'})

def mode(value='NORMAL'):
    if value not in MODES:raise ValueError('INVESTIGATOR_RECORDING_MODE')
    return value

class AuditContext:
    """One safe local journal, batched outer uploads; progress publishes now.

    IDs are logical audit IDs resolved by the published batch index. They are
    not mislabelled Blob paths or exact-replay evidence. Failure flushes partial
    audit records too. No raw provider bodies or native tapes are captured here.
    """
    def __init__(self,parent,run_id):
        self.parent=parent;self.root=Path(parent.root);self.run_id=run_id;self.rows=[];self.timings=[];self.uploaded=0
        self.path=self.root/'normal-audit.jsonl';self.path.parent.mkdir(parents=True,exist_ok=True)
    def __getattr__(self,name):return getattr(self.parent,name)
    def record(self,kind,value):
        raw=bytes_of(value);_safe(raw)
        identity='audit:'+self.run_id+':'+str(len(self.rows)+1)
        entry={'id':identity,'kind':kind,'sha256':hashlib.sha256(raw).hexdigest(),'value':json.loads(raw)}
        encoded=bytes_of(entry);_safe(encoded)
        with self.path.open('ab')as stream:stream.write(encoded+b'\n');stream.flush();os.fsync(stream.fileno())
        self.rows.append(entry)
        if len(self.rows)-self.uploaded>=64:self.flush(partial=True)
        return {'key':identity,'sha256':entry['sha256']}
    def flush(self,*,partial):
        pending=self.rows[self.uploaded:]
        if not pending:return
        reference=self.parent.record('normal-audit-batch',{'version':'normal-audit-v1','recording_mode':'NORMAL',
            'byte_exact_replay':False,'partial':partial,'records':pending})
        self.uploaded=len(self.rows)
        self.parent.record('normal-audit-index',{'version':'normal-audit-index-v1','artifact':reference,'ids':[row['id']for row in pending]})
    def step(self,name,call):
        started=time.monotonic();self.record('step-start',{'name':name})
        try:value=call()
        except BaseException:
            self.timings.append({'phase':name,'wall_seconds':max(0,time.monotonic()-started),'status':'FAILED'});raise
        else:
            elapsed=max(0,time.monotonic()-started);self.timings.append({'phase':name,'wall_seconds':elapsed,'status':'COMPLETED'})
            self.record('step-result',{'name':name,'wall_seconds':elapsed});return value
    def progress(self,value):
        _safe(bytes_of(value));self.record('progress',value)
        # A client never waits for final batch publication to see acknowledgement.
        return self.parent.record('progress',value)

@contextmanager
def normal_context(parent,run_id):
    audit=AuditContext(parent,run_id)
    keys=('INVESTIGATOR_RECORD_RUNS','INVESTIGATOR_RECORD_PLANNER')
    previous={key:os.environ.get(key)for key in keys}
    for key in keys:os.environ[key]='0'
    try:yield audit
    except BaseException as original:
        try:audit.flush(partial=True)
        except BaseException as publication:
            original.add_note('Partial normal-audit publication failed: '+type(publication).__name__)
        raise
    else:audit.flush(partial=False)
    finally:
        for key,value in previous.items():
            if value is None:os.environ.pop(key,None)
            else:os.environ[key]=value
