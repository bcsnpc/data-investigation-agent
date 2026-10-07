"""Run the real intake procedure over an explicitly synthetic evaluation catalog."""
import copy
import time
from types import SimpleNamespace
from .onboarding import digest
from .question_intake import Intake
from . import process_tape as journal


class EvaluationStore:
    """Synthetic metadata, existing durable usage/record storage. No data adapter."""
    def __init__(self,store,catalog):
        self.original=store;self.catalog=copy.deepcopy(catalog)
        # Namespace only the synthetic metadata lookup. The governor retains
        # the original store/environment and all of its charged counters.
        self.environment='synthetic-intake-evaluation'
    def connect(self):return self.original.connect()
    def list(self,enabled):return [{'id':m['id']} for m in self.catalog]
    def get(self,identity):
        model=next(m for m in self.catalog if m['id']==identity)
        return {'id':identity,'enabled':True,'revision':1,'context_id':'synthetic-evaluation',
                'context':{'reports':[{'report':r} for r in model.get('reports',[])]}}


def workspace(agent,catalog,resolver):
    store=EvaluationStore(agent.store,catalog)
    owner=SimpleNamespace(store=store,agent=agent,execution_enabled=True,clock=time.time)
    owner.model=lambda identity:copy.deepcopy(next(m for m in catalog if m['id']==identity))
    owner.target_options=lambda *_:[]
    return owner


def run_case(agent,golden,case,resolver,path,request_key):
    """No preview, create, investigation or read; reservations use the real governor."""
    owner=workspace(agent,golden['catalog'],resolver);intake=Intake(owner,resolver)
    bootstrap={'entry_point':'model_eval_intake','context_identity':'synthetic:'+digest(golden['catalog']),
        'config':agent.config,'profile':agent.planner_profile,'usage_policy':agent.governor.policy,
        'engine_hash':__import__('investigator.runtime',fromlist=['fingerprint']).fingerprint(),
        'state':{'case_id':case['id'],'golden_hash':digest(golden),'environment':agent.store.environment}}
    tape=journal.Tape(path,bootstrap);result=None;error=None
    with journal.active(tape):
        journal.event('OPERATION_START',{'name':'intake','args':[],'kwargs':{}})
        try:
            # Skip only the outer workspace-tape bootstrap. Inside, the original
            # procedure still performs catalog snapshot, reservations, retries,
            # provenance/schema validation, settlement and durable storage.
            result=intake.resolve.__wrapped__(intake,{'text':case['text'],'request_key':request_key,'parent_id':None})
            return result
        except BaseException as exc:error=exc;raise
        finally:
            journal.event('OPERATION_END',{'name':'intake','error':type(error).__name__ if error else None})
            tape.finish({'operation':'MODEL_EVALUATION_INTAKE','status':(result or {}).get('status'),
                         'result':result,'error':type(error).__name__ if error else None,'outputs':None})
