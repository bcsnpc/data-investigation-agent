"""A real user reply opens a new bounded hybrid clarification phase."""
from .onboarding import Conflict

DECISIONS=('DECISION','DECISION_REJECTED','ADMISSION_OR_PROVIDER_FAILED')

def used(journal):return sum(entry['event'] in DECISIONS for entry in journal)

def budget(ticket,journal,configuration,*,hybrid):
    total=used(journal);cap=configuration.get('step_cap',25)
    phase=ticket.get('hybrid_reply_budget') if hybrid else None
    before=phase['prior_decisions'] if phase else 0
    if before>total or before<0:raise Conflict('Reply phase decision baseline differs')
    if phase and phase['reply_id'] not in ticket.get('agent_consumed_replies',[]):
        raise Conflict('Reply phase has no consumed user reply')
    return {'version':'agent-step-phase-v1','kind':'HYBRID_REPLY' if phase else 'INITIAL_OR_CUMULATIVE',
        'reply_id':phase['reply_id'] if phase else None,'step_cap':cap,
        'cumulative_decisions':total,'decisions_before_phase':before,
        'used_in_phase':total-before,'steps_remaining':cap-(total-before)}
