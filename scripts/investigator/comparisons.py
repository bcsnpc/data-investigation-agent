"""Reviewed comparison intent and evidence gates; no causal certification."""
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from .onboarding import fields, text, encoded, digest, Conflict
from .diagnostic_evidence import read as native_read
from .source_diagnostics import evidence as source_read


def initialize(db):
    db.executescript('''
    CREATE TABLE IF NOT EXISTS comparison_mappings(
      id TEXT PRIMARY KEY,model_id TEXT,context_id TEXT,body TEXT,hash TEXT,actor TEXT,created TEXT);
    CREATE TABLE IF NOT EXISTS comparison_assessments(
      id TEXT PRIMARY KEY,model_id TEXT,context_id TEXT,body TEXT,hash TEXT,created TEXT);
    CREATE TABLE IF NOT EXISTS comparison_mapping_revocations(
      id TEXT PRIMARY KEY,reason TEXT,actor TEXT,created TEXT);
    ''')


def register(store, model_id, body, actor):
    expected = ['revision', 'context_id', 'measure_id', 'source_object_id', 'source_operation',
                'source_column_id', 'grain', 'unit', 'date_basis', 'blank_policy', 'filter_bindings', 'confirmed']
    if isinstance(body, dict) and 'native_input_id' in body:expected.append('native_input_id')
    fields(body, expected)
    model = store.get(model_id)
    if not model['enabled'] or type(body['revision']) is not int or body['revision'] != model['revision'] or body['context_id'] != model['context_id']:
        raise Conflict('Mapping review requires current enabled context')
    if body['confirmed'] is not True:raise ValueError('Explicit mapping confirmation required')
    if 'native_input_id' in body:text(body['native_input_id'], 500)
    if body['measure_id'] not in {m['id'] for m in model['context']['measures']}:
        raise ValueError('Unknown measure')
    for key in ['source_object_id', 'grain', 'unit', 'date_basis']:
        text(body[key], 500)
    if body['source_operation'] not in ('count_rows', 'sum') or body['blank_policy'] != 'preserve':
        raise ValueError('Unsupported comparison contract')
    if body['source_operation'] == 'sum':text(body['source_column_id'], 500)
    elif body['source_column_id'] is not None:raise ValueError('Count has no value column')
    bindings = body['filter_bindings']
    if not isinstance(bindings, list) or not 1 <= len(bindings) <= 8:raise ValueError('Bounded filter mapping required')
    native = set(); source = set()
    for binding in bindings:
        fields(binding, ['native_column_id', 'source_column_id'])
        left = text(binding['native_column_id'], 500); right = text(binding['source_column_id'], 500)
        if left in native or right in source:raise ValueError('Duplicate filter mapping')
        native.add(left); source.add(right)
    # This records a reviewed intent. Actual object/column bindings are checked
    # against executed receipts, not inferred from arbitrary IDs in this draft.
    identity = str(uuid4())
    with store.connect() as db:
        initialize(db)
        db.execute('INSERT INTO comparison_mappings VALUES(?,?,?,?,?,?,?)',
                   (identity, model_id, model['context_id'], encoded(body), digest(body), text(actor, 100), datetime.now(timezone.utc).isoformat()))
    return {'id': identity, 'context_id': model['context_id'], 'hash': digest(body),
            'provenance': 'TEAM_CONFIRMED_INTENT', 'equivalence_verified': False}


def mapping(store, model_id, identity):
    import json
    store.get(model_id)
    with store.connect() as db:
        initialize(db)
        row = db.execute('SELECT body,hash,actor FROM comparison_mappings WHERE id=? AND model_id=?', (identity, model_id)).fetchone()
        revoked = db.execute('SELECT reason,actor,created FROM comparison_mapping_revocations WHERE id=?', (identity,)).fetchone()
    if not row:raise KeyError('Mapping not found')
    body = json.loads(row[0])
    if digest(body) != row[1]:raise ValueError('Mapping integrity differs')
    return {'id': identity, 'body': body, 'hash': row[1], 'actor': row[2], 'revocation':list(revoked) if revoked else None}


