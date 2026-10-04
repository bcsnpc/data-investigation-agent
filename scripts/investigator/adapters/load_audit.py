"""Read the declared audit own accounting on a guarded Microsoft SQL surface."""
from ..load_accounting import COLUMNS,classify


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
    if audit['kind']=='LakehouseTable':
        return unavailable('LAKEHOUSE_SQL_AUDIT_SYNC_LAG: load audit tables must be read from a Warehouse; a lakehouse SQL endpoint cannot establish last-run currency.')
    if audit['kind']!='WarehouseTable' or producer['kind']!='DataPipeline' or delivery['kind']!='CopyJob':
        return unavailable('Declared audit-source kinds cannot be rendered by this adapter.')
    if adapter.execute_lower is None or adapter.read_endpoint is None:
        return unavailable('Declared audit has no configured independent reader execution surface.')
    parts=audit['parent_id'].removeprefix('fabric://').split('/')
    if len(parts)!=2:return unavailable('Declared audit container identity is malformed.')
    endpoint=adapter.read_endpoint({'workspace':parts[0],'warehouse':parts[1]})
    props=endpoint.get('properties',{})
    endpoint_asset=by_id.get(audit['parent_id'], {})
    reader=adapter.config['fabric']['sql_reader']
    if (endpoint.get('id')!=parts[1] or props.get('connectionString')!=reader['server']
            or endpoint_asset.get('kind')!='Warehouse' or endpoint_asset.get('availability','CURRENT')!='CURRENT'):
        return unavailable('Declared audit endpoint does not match the discovered object and approved connection.')
    database=endpoint_asset['name']
    name=audit['name'].split('.')
    if len(name)!=2:return unavailable('Declared audit must carry an explicit schema and object.')
    schema,table=name
    columns={a['name']:a['metadata'] for a in by_id.values()
             if a['kind']=='WarehouseColumn' and a['parent_id']==audit['id']
             and a.get('availability','CURRENT')=='CURRENT'}
    # The contract names fields; physical types must come from discovered schema.
    if not set(COLUMNS)<=set(columns):
        return unavailable('Declared audit schema does not establish every accounting field.')
    def physical_type(column):
        value=column.get('type') or column.get('dataType') or column.get('data_type') or column.get('type_name')
        if not isinstance(value,str):return None
        value=value.lower()
        return {'string':'nvarchar','long':'bigint'}.get(value,value)
    if any(physical_type(columns[k]) not in ({'varchar','nvarchar'} if t=='nvarchar' else {t}) for k,t in COLUMNS.items()):
        return unavailable('Declared audit physical schema differs from the accounting contract.')
    producer_id=producer['id'].rsplit('/',1)[-1]
    # Parameterisation and admission are performed by the existing compiler.
    query='SELECT TOP 20 '+','.join(quote(k) for k in COLUMNS)+' FROM '+quote(schema)+'.'+quote(table)
    query+=" WHERE [pipeline_name] = '"+producer_id.replace("'","''")+"' ORDER BY [start_time_utc] DESC"
    catalog=[{'id':audit['id'],'provenance':'DECLARED_BY_CONFIGURATION',
        'metadata':{'schema_name':schema,'name':table,'type_desc':'USER_TABLE',
                    'columns':[{'name':k,'data_type':physical_type(columns[k])} for k in COLUMNS]}}]
    plan={'model_id':adapter.model['id'],'revision':adapter.model['revision'],
          'context_id':adapter.model['context_id'],'query':query,'max_rows':20}
    execute=lambda:run_query(adapter.store,plan,adapter.config,'bounded_fabric_sql',
        lambda request:adapter.execute_lower(database,request),catalog=catalog)
    try:
        result=adapter.meter_read('bounded_fabric_sql',execute) if adapter.meter_read else execute()
    except ValueError as exc:
        return unavailable('Declared audit query could not be compiled faithfully: '+str(exc))
    if result['status']!='COMPLETED':return unavailable('Declared audit read did not complete; no monitoring fallback was attempted.')
    body=result['result'];reader=adapter.config['fabric']['sql_reader']
    surface={'engine':'Microsoft Azure SQL Data Warehouse','connection':'sql://'+reader['server'],
             'object':database,'identity':reader['account']}
    report=attest_surface(surface,body.get('surface_report'),('identity','engine','object'))
    if body['completeness']!='COMPLETE_RESPONSE' or report['consistency']!='MATCHED' or report['missing_required_fields']:
        return unavailable('Audit accounting lacks complete query-bound reader surface attestation.')
    from ..source_delivery import decode
    classified=classify(decode(body['rows']),producer_id)
    return {**classified,'evidence':{'id':result['id'],'tool':'bounded_fabric_sql',
        'metadata':{'declared_audit':entry,'load_accounting':classified},
        'values':body['rows'],'request_hash':result['request_hash'],
        'surface_attestation':report,'execution_surface':surface,'surface_report':body['surface_report'],
        'surface_report_binding':body.get('surface_report_binding'),
        'surface_report_types':{'identity':'PRINCIPAL_NAME','engine':'ENGINE_PRODUCT','object':'DATABASE_CATALOG_NAME'},
        'surface_report_receipt_id':result['id'],'completeness':body['completeness']}}
