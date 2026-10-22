"""Typed cloud value route; replay recomputes scope/compiler over exact responses.

Replay coverage deliberately excludes worker/guard/budget protocol replay.
Those live controls remain independently retained by the runner.
"""
import copy
import base64
import hashlib
import json
from pathlib import Path

from cloud_value_verifier import build, execute
from investigator import process_tape as journal
from investigator.onboarding import digest

COVERAGE='VALUE_COMPILER_AND_RECORDED_RESPONSES'


def _file(ref):
    if not isinstance(ref,dict) or set(ref)!={'path','sha256'}:raise ValueError('VALUE_INPUT_REFERENCE_REQUIRED')
    raw=Path(ref['path']).read_bytes()
    if len(raw)>32*1024*1024 or hashlib.sha256(raw).hexdigest()!=ref['sha256']:raise ValueError('VALUE_INPUT_HASH_DIFFERS')
    from investigator.planner_recording import _safe
    _safe(raw)
    return json.loads(raw)


def _compile(model,mappings,options):
    result=build(model,options['measure_id'],options['target_id'],mappings,tolerance=options['tolerance'])
    # Supported query-bound principal self-report; INFO metadata is deliberately
    # not added. A missing/mismatching identity can never earn confidence.
    native=result['native_statement']
    result['native_statement']='EVALUATE ADDCOLUMNS('+native.removeprefix('EVALUATE ')+',"surface_identity",USERPRINCIPALNAME())'
    from investigator.live_gateway import validate_dax
    validate_dax(result['native_statement'])
    return result


def _evaluate(plan,transport,retain):
    def native(statement):
        request={'layer':'SEMANTIC','statement':statement}
        return journal.bounded_call('mapped-value-read',request,lambda:transport(request))
    def lower(compiled):
        request={'layer':compiled['layer_id'],'statement':compiled['statement'],'compiled':compiled}
        return journal.bounded_call('mapped-value-read',request,lambda:transport(request))
    return execute(plan,native,lower,retain)


def _native(config,model,query):
    from metadata_config import worker_configuration
    from run_native_diagnostic import execute as native_execute,worker_failure
    from investigator.live_gateway import GatewayDenied
    from investigator.usage_governance import UsageHold
    from investigator.process_debugging import attest_surface
    request={'workspace':model['workspace'],'native_model_id':model['native_id'],'query':query,'requires_native_reader':True}
    projected=worker_configuration(config,request);fabric=projected['fabric'];reader=fabric['native_reader']
    declared={'identity':reader['account'],'engine':'OLAP Server','connection':model['workspace'],'object':model['native_id']}
    try:
        raw=native_execute(request,fabric['auth']['tenant_id'],reader,fabric['auth'])
        response=json.loads(raw,parse_float=str);rows=response['results'][0]['tables'][0]['rows']
        if len(rows)!=1:raise ValueError('NATIVE_SCALAR_RESPONSE_REQUIRED')
        row=rows[0];keys=[key for key in ('quantity','[quantity]') if key in row]
        if len(keys)!=1:raise ValueError('NATIVE_QUANTITY_FIELD_NOT_OBTAINED')
        identities=[row[key] for key in ('surface_identity','[surface_identity]') if key in row]
        reported={'identity':identities[0]} if len(identities)==1 and isinstance(identities[0],str) else None
        attestation={'declared':declared,'reported':reported,'reportable':['identity'],'binding':'VALUE_QUERY'}
        return {'status':'SUCCEEDED','value':row[keys[0]],'provider_response':raw,'request':request,
            'attestation':attestation,'attestation_result':attest_surface(declared,reported,['identity']),
            'snapshot':{'query_bound':False},'confidence_awarded':False}
    except (GatewayDenied,UsageHold):raise
    except Exception as error:
        return {'status':'FAILED','error':worker_failure(error),'request':request}


