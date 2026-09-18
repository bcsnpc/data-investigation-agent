"""Transport-observed principal binding, not effective report/RLS or causal proof."""
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID
from .onboarding import digest, fields

KEY = '_native_execution'
VERSION = 'native-reader-execution-v1'


def canonical(value):
    # Preserve decimal precision across the subprocess JSON boundary.
    if value is None or isinstance(value, (str, bool)):
        return value
    if isinstance(value, (int, Decimal)):
        number = Decimal(value)
        if not number.is_finite():
            raise ValueError('Non-finite native response')
        return {'number': str(number)}
    if isinstance(value, list):
        return {'array': [canonical(v) for v in value]}
    if isinstance(value, dict) and all(isinstance(k, str) for k in value):
        return {'object': {k: canonical(v) for k, v in value.items()}}
    raise ValueError('Unsupported native response')


def profile(value):
    scope='workspace_ids' if 'workspace_ids' in value else 'model_ids'
    fields(value, ['mode', 'tenant_id', 'account', 'principal_id', scope])
    if value['mode'] != 'isolated_reader':
        raise ValueError('Unsupported native reader mode')
    for key in ('tenant_id', 'principal_id'):
        if str(UUID(value[key])) != value[key]:
            raise ValueError('Expected canonical principal identifiers')
    account = value['account']
    if (not isinstance(account, str) or not 3 <= len(account) <= 254 or account.count('@') != 1
            or any(c.isspace() or ord(c) < 32 for c in account)):
        raise ValueError('Expected reader account')
    models = value[scope]
    if (not isinstance(models, list) or not 1 <= len(models) <= 50
            or any(not isinstance(m, str) or str(UUID(m)) != m for m in models)
            or len(set(models)) != len(models)):
        raise ValueError('Expected bounded native model allowlist')
    return value


def allows(reader, workspace, model):
    profile(reader)
    try:
        if str(UUID(model)) != model or str(UUID(workspace)) != workspace:return False
    except (ValueError, TypeError, AttributeError):return False
    return workspace in reader['workspace_ids'] if 'workspace_ids' in reader else model in reader['model_ids']


def make(response, request, reader):
    profile(reader)
    if KEY in response or not allows(reader,request['workspace'],request['native_model_id']):
        raise ValueError('Unexpected native response or target')
    return {'version': VERSION, 'mode': reader['mode'], 'tenant_id': reader['tenant_id'],
            'principal_id': reader['principal_id'], 'account': reader['account'],
            'workspace_id': request['workspace'], 'model_id': request['native_model_id'],
            'query_hash': digest(request['query']), 'response_hash': digest(canonical(response)),
            'captured_at': datetime.now(timezone.utc).isoformat()}


def observed(response, request):
    if KEY not in response:
        return None  # Legacy/injected transports do not acquire a fabricated identity.
    value = response[KEY]
    fields(value, ['version', 'mode', 'tenant_id', 'principal_id', 'account', 'workspace_id',
                   'model_id', 'query_hash', 'response_hash', 'captured_at'])
    profile({k: value[k] for k in ('mode', 'tenant_id', 'principal_id', 'account')} | {'model_ids': [value['model_id']]})
    if (value['version'] != VERSION or value['workspace_id'] != request['workspace']
            or value['model_id'] != request['native_model_id'] or value['query_hash'] != digest(request['query'])
            or value['response_hash'] != digest(canonical({k: v for k, v in response.items() if k != KEY}))):
        raise ValueError('Native identity binding differs')
    if datetime.fromisoformat(value['captured_at']).tzinfo is None:
        raise ValueError('Identity capture timestamp needs timezone')
    return dict(value, provenance='LOCAL_TRANSPORT_OBSERVATION', effective_identity_verified=False,
                limitation='Token principal used for this query; not report viewer, RLS equivalence, permissions stability or shared-generation proof.')


def require(response, request, reader):
    profile(reader)
    if not allows(reader,request['workspace'],request['native_model_id']):
        raise ValueError('Native model is outside reader allowlist')
    value = observed(response, request)
    if value is None or any(value[k] != reader[k] for k in ('mode', 'tenant_id', 'principal_id', 'account')):
        raise ValueError('Configured native reader evidence missing or different')
    return response


def guarded(config, request, execute):
    """Apply the same boundary to injected runtime transports and worker transports."""
    reader = config.get('fabric', {}).get('native_reader')
    if reader is None:
        if request.get('requires_native_reader'):raise ValueError('Discovered execution requires a read-only reader')
        return execute(request)
    profile(reader)
    if request['workspace'] != config['fabric']['workspace_id'] or not allows(reader,request['workspace'],request['native_model_id']):
        raise ValueError('Native reader target differs')
    return require(execute(request), request, reader)
