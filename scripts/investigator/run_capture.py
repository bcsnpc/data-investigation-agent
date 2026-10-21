"""Incremental immutable platform capture; publication precedes step return.

The local journal is useful, but is never the only copy after a completed step.
An abruptly killed process leaves STARTED/PARTIAL records and all published
events; only a successful final publication can declare completion.
"""
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import re
import os
from .planner_recording import _safe
from .process_tape import bytes_of, EVENT_OBSERVER, validate_bootstrap_header


class DurableCapture:
    def __init__(self, root, put, *, run_id, bootstrap):
        validate_bootstrap_header(bootstrap)
        if not re.fullmatch(r'[A-Za-z0-9_.-]{1,100}',run_id):raise ValueError('RUN_ID_INVALID')
        self.root=Path(root);self.put=put;self.run_id=run_id;self.sequence=0;self.records=[]
        self.root.mkdir(parents=True,exist_ok=False)
        self.record('header',bootstrap)
        self.record('status',{'status':'STARTED','partial':True})

    def record(self,kind,value):
        raw=bytes_of(value);_safe(raw)
        self.sequence+=1
        name=f'{self.sequence:08d}-{kind}.json'
        with (self.root/name).open('xb') as stream:
            stream.write(raw);stream.flush()
            __import__('os').fsync(stream.fileno())
        # Unique names and create-only Blob PUT make historical entries immutable.
        self.put(self.run_id+'/'+name,raw)
        ref={'key':self.run_id+'/'+name,'sha256':hashlib.sha256(raw).hexdigest()}
        self.records.append(ref)
        return ref

    def seal(self):
        value={'version':'dia-run-record-v1','run_id':self.run_id,'records':self.records}
        value['seal']=hashlib.sha256(bytes_of(value)).hexdigest()
        raw=bytes_of(value);_safe(raw)
        with (self.root/'run-record.json').open('xb') as stream:
            stream.write(raw);stream.flush();__import__('os').fsync(stream.fileno())
        self.put(self.run_id+'/run-record.json',raw)
        return value['seal']

    def event(self,tape,event):
        self.record('tape-event',{'tape':str(tape.path),'event':event})

    @contextmanager
    def observing(self):
        token=EVENT_OBSERVER.set(self.event)
        try:yield
        finally:EVENT_OBSERVER.reset(token)

    def step(self,name,call):
        self.record('step-start',{'name':name,'partial':True})
        result=call()
        self.record('step-result',{'name':name,'result':result})
        return result

    def fail(self,error):
        value={'status':'FAILED','partial':True,'error_type':type(error).__name__,'message':str(error)}
        try:_safe(bytes_of(value))
        except Exception:value['message']='REDACTED_ERROR_CONTENT'
        return self.record('status',value)


def blob_sink(config):
    from .adapters.runner_blobs import sink
    return sink(config)
