"""Run one pinned, recorded cloud approval verification; no ticket/model calls."""
import argparse
import hashlib
import json
import os
import time
from pathlib import Path
from investigator.estate_manifest import load,policy
from investigator.adapters.estate_installation import configuration
from investigator.onboarding import ModelStore,digest
from investigator.runtime import Runtime,fingerprint
from investigator.usage_governance import UsageGovernor
from cloud_binding_verifier import preflight
from cloud_verification_capture import Capture


def execute(manifest_path,prepared,spec_path,*,spec_sha256,session,deadline,capture):
    if os.environ.get('INVESTIGATOR_STATE_BACKEND')!='postgresql':raise ValueError('CLOUD_POSTGRES_AUTHORITY_REQUIRED')
    from investigator.live_gateway import current
    current().check_live()
    prepared=Path(prepared);spec_path=Path(spec_path);manifest=load(manifest_path);config=configuration(manifest)
    if hashlib.sha256(spec_path.read_bytes()).hexdigest()!=spec_sha256:raise ValueError('VERIFICATION_SPEC_CHANGED')
    spec=json.loads(spec_path.read_bytes())
    if spec['budgets']!=manifest['budgets']:raise ValueError('VERIFICATION_BUDGET_DIFFERS')
    approval=json.loads((prepared/'approval.json').read_bytes())
    if approval['config_hash']!=digest(config) or approval['manifest_sha256']!=hashlib.sha256(Path(manifest_path).read_bytes()).hexdigest():
        raise ValueError('CLOUD_CONFIG_APPROVAL_DIFFERS')
    if approval['engine_hash']!=fingerprint():raise ValueError('APPROVED_ENGINE_DIFFERS')
    context=json.loads((prepared/'context.json').read_bytes());model=json.loads((prepared/'model.json').read_bytes())
    planned=preflight(spec,config,context,receipt_path=prepared/'endpoints.json',manifest_budgets=manifest['budgets'])
    if not planned['admissible']:raise ValueError('VERIFICATION_BUDGET_DIFFERS')
    pinned_body={k:v for k,v in context.items() if k!='version'}
    if context.get('version')!=approval['context_id'] or digest(pinned_body)!=approval['context_hash']:
        raise ValueError('APPROVED_CONTEXT_DIFFERS')
    store=ModelStore(prepared/'catalog.sqlite',prepared/'inventory.sqlite',manifest['environment'])
    if store.shared_catalog is None or store.get(model['id'])!=model:raise ValueError('PUBLISHED_MODEL_DIFFERS')
    gov=UsageGovernor(Runtime(store,config,None,None),policy(manifest),time.time)
    if gov.shared is None:raise ValueError('SHARED_BUDGET_NOT_CONNECTED')
    if deadline<=time.time():raise ValueError('VERIFICATION_DEADLINE')
    inputs={'session_id':session,'engine_fingerprint':fingerprint(),'context_hash':digest(context),
        'model_context_id':model['context_id'],'verification_spec':spec,'deadline':deadline,
        'verification_cap':planned['verification_cap'],'native_route_contract':'declared-native-pair-v1'}
    recorder=Capture(capture,inputs=inputs,config=config,policy=policy(manifest),engine_hash=fingerprint(),
        program=Path(__file__).with_name('cloud_binding_verifier.py'),
        files={name:prepared/name for name in ('context.json','model.json','endpoints.json')},
        databases={'catalog.sqlite':store.database,'inventory.sqlite':store.inventory},
        environment=manifest['environment'],context_identity=context['version'],shared_usage=True)
    final=recorder.execute()
    # The original complete capture is retained even if publication/export fails.
    return {'status':final['status'],'accounting':final['accounting'],'error':final['error'],
            'tape':str(recorder.tape.path),'sha256':hashlib.sha256(recorder.tape.path.read_bytes()).hexdigest()}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('manifest','prepared','spec','capture'):parser.add_argument('--'+name,type=Path,required=True)
    for name in ('spec-sha256','session'):parser.add_argument('--'+name,required=True)
    parser.add_argument('--deadline',type=float,required=True)
    args=parser.parse_args()
    result=execute(args.manifest,args.prepared,args.spec,spec_sha256=args.spec_sha256,
        session=args.session,deadline=args.deadline,capture=args.capture)
    print(json.dumps(result))

if __name__=='__main__':main()
