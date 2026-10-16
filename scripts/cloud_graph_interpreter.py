"""Once-only, model-only proposals over at most four hash-pinned definitions.

Outputs are private INFERRED proposals for review, never graph mutations.
"""
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import time
from types import SimpleNamespace

from investigator import estate_graph_contract as contract
from investigator.graph_interpreter import propose,SCHEMA
from investigator.generation_policy import error_summary,failure_usage
from investigator.planner_recording import recording,_safe

VERSION='cloud-graph-interpreter-v1'
OPTIONS={'max_output_tokens':8000,'timeout_seconds':120,'reasoning_effort':'low'}


def failure_detail(error,stage):
    """Retain local stage and safe diagnostics, never arbitrary provider prose."""
    result={**error_summary(error),'stage':stage}
    if isinstance(error,OSError):
        result.update(errno=error.errno,winerror=getattr(error,'winerror',None),
            message=os.strerror(error.errno) if isinstance(error.errno,int) else 'Local I/O operation failed')
    elif isinstance(error,ValueError) and re.fullmatch(r'[A-Z][A-Z0-9_:]{0,160}',str(error)):
        result['message']=str(error)
    else:result['message']='Failure during '+stage+'; arbitrary exception text withheld'
    return result


def tasks_from_bytes(raw,expected):
    if not isinstance(raw,bytes) or len(raw)>250_000:raise ValueError('GRAPH_BATCH_INPUT_BOUND')
    if hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('GRAPH_BATCH_INPUT_HASH_DIFFERS')
    tasks=json.loads(raw)
    if not isinstance(tasks,list) or not 1<=len(tasks)<=4:raise ValueError('GRAPH_BATCH_TASK_BOUND')
    for task in tasks:
        required={'estate','owner','code','definition_hash','source_id','observed_at','nodes'}
        if not isinstance(task,dict) or not required<=task.keys():raise ValueError('GRAPH_BATCH_TASK_SHAPE')
        for name in ('estate','owner','source_id'):contract.text(task[name])
        contract.timestamp(task['observed_at'])
        if not isinstance(task['code'],str) or not 1<=len(task['code'])<=24000:raise ValueError('GRAPH_INTERPRETER_CODE_BOUND')
        if hashlib.sha256(task['code'].encode()).hexdigest()!=task['definition_hash']:raise ValueError('GRAPH_INTERPRETER_HASH_DIFFERS')
        if not isinstance(task['nodes'],list) or not 1<=len(task['nodes'])<=128:raise ValueError('GRAPH_INTERPRETER_OBJECT_BOUND')
        ids=[]
        for node in task['nodes']:
            if set(node)!={'id','kind','label'} or node['kind'] not in contract.NODE_KINDS:raise ValueError('GRAPH_INTERPRETER_OBJECT_SHAPE')
            contract.text(node['id']);contract.text(node['label']);ids.append(node['id'])
        if len(set(ids))!=len(ids):raise ValueError('GRAPH_INTERPRETER_DUPLICATE_OBJECT')
    _safe(raw)
    return tasks


def body(request):
    from ticket_planner import provider_body
    from investigator.contract_vocabulary import instructions
    return provider_body({key:value for key,value in request.items() if key!='instructions'},
        instructions(request['instructions'],SCHEMA),SCHEMA,'retained_graph_edge_proposals',generation_options=OPTIONS)


def runtime_governor(state,environment,work):
    """Use the existing shared policy unchanged, with a private mirror only."""
    from investigator.usage_governance import UsageGovernor
    retained=state.get('usage_policy',environment)['body']
    path=Path(work)/'usage-mirror.sqlite'
    @contextmanager
    def db():
        connection=sqlite3.connect(path);connection.row_factory=sqlite3.Row
        try:
            with connection:yield connection
        finally:connection.close()
    runtime=SimpleNamespace(store=SimpleNamespace(environment=environment),db=db,
        config={'_estate':{'round':retained['round_policy']}})
    governor=UsageGovernor(runtime,retained['policy'],time.time)
    if governor.shared is None:raise ValueError('GRAPH_BATCH_SHARED_USAGE_REQUIRED')
    return governor


def publish_files(paths,files):
    result={}
    for name,path in sorted(paths.items()):
        if path.is_symlink() or not path.is_file():raise ValueError('GRAPH_BATCH_CAPTURE_NOT_REGULAR')
        _safe(path.read_bytes())
        reference=files.capture(path);files.verify(reference['sha256']);result[name]=reference
    return result


