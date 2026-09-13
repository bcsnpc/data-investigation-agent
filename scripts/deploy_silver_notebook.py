"""Deploy reviewed PySpark source as a Fabric notebook; does not start its job."""
import base64
import json
import time
from fabric_api import api, ROOT
from metadata_config import load_config
from silver_snapshot_input import build

config = json.loads((ROOT/'infra/fabric/environment.json').read_text())
workspace = config['workspace_id']
metadata = load_config(ROOT/'infra/metadata/development.json')
snapshot = config['snapshot_bronze']
binding = build(metadata['storage']['database'], snapshot['source_snapshot_id'],
                snapshot['verification_id'], workspace, config['bronze_lakehouse_id'])
parameters = '\n'.join(f'{key} = {value!r}' for key,value in {
 'WORKSPACE':workspace,'BRONZE_ID':config['bronze_lakehouse_id'],
 'SILVER_ID':config['silver_lakehouse_id'],'BRONZE_BINDING':binding}.items())
source = (ROOT/'infra/fabric/read_pinned_bronze.py').read_text(encoding='utf-8')+'\n'+(ROOT/'infra/fabric/bronze_to_silver.py').read_text(encoding='utf-8')
compile(parameters+'\n'+source,'bronze_to_silver.py','exec')
notebook = {'nbformat':4,'nbformat_minor':5,'metadata':{
 'kernelspec':{'name':'synapse_pyspark','display_name':'Synapse PySpark'},
 'language_info':{'name':'python'},
 'dependencies':{'lakehouse':{'default_lakehouse':config['silver_lakehouse_id'],
 'default_lakehouse_name':'lh_investigator_silver','default_lakehouse_workspace_id':workspace}}},
 'cells':[{'cell_type':'code','metadata':{},'execution_count':None,'outputs':[],
 'source':(parameters+'\n'+source).splitlines(keepends=True)}]}
definition = {'format':'ipynb','parts':[{'path':'notebook-content.ipynb',
 'payload':base64.b64encode(json.dumps(notebook).encode()).decode(),'payloadType':'InlineBase64'}]}
result=api(f"workspaces/{workspace}/notebooks/{config['silver_notebook_id']}/updateDefinition",'post',{'definition':definition})
if result['status_code']==202:
    operation={k.lower():v for k,v in result['headers'].items()}['x-ms-operation-id']
    for _ in range(60):
        state=api(f'operations/{operation}')['text']['status']
        if state in ('Succeeded','Completed'):break
        if state in ('Failed','Cancelled'):raise RuntimeError('Silver notebook deployment failed')
        time.sleep(5)
    else:raise TimeoutError('Silver notebook deployment still pending')
(ROOT/'.local/fabric-notebook-deployment.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
