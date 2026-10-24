"""Resume completed logical operations without repeating native/model calls.

This is a case checkpoint, not a provider/network tape. Original evidence and
receipts are retained verbatim. Pins prevent reuse on a different ticket/path.
"""
import copy
import json
import os
from pathlib import Path
from .estate_graph_contract import canonical, digest
from .planner_recording import _safe
from .shared_state import StateConflict


class FileStore:
    """Atomic local backend for offline tests; production uses shared state."""
    def __init__(self, path):
        self.path = Path(path)

    def load(self):
        return json.loads(self.path.read_bytes()) if self.path.exists() else None

    def save(self, value):
        raw = canonical(value).encode(); _safe(raw)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix('.pending')
        with temporary.open('wb') as stream:
            stream.write(raw); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, self.path)


class SharedStore:
    NAMESPACE = 'ledger_investigator_checkpoints'

    def __init__(self, state, identity, *, resume=False):
        self.state, self.identity, self.resume = state, identity, resume
        self.revision = None

    def load(self):
        from .process_tape import bounded_call
        def read():
            try:return self.state.get(self.NAMESPACE,self.identity)
            except KeyError:return None
        value=bounded_call('ledger-checkpoint-load',{'identity':self.identity,'resume':self.resume},read)
        if value is None:return None
        if not self.resume:
            raise StateConflict('CHECKPOINT_ALREADY_EXISTS_USE_EXPLICIT_RESUME')
        self.revision = value['revision']
        return value['body']

    def save(self, value):
        _safe(canonical(value).encode())
        from .process_tape import bounded_call
        def write():return {'revision':self.state.put(self.NAMESPACE,self.identity,value,revision=self.revision)['revision']}
        result=bounded_call('ledger-checkpoint-save',{'identity':self.identity,'revision':self.revision},write)
        self.revision = result['revision']


class Checkpoint:
    def __init__(self, store, pins):
        self.store, self.pins = store, copy.deepcopy(pins)
        self.value = None; self.position = 0

    def begin(self, binding):
        self.position = 0
        pins = {**self.pins, **copy.deepcopy(binding)}
        saved = self.store.load()
        if saved is not None:
            body = {key: value for key, value in saved.items() if key != 'sha256'}
            if (saved.get('sha256') != digest(body) or body.get('version') != 'ledger-checkpoint-v1'
                    or body.get('pins') != pins):
                raise StateConflict('CHECKPOINT_HASH_OR_BINDING_DIFFERS')
            self.value = body
        else:
            self.value = {'version': 'ledger-checkpoint-v1', 'pins': pins, 'operations': [],
                          'elapsed_seconds': 0, 'case_file': None, 'outcome': None, 'pending': None, 'physical_owners': []}
        return copy.deepcopy(self.value)

    @property
    def replaying(self):
        return self.position < len(self.value['operations'])

    def save(self):
        self.store.save({**copy.deepcopy(self.value), 'sha256': digest(self.value)})

    def step(self, name, arguments, operation, *, snapshot, restore, elapsed):
        signature = digest([name, arguments])
        if self.replaying:
            prior = self.value['operations'][self.position]
            if prior['signature'] != signature or prior['name'] != name:
                raise StateConflict('CHECKPOINT_OPERATION_PREFIX_DIFFERS')
            restore(copy.deepcopy(prior['state']))
            self.position += 1
            return copy.deepcopy(prior['result'])
        extra=self.export_extra()if callable(getattr(self,'export_extra',None))else None
        owner=extra.get('physical_owner')if isinstance(extra,dict)else None
        if isinstance(owner,str) and owner not in self.value['physical_owners']:self.value['physical_owners'].append(owner)
        self.value['pending']={'name':name,'signature':signature,'extra':extra}
        self.save()
        result = operation()
        self.value['pending']=None
        entry = {'name': name, 'signature': signature, 'result': copy.deepcopy(result),
                 'state': snapshot()}
        _safe(canonical(entry).encode())
        self.value['operations'].append(entry); self.position += 1
        self.value['elapsed_seconds'] = max(self.value['elapsed_seconds'], elapsed())
        self.save()
        return result

    def note_case(self, value, *, elapsed):
        if self.replaying: return
        self.value['case_file'] = copy.deepcopy(value)
        self.value['elapsed_seconds'] = max(self.value['elapsed_seconds'], elapsed())
        self.save()

    def complete(self, outcome, *, elapsed):
        if self.replaying:raise StateConflict('CHECKPOINT_COMPLETED_BEFORE_RETAINED_PREFIX')
        self.value['outcome'] = copy.deepcopy(outcome)
        self.note_case(outcome['case_file'], elapsed=elapsed)
