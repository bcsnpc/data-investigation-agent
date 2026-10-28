"""Incremental immutable platform capture; publication precedes step return.

The local journal is useful, but is never the only copy after a completed step.
An abruptly killed process leaves STARTED/PARTIAL records and all published
events; only a successful final publication can declare completion.
"""
from contextlib import contextmanager
import base64
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import os
from .planner_recording import _safe
from .process_tape import bytes_of, EVENT_OBSERVER, validate_bootstrap_header
from .adapters.runner_blobs import MAX_BYTES as MAX_BLOB_BYTES

ENCODING='gzip-base64-v1'
MAX_DECODED_BYTES=128*1024*1024


def record_value(raw,encoding=None):
    """Decode only explicitly labelled outer records; native tape bytes stay exact."""
    if encoding is None:return json.loads(raw)
    if encoding!=ENCODING:raise ValueError('CAPTURE_RECORD_ENCODING_UNSUPPORTED')
    if len(raw)>MAX_BLOB_BYTES:raise ValueError('CAPTURE_RECORD_ENCODED_BOUND')
    value=json.loads(raw)
    if (set(value)!={'version','bytes','sha256','payload'} or value['version']!=ENCODING
            or type(value['bytes'])is not int or not 0<=value['bytes']<=MAX_DECODED_BYTES
            or not isinstance(value['sha256'],str) or not re.fullmatch('[0-9a-f]{64}',value['sha256'])):
        raise ValueError('CAPTURE_RECORD_ENCODING_INVALID')
    compressed=base64.b64decode(value['payload'],validate=True)
    with gzip.GzipFile(fileobj=io.BytesIO(compressed))as stream:
        original=stream.read(value['bytes']+1)
    if len(original)!=value['bytes'] or hashlib.sha256(original).hexdigest()!=value['sha256']:
        raise ValueError('CAPTURE_RECORD_DECODED_BYTES_CHANGED')
    return json.loads(original)


