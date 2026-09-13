"""Deploy the reporting dimension notebook using the existing Fabric login."""
import base64
import json
from fabric_api import api,ROOT

config=json.loads((ROOT/'infra/fabric/environment.json').read_text())
workspace=config['workspace_id']
name='nb_ordersops_reporting_dimensions'
source=f"WORKSPACE={workspace!r}\nGOLD_ID={config['gold_lakehouse_id']!r}\n"+(ROOT/'infra/fabric/prepare_reporting_dimensions.py').read_text()
compile(source,name,'exec')
notebook={'nbformat':4,'nbformat_minor':5,'metadata':{
 'kernelspec':{'name':'synapse_pyspark','display_name':'Synapse PySpark'},'language_info':{'name':'python'},
 'dependencies':{'lakehouse':{'default_lakehouse':config['gold_lakehouse_id'],
 'default_lakehouse_name':'lh_investigator_gold','default_lakehouse_workspace_id':workspace}}},
 'cells':[{'cell_type':'code','metadata':{},'execution_count':None,'outputs':[],'source':source.splitlines(keepends=True)}]}
definition={'format':'ipynb','parts':[{'path':'notebook-content.ipynb','payload':base64.b64encode(json.dumps(notebook).encode()).decode(),'payloadType':'InlineBase64'}]}
items=api(f'workspaces/{workspace}/items')['text']['value']
matches=[i for i in items if i['type']=='Notebook' and i['displayName']==name]
if matches:
    result=api(f"workspaces/{workspace}/notebooks/{matches[0]['id']}/updateDefinition",'post',{'definition':definition})
else:
    result=api(f'workspaces/{workspace}/notebooks','post',{'displayName':name,'definition':definition})
print(json.dumps(result))
