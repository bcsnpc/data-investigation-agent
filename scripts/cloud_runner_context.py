"""Fixed current-image retained-context preparation and replay dependencies.

Only the owner-configured platform catalog is published. There is no estate
write, permission change, arbitrary module, command, or resource provisioning.
"""
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
    context.step('install-verified-private-snapshots',lambda:install_private_snapshots(plan['manifest'],prepared))
    from investigator.estate_installation import build
    from cloud_form_worker import run_form
    from run_adaptive_investigation import local_azure_key
    manifest,workspace=build(plan['manifest'])
    try:
        model=manifest['model']
        settings={**model['credential'],'endpoint':model['endpoint'],'deployment':model['deployment']}
        with local_azure_key(settings):
            demo=context.step('family-a-demo',lambda:run_form(workspace,read(plan['options']['demo_ticket'])))
    finally:
        close=getattr(workspace,'close',None)
        if close is not None:close()
    return {'status':'DEMO_FINISHED','verification':verification,'demo':demo}
