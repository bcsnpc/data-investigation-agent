"""Typed, zero-live replay entrypoints. Replay coverage is stated explicitly."""
import importlib.util
import json
import hashlib
from pathlib import Path
from .process_tape import Tape,active,bytes_of


def boundary(folder,expected_image):
    """Scan boundary replay only; never claims graph recomputation coverage."""
    root=Path(folder);record=json.loads((root/'run-record.json').read_bytes())
    claimed=record.pop('seal',None)
    if claimed!=hashlib.sha256(bytes_of(record)).hexdigest():raise ValueError('RUN_RECORD_SEAL_DIFFERS')
    if record.get('version')!='dia-run-record-v1':raise ValueError('RUN_RECORD_VERSION')
    first=None;last=None;count=0
    for ordinal,ref in enumerate(record['records'],1):
        key=Path(ref['key'])
        if len(key.parts)!=2 or key.parts[0]!=record['run_id'] or not key.name.startswith(f'{ordinal:08d}-'):raise ValueError('RUN_RECORD_MEMBER_ORDER')
        raw=(root/key.name).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=ref['sha256']:raise ValueError('RUN_RECORD_MEMBER_CHANGED')
        from .run_capture import record_value
        value=record_value(raw,ref.get('encoding'))
        if first is None:first=value
        last=value;count+=1
    if first['state'].get('runner_image')!=expected_image:raise ValueError('RUN_REPLAY_IMAGE_DIFFERS')
    if last.get('status')!='COMPLETED' or last.get('partial') is not False:raise ValueError('RUN_RECORD_PARTIAL')
    return {'matched':True,'coverage':'BOUNDARY_ONLY','graph_recomputed':False,'network_requests':0,
            'records':count,'limit':'Sealed scan responses and results replayed; graph mutation semantics were not recomputed.'}


def probe(path):
    from fabric_sql_surface import read
    from .physical_reads import scope,guard_scope
    tape=Tape(path)
    if tape.bootstrap['entry_point']!='runner_probe':raise ValueError('RUNNER_PROBE_CAPTURE_CONTRACT_REQUIRED')
    from .runtime import fingerprint
    from .source_revision import committed_revision
    if tape.bootstrap['engine_hash']!=fingerprint() or tape.bootstrap['state']['engine_revision']!=committed_revision():raise ValueError('RUNNER_REPLAY_IMAGE_RUNTIME_DIFFERS')
    options=tape.bootstrap['state']['runner_probe']
    # The same compiled request and physical worker protocol run again. A
    # replaying Tape never launches a worker or acquires a token.
    with active(tape),scope(lambda kind,fn:fn()),guard_scope(lambda value:None):
        actual=read(options['config'],options['database'],options['request'])
        tape.finish(actual)
    return {'matched':True,'coverage':'NATIVE_PROBE_AND_PHYSICAL_PROTOCOL','network_requests':0,'result':actual}


def replay(options,output):
    kind=options.get('format','verification')
    if kind=='value-verification':
        from cloud_value_execution import replay as execute
        return execute(options['tape'])
    if kind=='verification':
        from cloud_verification_capture import replay as execute
        return execute(options['capture'],output)
    if kind=='probe':return probe(options['tape'])
    if kind=='scan-boundary':return boundary(options['capture'],options['image'])
    if kind=='investigation':
        # The existing pinned engine driver disables sockets in its child and
        # checks all worker/planner bytes and structured final state.
        root=Path(__file__).resolve().parents[2]
        source=root/'acceptance/unknown_domain/recorded_engine.py'
        spec=importlib.util.spec_from_file_location('runner_recorded_engine',source)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        # A slim pointer may need authenticated platform CAS restoration. Do
        # that in the parent; the isolated replay child remains socket-disabled
        # and receives a raw tape with all exact dependencies already present.
        from .slim_recording import materialize
        with materialize(options['tape']) as restored:
            return module.replay_revision(restored,output,options['engine_revision'],estate_manifest=options.get('manifest'))
    raise ValueError('RUNNER_REPLAY_FORMAT_UNSUPPORTED:'+str(kind))