class DurableCapture:
    def __init__(self, root, put, *, run_id, bootstrap,clock=None):
        validate_bootstrap_header(bootstrap)
        if not re.fullmatch(r'[A-Za-z0-9_.-]{1,100}',run_id):raise ValueError('RUN_ID_INVALID')
        from threading import RLock
        self._lock=RLock()
        self.root=Path(root);self.put=put;self.run_id=run_id;self.sequence=0;self.records=[]
        from .run_timing import RunTiming
        self.timing=RunTiming(clock)
        self._pending_publications=[]
        self._publication_failed=False
        self._publication_holds=0
        self.root.mkdir(parents=True,exist_ok=False)
        self.record('header',bootstrap)
        self.record('status',{'status':'STARTED','partial':True})

    def record(self,kind,value):
        with self._lock:
            started=self.timing.clock()
            raw=bytes_of(value);_safe(raw)
            encoding=None
            if len(raw)>MAX_BLOB_BYTES:
                if len(raw)>MAX_DECODED_BYTES:raise ValueError('CAPTURE_RECORD_DECODED_BOUND')
                raw=bytes_of({'version':ENCODING,'bytes':len(raw),
                    'sha256':hashlib.sha256(raw).hexdigest(),
                    'payload':base64.b64encode(gzip.compress(raw,compresslevel=6,mtime=0)).decode('ascii')})
                if len(raw)>MAX_BLOB_BYTES:raise ValueError('CAPTURE_RECORD_ENCODED_BOUND')
                encoding=ENCODING
            self.sequence+=1
            name=f'{self.sequence:08d}-{kind}.json'
            with (self.root/name).open('xb') as stream:
                stream.write(raw);stream.flush()
                __import__('os').fsync(stream.fileno())
            ref={'key':self.run_id+'/'+name,'sha256':hashlib.sha256(raw).hexdigest()}
            if encoding:ref['encoding']=encoding
            self.records.append(ref)
            # Preserve the original event immediately, even inside an application
            # transaction. Only remote publication waits for the lock to release.
            self._pending_publications.append((ref['key'], self.root/name, ref['sha256']))
            self.timing.local_seconds+=max(0,self.timing.clock()-started)
            from .shared_state import after_transaction
            after_transaction(self.flush_publications)
            return ref

    def flush_publications(self):
        with self._lock:
            from .shared_state import TRANSACTION_ACTIVE
            if TRANSACTION_ACTIVE.get(): raise RuntimeError('CAPTURE_PUBLICATION_DURING_TRANSACTION')
            if self._publication_holds:return
            while self._pending_publications:
                self._publish_pending(0)
            # Every queued immutable record has now been acknowledged. A temporary
            # transport failure must not permanently poison a later complete flush.
            # Failed or changed records stay queued and cannot reach this point.
            self._publication_failed=False

    def _publish_pending(self,index):
        key,path,expected=self._pending_publications[index]
        try:
            started=self.timing.clock()
            raw=path.read_bytes()
            if hashlib.sha256(raw).hexdigest()!=expected:raise RuntimeError('CAPTURE_PENDING_BYTES_CHANGED')
            self.put(key,raw)
        except BaseException:
            self._publication_failed=True
            raise
        finally:
            self.timing.publication_seconds+=max(0,self.timing.clock()-started)
            self.timing.publications+=1
        self._pending_publications.pop(index)

    def worker_lifecycle(self,value):
        # Small, value-free diagnostics survive a mid-step process kill without
        # flushing the large pending evidence queue onto the handshake path.
        ref=self.record('worker-lifecycle',value)
        def publish():
            from .shared_state import TRANSACTION_ACTIVE
            if TRANSACTION_ACTIVE.get():raise RuntimeError('CAPTURE_PUBLICATION_DURING_TRANSACTION')
            # Resolve and remove the queued index under the same lock used by
            # ordinary flushes. Parallel child callbacks must not pop a shifted
            # index and acknowledge a different, unpublished evidence record.
            with self._lock:
                for index,item in enumerate(self._pending_publications):
                    if item[0]==ref['key']:return self._publish_pending(index)
        from .shared_state import after_transaction
        after_transaction(publish)

    @contextmanager
    def protocol_publications(self):
        """Persist locally now; acknowledge remotely after the child is closed.

        A timed child must not wait for its parent's Blob publication between
        REQUEST and ALLOW. The enclosing step still cannot return or seal until
        every original record is acknowledged. A crash leaves the previously
        published step-start and an incomplete execution, never a fake result.
        """
        with self._lock:self._publication_holds+=1
        try:yield
        finally:
            with self._lock:
                self._publication_holds-=1
                flush=not self._publication_holds
            if flush:
                from .shared_state import after_transaction
                after_transaction(self.flush_publications)

    def readback(self,ref):
        """Read only a record this run already published, then verify its bytes."""
        if ref not in self.records or not ref.get('key','').startswith(self.run_id+'/'):
            raise ValueError('CAPTURE_READBACK_UNKNOWN_RECORD')
        self.flush_publications()
        read=getattr(self.put,'read',None)
        if read is None:raise ValueError('CAPTURE_READBACK_TRANSPORT_UNAVAILABLE')
        raw=read(ref['key'])
        if not isinstance(raw,bytes) or hashlib.sha256(raw).hexdigest()!=ref['sha256']:
            raise ValueError('CAPTURE_READBACK_BYTES_CHANGED')
        return raw

    def seal(self):
        started=self.timing.clock()
        from .shared_state import TRANSACTION_ACTIVE
        if TRANSACTION_ACTIVE.get(): raise RuntimeError('CAPTURE_SEAL_DURING_TRANSACTION')
        if self._publication_failed: raise RuntimeError('CAPTURE_PUBLICATION_FAILED_NO_SEAL')
        self.flush_publications()
        value={'version':'dia-run-record-v1','run_id':self.run_id,'records':self.records}
        value['seal']=hashlib.sha256(bytes_of(value)).hexdigest()
        raw=bytes_of(value);_safe(raw)
        with (self.root/'run-record.json').open('xb') as stream:
            stream.write(raw);stream.flush();__import__('os').fsync(stream.fileno())
        publication=self.timing.clock()
        try:self.put(self.run_id+'/run-record.json',raw)
        finally:
            self.timing.publication_seconds+=max(0,self.timing.clock()-publication)
            self.timing.publications+=1
            self.timing.seal_seconds=max(0,self.timing.clock()-started)
        return value['seal']

    def publish_timing(self,seal=None):
        """Post-seal observational sidecar; original index/tapes stay immutable."""
        value={'run_id':self.run_id,'run_record_seal':seal,'partial':seal is None,
               'not_part_of_semantic_tape':True,'excludes_its_own_publication':True,**self.timing.summary()}
        raw=bytes_of(value);_safe(raw)
        path=self.root/'timing-summary.json'
        with path.open('xb') as stream:
            stream.write(raw);stream.flush();os.fsync(stream.fileno())
        self.put(self.run_id+'/timing-summary.json',raw)
        return {'key':self.run_id+'/timing-summary.json','sha256':hashlib.sha256(raw).hexdigest(),'summary':value}

    def event(self,tape,event):
        self.timing.tape_event(tape,event)
        self.record('tape-event',{'tape':str(tape.path),'event':event})

    @contextmanager
    def observing(self):
        from .physical_reads import WORKER_OBSERVER
        worker_token=WORKER_OBSERVER.set(self.worker_lifecycle)
        token=EVENT_OBSERVER.set(self.event)
        try:yield
        finally:
            EVENT_OBSERVER.reset(token)
            WORKER_OBSERVER.reset(worker_token)

    def step(self,name,call):
        self.record('step-start',{'name':name,'partial':True})
        started=self.timing.clock()
        try:result=call()
        except BaseException:
            self.timing.step(name,self.timing.clock()-started,'FAILED')
            raise
        elapsed=max(0,self.timing.clock()-started);self.timing.step(name,elapsed,'COMPLETED')
        self.record('step-result',{'name':name,'result':result,'observed_wall_seconds':elapsed})
        return result

    def fail(self,error):
        value={'status':'FAILED','partial':True,'error_type':type(error).__name__,'message':str(error)}
        try:_safe(bytes_of(value))
        except Exception:value['message']='REDACTED_ERROR_CONTENT'
        return self.record('status',value)


def blob_sink(config):
    from .adapters.runner_blobs import sink
    return sink(config)


@contextmanager
def protocol_publications():
    observer=EVENT_OBSERVER.get()
    capture=getattr(observer,'__self__',None)
    if isinstance(capture,DurableCapture):
        with capture.protocol_publications():yield
    else:yield
