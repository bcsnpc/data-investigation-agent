"""Compile key membership only through declared Copy and semantic mappings."""
import re
from .. import context_search
from ..model_context import assets
from ..flexible_tools import run as run_query
from ..record_presence import counts
from ..process_debugging import attest_surface
from ..source_diagnostics import quote


def plan(adapter,path,layer,requested,scope):
    from ..query_sql import capabilities
    from ..proposal_limits import EXACT_INTEGER
    if scope.get('filters') or scope.get('dimension_ids'):
        raise ValueError('Expected-record membership cannot translate filtered scope faithfully.')
    if not requested or len(requested)>capabilities()['max_result_columns']:
        raise ValueError('Expected-record membership exceeds the bounded count-column allowance.')
    for record in requested:
        value=record['value']
        if not isinstance(value,str) or not re.fullmatch(r'-?\d+',value) or abs(int(value))>EXACT_INTEGER:
            raise ValueError('Expected record requires an exact integral key in the supported range.')
    if len({r['value'] for r in requested})!=len(requested):raise ValueError('Repeated expected-record key is ambiguous.')
    context=context_search.latest(adapter.store) or {};by_id={a['id']:a for a in context.get('assets',[]) if a.get('availability')=='CURRENT'}
    source=(adapter.config.get('source_delivery') or {}).get('source_asset_id')
    sources=[l for l in path['layers'] if l['id']==source and l.get('copy_mapping_proof')]
    if len(sources)!=1:raise ValueError('No declared key-preserving source mapping supports membership.')
    source_layer=sources[0];proof=source_layer['copy_mapping_proof']
    key=by_id.get(adapter.config['source_delivery']['key_column_id'],{})
    if key.get('parent_id')!=source or key.get('kind')!='SqlColumn' or key.get('metadata',{}).get('data_type') not in ('int','bigint'):
        raise ValueError('Declared source key is not a current integral source column.')
    mappings=[m for m in proof['mapping']['translator']['mappings'] if m['source']['name']==key['name']]
    if len(mappings)!=1:raise ValueError('Copy does not declare one exact mapping for the key.')
    destination_key=mappings[0]['destination']['name']
    source_index=path['layers'].index(source_layer)
    if source_index<1:raise ValueError('Declared application has no mapped landing layer.')
    landing=path['layers'][source_index-1]
    if layer['id']==source:
        if adapter.config.get('system_of_record',{}).get('reachable') is False:
            raise ValueError('Application is configured unreachable; membership was not read.')
        name=key['name'];catalog=[proof['source']];meta=proof['source']['metadata']
        database=proof['database'];tool='bounded_sql'
        if (proof['server'],database)!=(adapter.config['sql']['server'],adapter.config['sql']['database']):
            raise ValueError('Membership leaves the approved source connection.')
    elif layer['id']==landing['id']:
        if layer.get('kind')!='declared_source':raise ValueError('Membership does not approximate an intervening transformation.')
        meta={'schema_name':layer['binding']['declared_partition']['schema_name'],
              'name':layer['binding']['declared_partition']['entity_name'],'type_desc':'USER_TABLE',
              'columns':[dict(proof['destination_columns'][destination_key],name=destination_key)]}
        name=destination_key;catalog=[{'id':layer['id'],'metadata':meta}]
        endpoint=by_id.get(layer['binding']['declared_connection_asset_id'],{})
        if endpoint.get('kind')!='SQLEndpoint':raise ValueError('Membership endpoint is not discovered.')
        props=endpoint.get('metadata',{}).get('properties',{})
        if props.get('connectionString')!=adapter.config['fabric']['sql_reader']['server']:
            raise ValueError('Membership leaves the approved lower connection.')
        database=endpoint['name'];tool='bounded_fabric_sql'
    elif layer.get('kind')=='presentation' and path['layers'].index(layer)==source_index-2:
        binding=landing.get('binding',{})
        if not binding.get('unchanged_connection') or binding.get('declared_role_count')!=0:
            raise ValueError('Semantic membership needs unchanged source and no declared security filters.')
        columns=[a for a in assets(adapter.model['context']) if a['kind']=='SemanticColumn' and a['parent_id']==layer['id']
                 and a.get('metadata',{}).get('sourceColumn')==destination_key
                 and a.get('metadata',{}).get('dataType')=='int64'
                 and not a.get('metadata',{}).get('expression')]
        table=next((a for a in assets(adapter.model['context']) if a['id']==layer['id']),None)
        if len(columns)!=1 or not table:raise ValueError('Semantic key mapping is absent or ambiguous.')
        table_name="'"+table['name'].replace("'","''")+"'";column_name='['+columns[0]['name'].replace(']',']]')+']'
        query='EVALUATE ROW('+','.join('"presence_'+str(i)+'",COALESCE(COUNTROWS(FILTER('+table_name+','+table_name+column_name+' = '+r['value']+')),0)' for i,r in enumerate(requested))+')'
        from .microsoft_self_report import compose
        return {'query':compose(query),'tool':'bounded_dax','database':None,'catalog':None}
    else:raise ValueError('No faithful declared key mapping reaches this layer; membership was not approximated.')
    query='SELECT '+','.join('COUNT(CASE WHEN '+quote(name)+' = '+r['value']+' THEN 1 END) AS '+quote('presence_'+str(i)) for i,r in enumerate(requested))
    query+=' FROM '+quote(meta['schema_name'])+'.'+quote(meta['name'])
    return {'query':query,'tool':tool,'database':database,'catalog':catalog}


