"""Fixed current-image retained-context preparation and replay dependencies.

Only the owner-configured platform catalog is published. There is no estate
write, permission change, arbitrary module, command, or resource provisioning.
"""
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path


def read(path):
    return json.loads(Path(path).read_bytes())


def prepare_for_verification(plan, context):
    from cloud_stage_worker import prepare_phase
    from cloud_context_prepare import publish
    from investigator.shared_state import configured_state
    inputs=Path(plan['options']['inputs'])
    state=configured_state()
    if state is None:
        raise ValueError('CLOUD_POSTGRES_AUTHORITY_REQUIRED')
    # prepare_phase deliberately unsets live PG authority while deriving the
    # fresh approval and private catalog from unchanged retained definitions.
    result=context.step('retained-context-current-image',lambda:prepare_phase(inputs,context.root))
    prepared=context.root/'verification'
    for name in ('approval.json','context.json','model.json','publication-candidate.json'):
        context.record('prepared-artifact',{'name':name,'body':read(prepared/name)})
    proof=context.step('publish-retained-context',lambda:publish(state,read(prepared/'publication-candidate.json')))
    (prepared/'publication.json').write_text(json.dumps(proof,sort_keys=True),encoding='utf8')
    return prepared


def capture_configuration():
    from investigator.slim_recording import validate, CONFIG_ENV
    path=os.environ.get(CONFIG_ENV)
    if not path:
        raise ValueError('VERIFICATION_DEPENDENCY_CAPTURE_CONFIGURATION_REQUIRED')
    return validate(read(path))


PREPARED_NAMES=frozenset({'approval.json','context.json','model.json','publication-candidate.json',
    'publication.json','endpoints.json','catalog.sqlite','inventory.sqlite'})
CAPTURE_NAMES=frozenset({'code_verifier_capture.py','endpoints.json','catalog.sqlite','tape.events.jsonl',
    'context.json','inventory.sqlite','tape.json','verification_program.py','catalog-after.sqlite',
    'model.json','capture-summary.json','working/endpoints.json','working/catalog.sqlite',
    'working/verification-progress.json','working/context.json','working/inventory.sqlite','working/model.json'})


def retain_dependencies(folder,context,*,kind,phase,config=None,files=None):
    """CAS-store only the fixed verifier dependency inventory, also on failure."""
    from cloud_verification_capture import audit
    from cloud_stage_worker import audit_database
    from investigator.slim_recording import stores
    root=Path(folder)
    allowed=PREPARED_NAMES if kind=='prepared' else CAPTURE_NAMES if kind=='verification' else None
    if allowed is None:
        raise ValueError('VERIFICATION_DEPENDENCY_KIND_REQUIRED')
    if not root.exists():
        context.record('dependency-manifest',{'kind':kind,'phase':phase,'status':'NOT_CREATED','files':[]})
        return None
    selected=[]
    for path in root.rglob('*'):
        if path.is_symlink() or (getattr(path.lstat(),'st_file_attributes',0)&0x400):
            raise ValueError('VERIFICATION_DEPENDENCY_LINK_FORBIDDEN')
        if not path.is_file():
            continue
        name=path.relative_to(root).as_posix()
        if name not in allowed:
            raise ValueError('VERIFICATION_DEPENDENCY_UNDECLARED_MEMBER:'+name)
        selected.append((name,path))
    if files is None:
        files,_=stores(config or capture_configuration())
    rows=[]
    for name,path in sorted(selected):
        if path.suffix in ('.sqlite','.db'):
            audit_database(path,progress=lambda value:context.record('dependency-audit-progress',{'name':name,**value}))
        else:
            audit(path)
        ref=files.capture(path)
        rows.append({'name':name,'sha256':ref['sha256'],'bytes':ref['bytes']})
        # Retain each successful member even if a later member fails to upload.
        context.record('dependency-file',{'kind':kind,'phase':phase,**rows[-1]})
    result={'version':'cloud-verifier-cas-dependencies-v1','kind':kind,'phase':phase,
            'native_root':str(root.resolve()),'files':rows,'status':'RETAINED'}
    context.record('dependency-manifest',result)
    return result


