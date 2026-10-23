"""Existing Azure job execution adapter; no scope or resource provisioning."""
import copy,json,re,subprocess,time
from pathlib import Path
from ..process_tape import bytes_of
from ..planner_recording import _safe
from ..unified_runner import command

def input_policy_preflight(config):
    """Validate generated input bindings before launch; never widen them."""
    if 'input' not in config:return {'status':'NOT_REQUIRED'}
    raw=config.get('environment',{}).get('DIA_PLATFORM_GATEWAY_POLICY')
    if not raw:return {'status':'UNESTABLISHED','reason':'INPUT_POLICY_NOT_RETAINED'}
    policy=json.loads(raw);channel=config['capture']['channel']
    grants=policy['identities'].get(channel,{}).get('http',[])
    matches=[x for x in grants if x.get('method')=='GET' and x.get('url')==config['input']['url']
             and x.get('purpose') in ('platform_blob','blob_read')]
    if len(matches)!=1:raise ValueError('RUNNER_INPUT_EXACT_READ_NOT_DECLARED')
    return {'status':'PASS','channel':channel,'url':config['input']['url']}


def demo_preflight(job,resource,*,execute,cli):
    """Bounded point-in-time control read; never install a network-blocking lease."""
    timeout=job['properties'].get('configuration',{}).get('replicaTimeout')
    if type(timeout)is not int or timeout<3600:raise ValueError('RUNNER_DEMO_RUNTIME_BELOW_3600')
    if resource.rsplit('/',1)[-1]!='job-dia-worker':raise ValueError('RUNNER_DEMO_EXISTING_WORKER_REQUIRED')
    parts=resource.split('/');subscription=parts[2];group=parts[4];observations=[]
    for name in ('job-dia-worker','job-dia-graph-scan'):
        response=execute(cli+['containerapp','job','execution','list','--name',name,'--resource-group',group,
            '--subscription',subscription,'--output','json','--only-show-errors'],capture_output=True,text=True,check=True,timeout=60)
        executions=json.loads(response.stdout)
        if not isinstance(executions,list):raise ValueError('RUNNER_DEMO_EXECUTION_LIST_UNESTABLISHED')
        rows=[]
        for item in executions:
            status=item.get('properties',{}).get('status')
            if not isinstance(status,str):raise ValueError('RUNNER_DEMO_EXECUTION_STATUS_UNESTABLISHED')
            rows.append({'name':item.get('name'),'status':status})
            if status.casefold()not in ('succeeded','completed','failed','stopped','cancelled','canceled'):
                raise ValueError('RUNNER_DEMO_COMPETING_EXECUTION:'+name+':'+status)
        observations.append({'job':name,'executions':rows})
    return {'status':'ADMITTED','replica_timeout':timeout,'observed_at':time.time(),'jobs':observations,
        'isolation':'POINT_IN_TIME_EXECUTION_ADMISSION; short database transactions only; no long writer lease',
        'limitation':'Later scheduled or external starts are not excluded by this control read.'}