def execute(tasks,*,batch_id,input_sha256,state,governor,files,work,producer=None):
    """All external seams are existing governed producers; no estate transport."""
    if not re.fullmatch(r'[A-Za-z0-9_.:-]{1,100}',batch_id):raise ValueError('GRAPH_BATCH_ID')
    if not re.fullmatch(r'[a-f0-9]{64}',input_sha256):raise ValueError('GRAPH_BATCH_INPUT_HASH')
    check=json.dumps(tasks,ensure_ascii=False).encode();tasks_from_bytes(check,hashlib.sha256(check).hexdigest())
    from investigator.adapters.graph_interpreter_model import propose as installed_producer
    producer=producer or installed_producer
    work=Path(work);work.mkdir(parents=True,exist_ok=True)
    # Immutable shared admission prevents a retried Container Apps execution
    # from repeating a model attempt, even when the previous worker died.
    state.put('graph_interpreter_batch',batch_id,{'version':VERSION,'input_sha256':input_sha256,'tasks':len(tasks),'state':'ADMITTED'})
    results=[];captures=[];publication_errors=[];settlement_errors=[]
    prior_flag=os.environ.get('INVESTIGATOR_RECORD_PLANNER');os.environ['INVESTIGATOR_RECORD_PLANNER']='1'
    try:
        for number,task in enumerate(tasks):
            metadata={};record_path=None;reserved=False;key='graph:'+str(number);stage='EDGE_INPUT_VALIDATION'
            def provider(request,schema):
                nonlocal stage
                stage='PROVIDER_CALL'
                answer,meta=producer(request,schema,OPTIONS);metadata.update(meta);stage='EDGE_VALIDATION';return answer
            def call(request,send):
                nonlocal reserved,record_path,stage
                stage='PROVIDER_BODY_COMPILATION'
                request_body=body(request)
                characters=len(json.dumps(request_body,ensure_ascii=False,separators=(',',':')))
                if characters>64_000:raise ValueError('GRAPH_BATCH_PROVIDER_BODY_BOUND')
                stage='USAGE_RESERVATION'
                with governor.runtime.db() as db:
                    governor.reserve(db,batch_id,key,'planner',characters,output_tokens=8000)
                reserved=True
                stage='CAPTURE_INITIALIZATION'
                with recording({'session_id':batch_id,'planner_call':number+1,'call_kind':'graph_interpreter',
                    'definition_hash':task['definition_hash'],'reservation':{'input_characters':characters,'output_tokens':8000}},distinct=True,directory=work/'planner-recordings') as record:
                    if record is None:raise ValueError('GRAPH_BATCH_RECORDING_REQUIRED')
                    record_path=record.path
                    record.safe_write('compiled-provider-body.json',json.dumps(request_body,sort_keys=True).encode())
                    return send()
            error=None
            try:
                result=propose(**{key:task[key] for key in ('estate','owner','code','definition_hash','source_id','observed_at','nodes')},
                    producer=provider,model_call=call)
                results.append({'task':number,'status':'PROPOSED_FOR_REVIEW','result':result,'metadata':metadata})
            except Exception as exc:
                error=exc;results.append({'task':number,'status':'FAILED','error':failure_detail(exc,stage)})
            finally:
                if reserved:
                    usage=metadata.get('usage') if error is None else failure_usage(error) or metadata.get('usage')
                    try:
                        with governor.runtime.db() as db:governor.settle(db,batch_id,key,usage,uncertain=usage is None)
                    except Exception as exc:
                        settlement_errors.append({'task':number,'error':failure_detail(exc,'USAGE_SETTLEMENT')})
                if record_path is not None:
                    try:
                        manifest=json.loads((record_path/'manifest.json').read_bytes())
                        refs=publish_files({p.name:p for p in record_path.iterdir() if p.is_file()},files)
                        captures.append({'task':number,'files':refs,'complete':manifest.get('request_captured') is True and
                            manifest.get('response_captured') is True and manifest.get('exclusion') is None})
                    except Exception as exc:publication_errors.append({'task':number,'error':failure_detail(exc,'CAPTURE_PUBLICATION')})
            if error is not None or publication_errors or settlement_errors or not captures or not captures[-1]['complete']:break
    finally:
        if prior_flag is None:os.environ.pop('INVESTIGATOR_RECORD_PLANNER',None)
        else:os.environ['INVESTIGATOR_RECORD_PLANNER']=prior_flag
    result={'version':VERSION,'batch_id':batch_id,'input_sha256':input_sha256,
        'status':'COMPLETED' if len(results)==len(tasks) and all(r['status']=='PROPOSED_FOR_REVIEW' for r in results)
            and len(captures)==len(tasks) and all(c['complete'] for c in captures) and not publication_errors and not settlement_errors else 'STOPPED',
        'results':results,'captures':captures,'publication_errors':publication_errors,
        'settlement_errors':settlement_errors,
        'not_run':list(range(len(results),len(tasks))),'estate_reads':0,'graph_mutations':0}
    target=work/'result.json'
    raw=json.dumps(result,ensure_ascii=False,indent=2).encode();_safe(raw)
    with target.open('xb') as stream:stream.write(raw)
    reference=publish_files({'result.json':target},files)['result.json']
    return {'version':VERSION,'status':result['status'],'batch_id':batch_id,'result':reference,
        'attempted':len(results),'not_run':len(tasks)-len(results),'estate_reads':0,'graph_mutations':0}


def main():
    from investigator.source_revision import committed_revision
    from cloud_stage_environment import install
    from cloud_stage_worker import transport
    from investigator.shared_state import configured_state
    from investigator.adapters.managed_identity import model_session
    from investigator.slim_recording import stores,validate
    committed_revision()
    install()
    config=json.loads(os.environ['DIA_CLOUD_GRAPH_INTERPRETER'])
    download,upload=transport(config)
    raw=download(config['input_url'],250_000);tasks=tasks_from_bytes(raw,config['input_sha256'])
    state=configured_state()
    if state is None or state.backend!='postgresql':raise ValueError('CLOUD_POSTGRES_REQUIRED')
    work=Path('/work')/'graph-interpreter';work.mkdir(parents=True,exist_ok=True)
    governor=runtime_governor(state,config['environment'],work)
    _,files=stores(validate(json.loads(Path(os.environ['DIA_SLIM_RECORDING_CONFIG']).read_bytes())))
    with model_session(config['model']):
        summary=execute(tasks,batch_id=config['batch_id'],input_sha256=config['input_sha256'],state=state,
            governor=governor,files=files,work=work)
    upload(config['output_url'],json.dumps(summary,sort_keys=True).encode())
    print(json.dumps(summary))


if __name__=='__main__':main()
