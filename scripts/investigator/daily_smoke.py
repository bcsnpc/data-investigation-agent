"""Daily health control on existing worker; no estate writes or new resource.

The registry calls handler(plan, context); all endpoints and identity references
are deployment-owned configuration, never model tool arguments.
"""
from datetime import datetime, timezone
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

CRON = '0 6 * * *'


def schedule_plan(*, resource_id, image, platform_monthly_usd, smoke_monthly_usd,demo_earned=False):
    # Prices are an explicit dated operator estimate, never guessed in code.
    from decimal import Decimal
    base, extra = Decimal(str(platform_monthly_usd)), Decimal(str(smoke_monthly_usd))
    from .adapters.runner_deployment import existing_job
    if not existing_job(resource_id) or '@sha256:' not in image:
        raise ValueError('EXISTING_SMOKE_JOB_AND_PINNED_IMAGE_REQUIRED')
    if base < 0 or extra < 0 or base + extra > 20:
        raise ValueError('SMOKE_EXCEEDS_PLATFORM_MONTHLY_BUDGET')
    if type(demo_earned)is not bool:raise ValueError('DAILY_SMOKE_DEMO_EARNED_FLAG')
    return {'resource_id': resource_id, 'image': image, 'cron_expression': CRON,
            'timezone': 'UTC', 'replica_timeout_seconds': 3600 if demo_earned else 1800, 'parallelism': 1,
            'completion_count': 1, 'replica_retry_limit': 0,
            'monthly_platform_estimate_usd': str(base + extra),
            'marginal_smoke_estimate_usd': str(extra), 'new_resources': []}


def validate_gold_payload(payload):
    """Health means one ordinary bounded value read, never a catalog control."""
    if not isinstance(payload,dict) or payload.get('require_read_only')is not True or payload.get('control_mode'):
        raise ValueError('SMOKE_GOLD_DATA_QUERY_REQUIRED')
    from .adapters.binding_catalog import compiled_control_objects
    from .adapters.graph_sql_changes import compiled_control_objects as graph_controls
    if compiled_control_objects(payload)is not None or graph_controls(payload)is not None:
        raise ValueError('SMOKE_GOLD_DATA_QUERY_REQUIRED')
    from .live_gateway import validate_sql,_object
    try:
        objects={_object(value)for value in payload['read_only_objects']}
        if not objects or any(schema in ('sys','information_schema')for schema,_ in objects):raise ValueError('metadata object')
        validate_sql(payload['query'],objects)
    except Exception:raise ValueError('SMOKE_GOLD_DATA_QUERY_REQUIRED')from None
    return payload


def _gold_read(payload):
    validate_gold_payload(payload)
    from .physical_reads import run
    child = run([sys.executable, str(Path(__file__).resolve().parents[1] / 'managed_sql_worker.py')],
                input=json.dumps(payload), timeout=240, fallback=subprocess.run,
                capture_output=True, text=True, encoding='utf8')
    if child.returncode:
        raise RuntimeError('SMOKE_GOLD_READ_FAILED')
    value = json.loads(child.stdout)
    if value.get('read_only_verified') is not True or not value.get('execution_identity'):
        raise RuntimeError('SMOKE_GOLD_ATTESTATION_MISSING')
    return value


def _blob_roundtrip(config, body):
    from .adapters.blob_artifacts import BlobObjects, bound_credential
    from .artifact_store import Files
    from .live_gateway import current
    objects = BlobObjects(config['account_url'], 'captures', bound_credential(config['identity']),
                          channel=config['channel'], gateway=current())
    files = Files(objects)
    with tempfile.TemporaryDirectory() as folder:
        source = Path(folder) / 'health.json'
        source.write_bytes(body)
        identity = files.capture(source)
        files.restore(identity['sha256'], Path(folder) / 'readback.json')
        if (Path(folder) / 'readback.json').read_bytes() != body:
            raise ValueError('SMOKE_BLOB_READBACK_DIFFERS')
    return {'status': 'PASS', 'sha256': hashlib.sha256(body).hexdigest(), 'file_identity': identity}


def capture_roundtrip(context,body):
    """Use this execution's approved immutable recorder, never broad CAS rights."""
    ref=context.record('blob-health',json.loads(body))
    if context.readback(ref)!=body:raise ValueError('SMOKE_BLOB_READBACK_DIFFERS')
    return {'status':'PASS','sha256':hashlib.sha256(body).hexdigest(),
            'record':ref,'surface':'RUN_BOUND_OUTER_CAPTURE'}


