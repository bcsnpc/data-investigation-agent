"""Private bounded-worker journal. Upstream decoding is outside replay coverage."""
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
import base64
import hashlib
import json
from pathlib import Path
import time
import math
import re
import sqlite3
from contextlib import closing
from uuid import uuid4 as new_uuid, UUID

ACTIVE = ContextVar('process_tape', default=None)
VERSION = 'bounded-worker-tape-v5'
SUPPORTED_VERSIONS = frozenset(('bounded-worker-tape-v1', 'bounded-worker-tape-v2', 'bounded-worker-tape-v3', 'bounded-worker-tape-v4', VERSION))
PINNED_VERSIONS = SUPPORTED_VERSIONS - {'bounded-worker-tape-v1'}
ACCOUNTED_VERSIONS = frozenset(('bounded-worker-tape-v3','bounded-worker-tape-v4',VERSION))
SMART_VERSIONS = frozenset((VERSION,))
SMART_OPERATIONS=frozenset(('ticket_submit','ticket_reply','ticket_attach','ticket_share','ticket_close','ticket_respond','ticket_finish'))
KINDS = frozenset({'BOOTSTRAP','OPERATION_START','OPERATION_END','CONFIGURATION',
    'BUDGET','BUDGET_INPUT','CLOCK','IDENTITY','WORKER_START','WORKER_SEND','WORKER_READ','WORKER_END','WORKER_FAILURE',
    'PROVIDER_REQUEST','PROVIDER_RESPONSE','PROVIDER_FAILURE','AUTH_STATE',
    'BOUNDED_REQUEST','BOUNDED_RESPONSE','BOUNDED_FAILURE','FINAL'})
UUID_PATTERN=re.compile(r'(?i)\b[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\b')


class TapeError(ValueError):
    pass


def bytes_of(value):
    return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()


def sha(data):return hashlib.sha256(data).hexdigest()


def validate_event(event,ordinal):
    if not isinstance(event,dict) or set(event)!={'ordinal','kind','body','sha256','at'}:
        raise TapeError('TAPE_EVENT_FIELDS')
    if type(event['ordinal']) is not int or event['ordinal']!=ordinal or event['kind'] not in KINDS:
        raise TapeError('TAPE_EVENT_ORDER_OR_KIND')
    if type(event['at']) not in (int,float) or not math.isfinite(event['at']):raise TapeError('TAPE_EVENT_TIME')
    try:body=base64.b64decode(event['body'],validate=True)
    except (ValueError,TypeError) as exc:raise TapeError('TAPE_BODY_ENCODING') from exc
    if sha(body)!=event['sha256']:raise TapeError('TAPE_BODY_INTEGRITY')
    return body


