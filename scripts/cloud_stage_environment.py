"""Prepare public job environment and materialize validated worker config files.

No cloud call, credential retrieval, budget mutation or policy expansion occurs.
"""
import argparse
import json
import os
from pathlib import Path
import re

from investigator.adapters.managed_identity import validate as identity_validate
from investigator.live_gateway import Gateway
from investigator.slim_recording import validate as slim_validate


def install(*,environment=None,work=Path('/work')):
    env=os.environ if environment is None else environment
    work=Path(work);work.mkdir(parents=True,exist_ok=True)
    for name,target,validator,output in (
        ('DIA_PLATFORM_GATEWAY_POLICY','gateway-policy.json',Gateway,'DIA_GATEWAY_POLICY'),
        ('DIA_CLOUD_SLIM_RECORDING_JSON','slim-recording.json',slim_validate,'DIA_SLIM_RECORDING_CONFIG')):
        if name not in env:continue
        value=json.loads(env[name]);validator(value)
        raw=json.dumps(value,sort_keys=True,separators=(',',':')).encode()
        path=work/target
        if path.exists():
            if path.is_symlink() or path.read_bytes()!=raw:raise ValueError('CLOUD_CONFIG_FILE_ALREADY_DIFFERS')
        else:
            with path.open('xb') as destination:destination.write(raw)
        env[output]=str(path)
    if not env.get('DIA_GATEWAY_POLICY'):raise ValueError('CLOUD_GATEWAY_FILE_REQUIRED')


def build(stage,gateway,platform,slim,*,worker_id,ceiling_microdollars,margin_microdollars,
          investigation_channel='investigation',model_channel='model',state_channel='worker:state',
          job_observation=None,admission_now=None):
    Gateway(gateway);slim_validate(slim)
    identity=identity_validate(platform.get('worker_identity',platform.get('identity')))
    if stage.get('identity')!=identity or slim['identity']!=identity:
        raise ValueError('CLOUD_WORKER_IDENTITIES_DIFFER')
    if stage.get('phase') not in ('prepare','verify'):raise ValueError('CLOUD_STAGE_UNKNOWN')
    admission=None
    if stage['phase']=='verify':
        from cloud_job_admission import admit
        admission=admit(stage,job_observation,now=admission_now)
    if not isinstance(worker_id,str) or not re.fullmatch(r'[A-Za-z0-9_.:-]{1,100}',worker_id):
        raise ValueError('CLOUD_WORKER_ID_REQUIRED')
    if type(ceiling_microdollars)is not int or type(margin_microdollars)is not int or not 0<margin_microdollars<ceiling_microdollars:
        raise ValueError('EXISTING_SHARED_DOLLAR_POLICY_REQUIRED')
    pg=platform['postgres']
    if set(pg)!={'host','database','user'} or any(not isinstance(v,str) or not v for v in pg.values()):
        raise ValueError('CLOUD_POSTGRES_DECLARATION_REQUIRED')
    channels=gateway['identities']
    for channel in (stage['channel'],investigation_channel,model_channel,state_channel,slim['snapshot_channel'],slim['tape_channel']):
        if channel not in channels:raise ValueError('CLOUD_GATEWAY_CHANNEL_MISSING')
    for method,key in (('GET','input_url'),('PUT','output_url')):
        if {'method':method,'url':stage[key],'purpose':'platform_blob'} not in channels[stage['channel']].get('http',[]):
            raise ValueError('CLOUD_STAGE_ARTIFACT_GRANT_MISSING')
    for channel,container in ((slim['snapshot_channel'],'snapshots'),(slim['tape_channel'],'tapes')):
        if {'account_url':slim['account_url'],'container':container} not in channels[channel].get('platform_cas',[]):
            raise ValueError('CLOUD_CAS_GRANT_MISSING')
    if {'host':pg['host'],'database':pg['database']} not in channels[state_channel].get('platform_databases',[]):
        raise ValueError('CLOUD_STATE_GRANT_MISSING')
    env={'DIA_CLOUD_STAGE':json.dumps(stage),'DIA_PLATFORM_GATEWAY_POLICY':json.dumps(gateway),
         'DIA_CLOUD_SLIM_RECORDING_JSON':json.dumps(slim),
         'DIA_GATEWAY_HTTP_IDENTITY':investigation_channel,'DIA_GATEWAY_SQL_IDENTITY':investigation_channel,
         'DIA_GATEWAY_MODEL_IDENTITY':model_channel,'DIA_GATEWAY_STATE_IDENTITY':state_channel,
         'DIA_LIVE_ACCESS_DISABLED':'0' if gateway['live_enabled'] else '1',
         'DIA_PLATFORM_CONTROL_RECEIPTS':'/work/platform-controls.jsonl','DIA_GATEWAY_AUDIT_FILE':'/work/gateway-audit.jsonl',
         'INVESTIGATOR_STATE_BACKEND':'postgresql','INVESTIGATOR_PG_HOST':pg['host'],
         'INVESTIGATOR_PG_DATABASE':pg['database'],'INVESTIGATOR_PG_USER':pg['user'],
         'AZURE_CLIENT_ID':identity['client_id'],'INVESTIGATOR_WORKER_ID':worker_id,
         'INVESTIGATOR_MODEL_SPEND_MICRODOLLARS':str(ceiling_microdollars),
         'INVESTIGATOR_MODEL_SPEND_MARGIN_MICRODOLLARS':str(margin_microdollars),
         'INVESTIGATOR_RECORDING_CLASS':'EXACT'}
    if admission is not None:env['DIA_CLOUD_JOB_ADMISSION']=json.dumps(admission,sort_keys=True)
    return {'command':['python','/app/scripts/cloud_stage_worker.py'],
            'env':[{'name':name,'value':value} for name,value in env.items()]}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('stage','gateway','platform','slim','output','worker-id'):parser.add_argument('--'+name,required=True)
    parser.add_argument('--ceiling-microdollars',type=int,required=True)
    parser.add_argument('--margin-microdollars',type=int,required=True)
    parser.add_argument('--job-observation',help='Fresh control-plane job GET and observed_at Unix seconds; required for verify')
    args=parser.parse_args()
    output=Path(args.output)
    if output.exists():parser.error('Output exists; retain it and choose a new path')
    values=[json.loads(Path(getattr(args,name)).read_bytes()) for name in ('stage','gateway','platform','slim')]
    observation=json.loads(Path(args.job_observation).read_bytes()) if args.job_observation else None
    result=build(*values,worker_id=args.worker_id,ceiling_microdollars=args.ceiling_microdollars,
                 margin_microdollars=args.margin_microdollars,job_observation=observation)
    output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')


if __name__=='__main__':main()
