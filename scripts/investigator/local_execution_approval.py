"""Append-only local-copy authority, distinct from native discovery approval.

This never changes a discovery row, context identity, native policy or export.
The explicit operator control binds the approved LIVE source to a new exact
LOCAL configuration and is rechecked on every normal candidate admission.
"""
import copy
import json
from .onboarding import Conflict, digest, encoded
from .runtime import fingerprint
from .local_bundle import LocalBundle

VERSION = 'local-execution-approval-v1'


def _bundle(config):
    execution = config.get('_estate', {}).get('execution', {})
    if execution.get('mode') != 'LOCAL_EXPORTED': raise Conflict('LOCAL_APPROVAL_REQUIRES_LOCAL_MODE')
    return LocalBundle(execution['bundle'], execution['manifest_sha256'])


def _pins(store, config, bundle):
    from .context_search import latest
    enterprise = latest(store)
    if not enterprise: raise Conflict('LOCAL_ENTERPRISE_CONTEXT_PIN_REQUIRED')
    body = dict(enterprise); identity = body.pop('version')
    pin = {'id': identity, 'hash': digest(body)}
    if bundle.manifest.get('enterprise_context') != pin: raise Conflict('LOCAL_ENTERPRISE_CONTEXT_PIN_MISMATCH')
    models = []
    for record in bundle.manifest.get('contexts', []):
        model = store.get(record['model_id'])
        current = {'model_id': model['id'], 'context_id': model['context_id'],
                   'context_hash': digest(model['context']), 'revision': model['revision']}
        if current != record or not model['enabled']: raise Conflict('LOCAL_MODEL_CONTEXT_PIN_MISMATCH')
        models.append({**current, 'source_policy_hash': (model.get('discovery') or {}).get('policy_hash')})
    if not models: raise Conflict('LOCAL_MODEL_CONTEXT_PIN_REQUIRED')
    source_manifest = config['_estate']['execution']['source_manifest_hash']
    if bundle.manifest.get('estate_manifest_hash') != source_manifest: raise Conflict('LOCAL_SOURCE_MANIFEST_PIN_MISMATCH')
    return {'enterprise_context': pin, 'models': models, 'source_manifest_hash': source_manifest}


def _same_native_configuration(local, source):
    local, source = copy.deepcopy(local), copy.deepcopy(source)
    for config in (local, source):
        estate = config.get('_estate', {})
        for name in ('execution', 'investigation', 'manifest_hash'): estate.pop(name, None)
    return local == source


def approve(store, config, source_config, *, owner, decision, approved_at):
    if not all(isinstance(s, str) and s.strip() for s in (owner, decision, approved_at)):
        raise ValueError('Explicit dated local execution approval required')
    if source_config.get('_estate', {}).get('execution', {}).get('mode', 'LIVE') != 'LIVE':
        raise Conflict('LOCAL_APPROVAL_SOURCE_MUST_BE_LIVE')
    if not _same_native_configuration(config, source_config): raise Conflict('LOCAL_APPROVAL_NATIVE_CONFIGURATION_DIFFERS')
    bundle = _bundle(config); pins = _pins(store, config, bundle)
    source_hash = digest(source_config)
    if source_config.get('_estate', {}).get('manifest_hash') != pins['source_manifest_hash']:
        raise Conflict('LOCAL_APPROVAL_SOURCE_MANIFEST_DIFFERS')
    if any(m['source_policy_hash'] != source_hash for m in pins['models']):
        raise Conflict('LOCAL_APPROVAL_SOURCE_POLICY_UNESTABLISHED')
    body = {'version': VERSION, 'config_hash': digest(config), 'engine_hash': fingerprint(),
            'bundle_sha256': bundle.manifest_sha256, 'source_live_config_hash': source_hash,
            **pins, 'owner': owner, 'decision': decision, 'approved_at': approved_at}
    identity = 'local-approval:' + digest(body)
    from .process_tape import event
    with store.connect() as db:
        db.execute('BEGIN IMMEDIATE')
        db.execute('CREATE TABLE IF NOT EXISTS local_execution_approvals(id TEXT PRIMARY KEY, config_hash TEXT NOT NULL, body TEXT NOT NULL, hash TEXT NOT NULL)')
        existing = db.execute('SELECT body,hash FROM local_execution_approvals WHERE id=?', (identity,)).fetchone()
        if existing:
            if json.loads(existing[0]) != body or existing[1] != digest(body): raise Conflict('LOCAL_APPROVAL_INTEGRITY')
        else:
            event('CONFIGURATION', {'local_execution_approval': identity, 'body': body})
            db.execute('INSERT INTO local_execution_approvals VALUES(?,?,?,?)', (identity, digest(config), encoded(body), digest(body)))
    return {'id': identity, **body}


def validate(store, config, model):
    bundle = _bundle(config); current = _pins(store, config, bundle)
    with store.connect() as db:
        if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='local_execution_approvals'").fetchone():
            raise Conflict('LOCAL_EXECUTION_APPROVAL_REQUIRED')
        rows = db.execute('SELECT id,body,hash FROM local_execution_approvals WHERE config_hash=?', (digest(config),)).fetchall()
    for identity, raw, expected in rows:
        body = json.loads(raw)
        if digest(body) != expected or identity != 'local-approval:' + expected: raise Conflict('LOCAL_APPROVAL_INTEGRITY')
        if body['version'] != VERSION or body['engine_hash'] != fingerprint(): continue
        if body['bundle_sha256'] != bundle.manifest_sha256: continue
        if any(body[k] != current[k] for k in current): continue
        pin = next((m for m in body['models'] if m['model_id'] == model['id']), None)
        if pin and pin['source_policy_hash'] == (model.get('discovery') or {}).get('policy_hash'):
            return body
    raise Conflict('LOCAL_EXECUTION_APPROVAL_REQUIRED')
