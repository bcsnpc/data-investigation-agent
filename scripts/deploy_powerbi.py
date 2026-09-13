"""Deploy version-controlled semantic model/report definitions through Fabric."""
import argparse,base64,json,time
from fabric_api import api,ROOT

def deploy(folder,item_type,display_name):
    config=json.loads((ROOT/'infra/fabric/environment.json').read_text())
    workspace=config['workspace_id']
    parts=[{'path':p.relative_to(folder).as_posix(),'payload':base64.b64encode(p.read_bytes()).decode(),'payloadType':'InlineBase64'}
      for p in sorted(folder.rglob('*')) if p.is_file()]
    definition={'parts':parts}
    items=api(f'workspaces/{workspace}/items')['text']['value']
    matches=[i for i in items if i['type']==item_type and i['displayName']==display_name]
    if matches:
        result=api(f"workspaces/{workspace}/items/{matches[0]['id']}/updateDefinition",'post',{'definition':definition})
    else:
        result=api(f'workspaces/{workspace}/items','post',{'displayName':display_name,'type':item_type,'definition':definition})
    operation=result.get('headers',{}).get('x-ms-operation-id')
    if operation:
        print(f'Fabric operation: {operation}',flush=True)
        for attempt in range(30):
            status=api(f'operations/{operation}')['text']
            if status['status'] in ('Succeeded','Completed'):break
            if status['status'] in ('Failed','Cancelled'):raise RuntimeError(status)
            time.sleep(10)
        else:raise TimeoutError(f'Operation {operation} is still running; inspect before retrying.')
    print(f'{display_name}: deployment completed')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('folder');parser.add_argument('type',choices=['SemanticModel','Report']);parser.add_argument('name')
    args=parser.parse_args()
    deploy(ROOT/args.folder,args.type,args.name)
