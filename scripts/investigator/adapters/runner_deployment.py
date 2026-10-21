"""Existing Azure job execution adapter; no scope or resource provisioning."""
import copy,json,re,subprocess,time
from pathlib import Path
from ..process_tape import bytes_of
from ..planner_recording import _safe
from ..unified_runner import command

def launch(config,target,*,execute=subprocess.run):
    """Read existing job and start its pinned override; never update its roles."""
    import tempfile
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
    job=json.loads(read.stdout);template=writable_template(job['properties']['template'])
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
    return {'run_id':config.get('run_id'),'execution_name':result.get('name'),'image':config['image'],'status':'STARTED'}


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