def launch(config,target,*,execute=subprocess.run):
    """Read existing job and start its pinned override; never update its roles."""
    import tempfile
    from .runner_schedule import bind_execution
    config=bind_execution(config)
    input_policy_preflight(config)
    from ..build_phase import admit_platform
    observation=config.get('platform_cost_observation')
    if observation is not None:
        if set(observation)!={'charged_microdollars','observed_at','source'} or not isinstance(observation['source'],str):raise ValueError('RUNNER_PLATFORM_COST_OBSERVATION')
        if time.time()-float(observation['observed_at'])>86400:raise ValueError('RUNNER_PLATFORM_COST_OBSERVATION_STALE')
    admit_platform(observation['charged_microdollars'] if observation else None,time.time())
    deployment=config['deployment']
    if not {'resource_id','cli'}<=set(deployment)<={'resource_id','cli','execution_resources'}:raise ValueError('RUNNER_AZURE_DEPLOYMENT')
    resource=deployment['resource_id']
    if not re.fullmatch(r'/subscriptions/[0-9a-fA-F-]{36}/resourceGroups/[A-Za-z0-9_.()-]+/providers/Microsoft\.App/jobs/[a-z0-9-]+',resource):raise ValueError('RUNNER_EXISTING_JOB_ID')
    resources=deployment.get('execution_resources')
    if resources is not None and (resource.rsplit('/',1)[-1]!='job-dia-worker'
            or resources!={'cpu':1,'memory':'2Gi'} or type(resources.get('cpu'))is not int):
        raise ValueError('RUNNER_WORKER_RESOURCE_OVERRIDE_REFUSED')
    cli=deployment['cli']
    if not (cli==['az'] or isinstance(cli,list) and len(cli)==3 and cli[1:]==['-m','azure.cli'] and re.fullmatch(r'python(?:[0-9.]*)?(?:\.exe)?',Path(cli[0]).name,re.I)):raise ValueError('RUNNER_FIXED_AZURE_CLI_REQUIRED')
    base=cli+['containerapp','job']
    read=execute(base+['show','--ids',resource,'--output','json','--only-show-errors'],capture_output=True,text=True,check=True)
    job=json.loads(read.stdout)
    check=config.get('checks',{}).get(target,{})
    demo=check.get('kind')=='investigation' and 'verification_proof'in check.get('options',{})
    admission=demo_preflight(job,resource,execute=execute,cli=cli)if demo else None
    template=writable_template(job['properties']['template'])
    if len(template.get('containers',[]))!=1:raise ValueError('RUNNER_SINGLE_EXISTING_WORKER_REQUIRED')
    container=template['containers'][0]
    if resources is not None:container['resources']=copy.deepcopy(resources)
    container['image']=config['image'];container['command']=command('/work/runner-estate.json',target);container['args']=[]
    overrides=config.get('environment',{})
    env=[row for row in container.get('env',[]) if row['name'] not in {'DIA_RUNNER_ESTATE_JSON','INVESTIGATOR_OPERATING_MODE',*overrides}]
    env.extend({'name':name,'value':value} for name,value in overrides.items())
    env.extend([{'name':'DIA_RUNNER_ESTATE_JSON','value':json.dumps(config,sort_keys=True)},
                {'name':'INVESTIGATOR_OPERATING_MODE','value':'BUILD_PHASE'}])
    container['env']=env
    _safe(bytes_of(template))
    with tempfile.TemporaryDirectory(prefix='dia-runner-launch-') as folder:
        path=Path(folder)/'execution.yaml'
        # JSON is valid YAML. The optional approved resource increase applies
        # only to this execution; the job's scheduled template stays unchanged.
        path.write_bytes(bytes_of(template))
        started=execute(base+['start','--ids',resource,'--yaml',str(path),'--output','json','--only-show-errors'],capture_output=True,text=True,check=True)
    result=json.loads(started.stdout)
    return {'run_id':config.get('run_id'),'execution_name':result.get('name'),'image':config['image'],'status':'STARTED',**({'demo_admission':admission}if demo else {})}


def existing_job(resource_id):
    return bool(re.fullmatch(r'/subscriptions/[0-9a-fA-F-]{36}/resourceGroups/[A-Za-z0-9_.()-]+/providers/Microsoft\.App/jobs/[a-z0-9-]+',resource_id))


# ARM 2025-01-01 JobTemplate/Container request schema. GET enrichment such
# as imageType is not accepted by PATCH and must never be echoed back.
def writable_template(value):
    template={k:copy.deepcopy(v) for k,v in value.items() if k in ('containers','initContainers','volumes')}
    fields={'name','image','command','args','env','resources','volumeMounts','probes'}
    for group in ('containers','initContainers'):
        if template.get(group) is not None:
            template[group]=[{k:v for k,v in row.items() if k in fields and (group!='initContainers' or k!='probes')} for row in template[group]]
    return template
