"""Optional metadata-only refresh receipt; no publisher or execution-reader fallback."""
import base64
import json
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from uuid import UUID
from fabric_sql_auth import cli,session_status

RESOURCE='https://analysis.windows.net/powerbi/api'


def read(config,model):
    fabric=config['fabric'];profile=fabric['refresh_timing_reader']
    tenant=fabric['auth']['tenant_id'];account=profile['account']
    provenance={'purpose':'OPTIONAL_REFRESH_TIMING_ONLY','account':account,
                'tenant':tenant,'profile':profile['profile'],'interface':'POWER_BI_REST',
                'execution_reader':False}
    result={'status':'UNAVAILABLE','identity_provenance':provenance}
    if session_status(tenant,account,profile['profile'])['status']!='READY':
        return dict(result,reason='Configured metadata identity is not signed in; no fallback.')
    token=cli(['account','get-access-token','--tenant',tenant,'--resource',RESOURCE,
               '--output','json','--only-show-errors'],profile['profile'])['accessToken']
    part=token.split('.')[1];claims=json.loads(base64.urlsafe_b64decode(part+'='*(-len(part)%4)))
    actual=claims.get('upn') or claims.get('preferred_username')
    if (claims.get('tid','').casefold()!=tenant.casefold() or claims.get('aud','').rstrip('/')!=RESOURCE
        or not isinstance(actual,str) or actual.casefold()!=account.casefold()):
        return dict(result,reason='Metadata token account, tenant or audience mismatch.')
    provenance['token_identity']=actual;provenance['object_id']=claims.get('oid')
    workspace=str(UUID(model['workspace']));identity=str(UUID(model['native_id']))
    if workspace!=fabric['workspace_id']:raise ValueError('Timing read leaves approved workspace')
    url=f'https://api.powerbi.com/v1.0/myorg/groups/{workspace}/datasets/{identity}/refreshes?$top=1'
    try:
        with urlopen(Request(url,headers={'Authorization':'Bearer '+token}),timeout=30) as response:
            body=json.loads(response.read(65537));request_id=response.headers.get('RequestId')
    except HTTPError as exc:return dict(result,http_status=exc.code,reason='Configured metadata identity was refused.')
    rows=body.get('value')
    if not isinstance(rows,list):return dict(result,reason='Refresh response did not contain history.')
    # Record service state and refresh type; neither is a proven explanation of
    # this quantity discrepancy, nor a deadline against which lateness is known.
    return dict(result,status='AVAILABLE',request_id=request_id,model_id=identity,
                history=[{k:r[k] for k in ('requestId','refreshType','startTime','endTime','status') if k in r}
                         for r in rows[:1]],causal_explanation_established=False)
