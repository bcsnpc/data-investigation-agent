"""Pinned SQL catalog aggregates. No measure equivalence or cause inference."""
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
import re
import sqlite3
import subprocess
from uuid import uuid4

from .onboarding import fields, digest, encoded, Conflict


def snapshot(store, model, config):
    if not model['enabled'] or model['workspace'] != config['fabric']['workspace_id']:
        raise Conflict('Model disabled or connection workspace differs')
    scan = model['context']['scan_id']
    source = 'sql://' + config['sql']['server'] + '/' + config['sql']['database']
    with closing(sqlite3.connect(store.inventory)) as db:
        status = db.execute('SELECT status FROM scans WHERE id=?', (scan,)).fetchone()
        visibility = db.execute("SELECT status FROM observations WHERE scan_id=? AND asset_id=? AND capability='catalog_visibility'", (scan, source)).fetchall()
        if not status or status[0] not in ('COMPLETE', 'PARTIAL') or visibility != [('AVAILABLE',)]:
            raise ValueError('Pinned SQL metadata is unavailable')
        rows = db.execute("SELECT id,parent_id,kind,metadata,content_hash FROM assets WHERE scan_id=? AND kind IN ('SqlObject','SqlColumn')", (scan,)).fetchall()
    assets = {}
    for identity, parent, kind, raw, expected in rows:
        metadata = json.loads(raw)
        actual = hashlib.sha256(json.dumps(metadata, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        if actual != expected:
            raise ValueError('SQL metadata integrity differs')
        assets[identity] = {'id': identity, 'parent_id': parent, 'kind': kind, 'metadata': metadata, 'hash': expected}
    objects = {k: v for k, v in assets.items() if v['kind'] == 'SqlObject' and v['parent_id'] == source
               and v['metadata']['schema_name'] == config['sql']['visibility_schema'] and v['metadata']['type_desc'] == 'USER_TABLE'}
    columns = {k: v for k, v in assets.items() if v['kind'] == 'SqlColumn' and v['parent_id'] in objects}
    return objects, columns


def quote(name):
    if not isinstance(name, str) or not name or len(name) > 128 or any(ord(c) < 32 for c in name):
        raise ValueError('Invalid catalog identifier')
    return '[' + name.replace(']', ']]') + ']'


def connection_attempts(value):
    if value is None:return None
    if not isinstance(value,list) or not 1<=len(value)<=3:raise ValueError('Invalid connection attempts')
    for index,attempt in enumerate(value,1):
        fields(attempt,['attempt','started_at','finished_at','status','stage','sql_error_number','retry_delay_seconds'])
        if type(attempt['attempt']) is not int or attempt['attempt']!=index or attempt['status'] not in ('FAILED','SUCCEEDED'):
            raise ValueError('Invalid connection attempt state')
        if attempt['stage'] not in (None,'connect','query','unknown') or attempt['retry_delay_seconds'] not in (0,10,20):
            raise ValueError('Invalid connection stage')
        if attempt['sql_error_number'] is not None and type(attempt['sql_error_number']) is not int:raise ValueError('Invalid SQL error number')
        for key in ('started_at','finished_at'):
            if not isinstance(attempt[key],str) or len(attempt[key])>40:raise ValueError('Invalid connection timestamp')
            datetime.fromisoformat(attempt[key])
    return value


def build(store, plan, config):
    fields(plan, ['model_id', 'revision', 'context_id', 'object_id', 'operation', 'column_id', 'filters'] +
           [k for k in ('freshness_policy_id','comparison_mapping_id') if k in plan])
    if 'freshness_policy_id' in plan and plan['operation'] != 'watermark_age_microseconds':
        raise ValueError('Freshness policy requires watermark operation')
    model = store.get(plan['model_id'])
    if type(plan['revision']) is not int or model['revision'] != plan['revision'] or model['context_id'] != plan['context_id']:
        raise Conflict('Stale source plan')
    objects, columns = snapshot(store, model, config)
    if not isinstance(plan['object_id'], str) or plan['object_id'] not in objects:
        raise ValueError('Unknown or ineligible SQL object')
    obj = objects[plan['object_id']]
    def column(identity):
        if not isinstance(identity, str) or identity not in columns or columns[identity]['parent_id'] != obj['id']:
            raise ValueError('Column belongs to another object')
        if columns[identity]['metadata'].get('computed_definition'):
            raise ValueError('Computed-column execution is unsupported')
        return columns[identity]
    if plan['operation'] == 'count_rows' and plan['column_id'] is None:
        aggregate = 'COUNT_BIG(*)'; nonblank = 'COUNT_BIG(*)'
    elif plan['operation'] == 'sum':
        col = column(plan['column_id']); meta = col['metadata']
        if meta['data_type'] not in ('tinyint', 'smallint', 'int', 'bigint', 'decimal', 'numeric', 'money', 'smallmoney'):
            raise ValueError('Unsupported exact aggregate type')
        scale = meta['scale']
        if type(scale) is not int or not 0 <= scale <= 18:
            raise ValueError('Unsupported aggregate scale')
        ref = quote(meta['name'])
        aggregate = f'SUM(CAST({ref} AS decimal(38,{scale})))'; nonblank = 'COUNT_BIG(' + ref + ')'
    elif plan['operation'] == 'watermark_age_microseconds':
        col = column(plan['column_id']); meta = col['metadata']
        if meta['data_type'] != 'datetime2':
            raise ValueError('Watermark requires datetime2 with reviewed UTC meaning')
        ref = quote(meta['name'])
        aggregate = 'DATEDIFF_BIG(microsecond,MAX(' + ref + '),SYSUTCDATETIME())'
        nonblank = 'COUNT_BIG(' + ref + ')'
    else:
        raise ValueError('Unsupported aggregate operation')
    filters = plan['filters']
    if not isinstance(filters, list) or not 1 <= len(filters) <= 8:
        raise ValueError('Explicit bounded source filters required')
    predicates = []; parameters = []; used = set()
    for spec in filters:
        fields(spec, ['column_id', 'values'] + (['operator'] if 'operator' in spec else []))
        col = column(spec['column_id']); meta = col['metadata']
        if col['id'] in used:raise ValueError('Duplicate source filter')
        if 'operator' in spec:
            from .source_scope import compile_filter
            predicate, bound = compile_filter(spec, meta, quote(meta['name']), len(parameters))
            used.add(col['id']);predicates.append(predicate);parameters.extend(bound)
            continue
        if col['id'] in used or meta['data_type'] not in ('varchar', 'nvarchar', 'char', 'nchar'):
            raise ValueError('Only unique string-column source filters supported')
        used.add(col['id']); values = spec['values']
        if not isinstance(values, list) or not 1 <= len(values) <= 50:
            raise ValueError('Source value budget exceeded')
        names = []
        for value in values:
            if not isinstance(value, str) or len(value.encode('utf-16-le')) > 400 or any(ord(c) < 32 for c in value):
                raise ValueError('Invalid source filter value')
            name = '@p' + str(len(parameters)); names.append(name)
            parameters.append({'name': name, 'value': value})
        predicates.append(quote(meta['name']) + ' IN (' + ','.join(names) + ')')
    meta = obj['metadata']
    query = ('SELECT ' + aggregate + ' AS value,COUNT_BIG(*) AS row_count,' + nonblank + ' AS nonblank_count FROM ' +
             quote(meta['schema_name']) + '.' + quote(meta['name']) + ' WHERE ' + ' AND '.join(predicates) + ' OPTION (MAXDOP 1)')
    request = {'version': 'source-aggregate-v1', 'query': query, 'parameters': parameters,
            'object_sql':quote(meta['schema_name'])+'.'+quote(meta['name']), 'predicate_sql':' AND '.join(predicates),
            'model_id': model['id'], 'context_id': model['context_id'], 'context_hash': digest(model['context']),
            'scan_id': model['context']['scan_id'], 'scope_hash': digest(plan),
            'object_id': obj['id'], 'object_hash': obj['hash'],
            'catalog_hash': digest([objects, columns]), 'connection_hash': digest(config['sql'])}
    if any('operator' in f for f in filters):
        from .source_scope import VERSION
        request['filter_scope_version'] = VERSION
    if 'comparison_mapping_id' in plan:
        from .source_bindings import validate_plan
        request['reviewed_mapping'] = validate_plan(store, plan, columns)
    if plan['operation'] == 'watermark_age_microseconds':
        from .freshness import policy_for_plan
        request['freshness_policy'] = policy_for_plan(store, plan)
        request['watermark_semantics'] = 'MAX_DATETIME2_ASSUMED_UTC_MICROSECOND_BOUNDARIES_AT_SQL_READ'
        from .freshness import validate_binding
        validate_binding(request)
    return request


def run(store, plan, config, execute, *, receipt_id=None):
    request = build(store, plan, config); identity = receipt_id or str(uuid4())
    if receipt_id is not None:
        from uuid import UUID
        if str(UUID(receipt_id)) != receipt_id:raise ValueError('Invalid reserved receipt ID')
    with store.connect() as db:
        db.execute('CREATE TABLE IF NOT EXISTS source_diagnostics(id TEXT PRIMARY KEY,model_id TEXT,created TEXT,status TEXT,request TEXT,result TEXT)')
        db.execute('INSERT INTO source_diagnostics VALUES(?,?,?,?,?,NULL)',
                   (identity, plan['model_id'], datetime.now(timezone.utc).isoformat(), 'RUNNING', encoded({'plan': plan, **request})))
    attempts=None
    try:
        if build(store, plan, config) != request:raise Conflict('Source context changed')
        result = dict(execute(request))
        attempts=connection_attempts(result.pop('connection_attempts',None))
        fields(result, ['value', 'row_count', 'nonblank_count'])
        from decimal import Decimal
        for key, value in result.items():
            if key == 'value' and value is None:continue
            if not isinstance(value, str) or not re.fullmatch(r'-?[0-9]{1,38}(?:\.[0-9]{1,18})?', value):
                raise ValueError('Invalid source result')
        count = Decimal(result['row_count']); nonblank = Decimal(result['nonblank_count'])
        if count < 0 or count != int(count) or not 0 <= nonblank <= count or nonblank != int(nonblank):
            raise ValueError('Inconsistent counts')
        if plan['operation'] == 'count_rows' and (result['value'] is None or Decimal(result['value']) != count):
            raise ValueError('Count differs')
        if plan['operation'] in ('sum', 'watermark_age_microseconds') and (result['value'] is None) != (nonblank == 0):
            raise ValueError('Sum nullability differs')
        if plan['operation'] == 'watermark_age_microseconds' and result['value'] is not None:
            age = Decimal(result['value'])
            if age != int(age) or abs(age) > 315537897600000000:
                raise ValueError('Invalid datetime2 watermark age')
        if build(store, plan, config) != request:raise Conflict('Source context changed during read')
        result = {k: {'type': 'blank' if v is None else 'decimal', 'value': v} for k, v in result.items()}
        if plan['operation'] == 'watermark_age_microseconds':
            from .freshness import assess
            result['freshness'] = assess(request, result)
        status = 'COMPLETED'
    except Exception as exc:
        attempts=None
        try:attempts=connection_attempts(getattr(exc,'connection_attempts',None))
        except (ValueError,TypeError):pass
        uncertain = isinstance(exc, (TimeoutError, subprocess.TimeoutExpired)) or getattr(exc, 'error_number', None) == -2
        status = 'HELD' if isinstance(exc, Conflict) else 'INTERRUPTED' if uncertain else 'FAILED'
        result = {'error_type': type(exc).__name__}
        if type(getattr(exc, 'error_number', None)) is int:
            result['error_number'] = exc.error_number
        if getattr(exc, 'error_kind', None) in ('SqlException', 'InvalidOperationException', 'MethodException', 'ArgumentException', 'TransportError'):
            result['error_kind'] = exc.error_kind
    result.update(snapshot_comparable=False, measure_equivalence_verified=False, root_cause_verified=False)
    if attempts is not None:result['connection_attempts']=attempts
    with store.connect() as db:
        db.execute('UPDATE source_diagnostics SET status=?,result=? WHERE id=?', (status, encoded(result), identity))
    return {'id': identity, 'status': status, 'request_hash': digest(request), 'result': result}


def evidence(store, model_id, receipt_id=None):
    model = store.get(model_id)
    with store.connect() as db:
        exists = db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='source_diagnostics'").fetchone()
        if receipt_id is None:
            rows = db.execute('SELECT id,created,status FROM source_diagnostics WHERE model_id=? ORDER BY created DESC,id DESC LIMIT 100',
                              (model_id,)).fetchall() if exists else []
            return [{'id': r[0], 'created': r[1], 'status': r[2]} for r in rows]
        row = db.execute('SELECT created,status,request,result FROM source_diagnostics WHERE model_id=? AND id=?',
                         (model_id, receipt_id)).fetchone() if exists else None
    if row is None:raise KeyError('Source receipt not found')
    request = json.loads(row[2])
    result = json.loads(row[3]) if row[3] else None
    mapping_current = None
    if request.get('reviewed_mapping'):
        mapping_current = False
        from .comparisons import mapping
        try:
            review=mapping(store,model_id,request['reviewed_mapping']['id'])
            mapping_current=(review['revocation'] is None and review['hash']==request['reviewed_mapping']['hash']
                             and model['enabled'] and request['context_hash']==digest(model['context'])
                             and request['plan']['revision']==model['revision'])
        except (KeyError,ValueError):pass
    policy_current = None
    if result and result.get('freshness'):
        policy_current = False
        policy_id = result['freshness'].get('policy_id')
        if policy_id:
            from .freshness import read as read_policy
            try:
                policy = read_policy(store, model_id, policy_id)
                policy_current = (policy['revocation'] is None and policy['body_hash'] == result['freshness']['policy_hash']
                                  and model['enabled'] and request['context_hash'] == digest(model['context'])
                                  and request['plan']['revision'] == model['revision'])
            except (KeyError, ValueError):
                pass
    return {'id': receipt_id, 'created': row[0], 'status': row[1], 'request': request,
            'result': result, 'freshness_policy_current': policy_current, 'reviewed_mapping_current':mapping_current,
            'local_context_current': bool(model['enabled'] and request['context_id'] == model['context_id']
                                          and request['context_hash'] == digest(model['context'])
                                          and request['plan']['revision'] == model['revision']),
            'limitation': 'Historical source observation only; remote schema, data version and measure equivalence are unverified.'}
