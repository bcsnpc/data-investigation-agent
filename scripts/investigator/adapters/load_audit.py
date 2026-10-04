"""Read the declared audit's own accounting; no recount or monitoring substitution."""
from .job_history import timestamp

# This is the audit writer's interface, not an application/domain schema.
COLUMNS = {'run_id':'nvarchar','pipeline_name':'nvarchar','status':'nvarchar',
           'rows_read':'bigint','rows_written':'bigint','accounting_state':'nvarchar',
           'start_time_utc':'nvarchar','end_time_utc':'nvarchar','high_watermark':'nvarchar'}


def classify(rows, producer_native_id):
    def unavailable(reason): return {'status':'UNAVAILABLE','reason':reason}
    if not isinstance(rows,list) or not rows:
        return unavailable('The declared audit returned no run; successful completion is not established.')
    try:
        if any(set(r)!=set(COLUMNS) for r in rows):
            return unavailable('Audit response does not carry the complete accounting contract.')
        if any(r['pipeline_name']!=producer_native_id for r in rows):
            return unavailable('Audit row names a different producer.')
        ordered=sorted(rows,key=lambda r:timestamp(r['start_time_utc']))
        latest=ordered[-1]
        if any(timestamp(r['start_time_utc'])==timestamp(latest['start_time_utc']) and r!=latest for r in ordered[:-1]):
            return unavailable('Latest audit run is ambiguous.')
        if latest['status']!='Succeeded':
            return unavailable('Latest audited run does not establish successful completion: '+str(latest['status']))
        start,end=timestamp(latest['start_time_utc']),timestamp(latest['end_time_utc'])
        if end<start:return unavailable('Audit run timestamps are contradictory.')
        if latest['accounting_state']!='OBSERVED_COPY_OUTPUT':
            return unavailable('Audit accounting is not observed copy-activity output.')
        counts={}
        for key in ('rows_read','rows_written'):
            v=latest[key]
            if isinstance(v,bool) or v is None or str(int(v))!=str(v) or int(v)<0:
                return unavailable('Audit counter missing or not a nonnegative integer.')
            counts[key]=int(v)
        if not isinstance(latest['run_id'],str) or not latest['run_id']:
            return unavailable('Audit run identity is missing.')
    except (ValueError,TypeError,KeyError,AttributeError):
        return unavailable('Audit response has malformed accounting or run timestamps.')
    return {'status':'CURRENT','run_state':'SUCCEEDED','run_id':latest['run_id'],
            'started_at':start.isoformat(),'completed_at':end.isoformat(),
            'accounting':counts,'high_watermark':latest['high_watermark'],
            'reason':'The audited run completed with its own activity counters; source capture currency was not established.'}


def read(adapter, entry):
    from .. import context_search
    from ..flexible_tools import run as run_query
    from ..source_diagnostics import quote
    from ..process_debugging import attest_surface
    context=context_search.latest(adapter.store)
    by_id={a['id']:a for a in (context or {}).get('assets',[])}
    audit=by_id.get(entry['audit_asset_id']);producer=by_id.get(entry['producer_asset_id'])
    delivery=by_id.get(entry['delivery_asset_id'])
    def unavailable(reason):return {'status':'UNAVAILABLE','reason':reason}
    if any(not a or a.get('availability','CURRENT')!='CURRENT' for a in (audit,producer,delivery)):
        return unavailable('Declared audit, producer or delivery is absent from current discovery.')
    if audit['kind']!='LakehouseTable' or producer['kind']!='DataPipeline' or delivery['kind']!='CopyJob':
        return unavailable('Declared audit-source kinds cannot be rendered by this adapter.')
    if adapter.execute_lower is None or adapter.read_endpoint is None:
        return unavailable('Declared audit has no configured independent reader execution surface.')
    parts=audit['parent_id'].removeprefix('fabric://').split('/')
    if len(parts)!=2:return unavailable('Declared audit container identity is malformed.')
    endpoint=adapter.read_endpoint({'workspace':parts[0],'lakehouse':parts[1]})
    if endpoint.get('provisioningStatus')!='Success':return unavailable('Declared audit endpoint is not ready.')
    name=audit['name'].split('.')
    if len(name)!=2:return unavailable('Declared audit must carry an explicit schema and object.')
    schema,table=name
    columns={a['name']:a['metadata'] for a in by_id.values()
             if a['kind']=='LakehouseColumn' and a['parent_id']==audit['id']
             and a.get('availability','CURRENT')=='CURRENT'}
    # The contract names fields; physical types must come from discovered schema.
    if not set(COLUMNS)<=set(columns):
        return unavailable('Declared audit schema does not establish every accounting field.')
    def physical_type(column):
        value=column.get('type') or column.get('dataType') or column.get('data_type') or column.get('type_name')
        if not isinstance(value,str):return None
        value=value.lower()
        return {'string':'nvarchar','long':'bigint'}.get(value,value)
    if any(physical_type(columns[k])!=t for k,t in COLUMNS.items()):
        return unavailable('Declared audit physical schema differs from the accounting contract.')
    producer_id=producer['id'].rsplit('/',1)[-1]
    # Parameterisation and admission are performed by the existing compiler.
    query='SELECT TOP 20 '+','.join(quote(k) for k in COLUMNS)+' FROM '+quote(schema)+'.'+quote(table)
    query+=" WHERE [pipeline_name] = '"+producer_id.replace("'","''")+"' ORDER BY [start_time_utc] DESC"
    catalog=[{'id':audit['id'],'provenance':'DECLARED_BY_CONFIGURATION',
        'metadata':{'schema_name':schema,'name':table,'type_desc':'USER_TABLE',
                    'columns':[{'name':k,'data_type':v} for k,v in COLUMNS.items()]}}]
    plan={'model_id':adapter.model['id'],'revision':adapter.model['revision'],
          'context_id':adapter.model['context_id'],'query':query,'max_rows':20}
    execute=lambda:run_query(adapter.store,plan,adapter.config,'bounded_fabric_sql',
        lambda request:adapter.execute_lower(endpoint['name'],request),catalog=catalog)
    try:
        result=adapter.meter_read('bounded_fabric_sql',execute) if adapter.meter_read else execute()
    except ValueError as exc:
        return unavailable('Declared audit query could not be compiled faithfully: '+str(exc))
    if result['status']!='COMPLETED':return unavailable('Declared audit read did not complete; no monitoring fallback was attempted.')
    body=result['result'];reader=adapter.config['fabric']['sql_reader']
    surface={'engine':'Microsoft Azure SQL Data Warehouse','connection':'sql://'+reader['server'],
             'object':endpoint['name'],'identity':reader['account']}
    report=attest_surface(surface,body.get('surface_report'),('identity','engine','object'))
    if body['completeness']!='COMPLETE_RESPONSE' or report['consistency']!='MATCHED' or report['missing_required_fields']:
        return unavailable('Audit accounting lacks complete query-bound reader surface attestation.')
    classified=classify(body['rows'],producer_id)
    return {**classified,'evidence':{'id':result['id'],'tool':'bounded_fabric_sql',
        'metadata':{'declared_audit':entry,'load_accounting':classified},
        'values':body['rows'],'request_hash':result['request_hash'],
        'surface_attestation':report,'execution_surface':surface,'surface_report':body['surface_report']}}
