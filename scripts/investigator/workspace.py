"""Local single-operator workspace over the governed adaptive runtime.

Scope previews never dispatch. A start consumes one immutable preview once.
Restarted hosts cannot silently take over another host's queued/in-flight work.
"""
import json
import threading
import time
from uuid import uuid4

from .onboarding import Conflict, digest, encoded, fields, text
from .adaptive_candidates import catalog
from .adaptive_projection import read as project
from .filter_scope import catalog as filter_catalog
from .runtime import fingerprint

LIMITS = {'cloud_calls': 6, 'planner_calls': 6, 'wall_seconds': 900,
          'input_characters': 80000, 'max_depth': 3}
ACTIVE = ('SUBMITTING', 'QUEUED', 'RUNNING')
PHASES = {'CREATED': 'Investigation created', 'PLANNER_RESERVED': 'Choosing the next check',
          'DECISION_SAVED': 'Next check selected', 'TOOL_RESERVED': 'Preparing a check',
          'CHILD_LINKED': 'Checking the selected information', 'OBSERVED': 'Results captured',
          'PLANNER_ERROR': 'The next check could not be selected',
          'STOPPED': 'Investigation stopped', 'CANCELLED_RECEIPT_ADOPTED': 'A result arrived after cancellation'}


class Workspace:
    def __init__(self, agent, *, execution_enabled=False, clock=time.time):
        self.agent, self.store, self.clock = agent, agent.store, clock
        self.execution_enabled = execution_enabled
        if execution_enabled and (agent.planner is None or agent.governor is None):
            raise ValueError('Interactive execution requires planner and shared usage governance')
        self.owner = str(uuid4())
        self.stopping = threading.Event()
        with self.store.connect() as db:
            db.executescript('''
            CREATE TABLE IF NOT EXISTS workspace_previews(
              id TEXT PRIMARY KEY, model_id TEXT NOT NULL, body TEXT NOT NULL, hash TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS workspace_jobs(
              preview_id TEXT PRIMARY KEY, model_id TEXT NOT NULL, session_id TEXT UNIQUE,
              owner TEXT NOT NULL, status TEXT NOT NULL, created REAL NOT NULL, error TEXT);
            CREATE UNIQUE INDEX IF NOT EXISTS workspace_single_active ON workspace_jobs((1))
              WHERE status IN ('SUBMITTING','QUEUED','RUNNING');
            ''')

    def models(self):
        return {'execution_enabled': self.execution_enabled, 'models': [self.model(m['id']) for m in self.store.list(True)],
                'limits': LIMITS, 'deployment': 'LOCAL_SINGLE_OPERATOR', 'cause_verification_available': False}

    def model(self, identity):
        model = self.store.get(identity)
        context = model.get('context') or {}
        reports = context.get('reports') or []
        assets = reports[0]['model_assets'] if reports else []
        names = {a['id']: a['name'] for a in assets}
        scope = filter_catalog(model)
        columns = [dict(c, table_name=names.get(c['table_id'], '')) for c in scope['columns'] if c['operators']]
        return {'id': model['id'], 'name': model.get('name', model['id']), 'revision': model['revision'],
                'context_id': model['context_id'], 'enabled': model['enabled'],
                'measures': [{'id': m['id'], 'name': m['name']} for m in context.get('measures', [])],
                'columns': columns, 'range_semantics': scope['range_semantics']}

    def preview(self, request):
        fields(request, ['model_id', 'measure_id', 'filters', 'dimension_ids', 'symptom', 'predecessor'])
        model = self.store.get(request['model_id'])
        if not model['enabled']:
            raise Conflict('This model is not enabled')
        predecessor = request['predecessor']
        if predecessor is not None:
            previous = self.session(predecessor)
            if previous['model_id'] != model['id'] or previous['status'] != 'NEEDS_INPUT':
                raise Conflict('Clarification must continue a waiting investigation in the same model')
        envelope = {k: request[k] for k in ('model_id', 'measure_id', 'filters', 'dimension_ids', 'symptom')}
        envelope.update(revision=model['revision'], context_id=model['context_id'], source_tests=[],
                        source_selection='reviewed_mappings', record_selection='reviewed_mappings', limits=dict(LIMITS))
        candidates, gaps = catalog(self.store, self.agent.config, envelope)
        metadata = self.model(model['id'])
        labels = {m['id']: m['name'] for m in metadata['measures']}
        columns = {c['column_id']: c for c in metadata['columns']}
        contexts = {}
        for candidate in candidates:
            context = candidate.get('dependency_context')
            if context:
                contexts[digest(context['path'])] = {'path':[labels.get(m,'Related metric') for m in context['path']],
                    'filters':[{'column':columns[f['column_id']]['name'], 'mode':f['mode'], 'value':f['value']}
                               for step in context['steps'] for f in step['filters']]}
        body = {'id': str(uuid4()), 'model_id': model['id'], 'model_name': metadata['name'],
                'envelope': envelope, 'predecessor': predecessor, 'created': self.clock(),
                'expires': self.clock() + 900, 'engine_hash': fingerprint(), 'config_hash': digest(self.agent.config),
                'catalog_hash': digest(candidates), 'context_hash': digest(model['context']),
                'labels': labels, 'columns': columns, 'measure_name': labels[envelope['measure_id']],
                'candidate_count': len(candidates), 'gaps': gaps, 'cloud_calls': 0,
                'calculation_contexts':list(contexts.values()),
                'scope_note': 'Selected filters supply the starting context. Measures may apply their own filters; component paths are listed below when supported. A screenshot or report selection is not automatically reproduced.'}
        with self.store.connect() as db:
            db.execute('INSERT INTO workspace_previews VALUES (?,?,?,?)', (body['id'], model['id'], encoded(body), digest(body)))
        return body

    def read_preview(self, identity):
        with self.store.connect() as db:
            row = db.execute('SELECT body,hash,model_id FROM workspace_previews WHERE id=?', (identity,)).fetchone()
        if row is None:
            raise KeyError('Preview not found')
        body = json.loads(row['body'])
        if digest(body) != row['hash'] or body['model_id'] != row['model_id']:
            raise Conflict('Scope preview integrity differs')
        self.store.get(body['model_id'])
        return body

    def start(self, identity):
        if not self.execution_enabled:
            raise Conflict('This host is in history-only mode')
        preview = self.read_preview(identity)
        with self.store.connect() as db:
            row = db.execute('SELECT session_id,status FROM workspace_jobs WHERE preview_id=?', (identity,)).fetchone()
        if row:
            if row['session_id']:
                return self.session(row['session_id'])
            raise Conflict('Submission is incomplete; it will not be automatically retried')
        if self.clock() > preview['expires']:
            raise Conflict('Scope review expired; review the current scope again')
        if preview['engine_hash'] != fingerprint() or preview['config_hash'] != digest(self.agent.config):
            raise Conflict('Runtime or connection changed; review again')
        if digest(self.store.get(preview['model_id'])['context']) != preview['context_hash']:
            raise Conflict('Model context changed; review again')
        candidates, _ = catalog(self.store, self.agent.config, preview['envelope'])
        if digest(candidates) != preview['catalog_hash']:
            raise Conflict('Available checks changed; review again')
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute("SELECT 1 FROM workspace_jobs WHERE status IN ('SUBMITTING','QUEUED','RUNNING')").fetchone():
                raise Conflict('Another investigation is active; wait or cancel it first')
            db.execute('INSERT INTO workspace_jobs VALUES (?,?,NULL,?,?,?,NULL)',
                       (identity, preview['model_id'], self.owner, 'SUBMITTING', self.clock()))
        try:
            state = (self.agent.revise(preview['predecessor'], preview['envelope'], 'workspace:' + identity)
                     if preview['predecessor'] else self.agent.create(preview['envelope'], 'workspace:' + identity))
            with self.store.connect() as db:
                db.execute("UPDATE workspace_jobs SET session_id=?,status='QUEUED' WHERE preview_id=? AND status='SUBMITTING'",
                           (state['id'], identity))
        except Exception:
            with self.store.connect() as db:
                db.execute("UPDATE workspace_jobs SET status='INTERRUPTED',error='SUBMISSION_FAILED' WHERE preview_id=?", (identity,))
            raise
        return self.session(state['id'])

    def run_once(self):
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute("SELECT * FROM workspace_jobs WHERE owner=? AND status='QUEUED' ORDER BY created LIMIT 1", (self.owner,)).fetchone()
            if row is None:
                return False
            db.execute("UPDATE workspace_jobs SET status='RUNNING' WHERE preview_id=?", (row['preview_id'],))
        try:
            self.agent.run(row['session_id'])
            status, error = 'FINISHED', None
        except Exception:
            status, error = 'INTERRUPTED', 'WORKER_INTERRUPTED'
        with self.store.connect() as db:
            # Cancellation wins; a late worker cannot undo the visible cancel state.
            db.execute("UPDATE workspace_jobs SET status=?,error=? WHERE preview_id=? AND status='RUNNING'",
                       (status, error, row['preview_id']))
        return True

    def work(self):
        try:
            while not self.stopping.is_set():
                if not self.run_once():
                    self.stopping.wait(0.5)
        finally:
            self.stopping.set()

    def sessions(self):
        with self.store.connect() as db:
            rows = db.execute('SELECT * FROM workspace_jobs ORDER BY created DESC LIMIT 100').fetchall()
        results = []
        for row in rows:
            self.store.get(row['model_id'])
            p = self.read_preview(row['preview_id'])
            results.append({'id': row['session_id'], 'preview_id': row['preview_id'], 'model_id': row['model_id'],
                            'model_name': p['model_name'], 'measure_name': p['measure_name'],
                            'symptom': p['envelope']['symptom'], 'created': row['created'],
                            'job_status': row['status'], 'worker_attached': row['owner'] == self.owner and self.execution_enabled})
        return {'sessions': results}

    def session(self, identity):
        with self.store.connect() as db:
            job = db.execute('SELECT * FROM workspace_jobs WHERE session_id=?', (identity,)).fetchone()
        if job is None:
            raise KeyError('Workspace investigation not found')
        preview = self.read_preview(job['preview_id'])
        # Derive both views from one saved state read, not two racing snapshots.
        technical = project(self.store, job['model_id'], identity)
        if technical['scope_hash'] != digest(preview['envelope']) or technical['context_hash'] != preview['context_hash']:
            raise Conflict('Saved session and reviewed scope do not match')
        labels = preview['labels']
        facts = []
        for fact in technical['outcome']['facts']:
            facts.append({'id': fact['id'], 'metric': labels.get(fact['measure_id'], 'Related metric'),
                          'origin': 'Report' if fact['tool'].startswith('native') else 'Connected records',
                          **({'calculation_context':[labels.get(m,'Related metric') for m in fact['dependency_context']['path']]}
                             if fact.get('dependency_context') else {}),
                          'status': fact['status'], 'values': fact['values'], 'completeness': fact['completeness'],
                          'kind': 'records' if fact['tool'].endswith('records') else 'breakdown' if fact['dimension_id'] else 'metric'})
        stopped = technical['status'] not in ('READY', 'PLANNING', 'EXECUTING')
        attached = (job['owner'] == self.owner and self.execution_enabled and not self.stopping.is_set()
                    and job['status'] != 'INTERRUPTED')
        summary = ('The checks have stopped. More evidence is needed to explain the reported difference.' if stopped
                   else 'Checking the selected information. Results appear as each check finishes.')
        if technical['status'] == 'NEEDS_INPUT':
            summary = 'Your clarification is needed before further checks.'
        elif technical['status'] == 'CANCELLED':
            summary = 'Investigation cancelled. Checks already sent may still finish; saved results remain available.'
        elif job['status'] == 'INTERRUPTED' or (not attached and not stopped):
            summary = 'The worker is not attached to this investigation. Cancel it before starting a new review; no check will be silently retried.'
        return {'id': identity, 'model_id': job['model_id'], 'model_name': preview['model_name'],
                'measure_name': preview['measure_name'], 'symptom': preview['envelope']['symptom'],
                'status': technical['status'], 'job_status': job['status'], 'worker_attached': attached,
                'scope_hash': technical['scope_hash'], 'context_hash': technical['context_hash'],
                'outcome_hash': technical['outcome_hash'], 'summary': summary, 'question': technical['question'],
                'facts': facts, 'scope': preview['envelope'], 'columns': preview['columns'], 'predecessor': preview['predecessor'],
                'activity': [{'label': PHASES.get(e['kind'], 'Investigation updated'), **e} for e in technical['activity']],
                'cause_verified': technical['outcome']['cause_verified'], 'delivery_eligible': technical['outcome']['delivery_eligible'],
                'technical': technical}

    def cancel(self, identity):
        self.session(identity)
        self.agent.cancel(identity)
        with self.store.connect() as db:
            db.execute("UPDATE workspace_jobs SET status='CANCELLED' WHERE session_id=? AND status IN ('SUBMITTING','QUEUED','RUNNING','INTERRUPTED')", (identity,))
        return self.session(identity)
