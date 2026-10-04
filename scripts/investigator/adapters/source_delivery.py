"""Microsoft delivery observations using declared semantic columns and copy mappings."""
from ..process_tape import uuid4
from .. import context_search
from ..source_delivery import declaration,decode,classify
from ..source_diagnostics import quote
from ..process_debugging import attest_surface
from ..flexible_tools import run as run_query
from .microsoft_process import SQL_TYPES


def read(adapter,boundary,scope):
    result={'status':'UNAVAILABLE','observations':[]}
    def unavailable(reason):return dict(result,reason=reason)
    if scope.get('filters') or scope.get('dimension_ids'):
        return unavailable('Delivery membership supports whole-entity scope only; filtered lower scope remains refused.')
    configured=adapter.config.get('source_delivery')
    if configured is None:return unavailable('No source change/key/version semantics are declared.')
    roles=declaration(configured);layer=boundary['lower'];proof=layer.get('copy_mapping_proof')
    if not proof or layer['id']!=roles['source_asset_id']:
        return unavailable('No exact full-table Copy Job mapping reaches the declared source.')
    context=context_search.latest(adapter.store) or {};assets={a['id']:a for a in context.get('assets',[])}
    cols=[]
    for k in ('key_column_id','version_column_id','modified_column_id'):
        c=assets.get(roles[k],{})
        if c.get('kind')!='SqlColumn' or c.get('parent_id')!=layer['id'] or c.get('availability')!='CURRENT':
            return unavailable('A declared delivery column is absent from current source discovery.')
        cols.append(c['metadata'])
    if cols[0]['data_type'] not in ('int','bigint') or cols[1]['data_type'] not in ('timestamp','rowversion') or cols[2]['data_type']!='datetime2':
        return unavailable('Declared delivery key/version/time types are not supported by this adapter.')
    source_names=[c['name'] for c in cols];mapping=proof['mapping']['translator']['mappings']
    destination_names=[]
    for name in source_names:
        matches=[m['destination']['name'] for m in mapping if m['source']['name']==name]
        if len(matches)!=1:return unavailable('A delivery role lacks an exact one-to-one copied column.')
        destination_names.append(matches[0])
    job=adapter.job_history(boundary)
    evidence=job.get('evidence')
    if evidence:result['observations'].append(evidence)
    if job.get('status')!='CURRENT':return unavailable(job.get('reason') or 'Successful load accounting unavailable.')
    upper=boundary['upper'];asset=upper['binding']['asset'];parent=asset['parent_id']
    parts=parent.removeprefix('fabric://').split('/')
    endpoint=adapter.read_endpoint({'workspace':parts[0],'lakehouse':parts[1]})
    props=endpoint.get('properties',{}).get('sqlEndpointProperties',{})
    endpoint_asset=assets.get('fabric://'+parts[0]+'/'+str(props.get('id')), {})
    if props.get('connectionString')!=adapter.config['fabric']['sql_reader']['server'] or endpoint_asset.get('kind')!='SQLEndpoint':
        return unavailable('Delivery endpoint is not declared on the approved connection.')
    database=endpoint_asset['name'];dest_schema,dest_table=asset['name'].split('.')
    all_rows={};ids={}
    for side,names in (('source',source_names),('destination',destination_names)):
        schema,table=(proof['source']['metadata']['schema_name'],proof['source']['metadata']['name']) if side=='source' else (dest_schema,dest_table)
        catalog=[proof['source']] if side=='source' else [{'id':asset['id'],'metadata':{
            'schema_name':schema,'name':table,'type_desc':'USER_TABLE','columns':[
                {'name':names[0],'data_type':cols[0]['data_type']},{'name':names[1],'data_type':'varbinary'},
                {'name':names[2],'data_type':'datetime2'}]}}]
        rows=[];refs=[];last=None
        for _ in range(5):
            query='SELECT TOP 249 '+quote(names[0])+' AS [key], CAST('+quote(names[1])+' AS bigint) AS [version], CAST('+quote(names[2])+' AS nvarchar(40)) AS [modified] FROM '+quote(schema)+'.'+quote(table)
            if last is not None:query+=' WHERE '+quote(names[0])+' > '+str(last)
            query+=' ORDER BY '+quote(names[0])
            plan={'model_id':adapter.model['id'],'revision':adapter.model['revision'],'context_id':adapter.model['context_id'],'query':query,'max_rows':250}
            tool='bounded_sql' if side=='source' else 'bounded_fabric_sql'
            if side=='source':
                from application_sql_surface import read as execute_source,ENGINE
                execute=lambda:run_query(adapter.store,plan,adapter.config,tool,lambda request:execute_source(adapter.config,request),catalog=catalog)
                surface={'engine':ENGINE,'connection':'sql://'+proof['server'],'object':proof['database'],'identity':adapter.config['sql']['auth'].get('account')}
            else:
                execute=lambda:run_query(adapter.store,plan,adapter.config,tool,lambda request:adapter.execute_lower(database,request),catalog=catalog)
                r=adapter.config['fabric']['sql_reader'];surface={'engine':'Microsoft Azure SQL Data Warehouse','connection':'sql://'+r['server'],'object':database,'identity':r['account']}
            read=adapter.meter_read(tool,execute) if adapter.meter_read else execute()
            if read['status']!='COMPLETED':return unavailable('Delivery membership page did not complete; no gap is inferred.')
            body=read['result'];report=attest_surface(surface,body.get('surface_report'),('identity','engine','object'))
            observation={'id':read['id'],'tool':tool,'values':body['rows'],'completeness':body['completeness'],'request_hash':read['request_hash'],
                'delivery_page_after':last,
                'execution_surface':surface,'surface_report':body.get('surface_report'),'surface_attestation':report,
                'surface_report_types':SQL_TYPES,'surface_report_binding':body.get('surface_report_binding'),'surface_report_receipt_id':read['id']}
            result['observations'].append(observation)
            if body['completeness']!='COMPLETE_RESPONSE' or report['consistency']!='MATCHED' or report['missing_required_fields']:
                return unavailable('Delivery membership page has incomplete response or surface attestation.')
            page=decode(body['rows']);keys=[int(r['key']) for r in page]
            if keys!=sorted(set(keys)) or (last is not None and keys and keys[0]<=last):return unavailable('Delivery pagination did not establish unique ordered keys.')
            refs.append(read['id']);rows.extend(page)
            if len(page)<249:break
            last=keys[-1]
        else:return unavailable('Delivery membership exceeds its bounded enumeration; no completeness claim.')
        all_rows[side]=rows;ids[side]=refs
    facts=classify(job,all_rows['source'],all_rows['destination'])
    marker={'id':'source-delivery-'+str(uuid4()),'tool':'process','check_kind':'SOURCE_DELIVERY',
        'limitations':['Delivery row comparisons do not exclude Fabric SQL analytics endpoint synchronization delay; query-bound matching snapshots are unavailable.'],
        'audit_result':{k:v for k,v in job.items() if k!='evidence'},'audit_evidence_id':evidence['id'],
        'row_evidence':ids,'delivery_result':facts,'semantics':roles}
    result['observations'].append(marker)
    return {**result,**facts,'evidence':marker}
