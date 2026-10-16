"""Atomic visibility of fully serialized exact capture; no tape wire changes."""
import os,tempfile,time
from pathlib import Path

def publish(path,body):
    if not isinstance(body,bytes):raise TypeError('Atomic publication requires already serialized bytes')
    path=Path(path);stage=None
    try:
        with tempfile.NamedTemporaryFile(mode='wb',prefix='.'+path.name+'.publishing-',suffix='.tmp',dir=path.parent,delete=False) as stream:
            stage=Path(stream.name);stream.write(body);stream.flush();os.fsync(stream.fileno())
        # Same directory/volume: readers see old complete bytes or new complete bytes.
        deadline=time.monotonic()+1.0;delay=.01
        while True:
            try:
                os.replace(stage,path);break
            except PermissionError as exc:
                # Native Windows share-delete contention only; permission/refusal
                # on any other platform/code is not retried.
                remaining=deadline-time.monotonic()
                if os.name!='nt' or getattr(exc,'winerror',None) not in (5,32) or remaining<=0:raise
                time.sleep(min(delay,remaining));delay=min(.05,delay+.01)
    finally:
        if stage is not None:stage.unlink(missing_ok=True)
