"""Pure preparation from retained control-plane facts; never launch or grant."""
import copy
import json
import re
from ..planner_recording import _safe
from ..process_tape import bytes_of
from ..live_gateway import Gateway

def probe_plan(job,gateway,probe,slim,*,image,run_id,cli,budget_environment,platform_cost_observation=None):
    if not re.fullmatch(r'[^\s]+@sha256:[0-9a-f]{64}',image):raise ValueError('RUNNER_PINNED_IMAGE_REQUIRED')
    env={r['name']:r.get('value') for r in job['properties']['template']['containers'][0].get('env',[]) if 'value' in r}
    required=('INVESTIGATOR_PG_HOST','INVESTIGATOR_PG_DATABASE','INVESTIGATOR_PG_USER')
    if any(not env.get(key) for key in required):raise ValueError('RUNNER_EXISTING_POSTGRES_ENVIRONMENT_REQUIRED')
    identity=probe['authentication']['managed_identity'];account=slim['account_url']
    selected={'version':1,'live_enabled':True,'identities':{}}
    for channel in ('worker:state',slim['snapshot_channel'],slim['tape_channel']):
        selected['identities'][channel]=copy.deepcopy(gateway['identities'][channel])
        selected['identities'][channel]['http']=[]
    sql=gateway['identities']['investigation']
    matching=[r for r in sql['sql'] if r['server']==probe['server'] and r['database']==probe['database']]
    if len(matching)!=1:raise ValueError('RUNNER_PROBE_EXISTING_SCOPE_NOT_FOUND')
    grant=copy.deepcopy(matching[0]);grant['objects']=probe['request']['read_only_objects'];grant['controls']=[]
    # Narrowing a request cannot extend the original object allowlist.
    if not set(grant['objects'])<=set(matching[0]['objects']):raise ValueError('RUNNER_PROBE_OBJECT_SCOPE_EXPANSION')
    selected['identities']['investigation']={'sql':[grant]}
    channel='federated:'+probe['authentication']['tenant_id']+':'+probe['authentication']['client_id']+':sql'
    selected['identities'][channel]=copy.deepcopy(gateway['identities'][channel])
    selected['identities']['worker:state']['runner_captures']=[{'account_url':account,'prefix':'round-twenty/runner','run_id':run_id,'max_bytes':32*1024*1024}]
    Gateway(selected)
    config={'_estate':{'operating_mode':'BUILD_PHASE'},'fabric':{
        'auth':copy.deepcopy(probe['authentication']),
        'sql_reader':{**copy.deepcopy(probe['authentication']),'server':probe['server'],'account':probe['authentication']['principal_id']}}}
    environment={key:env[key] for key in required}
    environment.update({'INVESTIGATOR_STATE_BACKEND':'postgresql','AZURE_CLIENT_ID':identity['client_id'],
        'DIA_PLATFORM_GATEWAY_POLICY':json.dumps(selected,sort_keys=True),'DIA_CLOUD_SLIM_RECORDING_JSON':json.dumps(slim,sort_keys=True),
        'DIA_GATEWAY_HTTP_IDENTITY':'investigation','DIA_GATEWAY_SQL_IDENTITY':'investigation','DIA_GATEWAY_STATE_IDENTITY':'worker:state',
        'DIA_PLATFORM_CONTROL_RECEIPTS':'/work/platform-controls.jsonl','DIA_GATEWAY_AUDIT_FILE':'/work/gateway-audit.jsonl','DIA_LIVE_ACCESS_DISABLED':'0'})
    result={'version':'dia-runner-estate-v1','manifest':'retained-probe:'+probe['provenance']['tape_sha256'],
        'image':image,'run_id':run_id,'capture':{'account_url':account,'identity':identity,'channel':'worker:state','prefix':'round-twenty/runner'},
        'checks':{'bronze':{'kind':'probe','options':{'config':config,'database':probe['database'],'request':copy.deepcopy(probe['request']),
            'budget':{'environment':budget_environment},'max_requests':100}}},'output_root':'/work/runs','environment':environment,
        'deployment':{'resource_id':job['id'],'cli':cli}}
    if platform_cost_observation is not None:result['platform_cost_observation']=platform_cost_observation
    _safe(bytes_of(result));return result
