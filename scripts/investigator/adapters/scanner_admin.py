"""Bounded scanner-only admin metadata capture; it earns no graph edges itself."""
import time
from uuid import UUID
from .scanner_identity import require_job
from .metadata_error import MetadataUnavailable,safe_failure
from ..estate_graph_contract import canonical

ENDPOINT='admin/workspaces/getInfo?lineage=true&datasourceDetails=true&datasetSchema=true&datasetExpressions=true'


def collect(config,http,sink,*,sleep=time.sleep):
    if config.get('admin_metadata')is not True:return {'status':'NOT_REQUESTED','requests':0,'receipts':[]}
    require_job(config['authentication'],[config['workspace']])
    receipts=[];requests=0;waited=0
    def call(endpoint,method='get',body=None):
        nonlocal requests
        requests+=1
        request={'endpoint':endpoint,'method':method.upper(),'audience':'powerbi','body':body}
        try:response=http(endpoint,method=method,audience='powerbi',body=body)
        except Exception as error:
            receipts.append(sink(canonical({'request':request,'failure':safe_failure(error)}).encode()))
            raise
        retained={'request':request,'response':{'status_code':response['status_code'],'text':response.get('text')}}
        receipts.append(sink(canonical(retained).encode()))
        if response['status_code']not in (200,202):raise MetadataUnavailable(response['status_code'],response.get('text'))
        return response['text']
    def summary(status,**extra):
        return {'status':status,'requests':requests,'wait_seconds':waited,'receipts':receipts,
            'graph_evidence_admitted':False,**extra}
    try:
        first=call(ENDPOINT,'post',{'workspaces':[config['workspace']]})
        scan=str(UUID(first['id']))
        for index in range(8):
            status=call('admin/workspaces/scanStatus/'+scan)
            if str(UUID(status['id']))!=scan:raise ValueError('SCANNER_ADMIN_SCAN_ID_DIFFERS')
            if status.get('status')=='Succeeded':
                result=call('admin/workspaces/scanResult/'+scan)
                workspaces=result.get('workspaces')
                if (not isinstance(workspaces,list)or len(workspaces)!=1
                        or workspaces[0].get('id')!=config['workspace']):
                    return summary('UNKNOWN',reason='Admin scan returned missing or different workspace evidence.')
                return summary('COLLECTED',scan_id=scan,workspace=config['workspace'])
            if status.get('status')not in ('NotStarted','Running'):
                return summary('UNKNOWN',scan_id=scan,reason='Admin scan did not succeed; exact native status retained.')
            if index<7:sleep(2);waited+=2
        return summary('UNKNOWN',scan_id=scan,reason='Admin scan still pending after eight bounded status reads.')
    except Exception as error:
        from ..live_gateway import GatewayDenied
        from ..usage_governance import UsageHold
        from ..shared_state import StateConflict
        if isinstance(error,(GatewayDenied,UsageHold,StateConflict)) or str(error)=='GRAPH_PHYSICAL_REQUEST_CAP':raise
        return summary('UNKNOWN',failure=safe_failure(error))