class Tape:
    # Legacy v1-v4 are always exact. No new declaration can reinterpret their
    # bytes as privacy-projected or mix the contracts within an estate.
    tape_class='EXACT'
    def __init__(self,path,bootstrap=None):
        if bootstrap is not None and bootstrap.get('config',{}).get('_estate',{}).get('recording',{}).get('tape_class')=='PRIVACY_PROJECTED':
            raise TapeError('PRIVACY_PROJECTED_CANNOT_USE_EXACT_CAPTURE')
        self.path=Path(path);self.events=[];self.index=0;self.replaying=bootstrap is None
        self.journal_path=self.path.with_suffix('.events.jsonl')
        self.exclusions=[];self.finished=False;self.version=VERSION
        if self.replaying:
            value=json.loads(self.path.read_bytes())
            required={'version','events','exclusions','seal'}
            if value.get('version') in PINNED_VERSIONS:required.add('engine_revision')
            if value.get('version') in ACCOUNTED_VERSIONS:required.add('accounting_version')
            if set(value)!=required or value['version'] not in SUPPORTED_VERSIONS:
                raise TapeError('TAPE_SCHEMA')
            if value['seal']!=sha(bytes_of({k:v for k,v in value.items() if k!='seal'})):
                raise TapeError('TAPE_SEAL')
            self.version=value['version']
            from .budget_tape_contract import ACCOUNTING_VERSION
            if self.version in ACCOUNTED_VERSIONS and value['accounting_version']!=ACCOUNTING_VERSION:
                raise TapeError('TAPE_ACCOUNTING_VERSION')
            self.engine_revision=value.get('engine_revision')
            if self.version in PINNED_VERSIONS and self.engine_revision is not None and not re.fullmatch('[0-9a-f]{40}',self.engine_revision):
                raise TapeError('TAPE_ENGINE_REVISION')
            self.events=value['events'];self.exclusions=value['exclusions']
            if self.journal_path.exists():
                recorded=[json.loads(line) for line in self.journal_path.read_bytes().splitlines()]
                if recorded!=self.events:raise TapeError('TAPE_EVENT_JOURNAL_DIFFERS')
            self.validate()
            self.bootstrap=json.loads(self.take('BOOTSTRAP'))
        else:
            self.path.parent.mkdir(parents=True,exist_ok=True)
            if self.path.exists() or self.journal_path.exists():raise TapeError('TAPE_ALREADY_EXISTS')
            self.bootstrap=bootstrap
            self.engine_revision=None
            if self.version in PINNED_VERSIONS and (bootstrap['entry_point']=='workspace'
                    or self.version in ('bounded-worker-tape-v4','bounded-worker-tape-v5') and bootstrap['entry_point'] in ('code_reader','code_verifier')):
                import subprocess
                root=Path(__file__).resolve().parents[2]
                from .runtime import FINGERPRINT_TRANSPORTS
                scope=['scripts/investigator',*FINGERPRINT_TRANSPORTS]
                dirty=subprocess.check_output(['git','status','--porcelain','--untracked-files=all','--',*scope],cwd=root,text=True)
                if dirty.strip():raise TapeError('TAPE_UNCOMMITTED_ENGINE')
                self.engine_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
            self.event('BOOTSTRAP',bytes_of(bootstrap))

    def flush(self):
        if self.replaying:return
        value={'version':self.version,'events':self.events,'exclusions':self.exclusions}
        if self.version in PINNED_VERSIONS:value['engine_revision']=self.engine_revision
        if self.version in ACCOUNTED_VERSIONS:
            from .budget_tape_contract import ACCOUNTING_VERSION
            value['accounting_version']=ACCOUNTING_VERSION
        value['seal']=sha(bytes_of(value))
        # Only this still-open attempt is rewritten. Sealed tapes are immutable.
        self.path.write_bytes(bytes_of(value))

    def event(self,kind,body):
        if not isinstance(body,bytes):raise TypeError('Tape bodies must be bytes')
        if self.replaying:
            recorded=self.take(kind)
            if kind=='BUDGET':
                from .budget_tape_contract import equal
                if not equal(recorded,body):raise TapeError('TAPE_BUDGET_DECISION_DIFFERS')
            elif kind in ('PROVIDER_REQUEST','PROVIDER_RESPONSE'):
                from .provider_tape_contract import equal
                if not equal(kind,recorded,body):raise TapeError('TAPE_PROVIDER_CONTENT_DIFFERS')
            elif recorded!=body:raise TapeError('TAPE_REQUEST_BYTES_DIFFER')
            return
        if self.finished or kind not in KINDS:raise TapeError('TAPE_EVENT_NOT_ADMISSIBLE')
        from .planner_recording import _safe, RecordingError
        try:_safe(body)
        except RecordingError:
            self.exclusions.append({'ordinal':len(self.events)+1,'kind':kind,'reason':'SECRET_DETECTED'})
            self.flush()
            return
        self.events.append({'ordinal':len(self.events)+1,'kind':kind,
                            'body':base64.b64encode(body).decode(),'sha256':sha(body),'at':time.time()})
        # Persist every event once, including clocks. Rewriting all large worker
        # and budget bodies for every clock tick amplified local I/O quadratically
        # and consumed the live procedure's deadline before it dispatched work.
        with self.journal_path.open('ab') as journal:journal.write(bytes_of(self.events[-1])+b'\n')
        # The append-only journal retains every event before returning. Rewriting
        # all prior bodies during each admission delayed ALLOW to the child and
        # consumed its deadline. Materialize the envelope at the two boundaries;
        # FINAL includes the full journal. Interrupted journals remain evidence,
        # but are incomplete and cannot masquerade as replayable finished tapes.
        if kind in ('BOOTSTRAP','FINAL'):self.flush()

    def take(self,kind):
        if self.index>=len(self.events):raise TapeError('TAPE_EXHAUSTED')
        event=self.events[self.index]
        body=validate_event(event,self.index+1)
        if event['kind']!=kind:raise TapeError('TAPE_EVENT_DIFFERS:'+kind+':'+event['kind'])
        self.index+=1
        return body

    def validate(self):
        if self.exclusions:raise TapeError('TAPE_EXCLUDED_BODY')
        if not self.events or self.events[0]['kind']!='BOOTSTRAP' or self.events[-1]['kind']!='FINAL':
            raise TapeError('TAPE_INCOMPLETE')
        for n,event in enumerate(self.events,1):validate_event(event,n)
        bootstrap=json.loads(validate_event(self.events[0],1))
        required={'entry_point','context_identity','config','profile','usage_policy','engine_hash','state'}
        if not isinstance(bootstrap,dict) or set(bootstrap)!=required:
            raise TapeError('TAPE_BOOTSTRAP_FIELDS')
        if not bootstrap['context_identity'] or not bootstrap['engine_hash']:
            raise TapeError('TAPE_BOOTSTRAP_IDENTITY')
        if any(not isinstance(bootstrap[key],dict) for key in ('config','profile','state')) or not isinstance(bootstrap['usage_policy'],(dict,type(None))):
            raise TapeError('TAPE_BOOTSTRAP_CONFIGURATION')
        if self.version in ('bounded-worker-tape-v4','bounded-worker-tape-v5') and bootstrap['entry_point'] in ('code_reader','code_verifier') and self.engine_revision is None:
            raise TapeError('TAPE_ENGINE_REVISION_MISSING')
        if bootstrap['entry_point']=='workspace':
            if self.version in PINNED_VERSIONS and self.engine_revision is None:
                raise TapeError('TAPE_ENGINE_REVISION_MISSING')
            state=bootstrap['state']
            fields={'environment','workspace_owner','artifacts','dynamic_read_limit','dynamic_input_limit'}
            if 'smart_intake' in state:
                if self.version not in SMART_VERSIONS:raise TapeError('TAPE_SMART_INTAKE_VERSION')
                fields.add('smart_intake')
                from .ticket_clarification import settings as intake_settings
                from jsonschema.exceptions import ValidationError
                try:intake_settings(state['smart_intake'])
                except (ValueError,TypeError,ValidationError):raise TapeError('TAPE_SMART_INTAKE_CONFIGURATION')
            if 'smart_ownership' in state:
                if self.version not in SMART_VERSIONS:raise TapeError('TAPE_SMART_INTAKE_VERSION')
                fields.add('smart_ownership')
                from .ticket_protocol import OWNERSHIP
                from jsonschema import Draft202012Validator
                from jsonschema.exceptions import ValidationError
                try:Draft202012Validator(OWNERSHIP).validate(state['smart_ownership'])
                except ValidationError:raise TapeError('TAPE_SMART_OWNERSHIP_CONFIGURATION')
            if 'fixture_state' in state:
                fields.add('fixture_state')
                binding=state['fixture_state']
                if (not isinstance(binding,dict) or set(binding)!={'name','definition_hash','context','approval_reference'}
                    or not isinstance(binding['name'],str) or not re.fullmatch('[a-z][a-z0-9-]{0,99}',binding['name'])
                    or not isinstance(binding['definition_hash'],str) or not re.fullmatch('[0-9a-f]{64}',binding['definition_hash'])
                    or not isinstance(binding['approval_reference'],str) or not binding['approval_reference'].strip()):
                    raise TapeError('TAPE_FIXTURE_STATE')
                from .acceptance_context import validate_case_pin
                try:validate_case_pin({'context_pin':binding['context']})
                except (ValueError,TypeError,KeyError):raise TapeError('TAPE_FIXTURE_STATE')
                if binding['context'] not in state.get('context_pins',{}).values():raise TapeError('TAPE_FIXTURE_CONTEXT_DIFFERS')
            if 'context_pins' in state:
                fields.add('context_pins')
                pins=state['context_pins']
                if not isinstance(pins,dict) or not pins:raise TapeError('TAPE_CONTEXT_PINS')
                for identity,pin in pins.items():
                    if (not isinstance(identity,str) or not identity or not isinstance(pin,dict)
                        or set(pin)!={'context_id','hash'}
                        or not isinstance(pin['context_id'],str) or not UUID_PATTERN.fullmatch(pin['context_id'])
                        or not isinstance(pin['hash'],str) or not re.fullmatch('[0-9a-f]{64}',pin['hash'])):
                        raise TapeError('TAPE_CONTEXT_PINS')
            if set(state)!=fields:raise TapeError('TAPE_BOOTSTRAP_STATE_FIELDS')
            if not isinstance(state['environment'],str) or not state['environment']:
                raise TapeError('TAPE_BOOTSTRAP_ENVIRONMENT')
            if type(state['dynamic_read_limit']) is not int or state['dynamic_read_limit']<1 or type(state['dynamic_input_limit']) is not int or state['dynamic_input_limit']<1:
                raise TapeError('TAPE_BOOTSTRAP_LIMITS')
            artifacts=state['artifacts']
            if not isinstance(artifacts,dict) or set(artifacts)!={'catalog.sqlite','inventory.sqlite'} or any(not isinstance(v,str) or len(v)!=64 or any(c not in '0123456789abcdef' for c in v) for v in artifacts.values()):
                raise TapeError('TAPE_BOOTSTRAP_ARTIFACTS')
            final=json.loads(validate_event(self.events[-1],len(self.events)))
            if not isinstance(final,dict) or set(final)!={'operation','error','outputs','status','result'}:
                raise TapeError('TAPE_FINAL_FIELDS')
            synthesis=(final.get('result') or {}).get('synthesis') or {}
            failed_composition=(synthesis.get('status')=='FAILED'
                and type(synthesis.get('calls')) is int and synthesis['calls']>0
                and isinstance(synthesis.get('error'),dict)
                and isinstance(synthesis['error'].get('error_type'),str)
                and bool(synthesis['error']['error_type'])
                and not synthesis.get('outputs'))
            # Procedure completion is not narrative completion. A failed
            # composition is replayable failure evidence, with no outputs;
            # it must never satisfy the dual-output acceptance gate.
            if final['status']=='COMPLETED' and final['error'] is None and not failed_composition:
                outputs=final['outputs']
                if not isinstance(outputs,dict) or not {'business_output','technical_output'}<=outputs.keys() or any(not isinstance(outputs[key],dict) or not isinstance(outputs[key].get('explanation',{}).get('text'),str) or not outputs[key]['explanation']['text'] for key in ('business_output','technical_output')):
                    raise TapeError('TAPE_COMPLETED_OUTPUTS_MISSING')
            # A final result cannot introduce an identity whose provenance is
            # absent from recorded inputs, generated-identity events or pinned
            # bootstrap state. This catches missed identity producers rather
            # than declaring an incomplete tape valid until replay finds it.
            known=set()
            for event in self.events[:-1]:
                known.update(v.casefold() for v in UUID_PATTERN.findall(validate_event(event,event['ordinal']).decode('utf8')))
            for name,expected in artifacts.items():
                source=self.path.parent/name
                if not source.exists() or sha(source.read_bytes())!=expected:
                    raise TapeError('TAPE_BOOTSTRAP_ARTIFACT_CHANGED:'+name)
                with closing(sqlite3.connect(source.resolve().as_uri()+'?mode=ro',uri=True)) as db:
                    tables=[r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")]
                    for table in tables:
                        quoted='"'+table.replace('"','""')+'"'
                        for row in db.execute('SELECT * FROM '+quoted):
                            for value in row:
                                if isinstance(value,str):known.update(v.casefold() for v in UUID_PATTERN.findall(value))
            introduced={v.casefold() for v in UUID_PATTERN.findall(bytes_of(final).decode())}-known
            if introduced:raise TapeError('TAPE_UNRECORDED_IDENTITY:'+','.join(sorted(introduced)))
        # Every started operation/provider/worker has a terminal event, in order.
        operations=[];workers=0;providers=0;bounded=0
        previous_usage=None;external_checkpoint=False
        for event in self.events:
            kind=event['kind']
            if kind=='BUDGET_INPUT':external_checkpoint=True
            elif kind=='BUDGET':
                budget=json.loads(validate_event(event,event['ordinal']))
                if budget.get('phase') in ('BEFORE','AFTER') and 'usage_rows' in budget.get('state',{}):
                    rows=budget['state']['usage_rows']
                    if budget['phase']=='BEFORE' and previous_usage is not None and rows!=previous_usage and not external_checkpoint:
                        raise TapeError('TAPE_UNRECORDED_BUDGET_INPUT')
                    previous_usage=rows;external_checkpoint=False
            elif kind=='OPERATION_START':
                body=json.loads(validate_event(event,event['ordinal']))
                supported={'intake','preview','create','run','synthesize'}
                if self.version in SMART_VERSIONS:supported.update(SMART_OPERATIONS)
                if bootstrap['entry_point']=='workspace' and (set(body)!={'name','args','kwargs'} or body['name'] not in supported or not isinstance(body['args'],list) or not isinstance(body['kwargs'],dict)):
                    raise TapeError('TAPE_OPERATION_FIELDS')
                operations.append(body['name'])
            elif kind=='OPERATION_END':
                name=json.loads(validate_event(event,event['ordinal']))['name']
                if not operations or operations.pop()!=name:raise TapeError('TAPE_OPERATION_UNBALANCED')
            elif kind=='WORKER_START':workers+=1
            elif kind in ('WORKER_SEND','WORKER_READ') and workers!=1:raise TapeError('TAPE_WORKER_RESPONSE_WITHOUT_REQUEST')
            elif kind=='WORKER_FAILURE':
                if workers!=1:raise TapeError('TAPE_WORKER_FAILURE_WITHOUT_REQUEST')
                body=json.loads(validate_event(event,event['ordinal']))
                if set(body)!={'operation','failure'} or body['operation'] not in ('write','flush','readline','deadline'):
                    raise TapeError('TAPE_WORKER_FAILURE_FIELDS')
                from .process_failure import validate as failure_detail
                failure_detail(body['failure'])
            elif kind=='WORKER_END':
                workers-=1
                if workers<0:raise TapeError('TAPE_WORKER_UNBALANCED')
            elif kind=='PROVIDER_REQUEST':providers+=1
            elif kind in ('PROVIDER_RESPONSE','PROVIDER_FAILURE'):
                providers-=1
                if providers<0:raise TapeError('TAPE_PROVIDER_UNBALANCED')
                if kind=='PROVIDER_RESPONSE':
                    response=json.loads(validate_event(event,event['ordinal']))
                    if set(response)!={'status','body'} or type(response['status']) is not int:
                        raise TapeError('TAPE_PROVIDER_RESPONSE_FIELDS')
                    try:base64.b64decode(response['body'],validate=True)
                    except (ValueError,TypeError) as exc:raise TapeError('TAPE_PROVIDER_BODY_ENCODING') from exc
            elif kind=='BOUNDED_REQUEST':bounded+=1
            elif kind in ('BOUNDED_RESPONSE','BOUNDED_FAILURE'):
                bounded-=1
                if bounded<0:raise TapeError('TAPE_BOUNDED_READ_UNBALANCED')
        if operations or workers or providers or bounded:raise TapeError('TAPE_UNFINISHED_ATTEMPT')

    def finish(self,result):
        self.event('FINAL',bytes_of(result))
        self.finished=True
        self.validate()
        if self.replaying and self.index!=len(self.events):raise TapeError('TAPE_NOT_CONSUMED')


@contextmanager
def active(tape):
    token=ACTIVE.set(tape)
    try:yield tape
    finally:ACTIVE.reset(token)


def event(kind,value):
    tape=ACTIVE.get()
    if tape:tape.event(kind,bytes_of(value))


def value(kind,name,producer):
    tape=ACTIVE.get()
    if tape and tape.replaying:
        saved=json.loads(tape.take(kind))
        if saved['name']!=name:raise TapeError('TAPE_VALUE_SOURCE_DIFFERS')
        return saved['value']
    result=producer()
    if tape:tape.event(kind,bytes_of({'name':name,'value':result}))
    return result


def uuid4():return UUID(value('IDENTITY','uuid4',lambda:str(new_uuid())))
def clock(name,producer=time.time):return value('CLOCK',name,producer)
def utc_now():return datetime.fromtimestamp(clock('utc_now'),timezone.utc).isoformat()


def safe_request(text):
    """Authentication material is outside this boundary, never stored or matched."""
    body=json.loads(text)
    if isinstance(body,dict):
        body={k:v for k,v in body.items() if k not in ('access_token',)}
    return bytes_of(body)


def bounded_call(name,request,producer):
    """For a bounded reader which does not launch a child worker.

    Its upstream projection is deliberately outside the replay boundary.
    """
    tape=ACTIVE.get()
    if tape is None:return producer()
    tape.event('BOUNDED_REQUEST',bytes_of({'name':name,'request':request}))
    if tape.replaying:
        kind=tape.events[tape.index]['kind']
        if kind=='BOUNDED_FAILURE':
            failure=json.loads(tape.take(kind))
            import builtins
            cls=getattr(builtins,failure['type'],None)
            if not isinstance(cls,type) or not issubclass(cls,Exception):
                cls=type(failure['type'],(RuntimeError,),{})
            error=cls.__new__(cls);Exception.__init__(error,failure['message'])
            error.__dict__.update(failure['fields'])
            raise error
        return json.loads(tape.take('BOUNDED_RESPONSE'))
    try:result=producer()
    except Exception as exc:
        tape.event('BOUNDED_FAILURE',bytes_of({'type':type(exc).__name__,'message':str(exc),
            'fields':{k:v for k,v in exc.__dict__.items() if isinstance(v,(str,int,float,bool,type(None)))}}))
        raise
    tape.event('BOUNDED_RESPONSE',bytes_of(result))
    return result
