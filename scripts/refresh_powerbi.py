"""Synchronize Gold SQL metadata and frame a validated semantic model snapshot."""
import json,time
from fabric_api import api,ROOT
from metadata_config import load_config
from semantic_snapshot import registered_gold,alignment_query,validate_alignment

config=json.loads((ROOT/'infra/fabric/environment.json').read_text())
w=config['workspace_id'];g=config['gold_lakehouse_id'];m=config['semantic_model_id']
reference=registered_gold(load_config(ROOT/'infra/metadata/development.json')['storage']['database'],config)
gold=reference['report']
assert api(f'{w}/{g}/Files/validation/latest.json',audience='storage')['text']==gold,'Gold publication changed'
result=api(f"workspaces/{w}/sqlEndpoints/{config['gold_sql_endpoint_id']}/refreshMetadata",'post',{'recreateTables':False})
operation=result.get('headers',{}).get('x-ms-operation-id')
if operation:
    for _ in range(60):
        state=api(f'operations/{operation}')['text']
        if state['status']=='Succeeded':
            result=api(f'operations/{operation}/result');break
        if state['status'] in ('Failed','Cancelled'):raise RuntimeError(state)
        time.sleep(10)
    else:raise TimeoutError('SQL metadata synchronization still running')
required={'dim_date','dim_customer','dim_product','order_summary','order_line_summary','refund_summary'}
statuses={t['tableName']:t for t in result['text']['value']}
assert required<=statuses.keys(),result['text']
assert all(t['status']=='Success' or (t['status']=='NotRun' and t.get('lastSuccessfulSyncDateTime')) for t in statuses.values()),result['text']
response=api(f'groups/{w}/datasets/{m}/refreshes','post',{'type':'full','commitMode':'transactional'},audience='powerbi')
refresh_id=response['headers']['x-ms-request-id']
print('Refresh:',refresh_id,flush=True)
for _ in range(60):
    state=api(f'groups/{w}/datasets/{m}/refreshes/{refresh_id}',audience='powerbi')['text']
    if state['status']=='Completed':break
    if state['status'] in ('Failed','Cancelled','Disabled'):raise RuntimeError(state)
    time.sleep(10)
else:raise TimeoutError('Semantic model refresh still running')
tables=['DimDate','DimCustomer','DimProduct','FactOrder','FactOrderLine','FactRefund']
# DISTINCT excludes the engine's virtual blank relationship row; actual run IDs
# (including any mixed/stale run) remain visible and must match exactly.
dax=alignment_query()
observed=api(f'groups/{w}/datasets/{m}/executeQueries','post',{'queries':[{'query':dax}],'serializerSettings':{'includeNulls':True}},audience='powerbi')['text']
row=observed['results'][0]['tables'][0]['rows'][0]
alignment=validate_alignment(gold,row)
assert api(f'{w}/{g}/Files/validation/latest.json',audience='storage')['text']==gold,'Gold publication changed during refresh'
(ROOT/'.local/powerbi-refresh.json').write_text(json.dumps(state,indent=2))
(ROOT/'.local/semantic-snapshot-refresh.json').write_text(json.dumps({'gold_reference':reference,
 'model_id':m,'refresh_id':refresh_id,'refresh':state,'query':dax,'observed':observed,'alignment':alignment},indent=2))
print('SQL metadata and semantic model refresh completed. Run validate_powerbi.py next.')
