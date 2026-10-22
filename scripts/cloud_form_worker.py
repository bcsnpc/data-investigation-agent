"""One pinned form attempt through the normal cloud-governed workspace.

The operator prepares fixed container paths, approved config and six-stage route
evidence. This worker never relocates/reapproves a context, enables a model,
answers a question, creates a route, or changes a limit. Private SQLite files are
per-job execution/replay state; PostgreSQL owns tickets, catalog and accounting.
"""
import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
from uuid import UUID


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


def capture_ids(root):
    """List local capture identities only; never traverse their snapshots."""
    root=Path(root)
    if not root.exists():return set()
    return {entry.name for entry in root.iterdir()}


def _plain(path):
    info=path.lstat()
    if stat.S_ISLNK(info.st_mode) or getattr(info,'st_file_attributes',0)&0x400:
        raise ValueError('CLOUD_CAPTURE_LINK_FORBIDDEN')
    return info


def export_capture_pointers(root,before,job_root):
    """Retain native pointers byte-for-byte, including explicit incomplete rows.

    No remote read or database copy belongs here. A copied pointer records the
    publication receipt; actual CAS availability and replay remain separate.
    """
    from investigator.process_tape import bytes_of,sha,validate_event,SUPPORTED_VERSIONS
    from investigator.slim_recording import VERSION,validate
    root=Path(root);destination=Path(job_root)/'captures'
    destination.mkdir(exist_ok=False)
    rows=[]
    for identity in sorted(capture_ids(root)-before):
        row={'id':identity,'status':'UNINSPECTED'};rows.append(row)
        directory=root/identity
        try:
            if str(UUID(identity))!=identity:raise ValueError('CLOUD_CAPTURE_ID_INVALID')
            if not stat.S_ISDIR(_plain(directory).st_mode):raise ValueError('CLOUD_CAPTURE_NOT_DIRECTORY')
            tape_path=directory/'tape.json';pointer=directory/'slim-recording.json'
            # Export a present pointer even when validation below fails, so a
            # broken publication never disappears from the evidence inventory.
            receipt=None
            if pointer.exists():
                if not stat.S_ISREG(_plain(pointer).st_mode) or pointer.stat().st_size>1_000_000:
                    raise ValueError('CLOUD_CAPTURE_POINTER_BOUND')
                body=pointer.read_bytes();target=destination/identity/'slim-recording.json';target.parent.mkdir()
                with target.open('xb') as output:output.write(body)
                row['pointer']={'path':target.relative_to(job_root).as_posix(),
                    'sha256':hashlib.sha256(body).hexdigest(),'bytes':len(body)}
                receipt=json.loads(body)
            if not tape_path.exists():row['status']='MISSING_TAPE';continue
            if not stat.S_ISREG(_plain(tape_path).st_mode):raise ValueError('CLOUD_CAPTURE_TAPE_NOT_FILE')
            try:
                from investigator.streaming_tape import load,digest
                sealed=load(tape_path)
                # Full Tape validation requires retired SQLite snapshots. This
                # export validates only the native sealed envelope/event journal;
                # CAS restoration and complete engine replay remain separate.
                if (sealed.get('version') not in SUPPORTED_VERSIONS
                        or sealed.get('seal')!=digest({k:v for k,v in sealed.items() if k!='seal'})):
                    raise ValueError('CLOUD_CAPTURE_TAPE_SEAL')
                events=sealed.get('events',[])
                if not events or events[0]['kind']!='BOOTSTRAP' or events[-1]['kind']!='FINAL':
                    raise ValueError('CLOUD_CAPTURE_TAPE_INCOMPLETE')
                for ordinal,event in enumerate(events,1):validate_event(event,ordinal)
                journal=tape_path.with_suffix('.events.jsonl')
                if journal.exists():
                    if not stat.S_ISREG(_plain(journal).st_mode):raise ValueError('CLOUD_CAPTURE_JOURNAL_NOT_FILE')
                    with journal.open('rb') as source:
                        count=0
                        for count,line in enumerate(source,1):
                            if count>len(events) or json.loads(line)!=events[count-1]:
                                raise ValueError('CLOUD_CAPTURE_JOURNAL_DIFFERS')
                        if count!=len(events):raise ValueError('CLOUD_CAPTURE_JOURNAL_DIFFERS')
            except Exception as error:
                row.update(status='UNSEALED_OR_INVALID_TAPE',error_type=type(error).__name__,reason=str(error));continue
            row['source_seal']=sealed['seal']
            row['tape_validation']='SEALED_ENVELOPE_AND_EVENT_JOURNAL_ONLY'
            row['tape_sha256']=file_hash(tape_path)
            if receipt is None:
                row['status']='SEALED_WITHOUT_PUBLICATION_POINTER';continue
            if (receipt.get('version')!=VERSION or receipt.get('restoration_verified') is not True
                    or receipt.get('source_seal')!=sealed['seal']):
                raise ValueError('CLOUD_CAPTURE_POINTER_INVALID')
            validate(receipt['configuration'])
            reference=receipt.get('bundle',{})
            from investigator.artifact_store import hash_id
            hash_id(reference.get('sha256'))
            if set(reference)!={'sha256','bytes'} or type(reference['bytes']) is not int or reference['bytes']<0:
                raise ValueError('CLOUD_CAPTURE_BUNDLE_REFERENCE_INVALID')
            row.update(status='NATIVE_POINTER_EXPORTED',bundle_sha256=reference['sha256'],engine_replay='NOT_RUN')
        except Exception as error:
            row.update(status='CAPTURE_EXPORT_INVALID',error_type=type(error).__name__,reason=str(error))
    result={'version':'cloud-native-capture-index-v1','count':len(rows),
            'status':'NO_NEW_CAPTURES' if not rows else 'INDEXED',
            'native_pointers':sum(row['status']=='NATIVE_POINTER_EXPORTED' for row in rows),
            'incomplete':sum(row['status']!='NATIVE_POINTER_EXPORTED' for row in rows),'captures':rows}
    with (destination/'index.json').open('x',encoding='utf8') as output:json.dump(result,output,indent=2)
    return result


@contextmanager
def retaining_capture_pointers(job_root,capture_root):
    before=capture_ids(capture_root);primary=None
    try:yield
    except BaseException as error:primary=error;raise
    finally:
        try:export_capture_pointers(capture_root,before,job_root)
        except Exception as error:
            # A disk/export problem must not replace the actual model/worker
            # failure. Keep a separate private diagnostic whenever disk permits.
            try:
                with (Path(job_root)/'capture-export-error.json').open('x',encoding='utf8') as output:
                    json.dump({'status':'CAPTURE_EXPORT_FAILED','error_type':type(error).__name__,
                               'primary_error_type':type(primary).__name__ if primary else None},output)
            except Exception:pass
            if primary is None:raise


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
        from investigator.run_recording import ROOT as recording_root
        with retaining_capture_pointers(args.job_root,recording_root/'.local/process-tapes'):
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
