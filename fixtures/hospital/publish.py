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


def update(owner,name,folder,paths,reason):
    """Explicit, journaled update; retain original definitions and read back bytes."""
    if not reason.strip():raise ValueError('Update reason required')
    if owner.state['workspace']['id']!=WORKSPACE:raise ValueError('HealthNet workspace only')
    saved=owner.state.get('published',{}).get(name)
    if not saved or not(name in ('pl_clinical','pl_billing','pl_nightly_run_all','df_reference_mapping')):
        raise ValueError('Only journaled HealthNet build definitions can be updated')
    root=f"workspaces/{WORKSPACE}/items/{saved['item']['id']}"
    before=owner.call(root+'/getDefinition',{})
    parts=definition_parts(folder,paths)
    result=owner.call(root+'/updateDefinition',{'definition':{'parts':parts}})
    after=owner.call(root+'/getDefinition',{})
    native={p['path']:base64.b64decode(p['payload'])for p in after['definition']['parts']}
    for part in parts:
        expected=base64.b64decode(part['payload']);actual=native[part['path']]
        if part['path'].endswith('.json'):
            if json.loads(actual)!=json.loads(expected):raise ValueError('Native definition differs: '+part['path'])
        elif actual!=expected:raise ValueError('Native definition differs: '+part['path'])
    owner.state.setdefault('definition_updates',[]).append({'name':name,'reason':reason,'before':before,'after':after,'result':result})
    saved['definition_sha256']=hashlib.sha256(json.dumps(parts,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    owner.save()
    return after
