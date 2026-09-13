"""Deploy the reviewed Gold models and notebook; execution is a separate action."""
import base64
import json
from fabric_api import api, ROOT

config=json.loads((ROOT/'infra/fabric/environment.json').read_text())
workspace=config['workspace_id']
parameters='\n'.join(f'{key}={value!r}' for key,value in {
 'WORKSPACE':workspace,'SILVER_ID':config['silver_lakehouse_id'],
 'GOLD_ID':config['gold_lakehouse_id']}.items())
source=parameters+'\n'+(ROOT/'infra/fabric/gold_models.py').read_text(encoding='utf-8')+'\n'+(ROOT/'infra/fabric/silver_to_gold.py').read_text(encoding='utf-8')
compile(source,'silver_to_gold.py','exec')
notebook={'nbformat':4,'nbformat_minor':5,'metadata':{
 'kernelspec':{'name':'synapse_pyspark','display_name':'Synapse PySpark'},'language_info':{'name':'python'},
 'dependencies':{'lakehouse':{'default_lakehouse':config['gold_lakehouse_id'],
 'default_lakehouse_name':'lh_investigator_gold','default_lakehouse_workspace_id':workspace}}},
 'cells':[{'cell_type':'code','metadata':{},'execution_count':None,'outputs':[],'source':source.splitlines(keepends=True)}]}
definition={'format':'ipynb','parts':[{'path':'notebook-content.ipynb',
 'payload':base64.b64encode(json.dumps(notebook).encode()).decode(),'payloadType':'InlineBase64'}]}
items=api(f'workspaces/{workspace}/items')['text']['value']
matches=[i for i in items if i['type']=='Notebook' and i['displayName']=='nb_ordersops_silver_to_gold']
if matches:
    result=api(f"workspaces/{workspace}/notebooks/{matches[0]['id']}/updateDefinition",'post',{'definition':definition})
else:
    result=api(f'workspaces/{workspace}/notebooks','post',{'displayName':'nb_ordersops_silver_to_gold',
     'description':'Publish reconciled Gold reporting cohorts and order drill-through from one validated Silver run.','definition':definition})
(ROOT/'.local/fabric-gold-notebook-deployment.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
