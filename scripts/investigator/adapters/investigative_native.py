"""Existing SQL/DAX readers for AI-authored, parser-validated requests.

Routes/configurations are installation-owned. The model supplies only a layer
ID and query. There is no credential, owner fallback or control-plane operation
in this port. Existing gateway and physical-read instrumentation still apply.
"""
from copy import deepcopy
import json
from decimal import Decimal
from ..live_gateway import GatewayDenied
from ..round23_calendar import require_live_window


def values(value):
    """JSON-safe exact decimals, preserving the native rows/columns shape."""
    if isinstance(value,Decimal):
        if not value.is_finite():raise ValueError('NONFINITE_NATIVE_DECIMAL')
        return str(value)
    if isinstance(value,list):return [values(v) for v in value]
    if isinstance(value,dict):return {k:values(v) for k,v in value.items()}
    return value


class NativeQueries:
    def __init__(self,routes,*,source=None,fabric=None,dax=None,offline=False):
        if not isinstance(routes,dict) or not routes:raise ValueError('NATIVE_QUERY_ROUTES_REQUIRED')
        self.routes=deepcopy(routes);self.source,self.fabric,self.dax=source,fabric,dax
        if offline and any(port is None for port in (source,fabric,dax)):
            raise ValueError('OFFLINE_NATIVE_PORTS_MUST_ALL_BE_FIXTURES')
        self.offline=offline

    def __call__(self,layer,bound,*,timeout_seconds):
        if not self.offline:require_live_window()
        if layer not in self.routes:raise GatewayDenied('QUERY_ROUTE_OUTSIDE_ADMITTED_PATH')
        route=self.routes[layer];kind=route['kind'];config=deepcopy(route['config'])
        if not set(bound['asset_ids'])<=set(route['asset_ids']):raise GatewayDenied('QUERY_OBJECT_OUTSIDE_NATIVE_ROUTE')
        if type(timeout_seconds) is not int or not 1<=timeout_seconds<=30:
            raise ValueError('INSTALLED_STATEMENT_TIMEOUT_AT_MOST_30_SECONDS')
        request=deepcopy(bound)
        request['response_mode']='records'
        if kind in ('SOURCE_SQL','FABRIC_SQL'):
            # Installed SQL workers enforce a 30-second statement deadline and
            # their existing session/object permission guards before the SELECT.
            if timeout_seconds!=30:raise ValueError('INSTALLED_SQL_STATEMENT_TIMEOUT_IS_30_SECONDS')
            objects={a['id']:a for a in route['objects']}
            request['read_only_objects']=['['+objects[i]['metadata']['schema_name'].replace(']',']]')+'].['+
                objects[i]['metadata']['name'].replace(']',']]')+']' for i in bound['asset_ids']]
            request['require_read_only']=True
            if kind=='SOURCE_SQL':
                if self.source is None:
                    from run_source_diagnostic import transport
                    response=transport(config,request)
                else:response=self.source(config,request)
            else:
                if self.fabric is None:
                    from fabric_sql_surface import read
                    response=read(config,route['database'],request,attestation=False)
                else:response=self.fabric(config,route['database'],request,attestation=False)
            if response.get('read_only_verified') is not True:
                raise GatewayDenied('NATIVE_READ_ONLY_ENFORCEMENT_NOT_ESTABLISHED')
            if not isinstance(response.get('rows'),list):raise ValueError('NATIVE_SQL_ROWS_REQUIRED')
            return values(response)
        if kind!='DAX':raise ValueError('NATIVE_DIALECT_NOT_INSTALLED')
        from ..native_identity import allows
        reader=config['fabric'].get('native_reader')
        if reader is None or not allows(reader,route['workspace'],route['model']):
            raise GatewayDenied('ISOLATED_DAX_READER_REQUIRED_NO_OWNER_FALLBACK')
        request.update(workspace=route['workspace'],native_model_id=route['model'],requires_native_reader=True)
        execute=self.dax
        if execute is None:
            from run_native_diagnostic import execute
        raw=execute(request,config['fabric']['auth']['tenant_id'],reader,
                    authentication=config['fabric']['auth'],timeout_seconds=timeout_seconds)
        result=json.loads(raw,parse_float=Decimal) if isinstance(raw,str) else raw
        tables=result.get('results',[])
        if len(tables)!=1 or tables[0].get('error'):raise ValueError('NATIVE_DAX_RESULT_ERROR')
        tables=tables[0].get('tables',[])
        if len(tables)!=1 or not isinstance(tables[0].get('rows'),list):raise ValueError('NATIVE_DAX_ROWS_REQUIRED')
        return values({'rows':tables[0]['rows'],
                          'warnings':['attestation limited: the engine can’t self-report the calling principal; the token and connection were verified separately']})
