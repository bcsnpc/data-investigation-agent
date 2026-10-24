"""Permission declarations are questions, never evidence of effective access.

Only the adapter performs live probes. Results retain the exact map row and
identity; unavailable authentication never falls back to an owner session.
"""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path

VERSION = 'dia-permission-map-v1'
STATUSES = frozenset({'PASS', 'FAIL', 'NOT_TESTABLE'})


def load(path):
    # JSON is a YAML 1.2 subset; avoid an optional YAML parser in the worker.
    value = json.loads(Path(path).read_text(encoding='utf-8-sig'))
    if (not isinstance(value, dict) or set(value) != {'version', 'identities', 'checks'}
            or value['version'] != VERSION or not isinstance(value['identities'], dict)
            or not isinstance(value['checks'], list)):
        raise ValueError('PERMISSION_MAP_SCHEMA')
    seen = set()
    for row in value['checks']:
        if (not isinstance(row, dict) or set(row) != {'id', 'identity', 'resource', 'action', 'scopes', 'probe'}
                or row['identity'] not in value['identities'] or row['id'] in seen
                or not all(isinstance(row[k], str) and row[k] for k in ('id', 'resource', 'action'))
                or not isinstance(row['scopes'], list) or not row['scopes']
                or not all(isinstance(s, str) and s for s in row['scopes'])
                or not isinstance(row['probe'], dict)):
            raise ValueError('PERMISSION_MAP_ROW')
        seen.add(row['id'])
    return value


def utc(value):
    result = datetime.fromisoformat(value.replace('Z', '+00:00')) if isinstance(value, str) else value
    if not isinstance(result, datetime) or result.tzinfo is None:
        raise ValueError('ACCESS_TIME_MUST_BE_AWARE')
    return result.astimezone(timezone.utc)


def expiry_checks(metadata, now):
    """Metadata is sanitized rotation output, not a secret or a grant proof."""
    now = utc(now)
    rows = []
    for item in metadata:
        key = item['credential_key_id']
        expires = utc(item['expires_at_utc'])
        expired, warning = expires <= now, expires <= now + timedelta(days=7)
        rows.append({'id': 'secret-expiry:' + key, 'identity': item.get('identity', 'investigator'),
                     'resource': key, 'action': 'credential expiry',
                     'status': 'FAIL' if expired else 'PASS', 'warning': warning,
                     'reason': 'SECRET_EXPIRED' if expired else ('SECRET_EXPIRES_WITHIN_7_DAYS' if warning else 'SECRET_NOT_EXPIRED'),
                     'expires_at_utc': expires.isoformat(), 'evidence_class': 'SANITIZED_EXPIRY_METADATA'})
    return rows


def check(mapping, *, bindings=None, scope=None, backend=None, now=None, availability_sink=None):
    from .adapters.access_probes import LiveProbes, NotTestable
    now = utc(now or datetime.now(timezone.utc))
    bindings = bindings or {}
    backend = backend or LiveProbes(bindings)
    rows = []
    for declaration in mapping['checks']:
        if scope is not None and '*' not in declaration['scopes'] and scope not in declaration['scopes']:
            continue
        row = {k: declaration[k] for k in ('id', 'identity', 'resource', 'action')}
        attempts=[]
        try:
            from .source_availability import call as source_call
            def probe():
                try:return backend.probe(declaration, mapping['identities'][declaration['identity']])
                except NotTestable:raise
            proof = source_call(probe,observe=attempts.append,clock=lambda:now.isoformat())
            # A callable that returns True, a declaration, or a token is not a probe.
            if (not isinstance(proof, dict) or proof.get('permission_observed') is not True
                    or proof.get('identity') != declaration['identity']
                    or proof.get('resource') != declaration['resource']
                    or not proof.get('receipt')):
                raise ValueError('ACCESS_PROBE_IDENTITY_OR_RECEIPT_MISSING')
            row.update(status='PASS', reason='LIVE_READ_SUCCEEDED', evidence=proof)
        except NotTestable as exc:
            attempts=[] # Missing configuration is not a source outage.
            row.update(status='NOT_TESTABLE', reason=str(exc))
        except Exception as exc:
            from .live_gateway import GatewayDenied
            if isinstance(exc, GatewayDenied):
                close = getattr(backend, 'close', None)
                if close: close()
                raise
            # Never serialize provider exceptions, tokens, SQL connection strings,
            # or raw Key Vault bodies into the table.
            from urllib.error import HTTPError
            reason = ('HTTP_' + str(exc.code)) if isinstance(exc, HTTPError) else getattr(exc, 'safe_reason', type(exc).__name__)
            row.update(status='FAIL', reason=reason)
        if attempts:
            row['availability']=attempts[-1]
            if availability_sink is not None:availability_sink(declaration,row['availability'],row.get('evidence'))
        rows.append(row)
    close = getattr(backend, 'close', None)
    if close: close()
    metadata = bindings.get('secret_metadata', [])
    rows.extend(expiry_checks(metadata, now))
    if not metadata and any(r['id'].endswith('-fixed-connection') for r in mapping['checks']):
        rows.append({'id':'secret-expiry-metadata', 'identity':'investigator', 'resource':'fixed connections',
                     'action':'credential expiry', 'status':'NOT_TESTABLE', 'warning':True,
                     'reason':'SECRET_EXPIRY_METADATA_UNAVAILABLE'})
    if now.day >= 25:
        next_month = (now.replace(day=28) + timedelta(days=4)).replace(day=1)
        # This is an owner action reminder, not evidence an account was provisioned.
        rows.append({'id': 'next-month-budget', 'identity': 'owner', 'resource': next_month.strftime('%Y-%m'),
                     'action': 'provision monthly budget account', 'status': 'NOT_TESTABLE', 'warning': True,
                     'reason': 'OWNER_MUST_CONFIRM_NEXT_MONTH_ACCOUNT; worker has no INSERT right'})
    return {'version': 1, 'scope': scope or 'ALL', 'checked_at': now.isoformat(), 'rows': rows,
            'counts': {s: sum(r['status'] == s for r in rows) for s in sorted(STATUSES)},
            'status': 'FAIL' if any(r['status'] == 'FAIL' for r in rows) else
                      ('INCOMPLETE' if any(r['status'] == 'NOT_TESTABLE' for r in rows) else 'PASS')}


