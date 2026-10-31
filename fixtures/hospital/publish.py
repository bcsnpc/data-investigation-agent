"""Publish only hospital-owned definitions with the existing Fabric owner."""
import base64
import hashlib
import json
from pathlib import Path
from .owner_fabric import OwnerFabric

WORKSPACE='d237966c-b0b6-4123-bc89-e69643f4bf1f'


def definition_parts(folder,paths):
    folder=Path(folder)
    result=[]
    for name in paths:
        data=(folder/name).read_bytes()
        if b'REQUIRES_'in data:raise ValueError('Unbound definition: '+name)
        result.append({'path':name,'payloadType':'InlineBase64','payload':base64.b64encode(data).decode()})
    return result


def publish(owner,name,kind,folder,paths):
    if kind not in('Dataflow','DataPipeline')or not(name.startswith('pl_')or name=='df_reference_mapping'):
        raise ValueError('Only approved HealthNet dataflow/pipelines are supported')
    if owner.state['workspace']['id']!=WORKSPACE:raise ValueError('HealthNet workspace only')
    parts=definition_parts(folder,paths)
    digest=hashlib.sha256(json.dumps(parts,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    saved=owner.state.get('published',{}).get(name)
    if saved:
        if saved['definition_sha256']!=digest:raise ValueError('Published definition differs; inspect before update')
        return owner.call(f'workspaces/{WORKSPACE}/items/'+saved['item']['id'])
    existing=owner.call(f'workspaces/{WORKSPACE}/items')['value']
    if any(i['displayName']==name for i in existing):raise ValueError('Unjournaled existing item; inspect before adoption')
    item=owner.call(f'workspaces/{WORKSPACE}/items',{'displayName':name,'type':kind,
        'description':'Synthetic HealthNet owner build only; no DIA access',
        'definition':{'parts':parts}})
    owner.state.setdefault('published',{})[name]={'item':item,'definition_sha256':digest}
    owner.save()
    return item
