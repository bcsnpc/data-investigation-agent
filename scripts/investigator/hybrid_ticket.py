"""Pipeline first; a bounded agent may address only the retained missing answer."""
import copy
from .onboarding import Conflict, digest


def selected(workspace):
    return workspace.agent.config.get('_estate', {}).get('investigation', {}).get('mode') == 'HYBRID'


def gap(saved, state):
    ticket = saved['ticket']
    if ticket['state'] == 'BUSINESS_VALIDATION':
        return None  # An intended specialist handoff is not a technical gap.
    if state is not None and (state.get('synthesis') or {}).get('status') == 'COMPLETED':
        from .ticket_findings import from_state
        findings = from_state(state)  # Original observations, unchanged validators.
        accounts = [findings['outputs'][k].get('question_account') for k in ('business_output', 'technical_output')]
        if findings['assessment'] is not None and accounts and all(a and a['status'] == 'ANSWERED' for a in accounts):
            return None
        return {'reason': 'QUESTION_NOT_FULLY_ANSWERED', 'question_accounts': copy.deepcopy(accounts),
                'evidence_ids': findings['evidence_ids']}
    return {'reason': (state or {}).get('stop_reason') or
            ticket['history'][-1].get('detail', {}).get('reason') or ticket['state'],
            'detail': copy.deepcopy(ticket['history'][-1].get('detail', {})),
            'evidence_ids': [o['id'] for o in (state or {}).get('observations', [])]}


def complete(workspace, saved):
    """Called only after normal submission, never in the nested pipeline call."""
    if saved['ticket'].get('hybrid_pipeline'):
        return saved  # No invisible replacement fallback or second budget.
    if saved['ticket']['state'] == 'INVESTIGATING':
        workspace.run_session_once(saved['ticket']['session_id'])
        saved = workspace.smart_intake.finish({'ticket_id': saved['ticket']['id'], 'revision': saved['revision']})
    state = workspace.agent.get(saved['ticket']['session_id']) if saved['ticket'].get('session_id') else None
    policy=workspace.agent.config.get('_estate',{}).get('investigation',{}).get('fallback_scope','ANY_GAP')
    if policy=='INTAKE_ONLY' and state is not None:
        return saved  # Already admitted; retain the pipeline result without a post-intake agent.
    missing = gap(saved, state)
    if missing is None:
        return saved
    source=saved['ticket'].get('source_intake')
    parent = {'saved_ticket': copy.deepcopy(saved), 'session': copy.deepcopy(state), 'gap': missing,
              'intake':copy.deepcopy(workspace.intake.get(source)) if source else None}
    parent['hash'] = digest(parent)
    def retain(ticket):
        ticket['hybrid_pipeline'] = copy.deepcopy(parent)
        ticket['agent_diagnostic_reads'] = ((state or {}).get('cloud_calls') if state else
            ticket.get('form_candidate_diagnostic_reads', 0))
        ticket['agent_intake_diagnostic_reads'] = ticket.get('form_candidate_diagnostic_reads', 0)
        for key in ('session_id', 'source_intake', 'intake_id'):
            ticket.pop(key, None)
        return ticket
    current = workspace.smart_intake.tickets.update(saved['ticket']['id'], saved['revision'], retain)
    from .agent_ticket import AgentTicket
    return AgentTicket(workspace).run(current, pipeline_result=parent)


def submit(controller, request, pipeline):
    workspace = controller.workspace
    if not selected(workspace) or getattr(workspace, '_hybrid_pipeline_active', False):
        return pipeline(request)
    workspace._hybrid_pipeline_active = True
    try:
        saved = pipeline(request)
        return complete(workspace, saved)
    finally:
        workspace._hybrid_pipeline_active = False
