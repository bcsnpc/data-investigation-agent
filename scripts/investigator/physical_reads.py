"""Meter additional physical requests inside an already reserved logical dispatch.

The first slot is conservatively reserved before transport preparation. Each
subsequent SQL command/HTTP request needs admission before the child may send it.
Authentication and connection handshakes are not data/metadata read requests.
"""
from contextlib import contextmanager
from contextvars import ContextVar
import json
import subprocess
from threading import Timer

_scope=ContextVar('physical_read_scope',default=None)


@contextmanager
def scope(meter):
    state={'first':True,'meter':meter,'first_report':None}
    token=_scope.set(state)
    try: yield state
    finally: _scope.reset(token)


def run(command, *, input, timeout, fallback=None, **kwargs):
    state=_scope.get()
    if state is None: return (fallback or subprocess.run)(command,input=input,timeout=timeout,**kwargs)
    command=list(command)+(['-Metered'] if any(str(c).endswith('.ps1') for c in command) else ['--metered'])
    child=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,
                           text=True,encoding='utf-8')
    timer=Timer(timeout,child.kill);timer.daemon=True;timer.start()
    def line():
        value=child.stdout.readline(2*1024*1024+1)
        if not value or len(value)>2*1024*1024: raise RuntimeError('Physical read response unavailable')
        return value
    final=None
    try:
        child.stdin.write(input+'\n');child.stdin.flush()
        while True:
            raw=line();message=json.loads(raw)
            if message.get('physical_read')!='REQUEST':
                child.wait(timeout=5)
                return subprocess.CompletedProcess(command,child.returncode,raw,'')
            kind=message.get('kind')
            if kind not in ('sql_identity','sql_database_permissions','sql_object_permissions',
                            'sql_quantity','onelake_listing','onelake_commit'):
                raise ValueError('Unknown physical request')
            def send():
                nonlocal final
                child.stdin.write('ALLOW\n');child.stdin.flush()
                raw_done=line();done=json.loads(raw_done)
                if done.get('physical_read')!='DONE' or done.get('kind')!=kind:
                    if isinstance(done,dict) and (done.get('error') or done.get('status')=='UNAVAILABLE'):
                        final=raw_done
                        return {'status':'UNAVAILABLE','request_kind':kind}
                    raise RuntimeError('Physical request completion unavailable')
                if done.get('status')!='AVAILABLE': raise RuntimeError('Physical request failed')
                return {'status':'AVAILABLE','request_kind':kind}
            if state['first']:
                state['first']=False
                state['first_report']={'status':'UNCERTAIN','request_kind':kind}
                state['first_report']=send()
            else: state['meter'](kind,send)
            if final is not None:
                child.wait(timeout=5)
                return subprocess.CompletedProcess(command,child.returncode,final,'')
    finally:
        timer.cancel()
        try:
            if child.poll() is None: child.kill()
        except OSError: pass
        child.wait()
        for pipe in (child.stdin,child.stdout):
            try: pipe.close()
            except OSError: pass  # Cleanup must not replace an admission refusal.
