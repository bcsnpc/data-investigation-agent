"""Historical replay I/O isolation only; decision code and sealed events unchanged.

Old producers open a second metadata connection during a caller-owned write.
Reuse that connection for their load/admission reads, with no commit or close.
Current producers implement this directly. No returned evidence is patched.
"""
from contextlib import contextmanager,ExitStack
from contextvars import ContextVar
from pathlib import Path
from unittest.mock import patch


@contextmanager
def install(module):
    ModelStore=module.ModelStore;Runtime=module.Runtime;AdaptiveRuntime=module.AdaptiveRuntime
    if hasattr(ModelStore,'catalog_connection'):
        yield
        return
    writer=ContextVar('replay_catalog_writer',default=None)
    borrowed=ContextVar('replay_catalog_read',default=None)
    original_db=Runtime.db;original_connect=ModelStore.connect
    original_load=AdaptiveRuntime.load;original_admit=AdaptiveRuntime.admit
    def identity(store):return str(Path(store.database).resolve()).casefold()
    @contextmanager
    def runtime_db(owner):
        with original_db(owner) as db:
            token=writer.set((identity(owner.store),db))
            try:yield db
            finally:writer.reset(token)
    @contextmanager
    def connect(store):
        current=borrowed.get()
        if current is not None and current[0]==identity(store):
            yield current[1]
            return
        with original_connect(store) as db:yield db
    def load(owner,db,*args,**kwargs):
        token=borrowed.set((identity(owner.store),db))
        try:return original_load(owner,db,*args,**kwargs)
        finally:borrowed.reset(token)
    def admit(owner,*args,**kwargs):
        current=writer.get()
        token=borrowed.set(current)
        try:return original_admit(owner,*args,**kwargs)
        finally:borrowed.reset(token)
    with ExitStack() as stack:
        stack.enter_context(patch.object(Runtime,'db',runtime_db))
        stack.enter_context(patch.object(ModelStore,'connect',connect))
        stack.enter_context(patch.object(AdaptiveRuntime,'load',load))
        stack.enter_context(patch.object(AdaptiveRuntime,'admit',admit))
        yield
