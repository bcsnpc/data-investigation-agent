"""Revalidate a sealed fresh reader proof before a normal cloud form run.

No replay-before-live gate, READY label, code execution or profile publication.
"""
import base64,hashlib,json,re
from pathlib import Path
from investigator.onboarding import digest

VERSION='fresh-cloud-reader-proof-v1'


def sha(path):
    path=Path(path)
    if path.is_symlink() or getattr(path.lstat(),'st_file_attributes',0)&0x400:raise ValueError('FRESH_VERIFICATION_SOURCE_LINK')
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def reference(prepared,capture,spec):
    return {'version':VERSION,'prepared':str(prepared),'capture':str(capture),'spec':str(spec),
        'capture_sha256':sha(Path(capture)/'tape.json'),'approval_sha256':sha(Path(prepared)/'approval.json'),
        'spec_sha256':sha(spec)}


def validate(manifest_path,proof):
    expected={'version','prepared','capture','spec','capture_sha256','approval_sha256','spec_sha256'}
    if not isinstance(proof,dict) or set(proof)!=expected or proof['version']!=VERSION:
        raise ValueError('FRESH_VERIFICATION_PROOF_REFERENCE_REQUIRED')
    for name in ('capture_sha256','approval_sha256','spec_sha256'):
        if not isinstance(proof[name],str) or not re.fullmatch('[a-f0-9]{64}',proof[name]):raise ValueError('FRESH_VERIFICATION_HASH_REQUIRED')
    prepared=Path(proof['prepared']);capture=Path(proof['capture']);spec_path=Path(proof['spec']);tape_path=capture/'tape.json'
    if sha(tape_path)!=proof['capture_sha256'] or sha(prepared/'approval.json')!=proof['approval_sha256'] or sha(spec_path)!=proof['spec_sha256']:
        raise ValueError('FRESH_VERIFICATION_SOURCE_HASH_DIFFERS')
    from investigator.process_tape import Tape
    from investigator.estate_manifest import load,policy
    from investigator.adapters.estate_installation import configuration
    from investigator.runtime import fingerprint
    from investigator.source_revision import committed_revision
    from investigator.lineage_binding import revalidate_verification,seal
    manifest=load(manifest_path);config=configuration(manifest)
    approval=json.loads((prepared/'approval.json').read_bytes());context=json.loads((prepared/'context.json').read_bytes());model=json.loads((prepared/'model.json').read_bytes())
    scan={k:v for k,v in context.items() if k!='version'}
    if (approval['manifest_sha256']!=sha(manifest_path) or approval['config_hash']!=digest(config)
            or approval['engine_hash']!=fingerprint() or approval['context_id']!=context['version']
            or approval['context_hash']!=digest(scan)):
        raise ValueError('FRESH_VERIFICATION_APPROVAL_PIN_DIFFERS')
    tape=Tape(tape_path);boot=tape.bootstrap;state=boot['state'];inputs=state['inputs']
    if (boot['entry_point']!='code_verifier' or boot['engine_hash']!=fingerprint()
            or tape.engine_revision!=committed_revision() or state.get('engine_revision')!=tape.engine_revision
            or boot['config']!=config or boot['usage_policy']!=policy(manifest) or state.get('environment')!=manifest['environment'] or inputs.get('engine_fingerprint')!=fingerprint()
            or inputs.get('context_hash')!=digest(context) or inputs.get('model_context_id')!=model['context_id']
            or inputs.get('native_route_contract')!='declared-native-pair-v1'):
        raise ValueError('FRESH_VERIFICATION_RUNTIME_PIN_DIFFERS')
    if (model.get('enabled')is not True or model['context'].get('id')!=model['context_id']
            or model['context'].get('model_id')!=model['id'] or model['context'].get('scan_id')!=context['version']):
        raise ValueError('FRESH_VERIFICATION_MODEL_CONTEXT_PIN_DIFFERS')
    spec=json.loads(spec_path.read_bytes())
    if inputs['verification_spec']!=spec:raise ValueError('FRESH_VERIFICATION_SPEC_DIFFERS')
    from cloud_verification_capture import CONTRACT
    if state.get('capture_contract')!=CONTRACT:raise ValueError('FRESH_VERIFICATION_CAPTURE_CONTRACT')
    # Fixed producer dependencies are hash checked, never imported/executed here.
    members=state['members']
    required={'catalog.sqlite','inventory.sqlite','context.json','model.json','endpoints.json','verification_program.py','code_verifier_capture.py'}
    if set(members)!=required:raise ValueError('FRESH_VERIFICATION_DEPENDENCY_INVENTORY')
    for name,expected_hash in members.items():
        if sha(capture/name)!=expected_hash:raise ValueError('FRESH_VERIFICATION_DEPENDENCY_HASH_DIFFERS')
    for name in ('context.json','model.json','endpoints.json','inventory.sqlite'):
        if sha(prepared/name)!=members[name]:raise ValueError('FRESH_VERIFICATION_PREPARED_SOURCE_DIFFERS')
    for stored,installed in (('verification_program.py','cloud_binding_verifier.py'),('code_verifier_capture.py','cloud_verification_capture.py')):
        if members[stored]!=sha(Path(__file__).with_name(installed)):raise ValueError('FRESH_VERIFICATION_PRODUCER_DIFFERS')
    if json.loads((capture/'model.json').read_bytes())!=model:raise ValueError('FRESH_VERIFICATION_MODEL_DIFFERS')
    final=json.loads(base64.b64decode(tape.events[-1]['body']));result=final.get('result') or {}
    if final.get('status')!='COMPLETED' or result.get('status')!='VERIFIED':raise ValueError('FRESH_VERIFICATION_NOT_COMPLETED')
    if final.get('accounting',{}).get('pending_reservations')!=0:raise ValueError('FRESH_VERIFICATION_RESERVATIONS_PENDING')
    from cloud_binding_verifier import preflight
    planned=preflight(spec,config,context,receipt_path=prepared/'endpoints.json',manifest_budgets=manifest['budgets'])
    if (not planned['admissible'] or result.get('verification_reads')!=planned['verification_reads_needed']
            or result.get('plan',{}).get('verification_reads_needed')!=planned['verification_reads_needed']
            or result['plan'].get('verification_cap')!=planned['verification_cap'] or result.get('profile_published') is not False):
        raise ValueError('FRESH_VERIFICATION_CONSERVATION_FAILED')
    expected_ids=[seal(p)for p in spec['proposals']];witnesses=result.get('witnesses',[])
    actual_ids=[seal(v['proposal'])for v in witnesses]
    if len(set(expected_ids))!=len(expected_ids) or len(set(actual_ids))!=len(actual_ids) or sorted(expected_ids)!=sorted(actual_ids):
        raise ValueError('FRESH_VERIFICATION_WITNESS_COVERAGE_DIFFERS')
    for original in witnesses:
        checked=revalidate_verification(original)
        if checked['status']!='VERIFIED' or checked['context']!=model['context_id']:raise ValueError('FRESH_VERIFICATION_WITNESS_PIN_DIFFERS')
        for observation in checked['observations']:
            evidence=observation.get('evidence',{})
            if observation.get('status')!='COMPLETED' or not evidence.get('id') or evidence.get('surface_report_binding')!='VALUE_QUERY':
                raise ValueError('FRESH_VERIFICATION_NATIVE_RECEIPT_MISSING')
    native=result['native_route'];observations=native['observations']
    comparisons=[o for o in observations if o.get('comparison_status')=='CROSS_SURFACE_VERIFIED']
    if len(comparisons)!=1:raise ValueError('FRESH_VERIFICATION_NATIVE_BOUNDARY_COUNT')
    comparison=comparisons[0];ids={comparison['id'],comparison['upper_evidence_id'],comparison['lower_evidence_id']}
    route={'selected_observations':[o for o in observations if o['id']in ids],'read_receipts':native['process_read_receipts'],
        'captured_run_tape':str(tape_path.resolve()),'captured_run_tape_sha256':proof['capture_sha256'],'session_id':native['id']}
    from investigator.adapters.microsoft_readiness import validate_declared_route
    checked_route=validate_declared_route(route,manifest=manifest,scan=scan)
    return {'version':VERSION,'status':'PROOF_REVALIDATED','capture_sha256':proof['capture_sha256'],
        'model_pin':{'model_id':model['id'],'context_id':model['context_id'],'context_hash':digest(model['context'])},
        'model_sha256':digest(model),'witness_count':len(witnesses),'verification_reads':result['verification_reads'],'verification_cap':planned['verification_cap'],
        'native_route':checked_route,'constraints':checked_route['constraints'],'profile_published':False,
        'runtime_route':'STATIC_DECLARED','inference_enabled_locations':sum(b['may_infer_from_code']for b in manifest['lineage'].get('code_locations',[])),
        'readiness':'NOT_ASSESSED','snapshot_limitation':'Historical bounded witnesses do not establish current or aligned served versions.'}