def table(result):
    lines = ['CHECK | IDENTITY | RESOURCE | STATUS | REASON']
    for row in result['rows']:
        lines.append(' | '.join(str(row.get(k, '')).replace('\n', ' ') for k in ('id', 'identity', 'resource', 'status', 'reason')))
    return '\n'.join(lines)


def configured(spec, *, scope=None, backend=None, now=None, retain=None):
    if not spec:
        return {'version': 1, 'status': 'INCOMPLETE', 'scope': scope or 'ALL', 'counts': {'NOT_TESTABLE': 1},
                'rows': [{'id': 'permission-map', 'identity': 'unbound', 'resource': 'permission-map',
                          'action': 'access preflight', 'status': 'NOT_TESTABLE', 'reason': 'ACCESS_CHECK_NOT_CONFIGURED'}]}
    if not isinstance(spec, dict) or not {'map', 'bindings'} <= set(spec) <= {'map', 'bindings', 'scope'}:
        raise ValueError('ACCESS_CHECK_CONFIGURATION')
    try:
        bindings = json.loads(Path(spec['bindings']).read_text(encoding='utf-8-sig'))
        mapping = load(spec['map'])
    except (OSError, ValueError, TypeError):
        # No live read is attempted when deployment materialization is missing.
        # Build-phase runner retains this table as an admission warning.
        return {'version':1, 'status':'FAIL', 'scope':scope or spec.get('scope') or 'ALL',
                'counts':{'FAIL':1}, 'rows':[{'id':'permission-map', 'identity':'unbound',
                    'resource':'permission-map', 'action':'access preflight', 'status':'FAIL',
                    'reason':'ACCESS_CHECK_MAP_OR_BINDINGS_INVALID_OR_UNAVAILABLE'}]}
    sink=None
    if 'availability' in bindings:
        from .shared_state import configured_state,sha
        from .facts_ledger import FactLedger
        from .source_availability import fact as availability_fact
        declared=bindings['availability']
        if not isinstance(declared,dict) or set(declared)!={'estate','subjects'} or not isinstance(declared['subjects'],dict):
            raise ValueError('ACCESS_AVAILABILITY_BINDING')
        state=configured_state()
        if state is None:raise ValueError('ACCESS_AVAILABILITY_SHARED_LEDGER_REQUIRED')
        def sink(declaration,value,proof):
            subjects=declared['subjects'].get(declaration['id'],[])
            if not isinstance(subjects,list) or any(not isinstance(node,str) or not node for node in subjects):raise ValueError('ACCESS_AVAILABILITY_SUBJECTS')
            if not subjects:return
            receipt={'event':'ACCESS_AVAILABILITY','check_id':declaration['id'],'identity':declaration['identity'],
                'resource':declaration['resource'],'availability':value,'proof':proof}
            if retain is not None:ref=retain('source-availability',receipt);evidence=[ref['key']]
            else:
                identity=sha(receipt);state.put('source_availability_receipts',identity,receipt);evidence=['source_availability_receipts:'+identity]
            FactLedger(state).append(declared['estate'],[availability_fact(node,value,at=value['last_observed_at'],evidence=evidence,collector='dia-check-access')for node in subjects])
    return check(mapping, bindings=bindings, scope=scope or spec.get('scope'), backend=backend, now=now,availability_sink=sink)


def main(args):
    result = configured({'map': str(args.map), 'bindings': str(args.bindings)}, scope=args.scope)
    print(json.dumps(result, sort_keys=True) if args.json else table(result))
    return 1 if result['status'] == 'FAIL' else 0
