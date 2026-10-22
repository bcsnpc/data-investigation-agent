"""Plan-only approved thirty-minute collector job in the existing environment."""
import copy
from decimal import Decimal
import json
import re
from ..process_tape import bytes_of
from ..planner_recording import _safe
from .runner_deployment import existing_job, writable_template

NAME='job-dia-collectors'
CRON='*/30 * * * *'


def estimate(base='19.077133',storage='0.02'):
    # 31 days, no free grant assumed: $0.000024/vCPU-sec + $0.000003/GiB-sec.
    seconds=1488*60
    compute=Decimal(seconds)*(Decimal('0.25')*Decimal('0.000024')+Decimal('0.5')*Decimal('0.000003'))
    total=Decimal(base)+compute+Decimal(storage)
    if min(Decimal(base),Decimal(storage))<0 or not total.is_finite() or total>20:
        raise ValueError('COLLECTOR_PLATFORM_ESTIMATE_EXCEEDS_20')
    return {'estimate_not_invoice':True,'free_grants_assumed':False,'executions_31_days':1488,
        'runtime_seconds':60,'compute_monthly_usd':str(compute),'additional_storage_monthly_usd':storage,
        'existing_platform_monthly_usd':base,'combined_monthly_usd':str(total)}


def plan(existing,runner,*,cost=None):
    from ..unified_runner import command
    if not existing_job(existing.get('id','')) or existing['id'].rsplit('/',1)[-1]!='job-dia-worker':
        raise ValueError('COLLECTOR_EXISTING_WORKER_REQUIRED')
    if not re.fullmatch(r'[^\s]+@sha256:[a-f0-9]{64}',runner.get('image','')):raise ValueError('COLLECTOR_PINNED_IMAGE_REQUIRED')
    if runner.get('per_execution')is not True:raise ValueError('COLLECTOR_UNIQUE_CAPTURE_REQUIRED')
    checks=runner.get('checks',{})
    if len(checks)!=1:raise ValueError('COLLECTOR_SINGLE_TYPED_ROUTE_REQUIRED')
    target=next(iter(checks));check=checks[target]
    if check.get('kind')!='facts-dispatcher' or set(check.get('options',{}))!={'configs'}:
        raise ValueError('COLLECTOR_TYPED_DISPATCHER_REQUIRED')
    # Validate without obtaining state or contacting a provider.
    from cloud_facts_dispatcher import select
    class Empty:
        def get(self,*a):raise KeyError
    select(check['options']['configs'],Empty())
    template=writable_template(existing['properties']['template'])
    if len(template.get('containers',[]))!=1 or template.get('initContainers'):raise ValueError('COLLECTOR_SINGLE_WORKER_REQUIRED')
    container=template['containers'][0];overrides=runner.get('environment',{})
    replacement={*overrides,'DIA_RUNNER_ESTATE_JSON','INVESTIGATOR_OPERATING_MODE','DIA_GRAPH_SCAN_CONFIG','DIA_GRAPH_SCAN_GATEWAY'}
    env=[v for v in container.get('env',[]) if v['name'] not in replacement]
    env.extend({'name':k,'value':v} for k,v in overrides.items())
    env.extend([{'name':'DIA_RUNNER_ESTATE_JSON','value':json.dumps(runner,sort_keys=True)},
        {'name':'INVESTIGATOR_OPERATING_MODE','value':'BUILD_PHASE'}])
    container.update(image=runner['image'],command=command('/work/runner-estate.json',target),args=[],env=env,
        resources={'cpu':0.25,'memory':'0.5Gi'})
    identity=existing.get('identity',{})
    if identity.get('type')!='UserAssigned' or len(identity.get('userAssignedIdentities',{}))!=1:
        raise ValueError('COLLECTOR_EXISTING_MANAGED_IDENTITY_REQUIRED')
    identity={'type':'UserAssigned','userAssignedIdentities':{k:{} for k in identity['userAssignedIdentities']}}
    config={k:copy.deepcopy(v) for k,v in existing['properties']['configuration'].items() if k in ('identitySettings','registries','secrets')}
    config.update(triggerType='Schedule',replicaTimeout=60,replicaRetryLimit=0,
        scheduleTriggerConfig={'cronExpression':CRON,'parallelism':1,'replicaCompletionCount':1})
    resource=existing['id'].rsplit('/',1)[0]+'/'+NAME
    body={'location':existing['location'],'identity':identity,'properties':{
        'environmentId':existing['properties']['environmentId'],'configuration':config,'template':template}}
    if 'workloadProfileName'in existing['properties']:body['properties']['workloadProfileName']=existing['properties']['workloadProfileName']
    result={'status':'PLAN_ONLY','method':'PUT','resource_id':resource,
        'url':'https://management.azure.com'+resource+'?api-version=2025-01-01','body':body,
        'cost':estimate(**(cost or {})),'new_roles':[],
        'existing_schedules_unchanged':['job-dia-worker','job-dia-graph-scan']}
    _safe(bytes_of(result));return result


def preflight(job,existing):
    p=job.get('properties',{});c=p.get('configuration',{})
    if job.get('id','').rsplit('/',1)[-1]!=NAME or p.get('environmentId')!=existing['properties']['environmentId']:
        raise ValueError('COLLECTOR_EXACT_JOB_ENVIRONMENT_REQUIRED')
    if p.get('provisioningState') not in (None,'Succeeded'):
        raise ValueError('COLLECTOR_PROVISIONING_NOT_SUCCEEDED')
    if (c.get('triggerType')!='Schedule' or c.get('replicaTimeout')!=60 or c.get('replicaRetryLimit')!=0 or
        c.get('scheduleTriggerConfig')!={'cronExpression':CRON,'parallelism':1,'replicaCompletionCount':1}):
        raise ValueError('COLLECTOR_SCHEDULE_OR_RUNTIME_DIFFERS')
    containers=p.get('template',{}).get('containers',[])
    resources=containers[0].get('resources',{}) if len(containers)==1 else {}
    # ARM echoes an empty GET-only ephemeralStorage field; it is not a
    # requested allocation. Nonempty/unknown allocations still refuse.
    resources={k:v for k,v in resources.items() if not(k=='ephemeralStorage' and v in ('',None))}
    if resources!={'cpu':0.25,'memory':'0.5Gi'}:
        raise ValueError('COLLECTOR_RESOURCE_BOUND_DIFFERS')
    if set(job.get('identity',{}).get('userAssignedIdentities',{}))!=set(existing.get('identity',{}).get('userAssignedIdentities',{})):
        raise ValueError('COLLECTOR_MANAGED_IDENTITY_DIFFERS')
    from ..unified_runner import command
    container=containers[0]
    try:
        runner=json.loads(next(v['value'] for v in container['env'] if v['name']=='DIA_RUNNER_ESTATE_JSON'))
        target=container['command'][3]
        if container['command']!=command('/work/runner-estate.json',target):raise ValueError
        if runner['checks'][target]['kind']!='facts-dispatcher' or runner.get('per_execution')is not True:raise ValueError
        if container['image']!=runner['image'] or not re.fullmatch(r'[^\s]+@sha256:[a-f0-9]{64}',container['image']):raise ValueError
    except (KeyError,IndexError,StopIteration,TypeError,ValueError):
        raise ValueError('COLLECTOR_TYPED_PINNED_UNIQUE_RUNNER_REQUIRED') from None
    return {'status':'PASS','cron':CRON,'runtime_seconds':60,'resources':resources}
