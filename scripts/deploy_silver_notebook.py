"""Deploy reviewed PySpark source as a Fabric notebook; does not start its job."""
import base64
import json
from fabric_api import api, ROOT

config = json.loads((ROOT/'infra/fabric/environment.json').read_text())
workspace = config['workspace_id']
parameters = '\n'.join(f'{key} = {value!r}' for key,value in {
 'WORKSPACE':workspace,'BRONZE_ID':config['bronze_lakehouse_id'],
 'SILVER_ID':config['silver_lakehouse_id'],'BRONZE_RUN_ID':config['bronze_pipeline_run_id']}.items())
source = (ROOT/'infra/fabric/bronze_to_silver.py').read_text(encoding='utf-8')
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
items=api(f'workspaces/{workspace}/items')['text']['value']
matches=[i for i in items if i['type']=='Notebook' and i['displayName']=='nb_ordersops_bronze_to_silver']
if matches:
    result=api(f"workspaces/{workspace}/notebooks/{matches[0]['id']}/updateDefinition",'post',{'definition':definition})
else:
    result=api(f'workspaces/{workspace}/notebooks','post',{'displayName':'nb_ordersops_bronze_to_silver',
      'description':'Validate the initial Bronze baseline and publish conformed Silver entities with run evidence.', 'definition':definition})
(ROOT/'.local/fabric-notebook-deployment.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
