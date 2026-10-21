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
    """Use existing platform transport, managed identity and gateway allowlist."""
    from urllib.request import Request,build_opener
    from metadata_auth import NoRedirect
    from .adapters.managed_identity import Tokens
    from .live_gateway import current,open_http
    from .adapters.blob_artifacts import validate_account_url
    validate_account_url(config['account_url'])
    prefix=config['prefix'].strip('/')
    if not re.fullmatch(r'[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*',prefix):raise ValueError('RUN_CAPTURE_PREFIX_INVALID')
    tokens=Tokens(config['identity']);opener=build_opener(NoRedirect())
    def upload(key,raw):
        url=config['account_url']+'/captures/'+prefix+'/'+key
        headers={'x-ms-version':'2023-11-03','x-ms-blob-type':'BlockBlob','If-None-Match':'*','Content-Type':'application/json'}
        status=None
        try:
            current().http(config['channel'],'PUT',url,raw,headers)
            headers['Authorization']='Bearer '+tokens.get_token('https://storage.azure.com/.default')
            with open_http(opener,Request(url,data=raw,headers=headers,method='PUT'),timeout=120,identity=config['channel']) as response:
                status=response.status
                if status!=201:raise ValueError('RUN_CAPTURE_BLOB_PUT_FAILED')
        finally:
            log=Path(os.environ['DIA_PLATFORM_CONTROL_RECEIPTS']);log.parent.mkdir(parents=True,exist_ok=True)
            with log.open('ab') as stream:
                stream.write(bytes_of({'kind':'PLATFORM_ARTIFACT_CONTROL','method':'PUT','url':url,'http_status':status,'principal_id':config['identity']['principal_id'],'body_bytes':len(raw)})+b'\n')
                stream.flush();os.fsync(stream.fileno())
    return upload
