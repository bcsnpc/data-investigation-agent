"""Capture bounded child-worker bytes, not upstream network decoding."""
import json
from pathlib import Path
import subprocess
import re
from .process_tape import ACTIVE, bytes_of, safe_request, TapeError


def descriptor(command):
    values=[str(v) for v in command]
    # Ephemeral configuration paths are represented by their actual contents.
    for n,v in enumerate(values):
        if n==0 and re.fullmatch(r'python(?:\d(?:\.\d+)?)?(?:\.exe)?',Path(v).name.casefold()):
            values[n]='python'
        elif n and values[n-1]=='--config':
            values[n]='config:'+bytes_of(json.loads(Path(v).read_text(encoding='utf-8-sig'))).decode()
        elif v.endswith(('.py','.ps1')):values[n]=Path(v).name
    return values


class Pipe:
    def __init__(self,worker,reader):self.worker=worker;self.reader=reader
    def write(self,text):
        body=text.encode()
        try:body=safe_request(text)
        except (ValueError,TypeError):pass # ALLOW/REUSE protocol is literal bytes.
        self.worker.tape.event('WORKER_SEND',body)
        if self.worker.child:return self.perform('write',lambda:self.worker.child.stdin.write(text))
        self.perform('write',lambda:None)
        return len(text)
    def flush(self):
        self.perform('flush',lambda:self.worker.child.stdin.flush() if self.worker.child else None)
    def perform(self,location,call):
        if self.worker.tape.replaying:
            if self.worker.tape.events[self.worker.tape.index]['kind']=='WORKER_FAILURE':
                detail=json.loads(self.worker.tape.take('WORKER_FAILURE'))
                if detail['operation']!=location:raise TapeError('TAPE_WORKER_FAILURE_LOCATION_DIFFERS')
                raise_failure(detail['failure']['error_type'],[],None,detail['failure'])
            return call()
        try:return call()
        except OSError as exc:
            from .process_failure import capture
            exc.recorded_failure=capture(exc)
            self.worker.tape.event('WORKER_FAILURE',bytes_of({'operation':location,'failure':exc.recorded_failure}))
            raise
    def readline(self,limit=-1):
        if self.worker.child:
            text=self.perform('readline',lambda:self.worker.child.stdout.readline(limit))
            self.worker.tape.event('WORKER_READ',text.encode())
            return text
        self.perform('readline',lambda:None)
        text=self.worker.tape.take('WORKER_READ').decode()
        if limit>=0 and len(text)>limit:raise TapeError('TAPE_WORKER_RESPONSE_EXCEEDS_LIMIT')
        return text
    def close(self):
        if self.worker.child:
            (self.worker.child.stdout if self.reader else self.worker.child.stdin).close()


class Worker:
    def __init__(self,command,**kwargs):
        self.tape=ACTIVE.get();self.returncode=None;self.child=None
        deadline=kwargs.pop('worker_timeout',None)
        start={'command':descriptor(command),'mode':'STREAM'}
        # Legacy tapes never recorded a streaming deadline. Retain their
        # byte-exact event shape without asserting a retrospective deadline.
        legacy=False
        if self.tape.replaying:
            import base64
            prior=json.loads(base64.b64decode(self.tape.events[self.tape.index]['body']))
            legacy='timeout' not in prior
        if deadline is not None and not legacy:start['timeout']=deadline
        self.tape.event('WORKER_START',bytes_of(start))
        if not self.tape.replaying:
            try:self.child=subprocess.Popen(command,**kwargs)
            except Exception as exc:
                from .process_failure import capture
                exc.recorded_failure=capture(exc)
                self.tape.event('WORKER_END',bytes_of({'returncode':None,'error':type(exc).__name__,'failure':exc.recorded_failure}))
                raise
        elif self.tape.events[self.tape.index]['kind']=='WORKER_END':
            end=json.loads(self.tape.take('WORKER_END'))
            raise_failure(end['error'],command,deadline,end.get('failure'))
        self.stdin=Pipe(self,False);self.stdout=Pipe(self,True)
    def wait(self,timeout=None):
        if self.returncode is None:
            if self.child:
                self.returncode=self.child.wait(timeout=timeout)
                self.tape.event('WORKER_END',bytes_of({'returncode':self.returncode}))
            else:self.returncode=json.loads(self.tape.take('WORKER_END'))['returncode']
        return self.returncode
    def poll(self):return self.child.poll() if self.child else self.returncode
    def kill(self):
        if self.child:self.child.kill()


def popen(command,**kwargs):
    if ACTIVE.get():return Worker(command,**kwargs)
    kwargs.pop('worker_timeout',None)
    return subprocess.Popen(command,**kwargs)


def check_deadline(worker):
    tape=ACTIVE.get()
    if tape and tape.replaying:
        if tape.events[tape.index]['kind']=='WORKER_FAILURE':
            detail=json.loads(tape.take('WORKER_FAILURE'))
            if detail['operation']!='deadline':raise TapeError('TAPE_WORKER_FAILURE_LOCATION_DIFFERS')
            raise_failure(detail['failure']['error_type'],[],None,detail['failure'])
        return
    if getattr(worker,'deadline_expired',False) is True:
        import errno
        from .process_failure import capture
        try:raise OSError(errno.ETIMEDOUT,'Worker deadline expired')
        except OSError as exc:
            exc.recorded_failure=capture(exc)
            if tape:tape.event('WORKER_FAILURE',bytes_of({'operation':'deadline','failure':exc.recorded_failure}))
            raise


def raise_failure(name,command,timeout,detail=None):
    if name=='TimeoutExpired':raise subprocess.TimeoutExpired(command,timeout)
    import builtins
    cls=getattr(builtins,name,None)
    if not isinstance(cls,type) or not issubclass(cls,Exception):
        raise TapeError('RECORDED_WORKER_FAILURE:'+name)
    exc=cls(detail['errno'],detail['message']) if detail and issubclass(cls,OSError) else cls('Recorded bounded worker failure')
    if detail:exc.recorded_failure=detail
    raise exc


def run(command,*,input,timeout,fallback=None,**kwargs):
    tape=ACTIVE.get()
    if tape is None:return (fallback or subprocess.run)(command,input=input,timeout=timeout,**kwargs)
    tape.event('WORKER_START',bytes_of({'command':descriptor(command),'mode':'BOUNDED','timeout':timeout}))
    tape.event('WORKER_SEND',safe_request(input))
    if tape.replaying:
        stdout=tape.take('WORKER_READ').decode()
        end=json.loads(tape.take('WORKER_END'))
        if end.get('error'):
            raise_failure(end['error'],command,timeout,end.get('failure'))
        return subprocess.CompletedProcess(command,end['returncode'],stdout,'')
    try:
        result=(fallback or subprocess.run)(command,input=input,timeout=timeout,**kwargs)
        tape.event('WORKER_READ',result.stdout.encode() if isinstance(result.stdout,str) else result.stdout)
        tape.event('WORKER_END',bytes_of({'returncode':result.returncode,'error':None}))
        return result
    except Exception as exc:
        tape.event('WORKER_READ',b'')
        from .process_failure import capture
        exc.recorded_failure=capture(exc)
        tape.event('WORKER_END',bytes_of({'returncode':None,'error':type(exc).__name__,'failure':exc.recorded_failure}))
        raise
