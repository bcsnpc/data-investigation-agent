"""Golden planner views for historical failure shapes, using synthetic content."""
import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from investigator import dynamic_reasoning
from investigator.domain_profile import for_planner
from investigator.onboarding import digest, encoded
from investigator.planner_projection import fit

FIXTURES = Path(__file__).parent / 'fixtures' / 'planner-view'


def project(case):
    payload = copy.deepcopy(case['payload'])
    if 'domain_profile' in payload:
        payload['domain_profile'] = for_planner(payload['domain_profile'], case.get('focus_table'))
    dynamic_reasoning.compact_context(payload)
    payload = fit(payload, case['ceiling'])
    wire, schema, handles = dynamic_reasoning.wire_contract(payload)
    return {'projected': payload, 'wire': wire, 'schema_hash': digest(schema), 'handles': handles}


class PlannerProjectionTests(unittest.TestCase):
    def test_directory_coverage_survives_context_projection(self):
        from types import SimpleNamespace
        case=json.loads((FIXTURES/'directory-coverage.json').read_text(encoding='utf-8'))
        store=SimpleNamespace(get=lambda _: {'context':{'model_assets':[]}})
        state={'model_id':'model','observations':[], 'decisions':[],
               'discovery_version':'synthetic','planner_calls':0,'input_characters':0,
               'envelope':{'measure_id':'measure','dimension_ids':[],
                           'limits':{'planner_calls':12,'input_characters':384000}}}
        with patch.object(dynamic_reasoning.context_search,'latest',return_value=case):
            payload=dynamic_reasoning.enrich(store,state,{'observations':[]})
        entries=payload['context_entry_points']
        self.assertEqual(len(entries),case['expected_entries'])
        self.assertEqual(sum(e['kind']=='SqlObject' for e in entries),case['expected_sql_objects'])
        self.assertTrue(payload['context_directory_truncated'])
        self.assertTrue(all(set(e)=={'id','kind','name'} for e in entries))
        self.assertLessEqual(sum(len(encoded(e)) for e in entries),4000)

    def setUp(self):
        self.inputs = json.loads((FIXTURES / 'inputs.json').read_text(encoding='utf-8'))
        self.golden = json.loads((FIXTURES / 'expected.json').read_text(encoding='utf-8'))

    def test_exact_projected_and_wire_context_goldens(self):
        for name, case in self.inputs.items():
            with self.subTest(name=name):
                before = encoded(case)
                self.assertEqual(project(case), self.golden[name])
                self.assertEqual(encoded(case), before)

    def test_recorded_sdk_requests_match_all_wire_goldens_without_network(self):
        import httpx
        from openai import DefaultHttpxClient
        from investigator import planner_recording
        from investigator.adaptive_planner import azure_plan
        with tempfile.TemporaryDirectory() as folder:
            def transport(request):
                body = json.loads(request.content)
                slots = body['tools'][0]['parameters']['properties']['hypotheses']['required']
                proposal = {'next': {'kind': 'ASK', 'question': 'Which intended rule applies?'},
                            'hypotheses': {slot: None for slot in slots}}
                return httpx.Response(200, json={'id': 'mock', 'object': 'response', 'model': 'mock',
                    'status': 'completed', 'usage': None, 'output': [{'type': 'function_call',
                    'call_id': 'mock-call', 'name': 'dynamic_investigation_action',
                    'arguments': json.dumps(proposal)}]})
            with patch.object(planner_recording, 'ROOT', Path(folder)), patch.dict(os.environ, {
                    'INVESTIGATOR_RECORD_PLANNER': '1', 'AZURE_OPENAI_ENDPOINT': 'https://offline.openai.azure.com',
                    'AZURE_OPENAI_DEPLOYMENT': 'offline', 'AZURE_OPENAI_API_KEY': 'offline-placeholder-credential'}), \
                    patch('openai.DefaultHttpxClient', side_effect=lambda **kw: DefaultHttpxClient(
                        transport=httpx.MockTransport(transport), **kw)):
                for name, case in self.inputs.items():
                    with planner_recording.recording({'session_id': name, 'planner_call': 1,
                            'context_version': 'synthetic', 'budget': None, 'reservation': None}):
                        azure_plan(project(case)['projected'])
                    calls = planner_recording.load_session(name, Path(folder) / '.local/planner-recordings')
                    body = json.loads(calls[0]['bodies']['request.body'])
                    self.assertEqual(json.loads(body['input']), self.golden[name]['wire'])
                    self.assertEqual(digest(body['tools'][0]['parameters']), self.golden[name]['schema_hash'])

    def test_dense_scoped_profile_keeps_selected_table_and_members(self):
        result = project(self.inputs['dense-profile'])['projected']['domain_profile']
        table = result['tables'][0]
        self.assertEqual(table['asset_id'], self.inputs['dense-profile']['focus_table'])
        self.assertTrue(table['numeric_columns'])
        self.assertTrue(table['measure_ids'])
        self.assertEqual(table['numeric_columns_profile_count'], 8)
        self.assertLessEqual(len(encoded(result)), 2500)
        self.assertEqual(result['planner_tables_available'], len(result['tables']) + result['planner_tables_omitted'])

    def test_definition_child_after_ten_other_children_remains_navigable(self):
        result = project(self.inputs['definition-children'])
        children = result['projected']['observations'][0]['metadata']['children']
        self.assertIn('definition:part', [child['id'] for child in children])
        wire, schema, handles = dynamic_reasoning.wire_contract(result['projected'])
        content = next(choice for choice in schema['properties']['next']['anyOf']
                       if choice['properties'].get('operation', {}).get('enum') == ['content'])
        self.assertIn('definition:part', [handles[h] for h in content['properties']['value']['enum']])
        audit = wire['lookup_handle_projection']
        self.assertEqual(audit['available_identities'], audit['retained_handles'] + audit['omitted_handles'])
        self.assertGreater(audit['omitted_handles'], 0)
        self.assertFalse(audit['catalog_removal'])

    def test_paged_old_content_omission_is_counted_not_catalog_removal(self):
        result = project(self.inputs['paged-content'])['projected']
        metadata = [o['metadata'] for o in result['observations'][:-1]]
        self.assertEqual(sum(len(m['content']) for m in metadata), 2500)
        self.assertTrue(metadata[-1]['content'])
        self.assertEqual(metadata[0]['planner_content_projection']['status'], 'OMITTED')
        self.assertEqual(metadata[-1]['planner_content_projection']['status'], 'TRUNCATED')
        for index, m in enumerate(metadata):
            audit = m['planner_content_projection']
            self.assertEqual(audit['retained_characters'] + audit['omitted_characters'], 6000)
            self.assertFalse(audit['catalog_removal'])
            self.assertEqual(m['offset'], index * 6000)
            self.assertEqual(m['next_offset'], (index + 1) * 6000)
            self.assertEqual(m['retained_end_offset'], m['offset'] + len(m['content']))

    def test_excess_per_call_input_is_fitted_deterministically(self):
        case = self.inputs['per-call-ceiling']
        self.assertGreater(len(encoded(case['payload'])), case['ceiling'])
        result = project(case)['projected']
        self.assertLessEqual(len(encoded(result)), case['ceiling'])
        self.assertEqual(result['planner_projection']['status'], 'TRUNCATED')
        self.assertEqual(result, project(case)['projected'])
        self.assertEqual(result['scope_hash'], case['payload']['scope_hash'])

    def test_protected_scope_cannot_be_silently_shed(self):
        payload = {'symptom': 'x' * 35000, 'observations': [], 'scope_hash': 'scope'}
        projected = fit(payload, 32000)
        self.assertEqual(projected['symptom'], payload['symptom'])
        self.assertEqual(projected['planner_projection']['status'], 'PROTECTED_CONTEXT_EXCEEDS_LIMIT')

    def test_metadata_compaction_does_not_inflate_an_already_bounded_schema(self):
        payload = copy.deepcopy(self.inputs['per-call-ceiling']['payload'])
        original = encoded(payload['observations'][0]['metadata'])
        dynamic_reasoning.compact_context(payload)
        self.assertLessEqual(len(encoded(payload['observations'][0]['metadata'])), len(original))

    def test_runtime_fits_before_reserving_and_dispatching(self):
        import test_flexible_investigation as fixture
        from investigator.adaptive_runtime import AdaptiveRuntime
        helper = fixture.DynamicTests()
        helper.setUp()
        self.addCleanup(helper.doCleanups)
        calls = []
        def planner(payload):
            calls.append(payload)
            self.assertLessEqual(len(encoded(payload)), 32000)
            return helper.decision('ASK', question='Which intended business rule applies?')
        agent = AdaptiveRuntime(helper.runtime, planner)
        payload = self.inputs['per-call-ceiling']['payload']
        with patch.object(agent, 'payload', return_value=copy.deepcopy(payload)):
            state = agent.run(agent.create(helper.envelope, 'projection-bound')['id'])
        self.assertEqual(len(calls), 1)
        self.assertEqual(state['planner_calls'], 1)
        self.assertEqual(state['input_characters'], len(encoded(calls[0])))
        self.assertEqual(state['stop_reason'], 'CLARIFICATION_REQUIRED')


if __name__ == '__main__':
    unittest.main()