def install_private_snapshots(manifest_path,prepared):
    """Copy the just-approved catalog; never reuse a stale private model row."""
    from contextlib import closing
    import sqlite3
    manifest=read(manifest_path)
    prepared=Path(prepared)
    targets={}
    for key in ('catalog','inventory'):
        source=(prepared/(key+'.sqlite')).resolve()
        destination=Path(manifest['storage'][key]).resolve()
        if source==destination:
            targets[key]=str(destination)
            continue
        if destination.exists():
            raise FileExistsError('RUNNER_PRIVATE_SNAPSHOT_ALREADY_EXISTS:'+key)
        destination.parent.mkdir(parents=True,exist_ok=True)
        with closing(sqlite3.connect(source.as_uri()+'?mode=ro',uri=True)) as db:
            with closing(sqlite3.connect(destination)) as target:
                db.backup(target)
        targets[key]=str(destination)
    return targets


def demo_after_verification(verification,plan,context,prepared):
    """Separate recorded normal form step after fresh reader verification."""
    if verification.get('status')!='COMPLETED' or verification.get('verification_status')!='VERIFIED':
        context.record('demo-not-admitted',{'reason':'FRESH_READER_VERIFICATION_NOT_COMPLETED','verification':verification})
        return {'status':'VERIFICATION_STOPPED','verification':verification,'demo':None}
    from cloud_verification_proof import reference
    options=plan['options']
    proof=reference(prepared,context.root/'verification-capture',options['spec'])
    return demo_from_proof({**plan,'options':{'ticket':options['demo_ticket'],'verification_proof':proof}},context,verification=verification)


@contextmanager
def retaining_native_captures(context):
    """Publish exact native CAS pointers through durable runner records."""
    from cloud_form_worker import retaining_capture_pointers
    from metadata_config import ROOT as recording_root
    root=Path(context.root);primary=None
    try:
        with retaining_capture_pointers(root,recording_root/'.local/process-tapes'):
            yield
    except BaseException as exc:
        primary=exc
        raise
    finally:
        try:
            index=root/'captures/index.json'
            paths=([index] if index.exists() else [])+sorted((root/'captures').glob('*/slim-recording.json'))
            error=root/'capture-export-error.json'
            if error.exists():paths.append(error)
            for path in paths:
                kind='native-capture-index' if path==index else 'native-capture-export-error' if path==error else 'native-capture-pointer'
                raw=path.read_bytes()
                context.record(kind,{'path':path.relative_to(root).as_posix(),
                    'sha256':hashlib.sha256(raw).hexdigest(),'body':json.loads(raw)})
        except Exception:
            # Preserve the original native/model/runtime error even if the
            # independent pointer upload also fails. Its local files remain.
            if primary is None:raise


def sealed_verification_label(reference):
    """Report the retained native FINAL; never upgrade a failed check to VERIFIED."""
    import base64
    from cloud_verification_proof import sha
    from investigator.process_tape import Tape
    path=Path(reference['capture'])/'tape.json'
    if sha(path)!=reference['capture_sha256']:raise ValueError('FRESH_VERIFICATION_SOURCE_HASH_DIFFERS')
    tape=Tape(path)
    final=json.loads(base64.b64decode(tape.events[-1]['body']))
    return {'status':final['status'],'error':final.get('error'),
        'verification_status':(final.get('result') or {}).get('status'),
        'capture_sha256':reference['capture_sha256'],'source_engine_revision':tape.engine_revision}


