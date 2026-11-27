"""Publish only journaled new benchmark workspace items, as the owner."""
import argparse
import hashlib
import json
from pathlib import Path
from .native_artifacts import parts,write_model,report


def publish(plan_path,spec_path,journal_path,cli_packages,output):
    from fixtures.hospital.owner_fabric import OwnerFabric,CAPACITY
    p=json.loads(Path(plan_path).read_text())
    spec=next(s for s in json.loads(Path(spec_path).read_text())['estates']if s['id']==p['estate'])
    if p['workspace']!=spec['workspace']or p['database']!=spec['database']:raise ValueError('Build scope differs')
    owner=OwnerFabric(journal_path,cli_packages)
    if owner.state.get('pending_operation'):raise ValueError('Reconcile saved operation before admitting another')
    key='benchmark_'+p['estate']+'_workspace'
    if key not in owner.state:raise ValueError('Only an owner-journaled benchmark workspace may be targeted')
    workspace=owner.state[key]['id'];readback=owner.call('workspaces/'+workspace)
    if readback['capacityId']!=CAPACITY:raise ValueError('Existing trial capacity required')
    files=write_model(spec,p,'sql-orderops-9696025.database.windows.net',Path(output)/p['estate']/'model')
    mk='benchmark_'+p['estate']+'_model'
    if mk not in owner.state:
        if mk+'_intent'in owner.state:raise ValueError('Unresolved model creation intent; inspect native items first')
        owner.state[mk+'_intent']=dict(workspace=workspace,sha256=hashlib.sha256(json.dumps(files,sort_keys=True).encode()).hexdigest());owner.save()
        owner.state[mk]=owner.call(f'workspaces/{workspace}/items',dict(displayName=spec['workspace']+' Model',type='SemanticModel',definition=parts(files)))
        owner.save()
    rk='benchmark_'+p['estate']+'_report'
    if rk not in owner.state:
        if rk+'_intent'in owner.state:raise ValueError('Unresolved report creation intent; inspect native items first')
        definitions=report(spec,owner.state[mk]['id'])
        owner.state[rk+'_intent']=dict(workspace=workspace,model=owner.state[mk]['id']);owner.save()
        owner.state[rk]=owner.call(f'workspaces/{workspace}/items',dict(displayName=spec['workspace']+' Report',type='Report',definition=parts(definitions)))
        owner.save()
    items=owner.call('workspaces/'+workspace+'/items');owner.state['benchmark_'+p['estate']+'_items_readback']=items;owner.save()
    return dict(workspace=workspace,model=owner.state[mk]['id'],report=owner.state[rk]['id'],
        refreshed=False,status='DEFINITIONS_PUBLISHED_NOT_REFRESHED')


def main():
    a=argparse.ArgumentParser(description=__doc__)
    for arg in ('plan','spec','journal','cli-packages','output'):a.add_argument('--'+arg,required=True)
    v=a.parse_args();print(json.dumps(publish(v.plan,v.spec,v.journal,v.cli_packages,v.output),indent=2))


if __name__=='__main__':main()
