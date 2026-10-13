"""One pinned form attempt through the normal cloud-governed workspace.

The operator prepares fixed container paths, approved config and six-stage route
evidence. This worker never relocates/reapproves a context, enables a model,
answers a question, creates a route, or changes a limit. Private SQLite files are
per-job execution/replay state; PostgreSQL owns tickets, catalog and accounting.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil


def file_hash(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def pinned(root,ref):
    if not isinstance(ref,dict) or set(ref)!={'path','sha256'}:
        raise ValueError('CLOUD_ARTIFACT_REFERENCE_REQUIRED')
    root=Path(root).resolve();relative=Path(ref['path'])
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('CLOUD_ARTIFACT_PATH_NOT_RELATIVE')
    source=(root/relative).resolve(strict=True)
    if not source.is_relative_to(root) or not source.is_file() or file_hash(source)!=ref['sha256']:
        raise ValueError('CLOUD_ARTIFACT_HASH_OR_PATH_DIFFERS')
    return source


def prepare(bundle_path,sha256,job_root):
    """Offline artifact preparation, without credential or model acquisition."""
    path=Path(bundle_path).resolve(strict=True)
    if file_hash(path)!=sha256:raise ValueError('CLOUD_BUNDLE_HASH_DIFFERS')
    bundle=json.loads(path.read_bytes());root=path.parent
    if set(bundle)!={'version','manifest','approval','index','scope','form','snapshots','model_pin'} or bundle['version']!='cloud-form-attempt-v1':
        raise ValueError('CLOUD_BUNDLE_SCHEMA_DIFFERS')
    files={key:pinned(root,bundle[key]) for key in ('manifest','approval','index','scope','form')}
    manifest=json.loads(files['manifest'].read_bytes())
    from investigator.estate_manifest import validate
    validate(manifest)
    if manifest.get('recording',{}).get('tape_class','EXACT')!='EXACT':
        raise ValueError('CLOUD_PROJECTED_PERSISTENCE_UNAVAILABLE')
    if manifest['model']['credential'].get('mode') not in ('managed_identity','key_vault'):
        raise ValueError('CLOUD_MODEL_EXPLICIT_IDENTITY_REQUIRED')
    if 'shared_accounting' in manifest['storage']:
        raise ValueError('CLOUD_SQLITE_SHARED_AUTHORITY_FORBIDDEN')
    if set(bundle['snapshots'])!={'catalog','inventory'}:
        raise ValueError('CLOUD_BOTH_PRIVATE_SNAPSHOTS_REQUIRED')
    model_pin=bundle['model_pin']
    if not isinstance(model_pin,dict) or set(model_pin)!={'model_id','context_id','context_hash'}:
        raise ValueError('CLOUD_MODEL_CONTEXT_PIN_REQUIRED')
    job_root=Path(job_root).resolve()
    if job_root.exists():raise FileExistsError('CLOUD_JOB_DIRECTORY_ALREADY_EXISTS')
    sources={key:pinned(root,ref) for key,ref in bundle['snapshots'].items()}
    targets={key:Path(manifest['storage'][key]) for key in sources}
    # Fixed absolute container paths are approved before upload. No runtime
    # rewrite can silently invalidate manifest/config/context evidence hashes.
    for target in targets.values():
        if not target.is_absolute() or not target.resolve().is_relative_to(job_root):
            raise ValueError('CLOUD_PRIVATE_STORAGE_OUTSIDE_JOB')
    if targets['catalog'].resolve()==targets['inventory'].resolve():
        raise ValueError('CLOUD_SNAPSHOT_PATH_ALIAS')
    job_root.mkdir(parents=True,exist_ok=False)
    for key,source in sources.items():
        target=targets[key];target.parent.mkdir(parents=True,exist_ok=True)
        with source.open('rb') as src,target.open('xb') as dst:shutil.copyfileobj(src,dst)
        if file_hash(target)!=bundle['snapshots'][key]['sha256']:
            raise ValueError('CLOUD_SNAPSHOT_COPY_DIFFERS')
    # The standard consumer recomputes source proofs; a supplied READY label is
    # not accepted. All evidence paths must already resolve on this container.
    from estate_readiness import current_pins
    from investigator.estate_readiness import assess_named_scope
    _,pins=current_pins(files['manifest'],files['approval'])
    index=json.loads(files['index'].read_bytes())
    readiness=assess_named_scope(manifest,pins,index,
        {'path':str(files['scope']),'sha256':bundle['scope']['sha256']},base=root)
    with (job_root/'readiness.json').open('x',encoding='utf8') as stream:json.dump(readiness,stream,indent=2)
    if readiness['status']!='READY':raise ValueError('CLOUD_ROUTE_NOT_READY:'+str(readiness.get('detail',readiness.get('reason'))))
    return bundle,files,manifest,readiness


def run_form(workspace,form):
    """One normal form pass. Refusals/questions remain terminal for this job."""
    saved=workspace.forms.submit(form)
    if saved['ticket']['state']!='INVESTIGATING':return saved
    identity=saved['ticket']['session_id']
    if not workspace.run_session_once(identity):
        raise ValueError('CLOUD_QUEUED_SESSION_NOT_OWNED_OR_ALREADY_RUN')
    with workspace.store.connect() as db:
        row=db.execute('SELECT status FROM workspace_jobs WHERE session_id=?',(identity,)).fetchone()
    if row is None or row[0]!='FINISHED':
        raise ValueError('CLOUD_WORKER_OPERATION_INTERRUPTED')
    return workspace.smart_intake.finish({'ticket_id':saved['ticket']['id'],'revision':saved['revision']})


def guard_preview(workspace,readiness,model_id):
    """Bind the actual interpreted scope before the normal start admits reads."""
    constraints=readiness['scope']['constraints']
    if constraints.get('kind')!='WHOLE_ENTITY_QUANTITY' or constraints.get('filters')!=[] or constraints.get('dimension_ids')!=[]:
        raise ValueError('CLOUD_DEMO_SCOPE_KIND_NOT_IMPLEMENTED')
    original=workspace.preview
    def preview(request):
        if (request.get('model_id')!=model_id or request.get('measure_id') not in constraints['measure_ids']
                or request.get('filters')!=[] or request.get('dimension_ids')!=[]):
            raise ValueError('CLOUD_FORM_OUTSIDE_VERIFIED_SCOPE')
        return original(request)
    workspace.preview=preview


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle',type=Path,required=True)
    parser.add_argument('--sha256',required=True)
    parser.add_argument('--job-root',type=Path,required=True)
    args=parser.parse_args(argv)
    # Never interpret an absent cloud authority as permission to use SQLite.
    if os.environ.get('INVESTIGATOR_STATE_BACKEND')!='postgresql':
        raise ValueError('CLOUD_POSTGRES_AUTHORITY_REQUIRED')
    if not os.environ.get('DIA_SLIM_RECORDING_CONFIG'):
        raise ValueError('CLOUD_DURABLE_RECORDING_REQUIRED')
    from investigator.live_gateway import current
    current().check_live()
    bundle,files,manifest,readiness=prepare(args.bundle,args.sha256,args.job_root)
    result={'status':'STARTED','bundle_sha256':args.sha256,'readiness':readiness}
    try:
        from investigator.estate_installation import build
        from investigator.onboarding import digest
        from run_adaptive_investigation import local_azure_key
        _,workspace=build(files['manifest'])
        if workspace.store.shared_catalog is None or workspace.agent.governor.shared is None:
            raise ValueError('CLOUD_SHARED_AUTHORITY_NOT_CONNECTED')
        pin=bundle['model_pin'];model=workspace.store.get(pin['model_id'])
        if not model['enabled'] or model['context_id']!=pin['context_id'] or digest(model['context'])!=pin['context_hash']:
            raise ValueError('CLOUD_PUBLISHED_MODEL_CONTEXT_DIFFERS')
        guard_preview(workspace,readiness,pin['model_id'])
        settings={**manifest['model']['credential'],'endpoint':manifest['model']['endpoint'],'deployment':manifest['model']['deployment']}
        with local_azure_key(settings):
            result['ticket']=run_form(workspace,json.loads(files['form'].read_bytes()))
        result['status']=result['ticket']['ticket']['state']
    except BaseException as exc:
        result.update(status='ERROR',error_type=type(exc).__name__)
        raise
    finally:
        # Exact transport failures remain in governed captures. Do not print
        # provider details, cache contents or credentials to container logs.
        with (args.job_root/'result.json').open('x',encoding='utf8') as stream:json.dump(result,stream,indent=2)
        print(json.dumps({'status':result['status'],'result':'result.json','error_type':result.get('error_type')}))
    return 0


if __name__=='__main__':
    try:raise SystemExit(main())
    except Exception as exc:
        # Driver/operator inspects private receipts. Arbitrary connector error
        # text must not become a second, uncontrolled cloud logging surface.
        print(json.dumps({'status':'ERROR','error_type':type(exc).__name__}))
        raise SystemExit(2)
