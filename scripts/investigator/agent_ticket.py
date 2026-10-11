"""One governed tool loop from retained ticket intake through investigation.

Picked form facts stay immutable. No investigation port exists until the normal
intake review, preview and controller-owned start have admitted the scope.
"""
import copy
from .onboarding import Conflict, digest
from .question_intake import snapshot
from .agent_catalog_guard import CatalogGuard
from .agent_loop import AgentLoop
from .agent_provider import GovernedDecision
from .agent_journal import Journal
from .agent_intake_tools import IntakeTools
from .agent_intake_settlement import Settlement, SCHEMA, DESCRIPTION
from .investigation_tools import InvestigationTools, schemas as investigation_schemas
from .definition_target import procedure_scope
from .process_outcomes import OUTCOMES
from . import ticket_protocol as protocol


def selected(workspace):
    return workspace.agent.config.get('_estate', {}).get('investigation', {}).get('mode', 'PIPELINE') == 'AGENT'


class AgentTicket:
    def __init__(self, workspace, *, generate=None, synthesis_provider=None):
        self.workspace = workspace
        self.generate, self.synthesis_provider = generate, synthesis_provider

    def resume(self, identity, *, revision, comment_id):
        tickets = self.workspace.smart_intake.tickets
        saved = tickets.get(identity)
        if saved['revision'] != revision: raise Conflict('Agent reply revision changed')
        loop = saved['ticket'].get('agent_loop') or {}
        if loop.get('status') != 'WAITING_FOR_USER': raise Conflict('Agent ticket is not awaiting a real reply')
        comments = saved['ticket'].get('comments', [])
        match = [c for c in comments if c['id'] == comment_id and c['actor'] == 'USER']
        asked = [i for i,c in enumerate(comments) if c['actor'] == 'AGENT']
        if len(match) != 1 or not asked or comments.index(match[0]) <= asked[-1]:
            raise Conflict('Agent continuation requires a retained user reply after its question')
        if comment_id in saved['ticket'].get('agent_consumed_replies', []): raise Conflict('Agent reply already consumed')
        if saved['ticket'].get('session_id'):
            previous = self.workspace.agent.get(saved['ticket']['session_id'])
            if previous['status'] != 'NEEDS_INPUT': raise Conflict('Agent predecessor is not waiting')
            self.workspace.smart_intake._bound_session(saved['ticket'], previous['id'])
        else: previous = None
        def retain(ticket):
            ticket.setdefault('agent_consumed_replies', []).append(comment_id)
            ticket.setdefault('agent_loop_history', []).append(copy.deepcopy(ticket.pop('agent_loop')))
            ticket.setdefault('agent_replies', []).append(copy.deepcopy(match[0]))
            if previous is not None:
                ticket.setdefault('agent_scope_history', []).append({k: copy.deepcopy(ticket.get(k))
                    for k in ('source_intake','intake_id','session_id','settled','confirmed')})
                ticket['agent_predecessor'] = previous['id']
                ticket['agent_diagnostic_reads'] = previous['cloud_calls']
                for key in ('source_intake','intake_id','session_id'): ticket.pop(key, None)
                ticket['settled'] = {}; ticket['confirmed'] = {}; ticket['questions'] = []
            return protocol.transition(ticket, 'CLARIFYING', actor='USER', detail={'comment_id': comment_id})
        saved = tickets.update(identity, revision, retain)
        return self.run(saved, pipeline_result=saved['ticket'].get('hybrid_pipeline'))

    def run(self, saved, *, pipeline_result=None):
        hybrid = self.workspace.agent.config.get('_estate', {}).get('investigation', {}).get('mode') == 'HYBRID'
        if hybrid:
            if not pipeline_result or saved['ticket'].get('hybrid_pipeline') != pipeline_result:
                raise Conflict('Hybrid agent requires its retained pipeline result')
            sealed = copy.deepcopy(pipeline_result); expected = sealed.pop('hash', None)
            if expected != digest(sealed):raise Conflict('Hybrid pipeline evidence changed')
        elif not selected(self.workspace): raise Conflict('Agent mode is not selected')
        tickets = self.workspace.smart_intake.tickets
        identity = saved['ticket']['id']; runtime = self.workspace.agent
        if saved['ticket'].get('agent_loop'): return saved
        def mark(ticket):
            # A fallback is a new clarification phase, not an attempt to hold
            # a previously shared finding (or to hold an already held ticket).
            # Keep the sealed pipeline result; normal admission gates still apply.
            if hybrid and ticket['state'] in ('FINDINGS_SHARED','HELD'):
                ticket=protocol.transition(ticket,'CLARIFYING',actor='AGENT',
                    detail={'reason':'HYBRID_GAP_REOPENED','pipeline_hash':pipeline_result['hash']})
            ticket['investigation_mode'] = 'HYBRID' if hybrid else 'AGENT'
            ticket.setdefault('agent_loop_started_at', runtime.clock())
            return ticket
        saved = tickets.update(identity, saved['revision'], mark)
        self.workspace._form_candidate_session = identity
        self.workspace._form_candidate_count = saved['ticket'].get('agent_intake_diagnostic_reads', 0)
        initial_candidates = self.workspace._form_candidate_count
        prior_diagnostics = saved['ticket'].get('agent_diagnostic_reads', initial_candidates)
        form = copy.deepcopy(saved['ticket'].get('form_input'))
        from .ticket_inputs import document
        input_request = copy.deepcopy(saved['request'])
        replies = saved['ticket'].get('agent_replies', [])
        if form is None and replies:
            input_request['text'] += ''.join('\n\nRetained user reply:\n'+c['text'] for c in replies)
        if form is not None and replies:
            form['description'] += ''.join('\n\nRetained user reply:\n'+c['text'] for c in replies)
        text = document(input_request)['text'] if form is None else form['description']
        catalog_guard = CatalogGuard(self.workspace, snapshot)
        catalog = catalog_guard.read()
        journal = Journal(self.workspace.store, identity, now=runtime.clock)
        retain = lambda body: journal.persist({'event': 'INTAKE_TOOL_EVIDENCE', 'result': body})
        generation = len(saved['ticket'].get('agent_loop_history', []))
        settlement = Settlement(self.workspace, text=text, key_prefix='agent:' + identity[:18] + ':' + str(generation),
            record_evidence=retain, form_request=form,
            input_request=input_request if form is None else None,
            candidate_binding=saved['ticket'].get('form_candidate_binding'),
            predecessor=saved['ticket'].get('agent_predecessor'))
        active = {}
        fixed = {k: copy.deepcopy(form[k]) for k in
            ('report_id','page_id','target_id','comparison','cell_mode','cell_keys')
            if form is not None and k in form}
        reader = getattr(self.workspace, 'form_candidate_reader', None)
        def candidate_reader(candidate):
            used = prior_diagnostics + self.workspace._form_candidate_count - initial_candidates
            if used >= self.workspace.dynamic_read_limit: raise Conflict('Agent diagnostic-read cap reached')
            if reader is None: raise Conflict('Candidate-value reader unavailable')
            return reader(candidate)
        from .agent_screenshot_reader import reader as screenshot_reader
        tools = IntakeTools(catalog_guard.read, retain,
            candidate_reader=candidate_reader if reader is not None else None,
            screenshot_reader=screenshot_reader(self.workspace, identity),
            fixed_facts=fixed, comment_port=self._comments(identity))
        investigation_definitions=investigation_schemas(include_standard=hybrid)
        intake_only=hybrid and runtime.config.get('_estate',{}).get('investigation',{}).get('fallback_scope')=='INTAKE_ONLY'
        if intake_only:
            investigation_definitions=[d for d in investigation_definitions if d['name']=='run_standard_investigation']
        definitions = tools.definitions() + investigation_definitions + [
            {'name': 'resolve_ticket', 'description': DESCRIPTION, 'parameters': SCHEMA}]
        handlers = tools.handlers()

        def resolve_ticket(extraction):
            result = settlement.resolve_ticket(extraction)
            if result['status'] != 'INTAKE_ADMITTED': return result
            if active:
                return {**result, **active['binding']}
            # Fully settled authority comes from the validator, never the model.
            def attach(ticket):
                ticket['intake_id'] = result['intake_id']; ticket['source_intake'] = result['intake_id']
                scope = result['scope']
                for field, value in [('REPORT_PAGE', scope.get('report_binding')),
                                     ('NUMBER', {'measure_id': scope['measure_id'],
                                        'target_visual': scope.get('target_visual'),
                                        'reported_figure': scope.get('reported_figure')}),
                                     ('COMPARISON', scope.get('ticket_route'))]:
                    ticket['settled'][field] = {'authority': 'VALIDATED_AGENT_INTAKE', 'value': copy.deepcopy(value)}
                return ticket
            current = tickets.get(identity); current = tickets.update(identity, current['revision'], attach)
            from .intake_confirmation import authority_hash
            from .onboarding import encoded
            with self.workspace.store.connect() as db:
                db.execute('BEGIN IMMEDIATE')
                body = self.workspace.intake.get(result['intake_id'])
                body['confirmation_ticket'] = {'id': identity, 'revision': current['revision'],
                    'authority_hash': authority_hash(current['ticket'])}
                db.execute('UPDATE workspace_intakes SET body=?,hash=? WHERE id=?',
                    (encoded(body), digest(body), result['intake_id']))
            run = settlement.start(controller_owned=True)
            session_id = run['id']; active['session_id'] = session_id
            used = prior_diagnostics + getattr(self.workspace, '_form_candidate_count', 0) - initial_candidates
            with runtime.runtime.db() as db:
                db.execute('BEGIN IMMEDIATE'); state = runtime.load(db, session_id)
                if used > state['envelope']['limits']['cloud_calls']: raise Conflict('Agent intake diagnostic cap exceeded')
                state['cloud_calls'] = used
                state['agent_intake_diagnostic_reads'] = used
                if hybrid and pipeline_result.get('session'):
                    state['diagnostic_phase_counts'] = copy.deepcopy(pipeline_result['session'].get('diagnostic_phase_counts', {'WALK':0,'REPRODUCTION':0}))
                if runtime.config.get('_estate', {}).get('execution', {}).get('mode') == 'LOCAL_EXPORTED':
                    state['local_diagnostic_reads'] = used
                runtime.save(db, state, 'AGENT_INTAKE_BUDGET_CARRIED', {'diagnostic_reads': used})
            def investigating(ticket):
                ticket = protocol.transition(ticket, 'INVESTIGATING', actor='AGENT', detail={'session_id': session_id})
                ticket['session_id'] = session_id
                return ticket
            current = tickets.get(identity); tickets.update(identity, current['revision'], investigating)
            runtime.begin_agent_process(session_id)
            state = runtime.get(session_id); envelope = state['envelope']
            scope = procedure_scope(envelope)
            target_id = 'resolved-target:' + digest({'measure': envelope['measure_id'], 'scope': scope})
            scope_id = 'admitted-scope:' + digest(scope)
            targets = {target_id: {'measure_id': envelope['measure_id'], 'scope_id': scope_id}}
            def standard(measure, admitted_scope):
                if measure != envelope['measure_id'] or digest(admitted_scope) != digest(scope):
                    raise Conflict('Standard investigation admitted scope differs')
                previous = pipeline_result.get('session') if hybrid else None
                if previous and previous.get('assessment') and previous['envelope']['measure_id']==measure and digest(procedure_scope(previous['envelope']))==digest(admitted_scope):
                    from .assessment_support import validate
                    original = {o['id']: copy.deepcopy(o) for o in previous['observations']}
                    validate(previous['assessment'], original)
                    return {'status':'AVAILABLE','assessment':copy.deepcopy(previous['assessment']),
                            'observations':original,'reused_pipeline_session':previous['id']}
                result = runtime.run_process(session_id, agent_candidate=True)
                if result.get('status') == 'AVAILABLE':return result
                return {'status':'UNAVAILABLE','reason':result.get('stop_reason','STANDARD_INVESTIGATION_INCOMPLETE'),
                        'data':copy.deepcopy(result),'native_evidence_ids':[o['id'] for o in result.get('observations',[])]}
            facade = InvestigationTools(runtime.process_adapter(session_id), targets,
                {scope_id: scope}, runtime.agent_tool_boundary(session_id), standard=standard if hybrid else None)
            active.update(session_id=session_id, facade=facade, target_id=target_id)
            active['binding'] = {'session_id': session_id, 'target_registry': targets,
                                 'scope_registry': {scope_id: scope}}
            return {**result, **active['binding']}

        handlers['resolve_ticket'] = resolve_ticket
        for item in investigation_definitions:
            def invoke(name=item['name'], **arguments):
                if not active:
                    return {'status': 'NOT_ADMITTED', 'reason': 'Resolve and admit the ticket first',
                            'evidence_ids': [retain({'status': 'NOT_ADMITTED', 'tool': name})]}
                return active['facade'].invoke(name, arguments)
            handlers[item['name']] = invoke

        def admit(kind, ordinal):
            catalog_guard.read()
            if active:
                with runtime.runtime.db() as db:
                    current = runtime.load(db, active['session_id']); runtime.admit(current, db)
                    if current['status'] != 'EXECUTING': raise Conflict('Agent session stopped')
                    if runtime.clock() >= current['deadline']: raise Conflict('Agent session deadline')

        def deliver(decision, evidence, **context):
            if not active: return {'validated': False, 'reason': 'INTAKE_NOT_ADMITTED'}
            refs = sorted({ref for claim in decision['claims'] for ref in claim['evidence_ids']})
            runtime.accept_agent_support(active['session_id'], active['facade'],
                decision['outcome'], active['target_id'], refs)
            runtime.synthesize(active['session_id'], self.synthesis_provider)
            from .ticket_findings import from_state
            return {'validated': True, 'outputs': from_state(runtime.get(active['session_id']))['outputs']}

        configuration = runtime.config['_estate']['investigation']
        prior_decisions = sum(1 for entry in journal.read() if entry['event'] in
            ('DECISION','DECISION_REJECTED','ADMISSION_OR_PROVIDER_FAILED'))
        remaining_steps = configuration.get('step_cap', 25) - prior_decisions
        remaining_wall = int(configuration.get('wall_seconds', 900) -
            max(0, runtime.clock() - saved['ticket']['agent_loop_started_at']))
        if remaining_steps <= 0 or remaining_wall <= 0:
            reason = 'AGENT_STEP_CAP' if remaining_steps <= 0 else 'AGENT_WALL_LIMIT'
            current = tickets.get(identity)
            def exhausted(ticket):
                ticket['agent_loop'] = {'status': 'HELD', 'reason': reason, 'outputs': None}
                return protocol.transition(ticket, 'HELD', actor='AGENT', detail={'reason': reason})
            return tickets.update(identity, current['revision'], exhausted)
        loop = AgentLoop(tools=handlers, schemas={d['name']: d['parameters'] for d in definitions},
            decide=GovernedDecision(runtime, identity, generate=self.generate,
                deadline=saved['ticket']['agent_loop_started_at']+configuration.get('wall_seconds',900)), persist=journal.persist,
            validate_delivery=deliver, outcomes=OUTCOMES, admit=admit,
            step_cap=remaining_steps, wall_seconds=remaining_wall)
        finalized = False
        try:
            payload = {'text': text, 'input': copy.deepcopy(saved['request']),
                'retained_user_replies': copy.deepcopy(replies),
                # Parameter contracts already occur in the strict decision
                # schema. Do not duplicate them in the payload.
                'tool_catalog': [{k: d[k] for k in ('name','description')} for d in definitions]}
            if hybrid:
                payload['pipeline_starting_state'] = copy.deepcopy(pipeline_result)
                payload['task'] = 'Close only the named pipeline gap or ask a better user question. Do not repeat completed work. After resolving intake use run_standard_investigation for the normal walk; low-level tools are for the remaining gap. Never use a business-rule refusal as permission to judge business correctness.'
                if intake_only:
                    payload['task']='Close the retained intake hold using the original ticket and picked facts. After validated admission, run_standard_investigation executes the pipeline. No low-level investigation tools are available in this profile. Do not change the reported referent or invent a user answer.'
            starting_evidence = None
            if hybrid:
                starting_evidence={o['id']:copy.deepcopy(o) for o in (pipeline_result.get('session') or {}).get('observations',[])}
                intake=pipeline_result.get('intake')
                if intake:starting_evidence[intake['id']]=copy.deepcopy(intake)
            result = loop.run(payload,
                fixed_facts=fixed, context_id=digest(catalog), starting_evidence=starting_evidence)
            if active:
                with runtime.runtime.db() as db:
                    db.execute('BEGIN IMMEDIATE'); current = runtime.load(db, active['session_id'])
                    current['agent_loop'] = copy.deepcopy(result)
                    if current['status'] == 'EXECUTING':
                        runtime.stop(db, current, result.get('reason', 'AGENT_WAITING_FOR_USER'),
                            'NEEDS_INPUT' if result['status'] == 'WAITING_FOR_USER' else 'HELD')
                    runtime.save(db, current, 'AGENT_LOOP_FINISHED', {'status': result['status']})
            current = tickets.get(identity)
            def finish(ticket):
                ticket['agent_loop'] = copy.deepcopy(result)
                ticket['agent_intake_diagnostic_reads'] = getattr(self.workspace, '_form_candidate_count', 0)
                ticket['agent_diagnostic_reads'] = (runtime.get(active['session_id'])['cloud_calls']
                    if active else prior_diagnostics + getattr(self.workspace, '_form_candidate_count', 0) - initial_candidates)
                if result['status'] == 'COMPLETED' and active:
                    from .ticket_findings import from_state
                    findings = from_state(runtime.get(active['session_id']))
                    ticket = protocol.transition(ticket, 'FINDINGS_SHARED', actor='AGENT',
                        detail={'findings_hash': digest(findings)})
                    ticket['findings'] = findings
                else:
                    ticket = protocol.transition(ticket, 'HELD', actor='AGENT',
                        detail={'reason': result.get('reason', result['status'])})
                return ticket
            saved_result = tickets.update(identity, current['revision'], finish)
            finalized = True
            return saved_result
        except Exception as error:
            journal.persist({'event': 'INTERRUPTED', 'error_type': type(error).__name__})
            if active:
                with runtime.runtime.db() as db:
                    db.execute('BEGIN IMMEDIATE'); state = runtime.load(db, active['session_id'])
                    if state['status'] == 'EXECUTING': runtime.stop(db, state, 'AGENT_INTERRUPTED', 'FAILED')
            current = tickets.get(identity)
            def interrupted(ticket):
                ticket['agent_loop'] = {'status': 'INTERRUPTED', 'error_type': type(error).__name__}
                return protocol.transition(ticket, 'HELD', actor='AGENT', detail={'reason': 'AGENT_INTERRUPTED'})
            tickets.update(identity, current['revision'], interrupted)
            raise
        finally:
            if active:
                with self.workspace.store.connect() as db:
                    db.execute("UPDATE workspace_jobs SET status=? WHERE session_id=? AND status='RUNNING'",
                        ('FINISHED' if finalized else 'INTERRUPTED', active['session_id']))

    def _comments(self, identity):
        def post(request):
            from .ticket_comments import append
            current = self.workspace.smart_intake.tickets.get(identity)
            text = request['question']
            if request.get('choices'): text += '\n' + '\n'.join(request['choices'])
            key = 'agent-question:' + digest({'ticket': identity, 'text': text})[:32]
            append(self.workspace, {'ticket_id': identity, 'revision': current['revision'],
                'request_key': key, 'text': text, 'attachment_id': None, 'review_id': None}, actor='AGENT')
            return {'comment_id': key, 'answer': None, 'ticket_id': identity}
        return post