def _lower(config,compiled):
    from fabric_sql_surface import read,declared
    from investigator.live_gateway import validate_sql,_object,GatewayDenied
    from investigator.usage_governance import UsageHold
    from investigator.process_debugging import attest_surface
    endpoint=compiled['endpoint']
    if endpoint['surface']!='FABRIC_SQL':return {'status':'FAILED','error':{'reason':'LOWER_SURFACE_UNSUPPORTED'}}
    if endpoint['server']!=config['fabric']['sql_reader']['server']:
        return {'status':'FAILED','error':{'reason':'MAPPED_SERVER_DIFFERS_FROM_READER'}}
    names=['['+obj['schema'].replace(']',']]')+'].['+obj['table'].replace(']',']]')+']' for obj in compiled['mapping']['objects'].values()]
    validate_sql(compiled['statement'],{_object(name) for name in names})
    request={'query':compiled['statement'],'read_only_objects':sorted(set(names)),
             'max_rows':2,'result_columns':['quantity','duplicate_lookup_keys']}
    try:
        body=read(config,endpoint['database'],request);rows=body['rows']
        if len(rows)!=1 or set(rows[0])!={'quantity','duplicate_lookup_keys'}:raise ValueError('LOWER_SCALAR_RESPONSE_REQUIRED')
        surface=declared(config['fabric']['sql_reader'],endpoint['database']);reported=body.get('surface_report')
        return {'status':'SUCCEEDED','value':rows[0]['quantity'],'duplicate_lookup_keys':int(rows[0]['duplicate_lookup_keys']),
            'provider_response':body,'request':request,'attestation':{'declared':surface,'reported':reported,'reportable':['identity','engine','object'],'binding':'VALUE_QUERY'},
            'attestation_result':attest_surface(surface,reported,['identity','engine','object']),
            'snapshot':{'query_bound':False},'confidence_awarded':False}
    except (GatewayDenied,UsageHold):raise
    except Exception as error:
        return {'status':'FAILED','error':{'type':type(error).__name__,'stage':getattr(error,'stage',None),
            'sql_error_number':getattr(error,'error_number',None)},'request':request}


