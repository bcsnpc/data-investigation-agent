"""Tool-led execution of an already admitted scope, with original claim gates.

Intake tools may inspect definitions but cannot revise the reviewed scope in this
phase. An agent intake controller supplies that scope through normal admission.
"""
import copy
from .agent_loop import AgentLoop
from .agent_journal import Journal
from .agent_provider import GovernedDecision
from .agent_intake_tools import IntakeTools
from .investigation_tools import InvestigationTools, schemas as investigation_schemas
from .process_outcomes import OUTCOMES
from .definition_target import procedure_scope
from .onboarding import digest, Conflict
from .question_intake import snapshot
from .run_recording import operation


class AgentProcess:
    def __init__(self, workspace, *, generate=None, synthesis_provider=None):
        self.workspace = workspace
        self.generate, self.synthesis_provider = generate, synthesis_provider

    @operation('agent_run')
    def run(self, identity):
        runtime = self.workspace.agent
        state = runtime.get(identity)
        envelope = copy.deepcopy(state['envelope'])
        configuration = runtime.config.get('_estate', {}).get('investigation', {})
        if configuration.get('mode', 'PIPELINE') != 'AGENT':
            raise Conflict('Agent mode is not selected in the installation')
        if state['status'] != 'READY':
            raise Conflict('Agent loop cannot restart an interrupted session')
        runtime.begin_agent_process(identity)
        adapter = runtime.process_adapter(identity)
        scope = procedure_scope(envelope)
        target_id = 'resolved-target:' + digest({'measure': envelope['measure_id'], 'scope': scope})
        scope_id = 'admitted-scope:' + digest(scope)
        targets = {target_id: {'measure_id': envelope['measure_id'], 'scope_id': scope_id}}
        facade = InvestigationTools(adapter, targets, {scope_id: scope}, runtime.agent_tool_boundary(identity))
        journal = Journal(self.workspace.store, identity, now=runtime.clock)
        fixed = {'target_id': target_id, 'measure_id': envelope['measure_id']}
        tools = IntakeTools(lambda: snapshot(self.workspace),
            lambda body: journal.persist({'event': 'INTAKE_TOOL_EVIDENCE', 'result': body}),
            # This phase already has a resolved target. Candidate reads belong
            # to the intake controller's independently governed admission.
            candidate_reader=None,
            fixed_facts=fixed, comment_port=self._comments(identity))
        definitions = tools.definitions() + investigation_schemas()
        schemas = {item['name']: item['parameters'] for item in definitions}
        handlers = tools.handlers()
        handlers.update({item['name']: (lambda name=item['name'], **arguments: facade.invoke(name, arguments))
                         for item in investigation_schemas()})

        def admit(kind, ordinal):
            with runtime.runtime.db() as db:
                current = runtime.load(db, identity); runtime.admit(current, db)
                if current['status'] != 'EXECUTING': raise Conflict('Agent session stopped')
                if runtime.clock() >= current['deadline']: raise Conflict('Agent session deadline')

        def deliver(decision, evidence, **context):
            refs = sorted({ref for claim in decision['claims'] for ref in claim['evidence_ids']})
            # Proposed model prose is never used as evidence or delivered prose.
            # Trusted support derives from original tool observations; normal
            # synthesis then applies outcome, coverage, vocabulary and prose gates.
            runtime.accept_agent_support(identity, facade, decision['outcome'], target_id, refs)
            runtime.synthesize(identity, self.synthesis_provider)
            from .ticket_findings import from_state
            findings = from_state(runtime.get(identity))
            return {'validated': True, 'outputs': findings['outputs']}

        loop = AgentLoop(tools=handlers, schemas=schemas,
            decide=GovernedDecision(runtime, identity, generate=self.generate),
            persist=journal.persist, validate_delivery=deliver, outcomes=OUTCOMES,
            admit=admit, step_cap=configuration.get('step_cap', 25),
            wall_seconds=configuration.get('wall_seconds', 900))
        result = loop.run({'text': envelope['symptom'], 'admitted_scope': scope,
                          'target_registry': targets, 'tool_catalog': definitions},
                         fixed_facts=fixed, context_id=state['context_hash'])
        with runtime.runtime.db() as db:
            db.execute('BEGIN IMMEDIATE'); current = runtime.load(db, identity)
            current['agent_loop'] = copy.deepcopy(result)
            if current['status'] == 'EXECUTING':
                runtime.stop(db, current, result.get('reason', 'AGENT_WAITING_FOR_USER'),
                             'NEEDS_INPUT' if result['status']=='WAITING_FOR_USER' else 'HELD')
            runtime.save(db, current, 'AGENT_LOOP_FINISHED', {'status': result['status'],
                'progress_count': len(result['transcript'])})
        return runtime.get(identity)

    def _comments(self, identity):
        def comment(request):
            from .ticket_comments import append
            candidates = [saved for saved in self.workspace.smart_intake.tickets.list()['tickets']
                          if saved['ticket'].get('session_id') == identity]
            if len(candidates) != 1: raise Conflict('Agent question has no unique ticket thread')
            saved = candidates[0]
            text = request['question']; choices = request.get('choices')
            if choices: text += '\n' + '\n'.join(str(i+1)+'. '+choice for i,choice in enumerate(choices))
            key = 'agent-question:' + digest({'session': identity, 'question': text})[:32]
            updated = append(self.workspace, {'ticket_id': saved['ticket']['id'],
                'revision': saved['revision'], 'request_key': key, 'text': text,
                'attachment_id': None, 'review_id': None}, actor='AGENT')
            return {'comment_id': key, 'answer': None, 'ticket_id': updated['ticket']['id']}
        return comment