def ledger_demo_matches(bundle,expected):
    """New engine, same earned operands and named producer; no label-only pass."""
    from decimal import Decimal,InvalidOperation
    if (not isinstance(expected,dict) or set(expected)!={'verdict','boundary','values','native_classification'}
            or expected['verdict']!='as designed' or not isinstance(expected['boundary'],dict)
            or expected['native_classification']!='TRANSFORMATION_LOGIC'
            or set(expected['boundary'])!={'downstream','upstream'}
            or set(expected['values'])!={expected['boundary']['downstream'],expected['boundary']['upstream']}):
        raise ValueError('SMOKE_LEDGER_EXPECTATION_SHAPE')
    if bundle.get('verdict')!=expected['verdict'] or bundle.get('status')=='blocked' or not all(bundle.get('outputs',{}).get(k)for k in ('business','technical')):return False
    checks=[row for row in bundle.get('evidence',{}).values()if row.get('kind')=='DESIGN_CHECK'
        and set(row.get('subjects',[]))==set(expected['values']) and row['value'].get('checked')is True
        and row['value'].get('business_correctness_claim')is False
        and row['value'].get('native_assessment',{}).get('classification')==expected['native_classification']]
    if not checks:return False
    reads=[row['value']for row in bundle.get('evidence',{}).values()if row.get('kind')=='READ']
    try:
        return all(any(row.get('subject')==node and row.get('state')=='VALUE' and row.get('read_only_verified')is True and row.get('route_admitted')is True
            and Decimal(str(row.get('value')))==Decimal(str(value))for row in reads)for node,value in expected['values'].items())
    except (InvalidOperation,ValueError,TypeError):return False


def monthly_budget_advisory(access, state):
    """Resolve only the calendar reminder using an actual platform ledger read.

    Keep the original access table intact. No account is created or altered,
    and a missing account or any other incomplete probe stays incomplete.
    """
    result = {'status': access['status'], 'result': access}
    rows = access.get('rows', [])
    reminders = [r for r in rows if r.get('id') == 'next-month-budget']
    if (access['status'] != 'INCOMPLETE' or len(reminders) != 1
            or reminders[0].get('status') != 'NOT_TESTABLE'
            or reminders[0].get('warning') is not True
            or not all(r.get('status') == 'PASS' for r in rows if r not in reminders)):
        return result
    period = reminders[0].get('resource', '')
    if not re.fullmatch(r'\d{4}-(?:0[1-9]|1[0-2])', period):
        return result
    account = 'model-microdollars:' + period
    try:
        observed = state.snapshot(account)
    except KeyError:
        return result
    if observed.get('identity') == account and observed.get('unit') == 'MICRODOLLARS':
        result.update(status='PASS', resolved_advisories=[{
            'id': 'next-month-budget', 'account': account,
            'reason': 'EXISTING_ACCOUNT_READ_FROM_SHARED_LEDGER',
            'account_exists': True, 'operation': 'READ_ONLY_SNAPSHOT',
            'account_created': False}])
    return result


