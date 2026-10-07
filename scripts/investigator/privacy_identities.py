"""Content identity remapping for a staged projected recording.

Producer hashes stay unchanged during execution. At capture, their preimages
are projected and all dependent references move together. Only projected
identities are durable; original preimages and lookup keys stay in memory.
"""
from contextvars import ContextVar
from contextlib import contextmanager
import hashlib
import re
from .privacy_projection import ProjectionError,canonical

ACTIVE=ContextVar('privacy_identities',default=None)
HEX=re.compile(r'\b[0-9a-f]{64}\b')


def digest(value,encode):
    data=encode(value)
    if isinstance(data,str):data=data.encode('utf8')
    identity=hashlib.sha256(data).hexdigest()
    active=ACTIVE.get()
    if active is not None:active.register(identity,value,encode)
    return identity


def text_digest(value):
    if isinstance(value,bytes):value=value.decode('utf8')
    if not isinstance(value,str):raise ProjectionError('PRIVACY_CONTENT_IDENTITY_TYPE')
    return digest(value,lambda text:text)


@contextmanager
def active(identities):
    token=ACTIVE.set(identities)
    try:yield identities
    finally:ACTIVE.reset(token)


class Identities:
    def __init__(self,projection):
        self.projection=projection;self.preimages={};self.resolved={}

    def register(self,identity,value,encode):
        import copy
        if identity not in self.preimages:self.preimages[identity]=(copy.deepcopy(value),encode)

    def prepare(self):
        for value,_ in self.preimages.values():self.projection.discover(value)

    def rekey(self):
        resolving=set();self.resolved={}
        def resolve(identity):
            if identity in self.resolved:return self.resolved[identity]
            if identity in resolving:raise ProjectionError('PRIVACY_CONTENT_IDENTITY_CYCLE')
            resolving.add(identity);value,encode=self.preimages[identity]
            for child in set(HEX.findall(canonical(value).decode())) & self.preimages.keys():resolve(child)
            projected=self.projection.project(value)
            data=encode(projected)
            if isinstance(data,str):data=data.encode('utf8')
            result=hashlib.sha256(data).hexdigest()
            self.resolved[identity]=result
            if identity!=result:
                self.projection._values[identity]=result
                self.projection._identity_values[identity]=result
            resolving.remove(identity)
            return result
        for identity in self.preimages:resolve(identity)
        return dict(self.resolved)
