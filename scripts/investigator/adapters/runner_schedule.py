"""Existing-job daily schedule and execution-local, narrow capture bindings."""
import copy
import json
import subprocess
import tempfile
import re
import time
from pathlib import Path
from ..process_tape import bytes_of,uuid4
from ..planner_recording import _safe


def bind_execution(config,*,identifier=None):
    value=copy.deepcopy(config)
    if not value.get('per_execution'):return value
    old=value['run_id'];new=identifier or str(uuid4())
    from ..adapters.runner_blobs import declaration
    gateway=json.loads(value['environment']['DIA_PLATFORM_GATEWAY_POLICY'])
    matched=0
    for channel in gateway['identities'].values():
        for grant in channel.get('runner_captures',[]):
            if grant['run_id']==old and grant['account_url']==value['capture']['account_url'] and grant['prefix']==value['capture']['prefix']:
                grant['run_id']=new;declaration(grant);matched+=1
    if matched!=1:raise ValueError('SCHEDULE_EXACT_CAPTURE_BINDING_REQUIRED')
    value['run_id']=new
    value['environment']['DIA_PLATFORM_GATEWAY_POLICY']=json.dumps(gateway,sort_keys=True)
    for check in value['checks'].values():
        if check['kind']=='smoke':check['options']['config']['run_id']=new
    _safe(bytes_of(value));return value


def plan(config,existing):
    from ..daily_smoke import schedule_plan
    from ..unified_runner import command
    schedule=config['schedule']
    if set(schedule)!={'target','platform_monthly_usd','smoke_monthly_usd'} or schedule['target'] not in config['checks']:raise ValueError('RUNNER_SCHEDULE_CONFIGURATION')
    if config['checks'][schedule['target']]['kind']!='smoke' or config.get('per_execution')is not True:raise ValueError('RUNNER_DAILY_UNIQUE_SMOKE_REQUIRED')
    if existing['id']!=config['deployment']['resource_id']:raise ValueError('RUNNER_SCHEDULE_EXISTING_JOB_DIFFERS')
    estimate=schedule_plan(resource_id=existing['id'],image=config['image'],platform_monthly_usd=schedule['platform_monthly_usd'],smoke_monthly_usd=schedule['smoke_monthly_usd'])
    from .runner_deployment import writable_template
    template=writable_template(existing['properties']['template'])
    if len(template.get('containers',[]))!=1:raise ValueError('RUNNER_SINGLE_EXISTING_WORKER_REQUIRED')
    container=template['containers'][0];overrides=config.get('environment',{})
    env=[v for v in container.get('env',[]) if v['name'] not in {*overrides,'DIA_RUNNER_ESTATE_JSON','INVESTIGATOR_OPERATING_MODE'}]
    env.extend({'name':key,'value':value}for key,value in overrides.items())
    env.extend([{'name':'DIA_RUNNER_ESTATE_JSON','value':json.dumps(config,sort_keys=True)},
                {'name':'INVESTIGATOR_OPERATING_MODE','value':'BUILD_PHASE'}])
    container.update(image=config['image'],command=command('/work/runner-estate.json',schedule['target']),args=[],env=env)
    settings={k:copy.deepcopy(v) for k,v in existing['properties']['configuration'].items() if k in ('eventTriggerConfig','identitySettings','manualTriggerConfig','registries','replicaRetryLimit','replicaTimeout','scheduleTriggerConfig','secrets','triggerType')}
    previous=copy.deepcopy(settings.get('scheduleTriggerConfig'))
    settings.pop('manualTriggerConfig',None);settings.pop('eventTriggerConfig',None)
    settings.update(triggerType='Schedule',scheduleTriggerConfig={'cronExpression':'0 6 * * *','parallelism':1,'replicaCompletionCount':1},replicaTimeout=1800,replicaRetryLimit=0)
    body={'properties':{'configuration':settings,'template':template}};_safe(bytes_of(body))
    return {'resource_id':existing['id'],'method':'PATCH','url':'https://management.azure.com'+existing['id']+'?api-version=2025-01-01',
            'body':body,'prior_schedule':previous,'new_schedule':settings['scheduleTriggerConfig'],
            'impact':'Replaces the prior six-hourly metadata schedule on this existing job with one daily 06:00 UTC smoke execution.',
            'cost':estimate,'new_resources':[]}


def apply(config,*,execute=subprocess.run,sleep=time.sleep):
    from ..build_phase import admit_platform
    from .control_failure import execute_checked
    observation=config.get('platform_cost_observation')
    admit_platform(observation['charged_microdollars'] if observation else None,__import__('time').time())
    cli=config['deployment']['cli'];resource=config['deployment']['resource_id']
    if not re.fullmatch(r'/subscriptions/[0-9a-fA-F-]{36}/resourceGroups/[A-Za-z0-9_.()-]+/providers/Microsoft\.App/jobs/[a-z0-9-]+',resource):raise ValueError('RUNNER_EXISTING_JOB_ID')
    if not (cli==['az'] or isinstance(cli,list) and len(cli)==3 and cli[1:]==['-m','azure.cli'] and re.fullmatch(r'python(?:[0-9.]*)?(?:\.exe)?',Path(cli[0]).name,re.I)):raise ValueError('RUNNER_FIXED_AZURE_CLI_REQUIRED')
    # CLI is already checked by the runner loader / deployment schema; never a
    # shell string, owner command, policy endpoint, or arbitrary executable.
    response=execute_checked(execute,cli+['containerapp','job','show','--ids',resource,'--output','json','--only-show-errors'],operation='schedule-show',capture_output=True,text=True,check=True)
    prepared=plan(config,json.loads(response.stdout))
    with tempfile.TemporaryDirectory(prefix='dia-smoke-schedule-') as folder:
        path=Path(folder)/'patch.json';path.write_bytes(bytes_of(prepared['body']))
        response=execute_checked(execute,cli+['rest','--method','PATCH','--url',prepared['url'],'--body','@'+str(path),'--output','json','--only-show-errors'],operation='schedule-patch',capture_output=True,text=True,check=True)
    # PATCH can return HTTP 202 with no body. It is a submission receipt, not
    # the resource readback; never parse it or repeat the mutation to poll.
    for attempt in range(3):
        response=execute_checked(execute,cli+['containerapp','job','show','--ids',resource,'--output','json','--only-show-errors'],operation='schedule-readback',capture_output=True,text=True,check=True)
        after=json.loads(response.stdout)
        actual=after['properties']['configuration']['scheduleTriggerConfig']
        state=after['properties'].get('provisioningState')
        if state in ('Failed','Canceled','Cancelled'):raise ValueError('RUNNER_DAILY_SCHEDULE_PROVISIONING_FAILED')
        pending=state in ('Updating','InProgress','Accepted','Provisioning')
        if actual==prepared['new_schedule'] and not pending:
            return {k:v for k,v in prepared.items()if k!='body'}|{'status':'APPLIED','actual_schedule':actual,'readback_attempts':attempt+1,'provisioning_state':state}
        if not pending or attempt==2:raise ValueError('RUNNER_DAILY_SCHEDULE_READBACK_DIFFERS')
        sleep(30+15*attempt)
