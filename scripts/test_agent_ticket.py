import copy
import unittest
from unittest.mock import patch, Mock
from investigator.agent_ticket import AgentTicket
from investigator.investigation_tools import schemas
from investigator import agent_intake_settlement
from investigator.onboarding import Conflict
from test_agent_intake_settlement import SettlementTests


class AgentTicketTests(unittest.TestCase):
    def setUp(self):
        self.fixture = SettlementTests(); self.fixture.setUp(); self.addCleanup(self.fixture.doCleanups)
        self.workspace = self.fixture.workspace
        # Owner-approved current agent bound; pipeline's bound is unchanged.
        self.workspace.agent.config['_estate'] = {'investigation': {'mode': 'AGENT', 'step_cap': 3, 'wall_seconds': 900, 'input_characters_per_request':150000}}
        self.fixture.catalog['versions']={m['id']:'test-retained-version' for m in self.fixture.catalog['models']}
        for m in self.fixture.catalog['models']:m['context_id']='test-retained-context'
        self.snapshot = patch('investigator.agent_ticket.snapshot', return_value=self.fixture.catalog)
        self.snapshot.start(); self.addCleanup(self.snapshot.stop)
        self.saved = self.workspace.smart_intake.tickets.submit({'text': 'Quantity differs.', 'request_key': 'unified-test'}, 'unified-test')

    def decisions(self, values):
        from test_intake_span_references import reference
        from investigator.intake_span_references import VERSION
        converted=[]
        for value in values:
            value=copy.deepcopy(value)
            if value.get('tool')=='ask_user':
                value['arguments'].setdefault('report_id',None);value['arguments'].setdefault('page_id',None)
            if value.get('tool')=='resolve_ticket':
                raw=value['arguments']['extraction'];text=self.fixture.form['description']
                raw['version']=VERSION;raw['primary']=reference(text,raw['primary'])
                for key in ('comparisons','contexts'):raw[key]=[reference(text,q) for q in raw[key]]
                for key in ('measures','figures','selections','visuals','reports','pages','dates','groupings','identifiers'):
                    for item in raw[key]:
                        occurrence=item.pop('occurrence',None) or 1
                        for field in ('quote','column','value','precision_quote'):
                            if field in item and item[field] is not None:item[field]=reference(text,item[field],occurrence if field=='quote' else 1)
            converted.append(value)
        decisions = Mock(side_effect=converted)
        patcher = patch('investigator.agent_ticket.GovernedDecision', return_value=decisions)
        patcher.start(); self.addCleanup(patcher.stop)
        return decisions

    def hold(self): return {'action': 'HOLD', 'summary': 'Cannot establish scope', 'reason': 'UNRESOLVED'}

    def test_no_old_provider_and_no_investigation_before_admission(self):
        tool = schemas()[0]
        decisions = self.decisions([{'action': 'TOOL', 'summary': 'Check admission', 'tool': tool['name'], 'arguments': {'target_id': 'untrusted-target'}}, self.hold()])
        with patch.object(self.workspace.intake, 'resolver', side_effect=AssertionError('old provider')), patch.object(self.workspace.agent, 'process_adapter', side_effect=AssertionError('not admitted')):
            result = AgentTicket(self.workspace).run(self.saved)
        self.assertEqual(result['ticket']['state'], 'HELD')
        transcript = result['ticket']['agent_loop']['transcript']
        observed = next(x['result'] for x in transcript if x['event'] == 'TOOL_RESULT')
        self.assertEqual(observed['status'], 'NOT_ADMITTED')
        self.assertEqual(decisions.call_count, 2)
        self.fixture.f.helper.h.native.assert_not_called()

    def test_one_loop_cap_includes_lookup_and_resolution(self):
        self.workspace.agent.config['_estate']['investigation']['step_cap'] = 2
        decisions = self.decisions([{'action': 'TOOL', 'summary': 'Find reports', 'tool': 'list_reports', 'arguments': {}},
            {'action': 'TOOL', 'summary': 'Find reports again', 'tool': 'list_reports', 'arguments': {}}])
        result = AgentTicket(self.workspace).run(self.saved)
        self.assertEqual(result['ticket']['agent_loop']['reason'], 'AGENT_STEP_CAP')
        self.assertEqual(decisions.call_count, 2)
        # Retrying submit never runs an interrupted/held loop again.
        AgentTicket(self.workspace).run(result)
        self.assertEqual(decisions.call_count, 2)

    def test_question_is_real_retained_comment_without_fabricated_answer(self):
        self.decisions([{'action': 'TOOL', 'summary': 'Ask for missing target', 'tool': 'ask_user',
            'arguments': {'field':'SELECTION'}}])
        result = AgentTicket(self.workspace).run(self.saved)
        self.assertEqual(result['ticket']['agent_loop']['status'], 'WAITING_FOR_USER')
        self.assertEqual(result['ticket']['comments'][0]['actor'], 'AGENT')
        self.assertFalse(any(c['actor'] == 'USER' for c in result['ticket']['comments']))

    def test_pipeline_does_not_select_agent(self):
        self.workspace.agent.config['_estate']['investigation']['mode'] = 'PIPELINE'
        with self.assertRaises(Conflict): AgentTicket(self.workspace).run(self.saved)

    def test_public_smart_and_form_submit_dispatch_agent_without_old_resolver(self):
        marker = {'ticket': {'state': 'HELD'}, 'revision': 0}
        with patch('investigator.agent_ticket.AgentTicket.run', return_value=marker) as run, patch.object(self.workspace.intake, 'resolver', side_effect=AssertionError('old provider')):
            self.assertIs(self.workspace.smart_intake.submit({'text': 'Quantity differs.', 'request_key': 'smart-agent'}), marker)
            self.assertIs(self.workspace.forms.submit({**self.fixture.form, 'request_key': 'form-agent'}), marker)
        self.assertEqual(run.call_count, 2)
        self.assertEqual(run.call_args.args[0]['ticket']['form_input']['target_id'], self.fixture.form['target_id'])

    def test_user_attached_screenshot_reaches_existing_governed_reader(self):
        from investigator.ticket_comments import append
        image = {'id': 'image', 'sha256': 'a'*64, 'available': True}
        with patch.object(self.workspace.screenshots, 'image', return_value=image):
            saved = append(self.workspace, {'ticket_id': self.saved['ticket']['id'], 'revision': self.saved['revision'],
                'request_key': 'user-image', 'text': 'My report screenshot', 'attachment_id': 'image', 'review_id': None})
        self.decisions([{'action': 'TOOL', 'summary': 'Read attached image', 'tool': 'read_screenshot',
            'arguments': {'image_id': 'image'}}, self.hold()])
        result = {'id': 'vision-receipt', 'status': 'EXTRACTED', 'attachment': image,
            'extraction': {'visible_text': 'Global card 16', 'readable': True, 'uncertainties': []}}
        with patch.object(self.workspace.screenshots, 'read', return_value=result) as read:
            delivered = AgentTicket(self.workspace).run(saved)
        self.assertEqual(read.call_count, 1)
        observation = next(x['result'] for x in delivered['ticket']['agent_loop']['transcript'] if x['event'] == 'TOOL_RESULT')
        self.assertEqual(observation['receipt_id'], 'vision-receipt')
        self.assertEqual(observation['positions_status'], 'UNAVAILABLE_FROM_TRANSCRIPTION')
        self.assertFalse(observation['interpretation_verified'])

    def test_other_tickets_screenshot_is_not_authorized(self):
        from investigator.agent_screenshot_reader import reader
        with patch.object(self.workspace.screenshots, 'read', side_effect=AssertionError('unattached image')):
            with self.assertRaises(Conflict): reader(self.workspace, self.saved['ticket']['id'])('other-user-image')

    def test_actual_provider_request_schema_fits_owner_approved_agent_bound(self):
        from investigator.contract_vocabulary import instructions
        from investigator.agent_loop import INSTRUCTIONS
        from ticket_planner import provider_body
        from investigator.privacy_capture import input_characters
        decisions = self.decisions([self.hold()])
        AgentTicket(self.workspace).run(self.saved)
        call = decisions.call_args
        wrapped = {'type': 'object', 'additionalProperties': False,
            'properties': {'decision': call.kwargs['schema']}, 'required': ['decision']}
        body = provider_body(call.args[0], instructions(INSTRUCTIONS, wrapped), wrapped,
            'verified_agent_decision', generation_options=self.workspace.agent.generation_options)
        from investigator.agent_provider import request_bound
        self.assertLessEqual(input_characters(body),request_bound(self.workspace.agent))

    def test_resume_needs_actual_user_reply_and_keeps_step_budget(self):
        from investigator.ticket_comments import append
        self.workspace.agent.config['_estate']['investigation']['step_cap'] = 2
        decisions = self.decisions([{'action': 'TOOL', 'summary': 'Ask target', 'tool': 'ask_user',
            'arguments': {'field':'SELECTION'}}, self.hold()])
        controller = AgentTicket(self.workspace); waiting = controller.run(self.saved)
        with self.assertRaises(Conflict): controller.resume(waiting['ticket']['id'], revision=waiting['revision'], comment_id='made-up')
        replied = append(self.workspace, {'ticket_id': waiting['ticket']['id'], 'revision': waiting['revision'],
            'request_key': 'actual-user-reply', 'text': 'The Global card.', 'attachment_id': None, 'review_id': None})
        result = controller.resume(replied['ticket']['id'], revision=replied['revision'], comment_id='actual-user-reply')
        self.assertEqual(decisions.call_count, 2)
        self.assertEqual(result['ticket']['agent_loop']['status'], 'HELD')
        self.assertEqual(decisions.call_args.args[0]['steps_remaining'], 1)
        self.assertEqual(len(result['ticket']['agent_loop_history']), 1)

    def test_settlement_controller_owns_start(self):
        settlement = agent_intake_settlement.Settlement(self.workspace, text='ticket', key_prefix='test', record_evidence=lambda _: 'id')
        settlement.preview_id = 'preview'
        with patch.object(self.workspace, 'start', return_value={'id': 'session'}) as start:
            settlement.start(controller_owned=True)
        start.assert_called_once_with('preview', controller_owned=True)

    def test_real_preview_start_authority_and_single_loop(self):
        from investigator.onboarding import digest
        self.fixture.f.helper.h.model['discovery']['policy_hash'] = digest(self.workspace.agent.config)
        def retain(ticket):
            ticket['form_input'] = self.fixture.form.copy()
            ticket['form_catalog_hash'] = digest(self.fixture.catalog)
            return ticket
        saved = self.workspace.smart_intake.tickets.update(self.saved['ticket']['id'], self.saved['revision'], retain)
        decisions = self.decisions([{'action': 'TOOL', 'summary': 'Resolve picked scope',
            'tool': 'resolve_ticket', 'arguments': {'extraction': self.fixture.raw}}, self.hold()])
        sequence = iter(decisions.side_effect)
        def decide(*args, **kwargs):
            # The trusted candidate port retains this counter before admission.
            self.workspace._form_candidate_count = 3
            return next(sequence)
        decisions.side_effect = decide
        with patch('investigator.context_search.latest', return_value={'version': 'synthetic-discovery', 'assets': []}), patch.object(self.workspace.agent, 'process_adapter', return_value=Mock()):
            result = AgentTicket(self.workspace).run(saved)
        self.assertTrue(result['ticket'].get('session_id'), result['ticket']['agent_loop'])
        state = self.workspace.agent.get(result['ticket']['session_id'])
        self.assertEqual(state['status'], 'HELD')
        self.assertEqual(state['cloud_calls'], 3)
        self.workspace.smart_intake._bound_session(result['ticket'], state['id'])
        self.assertEqual(result['ticket']['form_input'], self.fixture.form)
        with self.workspace.store.connect() as db:
            self.assertEqual(db.execute('SELECT status FROM workspace_jobs WHERE session_id=?', (state['id'],)).fetchone()[0], 'FINISHED')
        self.assertEqual(decisions.call_count, 2)
        self.fixture.f.helper.h.native.assert_not_called(); self.fixture.f.helper.h.source.assert_not_called()

    def test_client_predecessor_cannot_bypass_saved_intake_authority(self):
        from investigator.onboarding import digest
        self.fixture.f.helper.h.model['discovery']['policy_hash'] = digest(self.workspace.agent.config)
        from investigator.agent_intake_settlement import Settlement
        tool = Settlement(self.workspace, text=self.fixture.form['description'], key_prefix='no-client-parent',
            record_evidence=lambda _: 'evidence', form_request=self.fixture.form)
        admitted = tool.resolve_ticket(self.fixture.raw)
        self.assertEqual(admitted['status'], 'INTAKE_ADMITTED')
        body = self.workspace.intake.get(admitted['intake_id'])
        request = {k: body['proposal'][k] for k in ('model_id','measure_id','filters','dimension_ids')}
        request.update(symptom=body['text'], predecessor='client-invented-session')
        with self.assertRaises(Conflict): self.workspace.intake.review(body['id'], request)

    def test_post_admission_actual_reply_creates_normal_predecessor_not_restart(self):
        from investigator.onboarding import digest
        from investigator.ticket_comments import append
        self.workspace.agent.config['_estate']['investigation']['step_cap'] = 5
        self.fixture.f.helper.h.model['discovery']['policy_hash'] = digest(self.workspace.agent.config)
        def retain(ticket):
            ticket['form_input'] = self.fixture.form.copy()
            ticket['form_catalog_hash'] = digest(self.fixture.catalog)
            return ticket
        saved = self.workspace.smart_intake.tickets.update(self.saved['ticket']['id'], self.saved['revision'], retain)
        resolve = {'action': 'TOOL', 'summary': 'Resolve actual scope', 'tool': 'resolve_ticket', 'arguments': {'extraction': self.fixture.raw}}
        decisions = self.decisions([resolve, {'action': 'TOOL', 'summary': 'Ask owner', 'tool': 'ask_user',
            'arguments': {'field':'SELECTION'}}, resolve, self.hold()])
        controller = AgentTicket(self.workspace)
        with patch('investigator.context_search.latest', return_value={'version': 'synthetic-discovery', 'assets': []}), patch.object(self.workspace.agent, 'process_adapter', return_value=Mock()):
            waiting = controller.run(saved); predecessor = waiting['ticket']['session_id']
            self.assertEqual(self.workspace.agent.get(predecessor)['status'], 'NEEDS_INPUT')
            reply = append(self.workspace, {'ticket_id': waiting['ticket']['id'], 'revision': waiting['revision'],
                'request_key': 'owner-continue', 'text': 'Continue the same selected scope.', 'attachment_id': None, 'review_id': None})
            result = controller.resume(reply['ticket']['id'], revision=reply['revision'], comment_id='owner-continue')
        self.assertIn('session_id', result['ticket'], result['ticket']['agent_loop'])
        successor = result['ticket']['session_id']
        self.assertNotEqual(successor, predecessor)
        self.assertEqual(self.workspace.agent.get(predecessor)['status'], 'NEEDS_INPUT')
        self.assertEqual(self.workspace.agent.get(successor)['predecessor']['session_id'], predecessor)
        self.assertEqual(result['ticket']['form_input'], self.fixture.form)
        self.assertEqual(decisions.call_args.args[0]['steps_remaining'], 2)
        self.assertEqual(decisions.call_count, 4)


    def test_archived_initial_request_still_fits_32000_without_new_protocol(self):
        self.workspace.agent.config['_estate']['investigation']['input_characters_per_request']=32000
        with patch('investigator.intake_span_references.enabled',return_value=False):
            self.test_actual_provider_request_schema_fits_owner_approved_agent_bound()

if __name__ == '__main__': unittest.main()