def run(plan,context):
    from investigator.estate_manifest import load
    from investigator.adapters.estate_installation import configuration
    from investigator.shared_state import configured_state
    from scan_estate_graph import Meter
    from investigator.physical_reads import scope,guard_scope
    from investigator.runtime import fingerprint
    from investigator.source_revision import committed_revision
    options=plan['options']
    fields={'model','mappings','measure_id','target_id','tolerance','budget','max_requests'}
    if not fields<=set(options)or set(options)-fields-{'graph_binding'}:raise ValueError('VALUE_RUN_OPTIONS_DIFFER')
    if type(options['max_requests'])is not int or not 1<=options['max_requests']<=100:raise ValueError('VALUE_PHYSICAL_CAP_REQUIRED')
    manifest=load(plan['manifest']);config=configuration(manifest)
    model=_file(options['model']);mappings=_file(options['mappings']);compiled=_compile(model,mappings,options)
    graph_binding=_file(options['graph_binding'])if 'graph_binding'in options else None
    context.record('mapped-value-plan',compiled)
    state=configured_state()
    if state is None:raise ValueError('VALUE_SHARED_BUDGET_REQUIRED')
    meter=Meter(state,options['budget'],options['max_requests'])
    bootstrap={'entry_point':'value_verifier','context_identity':model['context_id'],'config':config,'profile':{},'usage_policy':None,
        'engine_hash':fingerprint(),'state':{'engine_revision':committed_revision(),'model':model,'mappings':mappings,
            'options':{k:options[k] for k in ('measure_id','target_id','tolerance')},'compiled_hash':digest(compiled),'coverage':COVERAGE}}
    tape=journal.Tape(context.root/'value-tape.json',bootstrap=bootstrap)
    def metered(call):
        if meter.used>=options['max_requests']:raise ValueError('VALUE_PHYSICAL_CAP_REACHED')
        return meter(call)
    def transport(request):
        # The bounded response tape explicitly does not claim replay of live
        # governor/worker internals. Real live controls still run and are retained.
        with journal.active(None):
            if request['layer']=='SEMANTIC':result=metered(lambda:_native(config,model,request['statement']))
            else:
                with scope(lambda kind,call:metered(call)):
                    result=metered(lambda:_lower(config,request['compiled']))
            result['observed_at']=journal.utc_now()
            context.record('mapped-value-query-receipt',{'layer':request['layer'],'result':result})
            return result
    try:
        before=meter.usage.snapshot()
        with journal.active(tape),guard_scope(lambda guard:context.record('mapped-value-guard',guard)):
            result=_evaluate(compiled,transport,lambda receipt:context.record('mapped-value-observation',receipt))
            result.update(confidence_awarded=False,coverage=COVERAGE)
            tape.finish(result)
        raw=tape.path.read_bytes()
        from investigator.planner_recording import _safe
        _safe(raw)
        tape_hash=hashlib.sha256(raw).hexdigest()
        context.record('mapped-value-tape',{'sha256':tape_hash,'bytes':len(raw),
            'body_base64':base64.b64encode(raw).decode('ascii'),'coverage':COVERAGE})
        result.update(physical_requests=meter.used,before=before,after=meter.usage.snapshot(),model_calls=0,
            tape_sha256=tape_hash,tape=str(tape.path),
            grade='NOT_AWARDED_REQUIRES_TRUSTED_GRAPH_RESOLVER')
        from investigator.graph_value_bridge import capability,attach
        result['proof_attachment_capability']=capability(compiled)
        if graph_binding is not None and result.get('status')=='VALUES_AGREE_UNDER_MAPPING':
            try:
                attachment=attach(state=state,environment=manifest['environment'],model=model,plan=compiled,result=result,binding=graph_binding,
                    retain=context.record,observed_at=journal.utc_now())
            except (ValueError,KeyError)as error:
                attachment={'status':'REFUSED','confidence_awarded':False,'reason':str(error)}
            result['graph_attachment']=attachment
            result['confidence_awarded']=attachment['confidence_awarded']
            result['grade']=attachment['status']if attachment['confidence_awarded']else 'NOT_AWARDED:'+attachment['reason']
            result['graph_proof_replay_coverage']='NOT_INCLUDED_IN_COMPILER_RESPONSE_REPLAY; proof bundle separately retained'
        elif graph_binding is not None:
            result['graph_attachment']={'status':'REFUSED','confidence_awarded':False,'reason':result.get('reason','VALUE_OBSERVATION_NOT_SUCCESSFUL')}
        context.record('mapped-value-result',result)
        return result
    finally:meter.close()


def replay(path):
    from investigator.runtime import fingerprint
    from investigator.source_revision import committed_revision
    tape=journal.Tape(path);bootstrap=tape.bootstrap;state=bootstrap['state']
    if bootstrap['entry_point']!='value_verifier' or state['coverage']!=COVERAGE:raise ValueError('VALUE_REPLAY_CONTRACT_REQUIRED')
    if bootstrap['engine_hash']!=fingerprint() or state['engine_revision']!=committed_revision():raise ValueError('VALUE_REPLAY_IMAGE_DIFFERS')
    compiled=_compile(state['model'],state['mappings'],state['options'])
    if digest(compiled)!=state['compiled_hash']:raise ValueError('VALUE_REPLAY_COMPILER_DIFFERS')
    def forbidden(request):raise AssertionError('VALUE_REPLAY_LIVE_FORBIDDEN')
    with journal.active(tape):
        result=_evaluate(compiled,forbidden,lambda receipt:None)
        result.update(confidence_awarded=False,coverage=COVERAGE)
        tape.finish(result)
    return {'matched':True,'coverage':COVERAGE,'result':result,'network_requests':0,
        'limit':'Compiler and recorded data responses replayed; worker, permission guard and shared-budget protocols are not replayed.'}
