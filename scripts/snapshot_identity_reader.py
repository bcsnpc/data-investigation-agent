"""Optional separately authenticated metadata; never claims a query-bound snapshot."""
import base64,json,subprocess
from datetime import datetime,timezone
from uuid import uuid4
from metadata_config import ROOT
from fabric_sql_auth import cli,session_status


def read(config,model,probe,workspace_name,run=subprocess.run):
    fabric=config['fabric'];profile=fabric['snapshot_identity_reader'];tenant=fabric['auth']['tenant_id']
    provenance={'purpose':'OPTIONAL_SNAPSHOT_IDENTITY_ONLY','account':profile['account'],
                'profile':profile['profile'],'tenant':tenant,'execution_reader':False}
    result={'status':'UNAVAILABLE','identity_provenance':provenance,'binding':'METADATA_ONLY',
            'evidence_id':str(uuid4()),'quantity_receipt_id':probe.evidence['id'],
            'surface':dict(probe.execution_surface),'observed_at':datetime.now(timezone.utc).isoformat()}
    if model['workspace']!=fabric['workspace_id']:raise ValueError('Snapshot read leaves approved workspace')
    surface=probe.execution_surface;kind=surface['engine']
    if kind=='POWER_BI_DAX':
        if surface['connection']!=model['workspace'] or surface['object']!=model['native_id']:
            return dict(result,reason='SURFACE_SCOPE_MISMATCH')
        library=fabric.get('xmla_client',{}).get('library')
        if not workspace_name or not library:return dict(result,reason='XMLA_NOT_CONFIGURED')
        library=(ROOT/library).resolve()
        if (ROOT/'.local').resolve() not in library.parents:return dict(result,reason='INVALID_LIBRARY')
        resource='https://analysis.windows.net/powerbi/api'
        request={'kind':kind,'library':str(library),'workspace_name':workspace_name,'model_name':model['native_id']}
    elif kind=='FABRIC_SQL':
        server=fabric.get('sql_reader',{}).get('server')
        if not server or surface['connection']!='sql://'+server:return dict(result,reason='SURFACE_SCOPE_MISMATCH')
        resource='https://database.windows.net/'
        request={'kind':kind,'server':server,'database':surface['object']}
    else:return dict(result,reason='UNSUPPORTED_SNAPSHOT_SURFACE')
    if session_status(tenant,profile['account'],profile['profile'])['status']!='READY':
        return dict(result,reason='METADATA_IDENTITY_NOT_SIGNED_IN_NO_FALLBACK')
    token=cli(['account','get-access-token','--tenant',tenant,'--resource',resource,
               '--output','json','--only-show-errors'],profile['profile'])['accessToken']
    part=token.split('.')[1];claims=json.loads(base64.urlsafe_b64decode(part+'='*(-len(part)%4)))
    account=claims.get('upn') or claims.get('preferred_username')
    if (claims.get('tid','').casefold()!=tenant.casefold() or claims.get('aud','').rstrip('/')!=resource.rstrip('/')
            or not isinstance(account,str) or account.casefold()!=profile['account'].casefold()):
        return dict(result,reason='METADATA_TOKEN_IDENTITY_MISMATCH')
    provenance.update(token_identity=account,object_id=claims.get('oid'),interface=kind)
    proc=run(['powershell','-NoProfile','-NonInteractive','-File',str(ROOT/'infra/scripts/Read-SnapshotMetadata.ps1')],
             input=json.dumps(dict(request,access_token=token)),capture_output=True,text=True,encoding='utf-8',timeout=150)
    if len(proc.stdout.encode('utf-8'))>65536:return dict(result,reason='METADATA_RESPONSE_LIMIT')
    try:response=json.loads(proc.stdout)
    except (ValueError,TypeError):return dict(result,reason='INVALID_METADATA_RESPONSE')
    if not isinstance(response,dict):return dict(result,reason='INVALID_METADATA_RESPONSE')
    return dict(result,status='AVAILABLE' if response.get('status')=='SERVED' else 'UNAVAILABLE',
                metadata=response,reason='SEPARATE_METADATA_QUERY_NOT_BOUND_TO_QUANTITY')
