"""Untrusted query candidates. Platform execution answers never become evidence."""
import copy
import base64,json
from typing import Protocol
from jsonschema import Draft202012Validator

TEXT={'type':'string','minLength':1,'maxLength':500}
OBJECT={'type':'object','additionalProperties':False,'required':['id','kind'],
        'properties':{'id':TEXT,'kind':{'enum':['TABLE','COLUMN','MEASURE']}}}
SCHEMA={'type':'object','additionalProperties':False,'required':['provenance','objects','expression'],
    'properties':{'provenance':{'const':'PROPOSED_BY_ASSISTANT'},
        'objects':{'type':'array','minItems':1,'maxItems':64,'uniqueItems':True,'items':OBJECT},
        'expression':{'type':'string','minLength':1,'maxLength':8000}}}

class AssistantProposer(Protocol):
    def propose(self,question:str)->dict: ...

def validate(value):
    Draft202012Validator(SCHEMA).validate(value)
    if len({o['id'] for o in value['objects']})!=len(value['objects']):raise ValueError('Assistant repeats a candidate identity')
    return copy.deepcopy(value)

def propose(manifest,question,assistant,model_call):
    if not manifest.get('assistant_proposer',False):return None
    if not isinstance(question,str) or not 1<=len(question)<=2000:raise ValueError('Assistant question exceeds bound')
    # The caller meters and records a model call, including failures and timing.
    # There is deliberately no results/values/receipt channel in this contract.
    return validate(model_call(question,lambda:assistant.propose(question)))

class RecordedModelCall:
    """Record the proposal interface, never an execution receipt.

    The transport separately discards platform execution results. Admission is
    performed by the supplied model-call meter before invoking the assistant.
    Existing provider events and replay clocks preserve failures and timing.
    """
    def __init__(self,meter,*,event=None,clock=None):
        from . import process_tape
        self.meter=meter;self.event=event or process_tape.event
        self.clock=clock or process_tape.clock

    def __call__(self,question,execute):
        def recorded():
            self.clock('assistant_proposer_start')
            self.event('PROVIDER_REQUEST',{'question':question,'contract':SCHEMA})
            try:
                from .process_tape import ACTIVE
                tape=ACTIVE.get()
                if tape is not None and tape.replaying:
                    if tape.events[tape.index]['kind']=='PROVIDER_FAILURE':
                        failure=json.loads(tape.take('PROVIDER_FAILURE'))
                        raise RecordedAssistantFailure(failure['category'])
                    response=json.loads(tape.take('PROVIDER_RESPONSE'))
                    return json.loads(base64.b64decode(response['body'],validate=True))
                response=execute()
            except RecordedAssistantFailure:raise
            except Exception as exc:
                self.event('PROVIDER_FAILURE',{'category':type(exc).__name__})
                raise
            else:
                body=json.dumps(response,sort_keys=True,separators=(',',':')).encode()
                self.event('PROVIDER_RESPONSE',{'status':200,'body':base64.b64encode(body).decode()})
                return response
            finally:self.clock('assistant_proposer_end')
        return self.meter(question,recorded)

class RecordedAssistantFailure(RuntimeError):
    """Recorded provider failure category; replay never calls the platform."""

def compile_candidate(proposal,catalog,compiler):
    proposal=validate(proposal)
    for o in proposal['objects']:
        if catalog.get(o['id'])!=o['kind']:raise ValueError('Assistant candidate is not an exact discovered object')
    # Only the existing governed compiler may turn the expression into a probe.
    # No reader is called here; normal admission/attestation owns execution.
    return compiler(copy.deepcopy(proposal))
