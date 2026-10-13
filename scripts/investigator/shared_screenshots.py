"""Screenshot pixels in Blob, metadata in shared state, expiry on every access."""
import hashlib
import json
import os
from pathlib import Path

from .onboarding import Conflict, digest, encoded
from .process_tape import ACTIVE, uuid4
from .screenshot_intake import MAX_STORED_BYTES


def configuration():
    path=os.environ.get('DIA_SCREENSHOT_STORAGE_CONFIG')
    if not path:raise Conflict('CLOUD_SCREENSHOT_STORAGE_NOT_CONFIGURED')
    value=json.loads(Path(path).read_bytes())
    if not isinstance(value,dict) or set(value)!={'account_url','identity','channel'}:
        raise Conflict('CLOUD_SCREENSHOT_STORAGE_CONFIGURATION')
    from .adapters.blob_artifacts import validate_account_url
    from .adapters.managed_identity import validate
    validate_account_url(value['account_url']);validate(value['identity'])
    if not isinstance(value['channel'],str) or not value['channel']:raise Conflict('CLOUD_SCREENSHOT_CHANNEL_REQUIRED')
    return value


class Pixels:
    def __init__(self, screenshots, objects=None):
        self.screenshots=screenshots;self.workspace=screenshots.workspace;self.store=screenshots.store
        self._objects=objects
        from .ticket_clarification import settings
        self.days=settings(getattr(self.workspace,'intake_configuration',None))['screenshot_retention_days']
        with self.store.connect()as db:
            db.execute('''CREATE TABLE IF NOT EXISTS workspace_image_objects(
                id TEXT PRIMARY KEY,object_key TEXT NOT NULL,created REAL NOT NULL,
                expires REAL NOT NULL,state TEXT NOT NULL,sha256 TEXT NOT NULL,bytes INTEGER NOT NULL)''')

    def objects(self):
        if self._objects is None:
            from .adapters.screenshot_blobs import Objects
            self._objects=Objects(configuration())
        return self._objects

    def _capture_guard(self):
        # Recording image bytes in immutable tapes would defeat pixel retention.
        # Metadata/review facts remain recordable. No raw capture fallback.
        if ACTIVE.get() is not None:
            raise Conflict('SCREENSHOT_PIXELS_IN_IMMUTABLE_CAPTURE_UNSUPPORTED')

    def upload(self, request, metadata, raw):
        self._capture_guard();self.purge()
        from .adapters.screenshot_blobs import object_key
        # Validate the storage declaration before retaining a pending upload.
        objects=self.objects()
        with self.store.connect()as db:
            db.execute('BEGIN IMMEDIATE')
            prior=db.execute('SELECT id,body FROM workspace_images WHERE request_key=?',(request['request_key'],)).fetchone()
            if prior:
                body=json.loads(prior['body'])
                if any(body[k]!=v for k,v in metadata.items()):raise Conflict('Upload key already used for another image')
                record=db.execute('SELECT * FROM workspace_image_objects WHERE id=?',(body['id'],)).fetchone()
                if record is None:raise Conflict('SCREENSHOT_BLOB_MIGRATION_REQUIRED')
                if record['state']!='PENDING':return self.image(body['id'])
                key=record['object_key']
            else:
                size=db.execute("SELECT COALESCE(SUM(bytes),0) FROM workspace_image_objects WHERE state IN ('ACTIVE','PENDING')").fetchone()[0]
                if size+len(raw)>MAX_STORED_BYTES:raise Conflict('Image storage limit reached; remove stored images first')
                at=self.workspace.clock();body=dict(metadata,id=str(uuid4()),created=at)
                key=object_key(self.store.environment,body['id'],metadata['sha256'])
                db.execute('INSERT INTO workspace_images VALUES(?,?,?,?,NULL)',(body['id'],request['request_key'],encoded(body),digest(body)))
                db.execute('INSERT INTO workspace_image_objects VALUES(?,?,?,?,?,?,?)',
                    (body['id'],key,at,at+self.days*86400,'PENDING',metadata['sha256'],len(raw)))
        objects.put(key,raw)
        with self.store.connect()as db:
            db.execute("UPDATE workspace_image_objects SET state='ACTIVE' WHERE id=? AND state='PENDING'",(body['id'],))
        return self.image(body['id'])

    def _record(self, identity):
        with self.store.connect()as db:
            row=db.execute('SELECT body,hash,content FROM workspace_images WHERE id=?',(identity,)).fetchone()
            record=db.execute('SELECT * FROM workspace_image_objects WHERE id=?',(identity,)).fetchone()
        if row is None:raise KeyError('Screenshot not found')
        body=json.loads(row['body'])
        if digest(body)!=row['hash'] or body['id']!=identity:raise Conflict('Image metadata integrity differs')
        if row['content'] is not None or record is None:raise Conflict('SCREENSHOT_BLOB_MIGRATION_REQUIRED')
        return body,dict(record)

    def image(self, identity, *, content=False):
        body,record=self._record(identity)
        if record['state']in('ACTIVE','PENDING')and self.workspace.clock()>=record['expires']:
            self._remove(identity,record,'EXPIRED');record['state']='EXPIRED'
        available=record['state']=='ACTIVE'
        if not content:return dict(body,available=available)
        if not available:raise Conflict('Stored image was removed or expired')
        self._capture_guard()
        raw=self.objects().get(record['object_key'])
        if len(raw)!=body['bytes']or hashlib.sha256(raw).hexdigest()!=body['sha256']:
            raise Conflict('Image content integrity differs')
        # Fetch latency may not extend the retention deadline.
        if self.workspace.clock()>=record['expires']:
            self._remove(identity,record,'EXPIRED');raise Conflict('Stored image expired')
        return body,raw

    def _remove(self,identity,record,status):
        self._capture_guard()
        self.objects().delete(record['object_key'])
        with self.store.connect()as db:
            db.execute('UPDATE workspace_image_objects SET state=? WHERE id=?',(status,identity))

    def remove(self,identity):
        _,record=self._record(identity)
        if record['state']in('ACTIVE','PENDING'):self._remove(identity,record,'REMOVED')
        return self.image(identity)

    def purge(self,limit=100):
        self._capture_guard()
        if type(limit)is not int or not 1<=limit<=1000:raise ValueError('BOUNDED_SCREENSHOT_PURGE_REQUIRED')
        at=self.workspace.clock()
        with self.store.connect()as db:
            rows=[dict(r)for r in db.execute("SELECT * FROM workspace_image_objects WHERE expires<=? AND state IN ('ACTIVE','PENDING') ORDER BY expires,id LIMIT ?",(at,limit))]
        for row in rows:self._remove(row['id'],row,'EXPIRED')
        return {'expired':len(rows),'checked_at':at,'limit':limit}
