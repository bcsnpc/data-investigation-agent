"""Transactional model registration and immutable retained-metadata contexts.

No cloud execution or inference. Server configuration owns the inventory path and
environment; API clients cannot provide a database path or credentials.
"""
from contextlib import contextmanager, closing
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
from uuid import UUID, uuid4

from report_definition_evidence import bundle
from .semantic_graph import analyze, affected


class Conflict(ValueError):
    pass


def encoded(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'))


def digest(value):
    return hashlib.sha256(encoded(value).encode()).hexdigest()


def text(value, maximum=2000):
    if not isinstance(value, str) or not value.strip() or len(value) > maximum or '\x00' in value:
        raise ValueError('Invalid text')
    return value.strip()


def fields(body, expected):
    if not isinstance(body, dict) or set(body) != set(expected):
        raise ValueError('Unexpected fields')


class ModelStore:
    def __init__(self, database, inventory, environment):
        self.database = Path(database)
        self.inventory = Path(inventory)
        self.environment = text(environment, 100)
        self.database.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript('''
            CREATE TABLE IF NOT EXISTS models(
              id TEXT PRIMARY KEY, environment TEXT NOT NULL, workspace TEXT NOT NULL,
              native_id TEXT NOT NULL, name TEXT NOT NULL, reports TEXT NOT NULL,
              revision INTEGER NOT NULL, enabled INTEGER NOT NULL DEFAULT 0,
              context_id TEXT, business TEXT NOT NULL,
              UNIQUE(environment,workspace,native_id));
            CREATE TABLE IF NOT EXISTS model_contexts(
              id TEXT PRIMARY KEY, model_id TEXT NOT NULL REFERENCES models(id),
              scan_id TEXT NOT NULL, body TEXT NOT NULL, hash TEXT NOT NULL,
              created TEXT NOT NULL, UNIQUE(model_id,scan_id));
            CREATE TABLE IF NOT EXISTS model_events(
              id INTEGER PRIMARY KEY, model_id TEXT NOT NULL REFERENCES models(id),
              revision INTEGER NOT NULL, action TEXT NOT NULL, actor TEXT NOT NULL,
              at TEXT NOT NULL, detail TEXT NOT NULL);
            ''')

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.database, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        try:
            with db:
                yield db
        finally:
            db.close()

    def row(self, db, identity):
        row = db.execute('SELECT * FROM models WHERE id=? AND environment=?',
                         (str(UUID(text(identity, 100))), self.environment)).fetchone()
        if row is None:
            raise KeyError('Model not found')
        return row

    def event(self, db, identity, revision, action, actor, detail):
        db.execute('INSERT INTO model_events(model_id,revision,action,actor,at,detail) VALUES(?,?,?,?,?,?)',
                   (identity, revision, action, actor, datetime.now(timezone.utc).isoformat(), encoded(detail)))

    def register(self, body, actor):
        fields(body, ['name', 'workspace', 'model_id', 'report_ids'])
        workspace, native = str(UUID(text(body['workspace'],100))), str(UUID(text(body['model_id'],100)))
        reports = body['report_ids']
        if not isinstance(reports, list) or not 1 <= len(reports) <= 50:
            raise ValueError('Select 1-50 reports')
        reports = sorted({str(UUID(text(x,100))) for x in reports})
        name = text(body['name'], 200)
        with self.connect() as db:
            identity = str(uuid4())
            try:
                db.execute('INSERT INTO models VALUES(?,?,?,?,?,?,1,0,NULL,?)',
                           (identity, self.environment, workspace, native, name, encoded(reports), '{}'))
            except sqlite3.IntegrityError as exc:
                raise Conflict('Model already registered') from exc
            self.event(db, identity, 1, 'REGISTERED', actor, {})
        return self.get(identity)

    def _context(self, db, identity, context_id):
        row = db.execute('SELECT body,hash FROM model_contexts WHERE id=? AND model_id=?',
                         (context_id, identity)).fetchone()
        if row is None:
            raise KeyError('Context not found')
        value = json.loads(row['body'])
        if digest(value) != row['hash']:
            raise ValueError('Context integrity failure')
        return value

    def get(self, identity):
        with self.connect() as db:
            row = dict(self.row(db, identity))
            row['reports'] = json.loads(row['reports'])
            row['business'] = json.loads(row['business'])
            row['enabled'] = bool(row['enabled'])
            context = self._context(db, identity, row['context_id']) if row['context_id'] else None
            row['context'] = context
            discovered = db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='discovery_models'").fetchone()
            discovered = db.execute('SELECT denied,policy_hash FROM discovery_models WHERE model_id=?',(identity,)).fetchone() if discovered else None
            row['discovery'] = dict(discovered) if discovered else None
            row['stage'] = ('ENABLED' if row['enabled'] else 'INVESTIGATION_READY') if context and row['business'].get('confirmed_context') == row['context_id'] else ('BUSINESS_CONTEXT_REVIEW' if context else 'REGISTERED')
            if discovered: row['stage'] = 'AVAILABLE_FOR_INVESTIGATION' if row['enabled'] else 'DISCOVERED_PARTIAL_OR_DENIED'
            row['readiness'] = 'PARTIAL' if context else 'NEEDS_CONTEXT'
            row['events'] = [dict(x) for x in db.execute('SELECT revision,action,actor,at,detail FROM model_events WHERE model_id=? ORDER BY id', (identity,))]
            row['context_history'] = [dict(x) for x in db.execute('SELECT id,scan_id,hash,created FROM model_contexts WHERE model_id=? ORDER BY created,id', (identity,))]
            return row

    def list(self, enabled_only=False):
        with self.connect() as db:
            ids = [x[0] for x in db.execute('SELECT id FROM models WHERE environment=? AND (?=0 OR enabled=1) ORDER BY name,id', (self.environment, int(enabled_only)))]
        return [self.get(x) for x in ids]

    def context(self, identity, context_id):
        with self.connect() as db:
            self.row(db, identity)
            return self._context(db, identity, str(UUID(text(context_id,100))))

    def check_revision(self, row, revision):
        if type(revision) is not int or row['revision'] != revision:
            raise Conflict('Model changed; reload before editing')

    def import_scan(self, identity, revision, scan_id, actor):
        scan_id = str(UUID(text(scan_id,100)))
        # Read and validate the complete registered report set in one inventory
        # snapshot. bundle validates immutable hashes and explicit model binding.
        model = self.get(identity)
        self.check_revision(model, revision)
        with closing(sqlite3.connect(self.inventory.resolve().as_uri()+'?mode=ro',uri=True)) as db:
            scan = db.execute('SELECT ended FROM scans WHERE id=? AND status IN (\'COMPLETE\',\'PARTIAL\')',(scan_id,)).fetchone()
        if not scan or not scan[0]:
            raise ValueError('Finished scan required')
        ended = datetime.fromisoformat(scan[0])
        if ended.tzinfo is None:
            raise ValueError('Scan time must include timezone')
        if model['context'] and ended <= datetime.fromisoformat(model['context']['scan_ended']):
            raise Conflict('Scan must be newer than current context')
        root = 'fabric://' + model['workspace']
        reports = [bundle(self.inventory, scan_id, root + '/' + r) for r in model['reports']]
        expected = root + '/' + model['native_id']
        if any(r['model_id'] != expected or r['gaps'] for r in reports):
            raise ValueError('Complete explicit report/model definitions required')
        assets = reports[0]['model_assets']
        if any(r['model_assets'] != assets for r in reports):
            raise ValueError('Metadata changed during import')
        measures = [{'id':a['id'], 'name':a['name'], 'definition':a['metadata'], 'hash':a['content_hash'],
                     'provenance':'DISCOVERED'} for a in assets if a['kind'] == 'Measure']
        source_hashes = {a['id']:a['content_hash'] for a in assets}
        for report in reports:
            source_hashes[report['report']['id']] = report['report']['content_hash']
            source_hashes.update({a['id']:a['content_hash'] for a in report['report_definitions']})
        prior = model['context']
        old_hashes = prior['source_hashes'] if prior else {}
        changes = {'added':sorted(source_hashes.keys()-old_hashes.keys()),
                   'removed':sorted(old_hashes.keys()-source_hashes.keys()),
                   'changed':sorted(k for k in source_hashes.keys() & old_hashes.keys() if source_hashes[k] != old_hashes[k])}
        semantic = analyze(assets)
        impacted = affected(changes['added']+changes['removed']+changes['changed'],semantic,
                            prior.get('semantic_graph') if prior else None)
        # A partial listing cannot establish deletion or replace last good context.
        if changes['removed'] and any(r['scan_status'] != 'COMPLETE' for r in reports):
            raise ValueError('Partial scan cannot remove retained assets')
        value = {'schema_version':1,'id':str(uuid4()),'model_id':identity,'scan_id':scan_id,'scan_ended':scan[0],
                 'measures':measures,'reports':reports,'source_hashes':source_hashes,'changes':changes,
                 'semantic_graph':semantic,'affected_measures':impacted,
                 'capabilities':{'MEASURE_DEFINITION_AVAILABLE':'SUPPORTED','REPORT_CONTEXT_AVAILABLE':'PARTIAL',
                                 'MODEL_QUERYABLE':'UNKNOWN','MEASURE_DEPENDENCIES_RESOLVED':semantic['dependency_state'],
                                 'AGGREGATE_RECONCILABLE':'UNKNOWN','SOURCE_PROVENANCE_VERIFIED':'UNKNOWN'},
                 'limitation':'Retained metadata and conservative dependency analysis only. Live execution and runtime filters are not verified.'}
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = self.row(db, identity)
            self.check_revision(row, revision)
            existing = db.execute('SELECT id FROM model_contexts WHERE model_id=? AND scan_id=?', (identity,scan_id)).fetchone()
            if existing:
                raise Conflict('Scan already imported')
            db.execute('INSERT INTO model_contexts VALUES(?,?,?,?,?,?)',
                       (value['id'],identity,scan_id,encoded(value),digest(value),datetime.now(timezone.utc).isoformat()))
            business = json.loads(row['business'])
            unchanged = (prior is not None and not any(changes.values()) and
                         prior.get('semantic_graph',{}).get('version')==semantic['version'])
            if unchanged and business.get('confirmed_context') == row['context_id']:
                business['confirmed_context'] = value['id']
            db.execute('UPDATE models SET context_id=?,revision=revision+1,enabled=?,business=? WHERE id=?',
                       (value['id'], row['enabled'] if unchanged else 0, encoded(business), identity))
            self.event(db, identity, revision+1, 'CONTEXT_IMPORTED', actor, {'context_id':value['id'],'changes':changes,'confirmed_context_carried':unchanged})
        return self.get(identity)

    def review(self, identity, revision, body, actor):
        fields(body, ['definition','owner','date_basis','refresh_expectation','tolerance','exceptions'])
        data = {k:text(v) for k,v in body.items()}
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = self.row(db, identity)
            self.check_revision(row, revision)
            if not row['context_id']:
                raise Conflict('Import context before review')
            self._context(db, identity, row['context_id'])
            data.update(provenance='TEAM_CONFIRMED',reviewer=actor,confirmed_context=row['context_id'])
            db.execute('UPDATE models SET business=?,revision=revision+1,enabled=0 WHERE id=?', (encoded(data),identity))
            self.event(db,identity,revision+1,'BUSINESS_CONTEXT_CONFIRMED',actor,data)
        return self.get(identity)

    def enable(self, identity, revision, enabled, actor):
        if type(enabled) is not bool:
            raise ValueError('Expected boolean')
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = self.row(db, identity)
            self.check_revision(row, revision)
            discovery_table=db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='discovery_models'").fetchone()
            discovered=db.execute('SELECT 1 FROM discovery_models WHERE model_id=?',(identity,)).fetchone() if discovery_table else None
            if enabled:
                if not row['context_id'] or (not discovered and json.loads(row['business']).get('confirmed_context') != row['context_id']):
                    raise Conflict('Review current context first')
                context=self._context(db, identity, row['context_id'])
                if discovered and not (context.get('discovery',{}).get('definition_available') and context.get('measures')):
                    raise Conflict('Current discovered definition unavailable')
            if discovered:db.execute('UPDATE discovery_models SET denied=? WHERE model_id=?',(int(not enabled),identity))
            db.execute('UPDATE models SET enabled=?,revision=revision+1 WHERE id=?',(int(enabled),identity))
            self.event(db,identity,revision+1,'ENABLED' if enabled else 'DISABLED',actor,{'mode':'catalog_only'})
        return self.get(identity)
