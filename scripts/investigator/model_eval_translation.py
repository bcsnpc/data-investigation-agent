"""One model proposal, then independent local verification; never an estate read."""
import copy,time
from .code_proposal_budget import Proposer
from . import process_tape as journal
from .translation_eval import request,verify
from .translation_proposer import SCHEMA
from .onboarding import digest
from .generation_policy import error_summary
from .usage_governance import UsageHold


class TranslationCall(Proposer):
    input_fields=frozenset(('translation',))
    phase='TRANSLATION_PROPOSAL'
    reservation_prefix='translation-proposal:'
    response_type=dict


def azure_propose(payload,schema,options):
    # Exercise the installed adapter's prompt, payload projection and strict
    # wire. The governor remains outside it, exactly as in verification service.
    from .adapters.translation_model import Provider
    installed=Provider(options=options)
    value=installed.propose(payload['translation'],schema)
    return value,installed.metadata


def run_case(agent,golden,case,provider,path,session_id):
    req=request(case);metadata=None;received=False;raw=None;result=None
    bootstrap={'entry_point':'model_eval_translation','context_identity':req['context'],
        'config':agent.config,'profile':agent.planner_profile,'usage_policy':agent.governor.policy,
        'engine_hash':__import__('investigator.runtime',fromlist=['fingerprint']).fingerprint(),
        'state':{'case_id':case['id'],'golden_hash':digest(golden),'environment':agent.store.environment}}
    tape=journal.Tape(path,bootstrap)
    def generate(*args):
        nonlocal metadata,received
        p,metadata=provider(*args);received=True;return p,metadata
    with journal.active(tape):
        journal.event('OPERATION_START',{'name':'TRANSLATION_EVALUATION','args':[],'kwargs':{}})
        options=agent.generation_options
        model=TranslationCall(generate,governor=agent.governor,session_id=session_id,options=options,
            deadline=time.time()+options['timeout_seconds']+60,max_calls=1,max_input=options['max_payload_characters'],
            event=lambda kind,detail:journal.event('CONFIGURATION',{'event':kind,'detail':detail}),context_version=req['context'])
        try:
            raw=model({'translation':req},copy.deepcopy(SCHEMA))
            evaluation=verify(case,raw)
            result={'proposal':raw,'evaluation':evaluation,'provider_error':None,'validation_error':None,'budget_hold':False}
        except Exception as exc:
            result={'proposal':raw,'evaluation':None,'provider_error':error_summary(exc) if not received else None,
                    'validation_error':error_summary(exc) if received else None,'budget_hold':isinstance(exc,UsageHold)}
        finally:
            journal.event('OPERATION_END',{'name':'TRANSLATION_EVALUATION','error':(result or {}).get('provider_error') or (result or {}).get('validation_error')})
            tape.finish({'operation':'TRANSLATION_EVALUATION','status':'RECORDED','result':result,'outputs':None,'error':None})
    return {**result,'model_calls':model.calls,'provider_metadata':metadata,'estate_physical_requests':0}
