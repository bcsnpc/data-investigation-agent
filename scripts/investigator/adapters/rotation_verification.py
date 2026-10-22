"""Read proofs are produced by the existing cloud reader, never the owner.

The owner only launches the approved platform job and reads its sealed capture.
"""
import hashlib
import json
from pathlib import Path
import time


def verify(name, target, owner):
    from azure.core.credentials import AccessToken
    from azure.storage.blob import ContainerClient
    from .runner_deployment import launch
    from .runner_schedule import bind_execution
    from ..unified_runner import load
    from ..process_tape import bytes_of
    from ..run_capture import record_value
    from .connection_rotation import ControlFailure
    v=target['verification']
    if set(v)!={'runner_estate','target'}:raise ValueError('ROTATION_VERIFIER_SCHEMA')
    config=load(v['runner_estate'])
    check=config['checks'][v['target']]
    if check['kind']!='authorization-check':raise ValueError('ROTATION_READER_CHECK_REQUIRED')
    folder=Path(owner.c['checkpoint']).parent/('verification-'+name)
    folder.mkdir(parents=True,exist_ok=True)
    files=sorted(folder.glob('attempt-*.json'))
    prior=json.loads(files[-1].read_bytes()) if files else None
    if prior and prior['status']=='STARTED':
        config=prior['config']; record=files[-1]
    else:
        config['per_execution']=True;config=bind_execution(config)
        config['capture']['prefix']=config['capture']['prefix'].strip('/')
        record=folder/('attempt-'+str(len(files)+1).zfill(4)+'.json')
        prior={'status':'STARTED','config':config,'launch':launch(config,v['target']),
               'started_at':time.time()}
        record.write_text(json.dumps(prior,indent=2)+'\n',encoding='utf-8')
    class Credential:
        def get_token(self,*scopes,**kw):
            if scopes!=('https://storage.azure.com/.default',):raise ValueError('ROTATION_PLATFORM_READ_AUDIENCE')
            return AccessToken(owner.token('https://storage.azure.com/'),int(time.time())+300)
    client=ContainerClient(config['capture']['account_url'],'captures',credential=Credential(),retry_total=1)
    prefix=config['capture']['prefix']+'/'+config['run_id']+'/'
    deadline=time.monotonic()+300
    raw=None
    while time.monotonic()<deadline:
        try:
            raw=client.get_blob_client(prefix+'run-record.json').download_blob(timeout=20).readall()
            break
        except Exception as exc:
            # Do not classify access failure as ingestion delay or retry forever.
            if getattr(exc,'status_code',None) not in (None,404):
                raise ControlFailure('ROTATION_CAPTURE_READ_HTTP_'+str(getattr(exc,'status_code',None))) from None
            time.sleep(10)
    if raw is None:
        raise ControlFailure('ROTATION_READER_PROOF_PENDING:'+name)
    envelope=json.loads(raw);seal=envelope.pop('seal')
    if hashlib.sha256(bytes_of(envelope)).hexdigest()!=seal:
        raise ControlFailure('ROTATION_CAPTURE_SEAL_DIFFERS')
    proof=None; completed=False
    for ref in envelope['records']:
        leaf=ref['key'].split('/')[-1]
        blob=client.get_blob_client(config['capture']['prefix']+'/'+ref['key'])
        digest=hashlib.sha256(); retained=bytearray()
        wanted=leaf.endswith(('-native-authorization-result.json','-status.json'))
        for chunk in blob.download_blob(timeout=30).chunks():
            digest.update(chunk)
            if wanted:
                retained.extend(chunk)
                if len(retained)>1000000:raise ControlFailure('ROTATION_PROOF_BYTE_BOUND')
        if digest.hexdigest()!=ref['sha256']:raise ControlFailure('ROTATION_CAPTURE_RECORD_DIFFERS')
        if wanted:
            value=record_value(bytes(retained),ref.get('encoding'))
            if leaf.endswith('-status.json') and value.get('status')=='COMPLETED':completed=True
            if leaf.endswith('-native-authorization-result.json'):
                actual=value.get('target',{})
                if (actual.get('workspace')!=target['workspace_id'] or actual.get('model')!=target['model_id']
                        or value.get('http_status')!=200 or value.get('status')!='SUCCEEDED'):
                    raise ControlFailure('ROTATION_READER_MODEL_READ_FAILED:'+name)
                proof={'status':'PASS','evidence_id':ref['sha256'],'capture_seal':seal,
                    'run_id':config['run_id'],'execution':prior['launch']['execution_name'],
                    'workspace_id':target['workspace_id'],'model_id':target['model_id'],
                    'physical_requests':value['physical_requests'],'model_calls':0,
                    'identity_verification':'FEDERATED_READER_TOKEN_BINDING_CHECKED',
                    'verified_at_utc':time.time()}
    if not completed or proof is None:raise ControlFailure('ROTATION_READER_PROOF_NOT_COMPLETE')
    prior['status']='PASS';prior['proof']=proof
    record.write_text(json.dumps(prior,indent=2)+'\n',encoding='utf-8')
    return proof