def read(adapter,path,layer,requested,scope):
    try:compiled=plan(adapter,path,layer,requested,scope)
    except (ValueError,KeyError,TypeError) as exc:return {'status':'UNAVAILABLE','reason':str(exc)}
    from ..record_presence import address
    tool=compiled['tool'];request={'model_id':adapter.model['id'],'revision':adapter.model['revision'],
        'context_id':adapter.model['context_id'],'query':compiled['query'],'max_rows':2,
        'read_address':address(layer['id'],requested)}
    from .microsoft_process import SEMANTIC_REPORT,SEMANTIC_TYPES,SQL_TYPES
    if tool=='bounded_dax':
        if adapter.execute_native is None:return {'status':'UNAVAILABLE','reason':'Semantic membership reader is unconfigured.'}
        request['surface_report']=SEMANTIC_REPORT
        dispatch=adapter.execute_native;reader=adapter.config['fabric']['native_reader']
        surface={'engine':'OLAP Server','connection':adapter.model['workspace'],'object':adapter.model['native_id'],'identity':reader['account']}
    elif tool=='bounded_sql':
        from application_sql_surface import read as sql_read,ENGINE
        dispatch=lambda req:sql_read(adapter.config,req)
        surface={'engine':ENGINE,'connection':'sql://'+adapter.config['sql']['server'],'object':compiled['database'],'identity':adapter.config['sql']['auth']['account']}
    else:
        if adapter.execute_lower is None:return {'status':'UNAVAILABLE','reason':'Lower membership reader is unconfigured.'}
        dispatch=lambda req:adapter.execute_lower(compiled['database'],req);reader=adapter.config['fabric']['sql_reader']
        surface={'engine':'Microsoft Azure SQL Data Warehouse','connection':'sql://'+reader['server'],'object':compiled['database'],'identity':reader['account']}
    execute=lambda:run_query(adapter.store,request,adapter.config,tool,dispatch,catalog=compiled['catalog'])
    try:result=adapter.meter_read(tool,execute) if adapter.meter_read else execute()
    except ValueError as exc:return {'status':'UNAVAILABLE','reason':'Membership could not be compiled faithfully: '+str(exc)}
    if result['status']!='COMPLETED':return {'status':'UNAVAILABLE','reason':'Expected-record query did not complete.'}
    body=result['result'];attestation=attest_surface(surface,body.get('surface_report'),('identity','engine','object'))
    if body['completeness']!='COMPLETE_RESPONSE' or attestation['consistency']!='MATCHED' or attestation['missing_required_fields']:
        return {'status':'UNAVAILABLE','reason':'Expected-record query lacks complete reader attestation.'}
    try:presence=counts(body['rows'],requested)
    except ValueError as exc:return {'status':'UNAVAILABLE','reason':str(exc)}
    fact={'requested':requested,'layer':layer['id'],'presence':presence}
    return {'status':'OBSERVED','evidence':{'id':result['id'],'tool':tool,'check_kind':'EXPECTED_RECORD_PRESENCE',
        'record_presence':fact,'read_address':request['read_address'],'values':body['rows'],'request_hash':result['request_hash'],'completeness':body['completeness'],
        'execution_surface':surface,'surface_report':body['surface_report'],'surface_report_binding':body['surface_report_binding'],
        'surface_attestation':attestation,'surface_report_types':SEMANTIC_TYPES if tool=='bounded_dax' else SQL_TYPES,
        'surface_report_receipt_id':result['id']}}
