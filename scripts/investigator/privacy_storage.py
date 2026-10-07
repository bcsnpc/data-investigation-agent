"""Installation-owned in-memory evidence stores with projected durable images.

Raw SQLite pages never have a filesystem name. Connections to a registered
installation path are routed to its memory database, including read-only URIs.
Exact installations retain the normal sqlite connection path.
"""
import hashlib
import json
from pathlib import Path
import sqlite3
from threading import RLock
from urllib.parse import unquote, urlsplit
from secrets import token_hex
from .privacy_projection import ProjectionError, canonical
from .provider_tape_contract import parse

_LOCK=RLock()
_STORES={}
VERSION='privacy-projected-evidence-v1'


def path_identity(path):
    text=str(path)
    if text.startswith('file:'):
        part=unquote(urlsplit(text).path)
        if len(part)>2 and part[0]=='/' and part[2]==':':part=part[1:]
        text=part
    return str(Path(text).resolve()).casefold()


def connect(path,*args,**kwargs):
    with _LOCK:store=_STORES.get(path_identity(path))
    if store is not None:return store.connection(path,*args,**kwargs)
    return sqlite3.connect(path,*args,**kwargs)


class EvidenceStore:
    def __init__(self,path,projection):
        self.path=Path(path).resolve();self.projection=projection;self.closed=False
        self.uri='file:privacy-'+token_hex(16)+'?mode=memory&cache=shared'
        self.keeper=sqlite3.connect(self.uri,uri=True)
        self.keeper.execute('PRAGMA temp_store=MEMORY')
        self.keeper.execute('PRAGMA journal_mode=MEMORY')
        with _LOCK:
            identity=path_identity(self.path)
            if identity in _STORES and not _STORES[identity].closed:
                self.keeper.close()
                raise ProjectionError('PRIVACY_STORE_ALREADY_OPEN')
            _STORES[identity]=self
        try:
            if self.path.exists():self._load()
        except BaseException:
            self.close();raise

    def connection(self,path,*args,**kwargs):
        if self.closed:raise ProjectionError('PRIVACY_STORE_CLOSED')
        if path_identity(path)!=path_identity(self.path):
            raise ProjectionError('PRIVACY_STORE_PATH_DIFFERS')
        # URI mode=ro is an access intent, not a licence to open a raw file.
        readonly=kwargs.pop('uri',False) and 'mode=ro' in str(path)
        db=sqlite3.connect(self.uri,*args,uri=True,**kwargs)
        db.execute('PRAGMA temp_store=MEMORY');db.execute('PRAGMA journal_mode=MEMORY')
        if readonly:db.execute('PRAGMA query_only=ON')
        return db

    def image(self):
        rows=self.keeper.execute("SELECT name,sql,type FROM sqlite_master WHERE name NOT LIKE 'sqlite_%' AND sql IS NOT NULL ORDER BY type='table' DESC,name").fetchall()
        objects=[]
        for name,sql,kind in rows:
            item={'name':name,'sql':sql,'type':kind}
            if kind=='table':
                quoted='"'+name.replace('"','""')+'"'
                item['columns']=[r[1] for r in self.keeper.execute('PRAGMA table_info('+quoted+')')]
                item['rows']=[list(r) for r in self.keeper.execute('SELECT * FROM '+quoted)]
                if any(isinstance(v,bytes) for row in item['rows'] for v in row):
                    raise ProjectionError('PRIVACY_OPAQUE_STORE_CELL')
            objects.append(item)
        return {'objects':objects}

    def prepare(self):
        image=self.image();self.projection.discover(image)
        return image

    def persist(self,image):
        projected=self.projection.project(image)
        # Schema is structure, never a sensitive-value replacement target.
        for old,new in zip(image['objects'],projected['objects']):
            if any(old[k]!=new[k] for k in ('name','sql','type')) or old.get('columns')!=new.get('columns'):
                raise ProjectionError('PRIVACY_VALUE_COLLIDES_WITH_STORE_SCHEMA')
        value={'version':VERSION,'projection':self.projection.descriptor(),'image':projected}
        value['seal']=self.projection.sign(value)
        data=canonical(value)
        from .planner_recording import _safe
        _safe(data)
        self.path.parent.mkdir(parents=True,exist_ok=True)
        # History is immutable; only the current projected image pointer changes.
        history=self.path.with_name(self.path.name+'.history')
        history.mkdir(exist_ok=True)
        sealed=history/(hashlib.sha256(data).hexdigest()+'.json')
        if not sealed.exists():
            with sealed.open('xb') as stream:stream.write(data)
        temporary=self.path.with_name(self.path.name+'.projected-'+token_hex(16)+'.tmp')
        with temporary.open('xb') as stream:stream.write(data)
        temporary.replace(self.path)
        return {'sha256':hashlib.sha256(data).hexdigest(),'tape_class':'PRIVACY_PROJECTED'}

    def _load(self):
        import hmac
        value=parse(self.path.read_bytes())
        if not isinstance(value,dict) or set(value)!={'version','projection','image','seal'} or value['version']!=VERSION:
            raise ProjectionError('PRIVACY_RAW_OR_UNSUPPORTED_STORE_REFUSED')
        self.projection.require_descriptor(value['projection'])
        if not isinstance(value['seal'],str) or not hmac.compare_digest(value['seal'],self.projection.sign({k:v for k,v in value.items() if k!='seal'})):
            raise ProjectionError('PRIVACY_STORE_SEAL')
        self.projection.trust_sealed_tokens(value)
        self.restore(value['image'])

    def restore(self,image):
        """Restore a keyed-sealed bootstrap into memory only, never a file."""
        if self.keeper.execute('SELECT 1 FROM sqlite_master LIMIT 1').fetchone():
            self.keeper.close()
            self.uri='file:privacy-'+token_hex(16)+'?mode=memory&cache=shared'
            self.keeper=sqlite3.connect(self.uri,uri=True)
            self.keeper.execute('PRAGMA temp_store=MEMORY')
            self.keeper.execute('PRAGMA journal_mode=MEMORY')
        objects=image['objects']
        for item in objects:
            self.keeper.execute(item['sql'])
            if item['type']=='table' and item['rows']:
                quoted='"'+item['name'].replace('"','""')+'"'
                self.keeper.executemany('INSERT INTO '+quoted+' VALUES ('+','.join('?' for _ in item['columns'])+')',item['rows'])
        self.keeper.commit()

    def close(self):
        if not self.closed:self.keeper.close();self.closed=True
        # Keep the closed route registered. Falling back to a raw file after
        # closing an installation would mix capture classes.