def run_smoke(config, context, *, state=None, sign_in=None, gold_read=None, blob_roundtrip=None, demo=None):
    required = {'version', 'run_id', 'reader_authentication', 'gold_payload', 'platform_blob', 'demo_earned'}
    if not isinstance(config, dict) or not required <= set(config) <= required | {'access_check', 'demo_expected_classification','demo_ledger_expectation'} or config['version'] != 1:
        raise ValueError('DAILY_SMOKE_CONFIGURATION')
    if not isinstance(config['run_id'], str) or not re.fullmatch(r'[A-Za-z0-9_.:-]{1,100}', config['run_id']):
        raise ValueError('DAILY_SMOKE_RUN_ID')
    if type(config['demo_earned']) is not bool:
        raise ValueError('DAILY_SMOKE_DEMO_EARNED_FLAG')
    if config['gold_payload'].get('authentication') != config['reader_authentication']:
        raise ValueError('SMOKE_GOLD_IDENTITY_DIFFERS')
    validate_gold_payload(config['gold_payload'])
    if config['demo_earned'] and demo is None:
        raise ValueError('EARNED_SMOKE_DEMO_HANDLER_REQUIRED')
    from .shared_state import configured_state
    from .adapters.vault_user_cache import provider
    state = state or configured_state()
    if state is None:
        raise ValueError('SMOKE_PLATFORM_STATE_REQUIRED')
    checks = {}
    def step(name, fn):
        try:
            result = context.step(name, fn)
            checks[name] = {'status': 'PASS', 'result': result}
        except Exception as exc:
            # Driver/auth errors can contain credentials: record the class only.
            checks[name] = {'status': 'FAIL', 'error_type': type(exc).__name__}
    from .access_check import configured as check_access
    access = context.step('check-access', lambda: check_access(config.get('access_check')))
    checks['check_access'] = {'status': access['status'], 'result': access}
    if any(row.get('id') == 'next-month-budget' for row in access.get('rows', [])):
        checks['check_access'] = context.step('next-month-budget-advisory',
                                            lambda: monthly_budget_advisory(access, state))
    def authenticate():
        tokens = provider(config['reader_authentication'])
        tokens.get_token('https://database.windows.net/.default')
        return {'status': 'PASS', 'principal_id': config['reader_authentication']['principal_id']}
    step('sign_in', sign_in or authenticate)
    step('gold_read', lambda: (gold_read or _gold_read)(config['gold_payload']))
    body = {'kind': 'DAILY_SMOKE', 'run_id': config['run_id'], 'challenge': hashlib.sha256(config['run_id'].encode()).hexdigest()}
    def postgres():
        # The tool platform's namespace only. This never writes to an estate DB.
        try:
            prior = state.get('daily_smoke', config['run_id'])
        except KeyError:
            prior = None
        state.put('daily_smoke', config['run_id'], body, revision=None if prior is None else prior['revision'])
        if state.get('daily_smoke', config['run_id'])['body'] != body:
            raise ValueError('SMOKE_POSTGRES_READBACK_DIFFERS')
        return {'status': 'PASS', 'namespace': 'daily_smoke', 'run_id': config['run_id']}
    step('postgres_write_read', postgres)
    raw = json.dumps(body, sort_keys=True, separators=(',', ':')).encode()
    step('blob_write_read', lambda: (blob_roundtrip or _blob_roundtrip)(config['platform_blob'], raw))
    if config['demo_earned']:
        step('family_a_demo', demo)
        # A delivered refusal is a legitimate investigation result, but cannot
        # prove an operator's earned demonstration still works. Preserve it.
        check = checks['family_a_demo']
        if check['status']=='PASS' and 'demo_ledger_expectation'in config:
            result=check['result'];expected=config['demo_ledger_expectation']
            check.update(expected_verdict=expected['verdict'],observed_verdict=result.get('verdict'))
            if not ledger_demo_matches(result,expected):check.update(status='FAIL',reason='SMOKE_LEDGER_BOUNDARY_EXPECTATION_NOT_MET')
        elif check['status'] == 'PASS':
            result = check['result']
            ticket = result.get('demo', {}).get('ticket', {}) if isinstance(result, dict) else {}
            actual = ticket.get('findings', {}).get('classification')
            expected = config.get('demo_expected_classification')
            check['expected_classification'] = expected
            check['observed_classification'] = actual
            if not isinstance(expected, str) or not expected:
                check.update(status='FAIL', reason='SMOKE_DEMO_EXPECTATION_MISSING')
            elif ticket.get('state') != 'FINDINGS_SHARED' or actual != expected:
                check.update(status='FAIL', reason='SMOKE_DEMO_EXPECTATION_NOT_MET')
    # An untestable legacy binding is reported, never represented as a pass.
    status = 'FAIL' if any(value['status'] == 'FAIL' for value in checks.values()) else ('PASS' if all(value['status'] == 'PASS' for value in checks.values()) else 'INCOMPLETE')
    return {'kind': 'DAILY_SMOKE', 'status': status, 'run_id': config['run_id'],
            'recorded_at': datetime.now(timezone.utc).isoformat(), 'checks': checks,
            'record': f"{config['run_id']} DAILY_SMOKE {status}", 'demo_included': config['demo_earned'],
            'budget_line': 'collectors', 'investigation_reads': 0}


def handler(plan, context):
    return run_smoke(plan['target'], context)
