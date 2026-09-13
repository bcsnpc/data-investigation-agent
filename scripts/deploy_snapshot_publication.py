"""Deploy an isolated snapshot publisher or independent verification notebook."""
import argparse
import base64
import json
import time
from uuid import UUID
from fabric_api import api, ROOT
from metadata_config import load_config
from source_snapshot import verify_registered
from metadata_protocol import pages


def deploy(snapshot_id, verify_only=False):
    snapshot_id=str(UUID(snapshot_id))
    config=json.loads((ROOT/'infra/fabric/environment.json').read_text())
    metadata=load_config(ROOT/'infra/metadata/development.json')
    reference=verify_registered(metadata['storage']['database'],snapshot_id)
    workspace=config['workspace_id']
    parameters={'WORKSPACE':workspace,'BRONZE_ID':config['bronze_lakehouse_id'],'SNAPSHOT_ID':snapshot_id,
                'MANIFEST_SHA256':reference['manifest_sha256'],'VERIFY_ONLY':verify_only}
    source='\n'.join(f'{k}={v!r}' for k,v in parameters.items())+'\n'+(ROOT/'infra/fabric/publish_source_snapshot.py').read_text()
    compile(source,'publish_source_snapshot.py','exec')
    notebook={'nbformat':4,'nbformat_minor':5,'metadata':{'kernelspec':{'name':'synapse_pyspark','display_name':'Synapse PySpark'},
        'language_info':{'name':'python'},'dependencies':{'lakehouse':{'default_lakehouse':config['bronze_lakehouse_id'],
        'default_lakehouse_name':'lh_investigator_bronze','default_lakehouse_workspace_id':workspace}}},
        'cells':[{'cell_type':'code','metadata':{},'execution_count':None,'outputs':[],'source':source.splitlines(keepends=True)}]}
    definition={'format':'ipynb','parts':[{'path':'notebook-content.ipynb','payload':base64.b64encode(json.dumps(notebook).encode()).decode(),'payloadType':'InlineBase64'}]}
    name='nb_orderops_snapshot_'+('verify' if verify_only else 'publish')
    items=pages(f'workspaces/{workspace}/items',api)
    matches=[i for i in items if i['displayName']==name and i['type']=='Notebook']
    if len(matches)>1:raise ValueError('Ambiguous notebook name')
    if matches:
        identity=matches[0]['id']
        result=api(f'workspaces/{workspace}/notebooks/{identity}/updateDefinition','post',{'definition':definition})
    else:
        result=api(f'workspaces/{workspace}/notebooks','post',{'displayName':name,'definition':definition})
        identity=(result.get('text') or {}).get('id')
    if result['status_code']==202:
        headers={k.lower():v for k,v in result['headers'].items()}
        operation=headers['x-ms-operation-id']
        for _ in range(60):
            state=api(f'operations/{operation}')['text']['status']
            if state in ('Succeeded','Completed'):break
            if state in ('Failed','Cancelled'):raise RuntimeError('Notebook deployment failed')
            time.sleep(5)
        else:raise TimeoutError('Notebook deployment pending')
    if identity is None:
        created=[i for i in pages(f'workspaces/{workspace}/items',api) if i['displayName']==name and i['type']=='Notebook']
        if len(created)!=1:raise ValueError('Created notebook not uniquely resolved')
        identity=created[0]['id']
    receipt={'notebook_id':identity,'workspace_id':workspace,'snapshot_id':snapshot_id,'verify_only':verify_only,'deployment':result}
    (ROOT/('.local/snapshot-'+('verify' if verify_only else 'publish')+'-deployment.json')).write_text(json.dumps(receipt,indent=2))
    return receipt


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--snapshot-id',required=True);parser.add_argument('--verify-only',action='store_true')
    args=parser.parse_args();print(json.dumps(deploy(args.snapshot_id,args.verify_only),indent=2))
