"""Owner-approved independent graph schedule; never replace the daily job."""
import copy
from decimal import Decimal
import json
from pathlib import Path
import re
import subprocess
import tempfile
import time

from ..process_tape import bytes_of
from ..planner_recording import _safe
from .runner_deployment import writable_template, existing_job

GRAPH_NAME='job-dia-graph-scan'
GRAPH_CRON='0 */6 * * *'
DAILY_CRON='0 6 * * *'


def costs(*,platform='14.822133',daily='0.857',graph='3.348',storage='0.05'):
    amounts={key:Decimal(str(value)) for key,value in
             dict(platform=platform,daily=daily,graph=graph,storage=storage).items()}
    if any(not value.is_finite() or value<0 for value in amounts.values()):raise ValueError('GRAPH_JOB_COST_ESTIMATE_INVALID')
    total=sum(amounts.values())
    if total>20:raise ValueError('GRAPH_AND_DAILY_EXCEED_PLATFORM_MONTHLY_BUDGET')
    return {'monthly_usd':{key:str(value) for key,value in amounts.items()},'combined_monthly_usd':str(total),
            'graph_executions_31_days':124,'seconds_per_execution':1800,
            'graph_vCPU_seconds':111600,'graph_GiB_seconds':223200,
            'free_grants_assumed':False,'estimate_not_invoice':True}


def plan(existing,daily_config,*,estimate=None):
    """Retained existing graph facts plus the current pinned runner declaration."""
    from ..unified_runner import command
    from .runner_schedule import bind_execution
    from ..live_gateway import Gateway
    from scan_estate_graph import validate
    if not existing_job(existing.get('id','')) or existing['id']!=daily_config['deployment']['resource_id']:
        raise ValueError('GRAPH_JOB_EXISTING_WORKER_ID_DIFFERS')
    if existing['id'].rsplit('/',1)[-1]==GRAPH_NAME:raise ValueError('GRAPH_JOB_SOURCE_MUST_BE_DAILY_WORKER')
    if not re.fullmatch(r'[^\s]+@sha256:[0-9a-f]{64}',daily_config.get('image','')):
        raise ValueError('RUNNER_PINNED_IMAGE_REQUIRED')
    if daily_config.get('per_execution') is not True:raise ValueError('GRAPH_JOB_UNIQUE_CAPTURE_REQUIRED')
    template=writable_template(existing['properties']['template'])
    if len(template.get('containers',[]))!=1 or template.get('initContainers'):raise ValueError('GRAPH_JOB_SINGLE_WORKER_REQUIRED')
    container=template['containers'][0]
    if container.get('resources')!={'cpu':0.5,'memory':'1Gi'}:raise ValueError('GRAPH_JOB_EXISTING_RESOURCE_SIZE_DIFFERS')
    old_env={row['name']:row.get('value') for row in container.get('env',[]) if 'value' in row}
    try:
        graph_config=json.loads(old_env['DIA_GRAPH_SCAN_CONFIG'])
        gateway=json.loads(old_env['DIA_GRAPH_SCAN_GATEWAY'])
    except (KeyError,TypeError,ValueError):raise ValueError('GRAPH_JOB_RETAINED_SCAN_DECLARATIONS_REQUIRED') from None
    validate(graph_config);Gateway(gateway)
    runner=bind_execution(daily_config,identifier='graph-scan-template')
    # This is a newly authored recurring template, unlike the concrete launch
    # produced by bind_execution. Every scheduled graph execution must rebind.
    runner['per_execution']=True
    runner.pop('schedule',None)
    runner['checks']={'graph':{'kind':'scan','options':{'config':graph_config}}}
    resource=existing['id'].rsplit('/',1)[0]+'/'+GRAPH_NAME
    runner['deployment']['resource_id']=resource
    # Keep precisely the retained graph authority; add only the already approved
    # runner-capture capability under the existing platform state identity.
    capture_gateway=json.loads(runner['environment']['DIA_PLATFORM_GATEWAY_POLICY'])
    capture_grants=capture_gateway['identities']['worker:state']['runner_captures']
    if len(capture_grants)!=1:raise ValueError('GRAPH_JOB_EXACT_CAPTURE_GRANT_REQUIRED')
    gateway['identities']['worker:state']['runner_captures']=copy.deepcopy(capture_grants)
    Gateway(gateway)
    runner['environment']['DIA_PLATFORM_GATEWAY_POLICY']=json.dumps(gateway,sort_keys=True)
    replacement=set(runner['environment'])|{'DIA_RUNNER_ESTATE_JSON','INVESTIGATOR_OPERATING_MODE',
                                          'DIA_GRAPH_SCAN_CONFIG','DIA_GRAPH_SCAN_GATEWAY'}
    env=[row for row in container.get('env',[]) if row['name'] not in replacement]
    env.extend({'name':name,'value':value}for name,value in runner['environment'].items())
    env.extend([{'name':'DIA_RUNNER_ESTATE_JSON','value':json.dumps(runner,sort_keys=True)},
                {'name':'INVESTIGATOR_OPERATING_MODE','value':'BUILD_PHASE'}])
    container.update(image=runner['image'],command=command('/work/runner-estate.json','graph'),args=[],env=env)
    identity=copy.deepcopy(existing.get('identity'))
    if (not isinstance(identity,dict) or identity.get('type')!='UserAssigned'
            or len(identity.get('userAssignedIdentities',{}))!=1):raise ValueError('GRAPH_JOB_EXISTING_MANAGED_IDENTITY_REQUIRED')
    identity={'type':'UserAssigned','userAssignedIdentities':{key:{} for key in identity['userAssignedIdentities']}}
    before=existing['properties']['configuration']
    settings={key:copy.deepcopy(before[key]) for key in ('identitySettings','registries','secrets') if key in before}
    settings.update(triggerType='Schedule',replicaTimeout=1800,replicaRetryLimit=0,
        scheduleTriggerConfig={'cronExpression':GRAPH_CRON,'parallelism':1,'replicaCompletionCount':1})
    properties={'environmentId':existing['properties']['environmentId'],'configuration':settings,'template':template}
    if 'workloadProfileName' in existing['properties']:properties['workloadProfileName']=existing['properties']['workloadProfileName']
    body={'location':existing['location'],'identity':identity,'properties':properties}
    result={'status':'PLAN_ONLY','method':'PUT','resource_id':resource,
        'url':'https://management.azure.com'+resource+'?api-version=2025-01-01','body':body,
        'runner':runner,'daily_resource_id':existing['id'],'cost':costs(**(estimate or {})),
        'approval':'Owner direction 2026-10-21: separate six-hour graph job, same identity and resources; daily job remains 06:00 UTC.',
        'new_resources':[resource],'new_roles':[]}
    _safe(bytes_of(result));return result