def demo_from_proof(plan,context,*,verification=None):
    """Normal form execution; BUILD_PHASE may label independent verification."""
    from cloud_verification_proof import validate,validate_form_scope
    options=plan['options']
    if not {'ticket','verification_proof'}<=set(options) or set(options)-{'ticket','verification_proof','verification_handling'}:
        raise ValueError('CLOUD_VERIFIED_DEMO_OPTIONS')
    handling=options.get('verification_handling','REQUIRE_VALID_PROOF')
    if handling not in ('REQUIRE_VALID_PROOF','LABEL_ONLY_BUILD_PHASE'):raise ValueError('CLOUD_VERIFICATION_HANDLING')
    label_only=handling=='LABEL_ONLY_BUILD_PHASE'
    if label_only and read(plan['manifest']).get('budgets',{}).get('operating_mode')!='BUILD_PHASE':
        raise ValueError('CLOUD_LABEL_ONLY_REQUIRES_DECLARED_BUILD_PHASE')
    warnings=[];label=None;proof=None
    def warn(stage,error):
        warning={'stage':stage,'error_type':type(error).__name__,'reason':str(error)}
        warnings.append(warning);context.record('verification-handoff-warning',warning)
    if label_only:
        try:label=context.step('retained-verification-label',lambda:sealed_verification_label(options['verification_proof']))
        except ValueError as exc:
            warn('retained-verification-label',exc)
            label={'status':'UNAVAILABLE','error':{'error_type':type(exc).__name__,'message':str(exc)},'verification_status':None}
        context.record('verification-label',label)
    try:proof=context.step('revalidate-fresh-reader-proof',lambda:validate(plan['manifest'],options['verification_proof']))
    except ValueError as exc:
        if not label_only:raise
        warn('revalidate-fresh-reader-proof',exc)
    if proof is not None:context.record('fresh-reader-proof',proof)
    prepared=Path(options['verification_proof']['prepared'])
    context.step('install-private-snapshots',lambda:install_private_snapshots(plan['manifest'],prepared))
    from investigator.estate_installation import build
    from investigator.onboarding import digest
    from cloud_form_worker import run_form,guard_preview
    from run_adaptive_investigation import local_azure_key
    manifest,workspace=build(plan['manifest'])
    try:
        if workspace.store.shared_catalog is None or workspace.agent.governor.shared is None:
            raise ValueError('CLOUD_SHARED_AUTHORITY_NOT_CONNECTED')
        pin=proof if proof is not None else {'model_pin':{'model_id':read(prepared/'model.json')['id']},
            'model_sha256':digest(read(prepared/'model.json'))}
        try:
            current=workspace.store.get(pin['model_pin']['model_id'])
            if digest(current)!=pin['model_sha256']:raise ValueError('CLOUD_VERIFIED_MODEL_CHANGED')
        except ValueError as exc:
            if not label_only:raise
            warn('current-model-handoff',exc)
        form=read(options['ticket'])
        if proof is not None:
            try:context.record('verified-form-scope',validate_form_scope(workspace,form,proof))
            except ValueError as exc:
                if not label_only:raise
                warn('form-scope-handoff',exc)
        elif label_only:warn('form-scope-handoff',ValueError('NO_VALID_READER_PROOF_FOR_SCOPE_CHECK'))
        # This wrapper binds a required reader-proof scope. In label-only mode,
        # the normal form's own scope and delivery checks remain authoritative.
        if not label_only:guard_preview(workspace,{'scope':{'constraints':proof['constraints']}},proof['model_pin']['model_id'])
        model=manifest['model']
        settings={**model['credential'],'endpoint':model['endpoint'],'deployment':model['deployment']}
        with retaining_native_captures(context):
            with local_azure_key(settings):
                demo=context.step('configured-demo',lambda:run_form(workspace,form))
    finally:
        close=getattr(workspace,'close',None)
        if close is not None:close()
    return {'status':'DEMO_FINISHED','verification':verification,'proof':proof,'demo':demo,
        'verification_handling':handling,'verification_label':label,'handoff_warnings':warnings}
