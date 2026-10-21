"""One bounded reader DAX authorization check, not an administrator data query."""
import hashlib
import json
import re
from pathlib import Path
from uuid import UUID


def run(plan, context):
    from investigator.estate_manifest import load
    from investigator.adapters.estate_installation import configuration
    from metadata_config import worker_configuration
    from investigator.native_identity import allows
    from investigator.live_gateway import validate_dax, GatewayDenied
    from investigator.shared_state import configured_state
    from run_native_diagnostic import execute, worker_failure
    from scan_estate_graph import Meter
    options=plan['options']
    if set(options)!={'request','request_sha256','budget'}:
        raise ValueError('DAX_AUTHORIZATION_OPTIONS_DIFFER')
    if not isinstance(options['request_sha256'],str) or not re.fullmatch('[a-f0-9]{64}',options['request_sha256']):
        raise ValueError('DAX_AUTHORIZATION_REQUEST_HASH_REQUIRED')
    raw=Path(options['request']).read_bytes()
    if len(raw)>128000 or hashlib.sha256(raw).hexdigest()!=options['request_sha256']:
        raise ValueError('DAX_AUTHORIZATION_REQUEST_BYTES_DIFFER')
    from investigator.planner_recording import _safe
    _safe(raw)
    request=json.loads(raw)
    manifest=load(plan['manifest']);config=configuration(manifest)
    projected=worker_configuration(config,request)
    fabric=projected['fabric'];reader=fabric['native_reader'];authentication=fabric['auth']
    if (reader['mode']!='federated_reader' or authentication['mode']!='federated_reader'
            or reader['tenant_id']!=authentication['tenant_id'] or reader['principal_id']!=authentication['principal_id']
            or request['workspace']!=fabric['workspace_id']
            or not allows(reader,request['workspace'],request['native_model_id'])):
        raise ValueError('DAX_AUTHORIZATION_FEDERATED_READER_REQUIRED')
    workspace=str(UUID(request['workspace']));model=str(UUID(request['native_model_id']))
    validate_dax(request['query'])
    url=f'https://api.powerbi.com/v1.0/myorg/groups/{workspace}/datasets/{model}/executeQueries'
    target={'method':'POST','url':url,'workspace':workspace,'model':model,
            'request_sha256':options['request_sha256'],'query_sha256':hashlib.sha256(request['query'].encode()).hexdigest()}
    context.record('native-authorization-target',target)
    state=configured_state()
    if state is None:raise ValueError('DAX_AUTHORIZATION_SHARED_BUDGET_REQUIRED')
    meter=Meter(state,options['budget'],4)
    observed=[]
    def identity(value):
        # Defense in depth at the persistence seam: the observer must not grow
        # into a token dumper if a future authenticator adds additional fields.
        if not isinstance(value,dict) or set(value)-{'aud','tid','oid','appid','azp'} or any(not isinstance(v,str) for v in value.values()):
            raise ValueError('DAX_AUTHORIZATION_CLAIMS_NOT_WHITELISTED')
        observed.append(dict(value));context.record('native-token-claims',dict(value))
    try:
        before=meter.usage.snapshot()
        def call():
            if meter.used>4:raise ValueError('DAX_AUTHORIZATION_PHYSICAL_CAP')
            return execute(request,authentication['tenant_id'],reader,authentication,identity_observer=identity)
        try:
            response=meter(call)
            result={'status':'SUCCEEDED','http_status':200,'response':response,'error':None}
        except GatewayDenied:
            raise  # A guard refusal is not a service authorization result.
        except Exception as error:
            # Preserve the existing bounded error grammar, not exception text
            # that might include authentication material or a full request.
            result={'status':'FAILED','response':None,'error':worker_failure(error)}
            result['http_status']=result['error'].get('http_status')
        result.update(target=target,actual_token_claims=observed,model_calls=0,
                      physical_requests=meter.used,before=before,after=meter.usage.snapshot(),
                      label='DAX_AUTHORIZATION_CHECK_ONLY',identity_or_permission_changed=False)
        context.record('native-authorization-result',result)
        return result
    finally:meter.close()