def validate_pair(daily,graph,*,image=None):
    """Preflight and post-apply use the same two-job schedule invariant."""
    if not daily or not graph:raise ValueError('DAILY_AND_GRAPH_SCHEDULES_REQUIRED')
    if daily.get('id')==graph.get('id') or graph.get('id','').rsplit('/',1)[-1]!=GRAPH_NAME:
        raise ValueError('DAILY_AND_GRAPH_JOBS_MUST_BE_DISTINCT')
    from ..unified_runner import command
    for job,cron,kind in ((daily,DAILY_CRON,'smoke'),(graph,GRAPH_CRON,'scan')):
        properties=job.get('properties',{});settings=properties.get('configuration',{})
        if properties.get('provisioningState')!='Succeeded':raise ValueError('SCHEDULE_PAIR_PROVISIONING_NOT_SUCCEEDED')
        if (settings.get('triggerType')!='Schedule'
                or settings.get('replicaRetryLimit')!=0
                or settings.get('scheduleTriggerConfig')!={'cronExpression':cron,'parallelism':1,'replicaCompletionCount':1}):
            raise ValueError('SCHEDULE_PAIR_MISSING_OR_DIFFERS:'+cron)
        containers=properties.get('template',{}).get('containers',[])
        resources={k:v for k,v in containers[0].get('resources',{}).items() if v is not None and v!=''} if len(containers)==1 else {}
        if len(containers)!=1 or resources!={'cpu':0.5,'memory':'1Gi'}:
            raise ValueError('SCHEDULE_PAIR_RESOURCES_DIFFER')
        if image is not None and containers[0].get('image')!=image:raise ValueError('SCHEDULE_PAIR_IMAGE_DIFFERS')
        container=containers[0]
        env={row['name']:row.get('value')for row in container.get('env',[])}
        try:
            runner=json.loads(env['DIA_RUNNER_ESTATE_JSON'])
            argv=container['command'];target=argv[3]
            typed=runner['checks'][target]['kind']
        except (KeyError,TypeError,ValueError,IndexError):raise ValueError('SCHEDULE_PAIR_TYPED_RUNNER_REQUIRED') from None
        if argv!=command('/work/runner-estate.json',target) or typed!=kind:
            raise ValueError('SCHEDULE_PAIR_TYPED_ROUTE_DIFFERS')
        earned=kind=='smoke' and runner['checks'][target].get('options',{}).get('config',{}).get('demo_earned')is True
        expected_runtime=3600 if earned else 1800
        if settings.get('replicaTimeout')!=expected_runtime:raise ValueError('SCHEDULE_PAIR_MISSING_OR_DIFFERS:'+cron)
    if daily['identity']!=graph['identity']:
        # ARM readbacks include principalId/clientId; compare declared identity
        # resource IDs, not mutable enrichment or ordering.
        if (daily['identity'].get('type')!=graph['identity'].get('type') or
                set(daily['identity'].get('userAssignedIdentities',{}))!=set(graph['identity'].get('userAssignedIdentities',{}))):
            raise ValueError('SCHEDULE_PAIR_IDENTITY_DIFFERS')
    if daily['properties'].get('environmentId')!=graph['properties'].get('environmentId'):
        raise ValueError('SCHEDULE_PAIR_ENVIRONMENT_DIFFERS')
    return {'status':'PASS','daily':{'resource_id':daily['id'],'cron':DAILY_CRON,'runtime_seconds':daily['properties']['configuration']['replicaTimeout']},
            'graph':{'resource_id':graph['id'],'cron':GRAPH_CRON,'runtime_seconds':1800},'runtime_seconds':1800}


