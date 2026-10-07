"""Evaluate only the MODEL extractor, before any binding verification/read."""
import copy
import time
from .code_sources import normalize
from .onboarding import digest
from . import process_tape as journal
from .code_proposal_budget import Proposer
from .transformation_reader import model_schema,validate_model_candidates
from .generation_policy import error_summary
from .usage_governance import UsageHold


def run_case(agent,golden,case,provider,path,session_id):
    unit=normalize('unit.py',case['code'].encode())
    boundary={'from_layer':'input','to_layer':'output'}
    schema=model_schema(unit,boundary=boundary,item='code-item',target_table=case['target_table'])
    layers=[{'id':'input','table':name,'columns':[{'name':c,'type':t} for c,t in cols.items()]}
            for name,cols in case['schemas'].items()]
    layers.append({'id':'output','table':case['target_table']})
    payload={'code':unit,'layers':layers}
    bootstrap={'entry_point':'model_eval_reader','context_identity':'synthetic:'+digest(case['schemas']),
        'config':agent.config,'profile':agent.planner_profile,'usage_policy':agent.governor.policy,
        'engine_hash':__import__('investigator.runtime',fromlist=['fingerprint']).fingerprint(),
        'state':{'case_id':case['id'],'golden_hash':digest(golden),'environment':agent.store.environment}}
    tape=journal.Tape(path,bootstrap);raw=[];metadata=None;received=False;result=None
    def generate(*args):
        nonlocal metadata,received
        value,metadata=provider(*args);received=True;return value,metadata
    options=agent.generation_options
    with journal.active(tape):
        journal.event('OPERATION_START',{'name':'MODEL_EXTRACTOR_EVALUATION','args':[],'kwargs':{}})
        model=Proposer(generate,governor=agent.governor,session_id=session_id,options=options,
            deadline=time.time()+options['timeout_seconds']+60,max_calls=1,max_input=options['max_payload_characters'],
            event=lambda kind,detail:journal.event('CONFIGURATION',{'event':kind,'detail':detail}),
            context_version=bootstrap['context_identity'])
        try:
            raw=model(payload,schema)
            validate_model_candidates(raw,unit=unit,schemas=case['schemas'],boundary=boundary,item='code-item',target_table=case['target_table'])
            result={'proposals':copy.deepcopy(raw),'semantic_refusal':not raw,'provider_error':None,'validation_error':None}
        except Exception as exc:
            # Preserve rejected raw proposals too; pre-verification precision
            # cannot improve by deleting the candidates that failed validation.
            result={'proposals':copy.deepcopy(raw),'semantic_refusal':False,
                    'provider_error':error_summary(exc) if not received else None,
                    'validation_error':error_summary(exc) if received else None}
            result['budget_hold']=isinstance(exc,UsageHold)
        finally:
            journal.event('OPERATION_END',{'name':'MODEL_EXTRACTOR_EVALUATION','error':(result or {}).get('provider_error') or (result or {}).get('validation_error')})
            tape.finish({'operation':'MODEL_EXTRACTOR_EVALUATION','status':'RECORDED','result':result,'outputs':None,'error':None})
    return {**result,'model_calls':model.calls,'provider_metadata':metadata,'verification_performed':False}
