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
        if self.worker.child:return self.worker.child.stdin.write(text)
        return len(text)
    def flush(self):
        if self.worker.child:self.worker.child.stdin.flush()
    def readline(self,limit=-1):
        if self.worker.child:
            text=self.worker.child.stdout.readline(limit)
            self.worker.tape.event('WORKER_READ',text.encode())
            return text
        text=self.worker.tape.take('WORKER_READ').decode()
        if limit>=0 and len(text)>limit:raise TapeError('TAPE_WORKER_RESPONSE_EXCEEDS_LIMIT')
        return text
    def close(self):
        if self.worker.child:
            (self.worker.child.stdout if self.reader else self.worker.child.stdin).close()


class Worker:
    def __init__(self,command,**kwargs):
        self.tape=ACTIVE.get();self.returncode=None;self.child=None
        self.tape.event('WORKER_START',bytes_of({'command':descriptor(command),'mode':'STREAM'}))
        if not self.tape.replaying:
            try:self.child=subprocess.Popen(command,**kwargs)
            except Exception as exc:
                self.tape.event('WORKER_END',bytes_of({'returncode':None,'error':type(exc).__name__}))
                raise
        elif self.tape.events[self.tape.index]['kind']=='WORKER_END':
            end=json.loads(self.tape.take('WORKER_END'))
            raise_failure(end['error'],command,kwargs.get('timeout'))
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
    return Worker(command,**kwargs) if ACTIVE.get() else subprocess.Popen(command,**kwargs)


def raise_failure(name,command,timeout):
    if name=='TimeoutExpired':raise subprocess.TimeoutExpired(command,timeout)
    import builtins
    cls=getattr(builtins,name,None)
    if not isinstance(cls,type) or not issubclass(cls,Exception):
        raise TapeError('RECORDED_WORKER_FAILURE:'+name)
    raise cls('Recorded bounded worker failure')


def run(command,*,input,timeout,fallback=None,**kwargs):
    tape=ACTIVE.get()
    if tape is None:return (fallback or subprocess.run)(command,input=input,timeout=timeout,**kwargs)
    tape.event('WORKER_START',bytes_of({'command':descriptor(command),'mode':'BOUNDED','timeout':timeout}))
    tape.event('WORKER_SEND',safe_request(input))
    if tape.replaying:
        stdout=tape.take('WORKER_READ').decode()
        end=json.loads(tape.take('WORKER_END'))
        if end.get('error'):
            raise_failure(end['error'],command,timeout)
        return subprocess.CompletedProcess(command,end['returncode'],stdout,'')
    try:
        result=(fallback or subprocess.run)(command,input=input,timeout=timeout,**kwargs)
        tape.event('WORKER_READ',result.stdout.encode() if isinstance(result.stdout,str) else result.stdout)
        tape.event('WORKER_END',bytes_of({'returncode':result.returncode,'error':None}))
        return result
    except Exception as exc:
        tape.event('WORKER_READ',b'')
        tape.event('WORKER_END',bytes_of({'returncode':None,'error':type(exc).__name__}))
        raise
