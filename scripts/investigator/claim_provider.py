"""Claim extraction through existing governed, dollar-guarded provider transport."""
import copy
from .agent_provider import GovernedDecision
from .claim_facts import EXTRACTION_SCHEMA,extraction,normalise
from .intake_span_references import wire_tokens

INSTRUCTIONS='''Extract only what the user stated in ticket_tokens. Return inclusive token references, never invented values, names, scope or business truth. Keep observed and expected figures distinct; component or contextual numbers are CONTEXT. Preserve plural visuals/page/report complaints. STALE and DEFINITION do not require a numeric figure. A proposed cause stays guessed_cause. Only assign enums when the quoted words support them. Missing facts stay absent. Candidate interpretation is not user confirmation.'''


class ClaimExtractionUnavailable(ValueError):
    """A bounded, retained refusal; provider usage uncertainty is conserved."""
    def __init__(self,reason,*,calls,error_type,rejections):
        self.reason=reason;self.audit={'calls':calls,'status':'HELD','reason':reason,
            'provider_error_type':error_type,'rejections':copy.deepcopy(rejections),
            'handled_timeout':reason=='PROVIDER_TIMEOUT'}
        super().__init__('CLAIM_EXTRACTION_UNAVAILABLE: '+reason)


def timeout(error):
    return isinstance(error,TimeoutError)or type(error).__name__=='APITimeoutError'

def extract(workspace,text,document_id,session_id):
    runtime=copy.copy(workspace.agent)
    runtime.config=copy.deepcopy(runtime.config)
    investigation=runtime.config.setdefault('_estate',{}).setdefault('investigation',{})
    investigation.pop('input_characters_per_request',None);investigation.pop('agent_deployment',None)
    investigation['mode']='PIPELINE'
    runtime.generation_options=copy.deepcopy(runtime.generation_options)
    runtime.generation_options['max_payload_characters']=min(32000,runtime.generation_options['max_payload_characters'])
    decision=GovernedDecision(runtime,session_id,generate=getattr(workspace,'claim_generate',None))
    payload={'ticket_tokens':wire_tokens(text)};failures=[];repairs=[]
    for attempt in range(2):
        try:raw=decision._call(payload,instructions=INSTRUCTIONS,schema=EXTRACTION_SCHEMA)
        except Exception as exc:
            if timeout(exc):
                raise ClaimExtractionUnavailable('PROVIDER_TIMEOUT',calls=attempt+1,error_type=type(exc).__name__,rejections=failures)from exc
            from .usage_governance import UsageHold
            if isinstance(exc,UsageHold):
                raise ClaimExtractionUnavailable('RETRY_ADMISSION_UNAVAILABLE'if attempt else'ADMISSION_UNAVAILABLE',
                    calls=attempt,error_type=type(exc).__name__,rejections=failures)from exc
            # Authentication, billing and transport failures retain their native
            # stop semantics. They are never mistaken for a repairable answer.
            if not isinstance(exc,ValueError)or str(exc)!='AGENT_PROVIDER_WRAPPER':raise
            failures.append({'type':type(exc).__name__,'message':str(exc)})
            if attempt:break
            payload={'ticket_tokens':wire_tokens(text),'validation_rejection':str(exc),'retry':'Return the required facts object.'}
            continue
        raw,changed=normalise(raw);repairs.extend(changed)
        try:
            facts=extraction(raw,text,document_id)
            return facts,{'calls':attempt+1,'rejections':failures,'repairs':repairs,
                'usable_fields':sorted({f['field']for f in facts}),
                'quantity_statements':sum(bool(f['value'].get('statement'))for f in facts if f['field']=='observation')}
        except (ValueError,__import__('jsonschema').ValidationError) as exc:
            failures.append({'type':type(exc).__name__,'message':str(exc)})
            payload={'ticket_tokens':wire_tokens(text),'validation_rejection':str(exc),'retry':'Return exact valid token references and field symbols.'}
    raise ValueError('CLAIM_EXTRACTION_REJECTED_TWICE: '+failures[-1]['message'])