def apply(prepared,*,execute=subprocess.run,sleep=time.sleep):
    from .control_failure import execute_checked
    from ..build_phase import admit_platform
    config=prepared['runner'];observation=config.get('platform_cost_observation')
    admit_platform(observation['charged_microdollars'] if observation else None,time.time())
    cli=config['deployment']['cli']
    if not (cli==['az'] or isinstance(cli,list) and len(cli)==3 and cli[1:]==['-m','azure.cli']
            and re.fullmatch(r'python(?:[0-9.]*)?(?:\.exe)?',Path(cli[0]).name,re.I)):
        raise ValueError('RUNNER_FIXED_AZURE_CLI_REQUIRED')
    expected=prepared['daily_resource_id'].rsplit('/',1)[0]+'/'+GRAPH_NAME
    if (prepared['resource_id']!=expected or not existing_job(expected) or prepared['method']!='PUT'
            or prepared['url']!='https://management.azure.com'+expected+'?api-version=2025-01-01'):
        raise ValueError('GRAPH_JOB_EXACT_APPROVED_TARGET_REQUIRED')
    with tempfile.TemporaryDirectory(prefix='dia-graph-schedule-')as folder:
        path=Path(folder)/'job.json';path.write_bytes(bytes_of(prepared['body']))
        execute_checked(execute,cli+['rest','--method','PUT','--url',prepared['url'],'--body','@'+str(path),
            '--output','json','--only-show-errors'],operation='graph-job-create',capture_output=True,text=True,check=True)
    for attempt in range(4):
        reads={}
        for key,resource in (('daily',prepared['daily_resource_id']),('graph',prepared['resource_id'])):
            response=execute_checked(execute,cli+['containerapp','job','show','--ids',resource,'--output','json','--only-show-errors'],
                operation=key+'-schedule-readback',capture_output=True,text=True,check=True)
            reads[key]=json.loads(response.stdout)
        status=reads['graph'].get('properties',{}).get('provisioningState')
        if status in ('Updating','InProgress','Accepted','Provisioning') and attempt<3:
            sleep(30+10*attempt);continue
        result=validate_pair(reads['daily'],reads['graph'],image=config['image'])
        return {'status':'APPLIED','validation':result,'readbacks':reads,'readback_attempts':attempt+1,
                'resource_id':prepared['resource_id'],'cost':prepared['cost'],'new_roles':[]}