def list_mappings(store, model_id):
    store.get(model_id)
    with store.connect() as db:
        initialize(db)
        rows=db.execute('SELECT id FROM comparison_mappings WHERE model_id=? ORDER BY created,id LIMIT 101',(model_id,)).fetchall()
    if len(rows)>100:raise ValueError('Mapping catalog exceeds diagnostic budget')
    return [mapping(store,model_id,row[0]) for row in rows]


def revoke(store, model_id, identity, reason, actor):
    mapping(store,model_id,identity);text(reason,1000);text(actor,100)
    with store.connect() as db:
        initialize(db)
        db.execute('INSERT OR IGNORE INTO comparison_mapping_revocations VALUES(?,?,?,?)',
                   (identity,reason,actor,datetime.now(timezone.utc).isoformat()))
    return mapping(store,model_id,identity)


def aligned(native_filters, source_filters, bindings):
    left = {f['column_id']: f for f in native_filters}; right = {f['column_id']: f for f in source_filters}
    if len(left) != len(native_filters) or len(right) != len(source_filters):return False
    if set(left) != {b['native_column_id'] for b in bindings} or set(right) != {b['source_column_id'] for b in bindings}:return False
    for binding in bindings:
        a = left[binding['native_column_id']]; b = right[binding['source_column_id']]
        operator=a.get('operator','in')
        if operator!=b.get('operator','in') or operator not in ('in','range'):return False
        # Compare exact JSON types/values, not coercion (True must not equal 1).
        if operator=='range':
            if encoded(a['values'])!=encoded(b['values']):return False
        elif sorted(encoded(v) for v in a['values'])!=sorted(encoded(v) for v in b['values']):return False
    return True


