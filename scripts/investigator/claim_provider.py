"""Claim extraction through existing governed, dollar-guarded provider transport."""
import copy
from .agent_provider import GovernedDecision
from .claim_facts import EXTRACTION_SCHEMA,extraction
from .intake_span_references import wire_tokens

INSTRUCTIONS='''Extract only what the user stated in ticket_tokens. Return inclusive token references, never invented values, names, scope or business truth. Keep observed and expected figures distinct; component or contextual numbers are CONTEXT. Preserve plural visuals/page/report complaints. STALE and DEFINITION do not require a numeric figure. A proposed cause stays guessed_cause. Only assign enums when the quoted words support them. Missing facts stay absent. Candidate interpretation is not user confirmation.'''

def extract(workspace,text,document_id,session_id):
    runtime=copy.copy(workspace.agent)
    runtime.config=copy.deepcopy(runtime.config)
    investigation=runtime.config.setdefault('_estate',{}).setdefault('investigation',{})
    investigation.pop('input_characters_per_request',None);investigation.pop('agent_deployment',None)
    investigation['mode']='PIPELINE'
    runtime.generation_options=copy.deepcopy(runtime.generation_options)
    runtime.generation_options['max_payload_characters']=min(32000,runtime.generation_options['max_payload_characters'])
    decision=GovernedDecision(runtime,session_id,generate=getattr(workspace,'claim_generate',None))
    payload={'ticket_tokens':wire_tokens(text)};failures=[]
    for attempt in range(2):
        raw=decision._call(payload,instructions=INSTRUCTIONS,schema=EXTRACTION_SCHEMA)
        try:return extraction(raw,text,document_id),{'calls':attempt+1,'rejections':failures}
        except (ValueError,__import__('jsonschema').ValidationError) as exc:
            failures.append({'type':type(exc).__name__,'message':str(exc)})
            payload={'ticket_tokens':wire_tokens(text),'validation_rejection':str(exc),'retry':'Return exact valid token references and field symbols.'}
    raise ValueError('CLAIM_EXTRACTION_REJECTED_TWICE: '+failures[-1]['message'])
