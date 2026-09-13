"""Deploy the reviewed Gold models and notebook; execution is a separate action."""
import base64
import json
import time
from fabric_api import api, ROOT
from metadata_config import load_config
from gold_snapshot_input import build_gold

config=json.loads((ROOT/'infra/fabric/environment.json').read_text())
workspace=config['workspace_id']
binding=build_gold(load_config(ROOT/'infra/metadata/development.json')['storage']['database'],config)
parameters='\n'.join(f'{key}={value!r}' for key,value in {
 'WORKSPACE':workspace,'SILVER_ID':config['silver_lakehouse_id'],
 'GOLD_ID':config['gold_lakehouse_id'],'SILVER_BINDING':binding}.items())
source=parameters+'\n'+(ROOT/'infra/fabric/gold_models.py').read_text(encoding='utf-8')+'\n'+(ROOT/'infra/fabric/silver_to_gold.py').read_text(encoding='utf-8')
compile(source,'silver_to_gold.py','exec')
notebook={'nbformat':4,'nbformat_minor':5,'metadata':{
 'kernelspec':{'name':'synapse_pyspark','display_name':'Synapse PySpark'},'language_info':{'name':'python'},
 'dependencies':{'lakehouse':{'default_lakehouse':config['gold_lakehouse_id'],
 'default_lakehouse_name':'lh_investigator_gold','default_lakehouse_workspace_id':workspace}}},
 'cells':[{'cell_type':'code','metadata':{},'execution_count':None,'outputs':[],'source':source.splitlines(keepends=True)}]}
definition={'format':'ipynb','parts':[{'path':'notebook-content.ipynb',
 'payload':base64.b64encode(json.dumps(notebook).encode()).decode(),'payloadType':'InlineBase64'}]}
result=api(f"workspaces/{workspace}/notebooks/{config['gold_notebook_id']}/updateDefinition",'post',{'definition':definition})
if result['status_code']==202:
    operation={k.lower():v for k,v in result['headers'].items()}['x-ms-operation-id']
    for _ in range(60):
        state=api(f'operations/{operation}')['text']['status']
        if state in ('Succeeded','Completed'):break
        if state in ('Failed','Cancelled'):raise RuntimeError('Gold deployment failed')
        time.sleep(5)
    else:raise TimeoutError('Gold deployment still pending')
(ROOT/'.local/fabric-gold-notebook-deployment.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
