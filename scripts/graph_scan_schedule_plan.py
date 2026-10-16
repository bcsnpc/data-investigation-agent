"""Prepare one existing Container Apps Job update; never deploy or create accounts."""
import argparse
import copy
import json
from pathlib import Path
import re
from scan_estate_graph import validate


def build(existing, config, gateway, image):
    from investigator.planner_recording import _safe
    from investigator.live_gateway import Gateway
    validate(config); Gateway(gateway)
    _safe(json.dumps(config,sort_keys=True).encode())
    _safe(json.dumps(gateway,sort_keys=True).encode())
    identity=existing.get('id','')
    if not re.fullmatch(r'/subscriptions/[0-9a-f-]{36}/resourceGroups/[A-Za-z0-9_.()-]+/providers/Microsoft.App/jobs/[a-z0-9-]+',identity):
        raise ValueError('EXISTING_CONTAINER_JOB_RESOURCE_REQUIRED')
    if not re.fullmatch(r'ghcr\.io/[a-z0-9_./-]+@sha256:[a-f0-9]{64}',image):
        raise ValueError('PINNED_EXISTING_WORKER_IMAGE_REQUIRED')
    template=copy.deepcopy(existing['properties']['template'])
    if len(template.get('containers',[]))!=1 or template.get('initContainers'):
        raise ValueError('SINGLE_EXISTING_WORKER_JOB_REQUIRED')
    container=template['containers'][0]
    env={item['name']:item for item in container.get('env',[])}
    for required in ('INVESTIGATOR_STATE_BACKEND','INVESTIGATOR_PG_HOST','INVESTIGATOR_PG_DATABASE','INVESTIGATOR_PG_USER','AZURE_CLIENT_ID','DIA_GATEWAY_STATE_IDENTITY','DIA_GATEWAY_HTTP_IDENTITY'):
        if required not in env:raise ValueError('EXISTING_PLATFORM_ENVIRONMENT_MISSING:'+required)
    env['DIA_GRAPH_SCAN_CONFIG']={'name':'DIA_GRAPH_SCAN_CONFIG','value':json.dumps(config,sort_keys=True,separators=(',',':'))}
    env['DIA_GRAPH_SCAN_GATEWAY']={'name':'DIA_GRAPH_SCAN_GATEWAY','value':json.dumps(gateway,sort_keys=True,separators=(',',':'))}
    container.update(image=image,command=['python','scripts/graph_scan_bootstrap.py'],args=[],env=list(env.values()))
    settings=copy.deepcopy(existing['properties']['configuration'])
    settings.pop('manualTriggerConfig',None);settings.pop('eventTriggerConfig',None)
    settings.update(triggerType='Schedule',scheduleTriggerConfig={'cronExpression':'0 */6 * * *','parallelism':1,'replicaCompletionCount':1},
        replicaTimeout=600,replicaRetryLimit=0)
    _safe(json.dumps({'configuration':settings,'template':template},sort_keys=True).encode())
    cpu=container['resources']['cpu'];memory=container['resources']['memory']
    if not isinstance(cpu,(int,float)) or not re.fullmatch(r'[0-9.]+Gi',memory):raise ValueError('EXISTING_RESOURCE_SIZE_REQUIRED')
    return {'status':'PLAN_ONLY','method':'PATCH','url':'https://management.azure.com'+identity+'?api-version=2025-01-01',
        'body':{'properties':{'configuration':settings,'template':template}},
        'approval':config['approval'],'budget':config['budget'],
        'compute_upper_bound_30_days':{'executions':120,'seconds_per_execution':600,'vCPU_seconds':120*600*cpu,'GiB_seconds':120*600*float(memory[:-2])},
        'cost_decision':'Compare this bound with the shared environment free allowance and existing platform spend before applying; no new resource.'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('existing-job','config','gateway','output'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--image',required=True);a=p.parse_args()
    result=build(json.loads(a.existing_job.read_bytes()),json.loads(a.config.read_bytes()),json.loads(a.gateway.read_bytes()),a.image)
    with a.output.open('x',encoding='utf8')as out:json.dump(result,out,indent=2)
    print(json.dumps({'status':'PLAN_ONLY','output':str(a.output),'url':result['url'],'compute_upper_bound_30_days':result['compute_upper_bound_30_days']}))


if __name__=='__main__':main()