def validate_form_scope(workspace,form,proof):
    """Resolve explicit form picks using retained definitions, without a model."""
    from investigator.question_intake import snapshot
    from investigator.form_intake import resolve
    models=snapshot(workspace)['models']
    if form.get('version')=='intake-questionnaire-v1':
        if form.get('screenshot_review_id'):raise ValueError('FRESH_VERIFICATION_SCREENSHOT_SCOPE_UNRESOLVED')
        from investigator.intake_questionnaire import to_form
        form=to_form(form,models,review=None)
    bound=resolve(form,models,workspace.intake_configuration)
    scope=bound.get('scope') or {};constraints=proof['constraints']
    if (bound['status']!='BOUND' or scope.get('model_id')!=proof['model_pin']['model_id']
            or scope.get('measure_id')not in constraints['measure_ids'] or scope.get('filters')!=[]
            or scope.get('cell_mode')!='UNGROUPED'):
        raise ValueError('FRESH_VERIFICATION_FORM_OUTSIDE_PROVEN_SCOPE')
    model=next(m for m in models if m['id']==scope['model_id'])
    visual=next(v for v in model['visuals']if v['target_id']==scope['target_id'])
    declared=visual.get('declared_scopes',{}).get(scope['measure_id'])
    if not declared or declared.get('state')!='COMPLETE' or declared.get('restrictions')!=[]:
        raise ValueError('FRESH_VERIFICATION_DECLARED_SCOPE_DIFFERS')
    return {'model_id':scope['model_id'],'measure_id':scope['measure_id'],'target_id':scope['target_id'],
        'scope':'WHOLE_ENTITY_QUANTITY','source':'RETAINED_FORM_DEFINITIONS'}
