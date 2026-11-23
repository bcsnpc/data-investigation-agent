from copy import deepcopy
import unittest
from investigator.delivery_references import reformat
from investigator.grounded_answers import cited


class ReferenceTests(unittest.TestCase):
    def setUp(self):
        self.query = {'id': 'query-one', 'layer': 'source', 'status': 'SUCCEEDED',
                      'time': '2026-11-21T00:00:00Z', 'result': {'rows': [{'units': 25}]}}
        self.evidence = {'fetch': {'tool': 'get_evidence', 'arguments': {'id': 'query-one'},
                                   'result': deepcopy(self.query)}}

    def run_reformat(self, args, evidence=None):
        return reformat(args, queries=[self.query], evidence=self.evidence if evidence is None else evidence,
                        layers={'source': {}})

    def test_exact_query_roles_are_reformatted_without_mutating_input(self):
        value = {'checked': ['query-one', 'source', 'fetch'], 'evidence_ids': ['fetch'],
                 'selected_target': 'explicit', 'numbers': [25]}
        before = deepcopy(value)
        result, changes = self.run_reformat(value)
        self.assertEqual(result['checked'], ['source'])
        self.assertEqual(result['evidence_ids'], ['query-one'])
        self.assertEqual(result['selected_target'], 'explicit')
        self.assertEqual(result['numbers'], [25])
        self.assertEqual(value, before)
        self.assertEqual(len(changes), 3)

    def test_unknown_and_graph_references_are_not_guessed(self):
        result, changes = self.run_reformat({'checked': ['graph-node', 'unknown'], 'evidence_ids': ['unknown']})
        self.assertEqual(result['checked'], ['graph-node', 'unknown'])
        self.assertEqual(result['evidence_ids'], ['unknown'])
        self.assertEqual(changes, [])

    def test_graph_address_maps_only_to_one_cited_successful_native_query_layer(self):
        self.query['asset_ids']=['native-measure']
        nodes=[{'id':'graph-measure','properties':{'asset_id':'native-measure'}}]
        value={'checked':['graph-measure'],'evidence_ids':['query-one'],'selected_target':'unchanged'}
        result,_=reformat(value,queries=[self.query],evidence={},layers={'source':{}},nodes=nodes)
        self.assertEqual(result['checked'],['source']);self.assertEqual(result['evidence_ids'],value['evidence_ids'])
        self.assertEqual(result['selected_target'],'unchanged')
        for queries,ids in [([self.query],[]),([{**self.query,'status':'ERROR'}],['query-one']),
                            ([self.query,{**self.query,'id':'q2','layer':'other'}],['query-one','q2'])]:
            with self.subTest(queries=queries,ids=ids):
                r,_=reformat({**value,'evidence_ids':ids},queries=queries,evidence={},layers={'source':{},'other':{}},nodes=nodes)
                self.assertEqual(r['checked'],['graph-measure'])

    def test_cited_observed_job_is_already_evidence_and_not_a_measured_layer(self):
        nodes=[{'id':'job','properties':{'asset_id':'native-job'}}]
        evidence={'j':{'tool':'get_job_runs','arguments':{'node':'job'},'result':
                      {'status':'OBSERVED','source':'native','observed_at':'2026-11-22T00:00:00Z'}}}
        value={'checked':['job'],'evidence_ids':['j']}
        result,changes=reformat(value,queries=[],evidence=evidence,layers={},nodes=nodes)
        self.assertEqual(result['checked'],[]);self.assertEqual(result['evidence_ids'],['j'])
        self.assertEqual(changes[0]['reason'],'ALREADY_CITED_NATIVE_OBJECT_NOT_QUERY_LAYER')
        for ids,status in [([], 'OBSERVED'),(['j'],'UNAVAILABLE')]:
            evidence['j']['result']['status']=status
            r,_=reformat({**value,'evidence_ids':ids},queries=[],evidence=evidence,layers={},nodes=nodes)
            self.assertEqual(r['checked'],['job'])
    def test_definition_binding_uses_the_exact_already_queried_measure_only(self):
        nodes=[{'id':'measure','kind':'MEASURE','properties':{'asset_id':'native-measure'}}]
        self.query['asset_ids']=['native-measure']
        evidence={'definition':{'kind':'RETAINED_DEFINITION_REFERENCE','asset_id':'native-measure'}}
        value={'checked':['source'],'evidence_ids':['query-one'],'numbers':[25],'selected_target':'explicit'}
        result,changes=reformat(value,queries=[self.query],evidence=evidence,layers={'source':{}},nodes=nodes,definition_measure='measure')
        self.assertEqual(result['evidence_ids'],['query-one','definition'])
        self.assertEqual(result['numbers'],value['numbers']);self.assertEqual(result['selected_target'],'explicit')
        self.assertEqual(changes[0]['reason'],'RETAINED_DEFINITION_OF_ALREADY_CITED_MEASURE')
        for queries,ids,refs,selected in [([self.query],[],evidence,'measure'),
                ([{**self.query,'status':'ERROR'}],['query-one'],evidence,'measure'),
                ([self.query],['query-one'],{**evidence,'duplicate':evidence['definition']},'measure'),
                ([self.query],['query-one'],evidence,'different-measure')]:
            with self.subTest(queries=queries,ids=ids,refs=refs,selected=selected):
                r,_=reformat({**value,'evidence_ids':ids},queries=queries,evidence=refs,layers={'source':{}},nodes=nodes,definition_measure=selected)
                self.assertEqual(r['evidence_ids'],ids)
    def test_calculation_measure_is_a_declared_selection_or_unique_visual_edge(self):
        from investigator.delivery_references import calculation_measure
        context={'intake':{'issue_type':'SOMETHING_ELSE','visual':'v','compared_with':{'kind':'NOTHING'}},
                 'path':{'nodes':[{'id':'m','kind':'MEASURE'},{'id':'m2','kind':'MEASURE'}],
                         'edges':[{'source':'v','target':'m','kind':'COMPUTED_FROM'}]}}
        draft={'verdict':'definition explained','classified_issue_type':'HOW_IS_THIS_CALCULATED'}
        self.assertEqual(calculation_measure(context,draft),'m')
        context['path']['edges'].append({'source':'v','target':'m2','kind':'COMPUTED_FROM'})
        self.assertIsNone(calculation_measure(context,draft))
        context['intake']['details']={'measure':'m2'}
        self.assertEqual(calculation_measure(context,draft),'m2')
        context['intake']['comparison_context']={'kind':'EXPECTED_NUMBER'}
        self.assertIsNone(calculation_measure(context,draft))

    def test_native_tool_wrapper_can_name_its_exact_query_layer(self):
        evidence = {'sql': {'tool': 'run_sql', 'result': {'record': self.query}}}
        result, _ = self.run_reformat({'checked': ['sql']}, evidence)
        self.assertEqual(result['checked'], ['source'])

    def test_nested_fetch_resolves_original_native_support(self):
        evidence = {**self.evidence, 'second': {'tool': 'get_evidence', 'arguments': {'id': 'fetch'}}}
        result, _ = self.run_reformat({'evidence_ids': ['second'], 'verdict': 'as designed'}, evidence)
        self.assertEqual(result['evidence_ids'], ['query-one'])
        self.assertEqual(cited(result, {'queries': [self.query], 'evidence': evidence})[0]['native_result'], self.query['result'])

    def test_fetch_does_not_turn_model_output_into_native_support(self):
        evidence = {'model': {'kind': 'MODEL_RESPONSE'},
                    'fetch': {'tool': 'get_evidence', 'arguments': {'id': 'model'}}}
        result, _ = self.run_reformat({'evidence_ids': ['fetch'], 'verdict': 'as designed'}, evidence)
        with self.assertRaisesRegex(ValueError, 'MODEL_OUTPUT_IS_NOT_NATIVE_SUPPORT'):
            cited(result, {'queries': [], 'evidence': evidence})

    def test_fetched_native_definition_retains_its_original_identity(self):
        definition = {'content': 'SUM(Activity[units])', 'provenance': {'source': 'COLLECTED_DEFINITION'}}
        evidence = {'definition': {'tool': 'get_definition', 'result': definition},
                    'fetch': {'tool': 'get_evidence', 'arguments': {'id': 'definition'}}}
        result, _ = self.run_reformat({'evidence_ids': ['fetch'], 'verdict': 'as designed'}, evidence)
        self.assertEqual(result['evidence_ids'], ['definition'])
        self.assertEqual(cited(result, {'queries': [], 'evidence': evidence}), [definition])

    def test_failed_query_still_cannot_support_a_successful_finding(self):
        self.query['status'] = 'ERROR'
        result, _ = self.run_reformat({'evidence_ids': ['fetch'], 'verdict': 'as designed'})
        with self.assertRaisesRegex(ValueError, 'FAILED_QUERY_DOES_NOT_SUPPORT'):
            cited(result, {'queries': [self.query], 'evidence': self.evidence})

    def test_cyclic_fetch_is_left_for_ordinary_validation(self):
        evidence = {'a': {'tool': 'get_evidence', 'arguments': {'id': 'b'}},
                    'b': {'tool': 'get_evidence', 'arguments': {'id': 'a'}}}
        result, changes = self.run_reformat({'evidence_ids': ['a']}, evidence)
        self.assertEqual(result['evidence_ids'], ['a'])
        self.assertEqual(changes, [])

    def test_dispatch_reformats_before_validation_and_records_the_change(self):
        from types import SimpleNamespace
        from unittest.mock import Mock
        from jsonschema import Draft202012Validator
        from investigator.ai_investigation import Investigator, toolbox
        from investigator.regression_features import configured
        loop = object.__new__(Investigator)
        loop.context = {}
        loop.queries = SimpleNamespace(records=[self.query], layers={'source': {'dialect': 'TSQL'}})
        loop.state = {'evidence': deepcopy(self.evidence)}
        loop.refresh_tools = lambda: None
        loop.tools = toolbox(loop.queries.layers, {})
        loop.schemas = {t['name']: Draft202012Validator(t['input_schema']) for t in loop.tools}
        loop.case_view = Mock(return_value={})
        loop.validate_finding = Mock(return_value={'business': 'The scoped read returned 25.'})
        loop.repair_delivery = Mock(side_effect=ValueError('MODEL_REFORMAT_REQUIRED'))
        args = {'verdict': 'observed value', 'cause': 'Scoped native read.', 'numbers': [25],
                'checked': ['query-one'], 'evidence_ids': ['fetch']}
        with configured({'r27_delivery_reference_reformat': True}):
            result = loop.dispatch('submit_finding', args)
        self.assertEqual(result['business'], 'The scoped read returned 25.')
        delivered = loop.validate_finding.call_args.args[0]
        self.assertEqual(delivered['checked'], ['source'])
        self.assertEqual(delivered['evidence_ids'], ['query-one'])
        self.assertTrue(any(x.get('kind') == 'DELIVERY_REFERENCE_REFORMAT' for x in loop.state['evidence'].values()))
        loop.repair_delivery.assert_not_called()
        with configured({'r27_delivery_reference_reformat': False}):
            with self.assertRaisesRegex(ValueError, 'MODEL_REFORMAT_REQUIRED'):
                loop.dispatch('submit_finding', args)


if __name__ == '__main__':
    unittest.main()
