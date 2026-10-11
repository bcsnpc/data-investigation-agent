"""Verified SHA-keyed, bounded in-memory UUID sets.

No path/mtime shortcut, no raw SQLite text retained, no failed result cached.
"""
from collections import OrderedDict
from contextlib import closing
from pathlib import Path
import hashlib, sqlite3, threading

class ArtifactChanged(ValueError):pass
def single_file(path):
    for suffix in ('-wal','-journal'):
        sidecar=Path(str(path)+suffix)
        try:
            if sidecar.exists() and sidecar.stat().st_size:raise ArtifactChanged('Artifact has an unsealed SQLite overlay')
        except OSError:raise ArtifactChanged('Artifact overlay cannot be verified') from None
class _Flight:
    def __init__(self):self.event=threading.Event();self.result=None;self.error=None
def file_sha(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
    return digest.hexdigest()
def scan(path,pattern):
    found=set()
    with closing(sqlite3.connect(Path(path).resolve().as_uri()+'?mode=ro',uri=True)) as db:
        tables=[r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        for table in tables:
            quoted='"'+table.replace('"','""')+'"'
            for row in db.execute('SELECT * FROM '+quoted):
                for value in row:
                    if isinstance(value,str):found.update(v.casefold() for v in pattern.findall(value))
    return frozenset(found)
class IdentityCache:
    def __init__(self,pattern,*,max_entries=8,max_identities=100000,scanner=scan):
        if max_entries<1 or max_identities<1:raise ValueError('Invalid cache bound')
        self.pattern=pattern;self.max_entries=max_entries;self.max_identities=max_identities;self.scanner=scanner
        self._lock=threading.Lock();self._entries=OrderedDict();self._flights={};self._identities=0
    def get(self,path,expected):
        path=Path(path)
        single_file(path)
        try:verified=file_sha(path)
        except OSError:raise ArtifactChanged('Artifact missing') from None
        if verified!=expected:raise ArtifactChanged('Artifact hash differs')
        single_file(path)
        # Each caller verified its actual file; no source path becomes a trust key.
        with self._lock:
            if expected in self._entries:
                result=self._entries.pop(expected);self._entries[expected]=result;single_file(path);return result
            flight=self._flights.get(expected);leader=flight is None
            if leader:flight=_Flight();self._flights[expected]=flight
        if not leader:
            flight.event.wait()
            if flight.error is not None:raise flight.error
            # Waiting never replaces validation of this caller's actual artifact.
            if file_sha(path)!=expected:raise ArtifactChanged('Artifact changed while awaiting scan')
            single_file(path)
            return flight.result
        try:
            result=self.scanner(path,self.pattern)
            if file_sha(path)!=expected:raise ArtifactChanged('Artifact changed during scan')
            single_file(path)
            with self._lock:
                if len(result)<=self.max_identities:
                    while self._entries and (len(self._entries)>=self.max_entries or self._identities+len(result)>self.max_identities):
                        _,old=self._entries.popitem(last=False);self._identities-=len(old)
                    self._entries[expected]=result;self._identities+=len(result)
                flight.result=result
            return result
        except BaseException as exc:
            flight.error=exc;raise
        finally:
            with self._lock:self._flights.pop(expected,None);flight.event.set()
    def stats(self):
        with self._lock:return {'entries':len(self._entries),'identities':self._identities,'flights':len(self._flights)}