def assess(store, model_id, body, *, assessment_id=None):
    fields(body, ['native_receipt_id', 'source_receipt_id', 'measure_id', 'mapping_id'])
    for key in ['native_receipt_id', 'source_receipt_id', 'measure_id']:text(body[key], 500)
    model = store.get(model_id)
    native = native_read(store, model_id, body['native_receipt_id'])
    source = source_read(store, model_id, body['source_receipt_id'])
    gaps = []; left = None; right = None
    if native['request']['plan'].get('context_path'):gaps.append('DEPENDENCY_CONTEXT_COMPARISON_UNSUPPORTED')
    if not native['assessment']['current_context'] or not source['local_context_current']:
        gaps.append('STALE_OR_DISABLED_CONTEXT')
    if native['request']['context_id'] != source['request']['context_id']:gaps.append('DIFFERENT_CONTEXT_VERSIONS')
    nresult = native['result'] or {}; sresult = source['result'] or {}
    if native['status'] != 'COMPLETED':gaps.append('NATIVE_READ_UNAVAILABLE')
    elif native['request']['dimension_id'] is not None or nresult.get('completeness') != 'COMPLETE_RESPONSE':
        gaps.append('NATIVE_SCALAR_COMPLETE_RESPONSE_REQUIRED')
    elif body['measure_id'] not in native['request']['measure_ids']:gaps.append('MEASURE_NOT_IN_RECEIPT')
    else:
        index = native['request']['measure_ids'].index(body['measure_id'])
        left = nresult['rows'][0]['[m' + str(index) + ']']
    if source['status'] != 'COMPLETED':gaps.append('SOURCE_READ_UNAVAILABLE')
    else:right = sresult['value']
    reviewed = None; semantic_shape = None
    if body['mapping_id'] is None:gaps.append('REVIEWED_MAPPING_REQUIRED')
    else:
        reviewed = mapping(store, model_id, text(body['mapping_id'], 500)); contract = reviewed['body']
        if reviewed['revocation'] is not None:gaps.append('MAPPING_REVOKED')
        if contract['context_id'] != model['context_id'] or contract['revision'] != model['revision']:
            gaps.append('MAPPING_REVIEW_STALE')
        plan = source['request']['plan']
        if (contract['measure_id'] != body['measure_id'] or contract['source_object_id'] != plan['object_id'] or
            contract['source_operation'] != plan['operation'] or contract['source_column_id'] != plan['column_id']):
            gaps.append('MAPPING_DOES_NOT_BIND_RECEIPTS')
        if not aligned(native['request']['plan']['filters'], plan['filters'], contract['filter_bindings']):
            gaps.append('FILTER_SCOPES_NOT_ALIGNED')
        if 'native_input_id' in contract:
            from .aggregate_semantics import assess_mapping
            semantic_shape = assess_mapping(model, contract, source)
            gaps.extend(semantic_shape['gaps'])
    # Numeric proximity is diagnostic only, and only after reviewed intent and
    # structural scope match. Proof is deliberately not accepted from the API.
    difference = None
    if not gaps and left and right and left['type'] == right['type'] == 'decimal':
        from decimal import localcontext
        with localcontext() as ctx:
            ctx.prec = 100
            a, b = Decimal(left['value']), Decimal(right['value'])
            if not a.is_finite() or not b.is_finite():raise ValueError('Invalid numeric evidence')
            difference = str(a - b)
    elif left and right and ('blank' in (left['type'], right['type'])):
        gaps.append('BLANK_OBSERVATION_NOT_NUMERIC')
    elif left and right and (left['type'] != 'decimal' or right['type'] != 'decimal'):
        gaps.append('NONNUMERIC_OBSERVATION')
    gaps.extend(['UPSTREAM_SEMANTIC_EQUIVALENCE_UNVERIFIED', 'EFFECTIVE_CONTEXT_UNVERIFIED',
                 'REMOTE_DEFINITION_VERSION_UNVERIFIED', 'SHARED_DATA_GENERATION_UNVERIFIED'])
    result = {'version': 'comparison-gates-v1', 'request': body, 'model_id': model_id,
              'context_id': model['context_id'], 'revision': model['revision'],
              'native_evidence_hash': digest(native), 'source_evidence_hash': digest(source),
              'mapping_hash': reviewed['hash'] if reviewed else None,
              'aggregate_semantics': semantic_shape,
              'observations': {'native': left, 'source': right},
              'diagnostic_difference_native_minus_source': difference,
              'gaps': sorted(set(gaps)), 'outcome': 'INSUFFICIENT_EVIDENCE',
              'comparable': False, 'root_cause_verified': False, 'delivery_eligible': False}
    current = store.get(model_id)
    if current['revision'] != model['revision'] or current['context_id'] != model['context_id']:
        raise Conflict('Context changed during assessment')
    identity = assessment_id or str(uuid4())
    if assessment_id is not None:
        from uuid import UUID
        if str(UUID(assessment_id)) != assessment_id:raise ValueError('Invalid reserved assessment ID')
    with store.connect() as db:
        initialize(db)
        db.execute('INSERT INTO comparison_assessments VALUES(?,?,?,?,?,?)',
                   (identity, model_id, model['context_id'], encoded(result), digest(result), datetime.now(timezone.utc).isoformat()))
    return dict(result, id=identity, hash=digest(result))


def read(store, model_id, identity):
    import json
    model = store.get(model_id)
    with store.connect() as db:
        initialize(db)
        row = db.execute('SELECT body,hash FROM comparison_assessments WHERE id=? AND model_id=?', (identity, model_id)).fetchone()
    if row is None:raise KeyError('Assessment not found')
    body = json.loads(row[0])
    if digest(body) != row[1]:raise ValueError('Assessment integrity differs')
    unchanged = False
    try:
        request = body['request']
        unchanged = (digest(native_read(store, model_id, request['native_receipt_id'])) == body['native_evidence_hash'] and
                     digest(source_read(store, model_id, request['source_receipt_id'])) == body['source_evidence_hash'])
        if request['mapping_id'] is not None:
            review=mapping(store, model_id, request['mapping_id'])
            unchanged = unchanged and review['hash'] == body['mapping_hash'] and review['revocation'] is None
    except (KeyError, ValueError, TypeError):
        unchanged = False
    return {'id': identity, 'hash': row[1], 'assessment': body,
            'input_evidence_unchanged': unchanged,
            'local_context_current': bool(model['enabled'] and model['context_id'] == body['context_id'] and model['revision'] == body['revision'])}
