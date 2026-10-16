import copy
import unittest
from unittest.mock import patch
from investigator.agent_intake_settlement import Settlement, DESCRIPTION
from investigator import intake_extraction
from investigator.onboarding import Conflict
import test_form_controller
from test_intake_extraction import fixture

class SettlementTests(unittest.TestCase):
    def setUp(self):
        self.f = test_form_controller.FormControllerTests(); self.f.setUp(); self.addCleanup(self.f.doCleanups)
        self.workspace = self.f.workspace; self.records = []
        # This fixture's neutral model ID is the actual store model ID. Use its
        # real retained measure IDs for normal preview/creation admission.
        from investigator.onboarding import digest
        self.f.helper.h.model.update(workspace='00000000-0000-0000-0000-000000000001', native_id='00000000-0000-0000-0000-000000000002')
        self.workspace.agent.config['fabric'].update(workspace_id=self.f.helper.h.model['workspace'], native_reader={
            'mode': 'isolated_reader', 'tenant_id': '00000000-0000-0000-0000-000000000003',
            'principal_id': '00000000-0000-0000-0000-000000000004', 'account': 'reader@example.test',
            'model_ids': [self.f.helper.h.model['native_id']]})
        self.f.helper.h.model['discovery'] = {'policy_hash': digest(self.workspace.agent.config)}
        for name in ('investigator.question_intake.fingerprint', 'investigator.workspace.fingerprint'):
            guard=patch(name, return_value='test-frozen-engine'); guard.start(); self.addCleanup(guard.stop)
        self.f.helper.h.model['context']['reports'][0]['report'] = {'id': 'report', 'name': 'Report'}
        self.catalog = self.f.catalog
        self.catalog['models'][0]['measures'][0].update(id='Unseen ratio', name='Quantity')
        for visual in self.catalog['models'][0]['visuals']:
            visual['measure_ids'] = ['Unseen ratio']
            visual['declared_scopes']['Unseen ratio'] = visual['declared_scopes'].pop('measure')
        p=patch('investigator.question_intake.snapshot', return_value=self.catalog); p.start(); self.addCleanup(p.stop)
        self.raw, _ = fixture('In Report, Global card Quantity differs.', visuals=[{'quote': 'Global card', 'role': 'PRIMARY', 'form': 'TITLE'}])
        self.form = {**self.f.request, 'description': 'In Report, Global card Quantity differs.'}
    def tool(self, **changes):
        return Settlement(self.workspace, text=self.form['description'], key_prefix='agent-test',
            record_evidence=lambda b: self.records.append(b) or 'settlement-evidence', form_request=changes.pop('form_request', self.form), **changes)
    def test_real_preview_durable_review_and_zero_old_provider_calls(self):
        tool = self.tool()
        with patch.object(self.workspace.intake, 'resolver', side_effect=AssertionError('old provider forbidden')):
            result = tool.resolve_ticket(self.raw)
        self.assertEqual(result['status'], 'INTAKE_ADMITTED', result)
        saved = self.workspace.intake.get(result['intake_id'])
        self.assertEqual(saved['provider_calls'], 0)
        self.assertEqual(saved['scope_provenance'], 'AGENT_VALIDATED_EXTRACTION')
        self.assertEqual(self.workspace.read_preview(result['preview_id'])['intake']['id'], result['intake_id'])
        self.assertEqual(saved['proposal']['target_visual']['target_id'], 'card')
        self.f.helper.h.native.assert_not_called(); self.f.helper.h.source.assert_not_called()
    def test_controller_normal_start_creates_ready_session_without_reads(self):
        tool = self.tool(); result = tool.resolve_ticket(self.raw)
        self.assertEqual(result['status'], 'INTAKE_ADMITTED')
        with patch('investigator.context_search.latest', return_value={'version': 'synthetic-discovery', 'assets': []}):
            session = tool.start()
        self.assertTrue(session['id'])
        self.assertEqual(self.workspace.agent.get(session['id'])['status'], 'READY')
        self.f.helper.h.native.assert_not_called(); self.f.helper.h.source.assert_not_called()

    def test_nonverbatim_and_picked_target_conflict_refuse_without_preview(self):
        raw = copy.deepcopy(self.raw); raw['primary'] = 'invented question'
        self.assertEqual(self.tool().resolve_ticket(raw)['status'], 'UNRESOLVED')
        raw = copy.deepcopy(self.raw); raw['visuals'][0]['quote'] = 'Warehouse matrix'
        form = {**self.form, 'description': 'In Report, Warehouse matrix Quantity differs.'}
        self.assertEqual(self.tool(form_request=form).resolve_ticket(raw)['status'], 'UNRESOLVED')
        self.f.helper.h.native.assert_not_called()
    def test_fixed_form_is_copied_and_missing_preview_cannot_start(self):
        tool = self.tool(); self.form['target_id'] = 'matrix'
        self.assertEqual(tool.form['target_id'], 'card')
        with self.assertRaises(Conflict): tool.start()
    def test_repeated_tool_call_reuses_preview_and_cannot_rebind(self):
        tool = self.tool(); first = tool.resolve_ticket(self.raw); second = tool.resolve_ticket(self.raw)
        self.assertEqual(first, second)
        changed = copy.deepcopy(self.raw); changed['figures'] = [{'quote': '16', 'occurrence': None, 'role': 'PRIMARY', 'state': 'NUMBER', 'precision_quote': None}]
        with self.assertRaises(Conflict): tool.resolve_ticket(changed)

    def test_empty_description_complete_form_needs_no_extraction_provider(self):
        tool = self.tool(form_request={**self.form, 'description': ''})
        self.assertEqual(tool.resolve_ticket(self.raw)['status'], 'INTAKE_ADMITTED')
    def test_citation_is_required(self):
        tool = self.tool(); tool.record_evidence = lambda body: None
        with self.assertRaises(Conflict): tool.resolve_ticket(self.raw)

    def test_agent_tool_supplies_shared_primary_ask_extraction_instructions(self):
        self.assertIn(intake_extraction.PRIMARY_REFERENT_INSTRUCTIONS, DESCRIPTION)
        self.assertIn(intake_extraction.PRIMARY_REFERENT_INSTRUCTIONS, intake_extraction.INSTRUCTIONS)

    def test_subject_form_requires_actual_ask_in_primary_quote(self):
        text = 'In Report, Global card Quantity looks high. Explain the numerator and denominator using the actual measure definitions.'
        form = {**self.form, 'description':text, 'comparison':None}
        raw = copy.deepcopy(self.raw)
        raw.update(primary='Quantity looks high',kind='METRIC_COMPONENTS',triage='MISMATCH_COMPLAINT:VERTICAL')
        rejected = self.tool(form_request=form).resolve_ticket(raw)
        self.assertEqual(rejected['status'],'UNRESOLVED')
        self.assertIn('comparison or declared subject',rejected['reason'])
        raw['primary']=text
        result=self.tool(form_request=form).resolve_ticket(raw)
        self.assertEqual(result['status'],'INTAKE_ADMITTED',result)
        self.assertEqual(result['scope']['question_kind']['kind'],'METRIC_COMPONENTS')
        self.assertEqual(result['scope']['target_visual']['target_id'],'card')
        self.f.helper.h.native.assert_not_called()

if __name__ == '__main__': unittest.main()
