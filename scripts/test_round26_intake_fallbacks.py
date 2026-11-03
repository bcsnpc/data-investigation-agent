from copy import deepcopy
import unittest
from investigator.guided_intake import Catalog, admit, admit_or_question
from test_round23_intake_queries import graph, request


class ComparisonFallbackTests(unittest.TestCase):
    def test_rejected_quantity_span_does_not_reask_report_for_known_measure(self):
        from unittest.mock import Mock
        from investigator.guided_text_resolver import Resolver
        from test_round23_text_resolver import reference
        from test_round23_reasoning import tool
        text='Measure shows 950 for record 42.'
        wide=reference(text,'950 for record 42');narrow=reference(text,'950')
        value={'version':'IntakeRequest/1','measure':'measure','issue_type':'NUMBER_LOOKS_WRONG',
               'reported_figure':{'state':'NUMBER','value':'950','precision':'EXACT'},'compared_with':{'kind':'NOTHING'}}
        def arguments(span):return {'proposal':deepcopy(value),'provenance':{'reported_figure':span},
                                  'figure_mentions':[{'role':'PRIMARY','reference':span}]}
        model=Mock();model.complete.side_effect=[tool('resolve_intake',arguments(wide)),tool('resolve_intake',arguments(narrow))]
        result=Resolver(catalog=Catalog(graph()),model=model,record=Mock()).resolve(text)
        self.assertEqual(result['status'],'READY');self.assertEqual(result['measure'],'measure')
        model=Mock();model.complete.return_value=tool('resolve_intake',arguments(wide))
        result=Resolver(catalog=Catalog(graph()),model=model,record=Mock()).resolve(text)
        self.assertEqual(result['status'],'NEEDS_INPUT');self.assertEqual(model.complete.call_count,2)
        self.assertEqual([x['field']for x in result['question']['fields']],['figure_interpretation'])
        self.assertEqual(result['prefilled']['measure'],'measure')
        self.assertEqual(result['extraction_rejection']['type'],'UnavailablePrecision')

    def test_ambiguous_table_target_question_offers_tables_not_reports(self):
        from unittest.mock import Mock
        from investigator.guided_text_resolver import Resolver
        from test_round23_reasoning import tool
        g=graph();g['nodes'] += [{'id':k,'kind':'TABLE','label':'Rows'}for k in ('left-table','right-table')]
        args={'proposal':{'version':'IntakeRequest/1','table':'left-table','issue_type':'NUMBER_LOOKS_WRONG',
                          'compared_with':{'kind':'NOTHING'}},'provenance':{},'figure_mentions':[]}
        model=Mock();model.complete.return_value=tool('resolve_intake',args)
        result=Resolver(catalog=Catalog(g),model=model,record=Mock()).resolve('Rows differ between exports.')
        self.assertEqual(result['status'],'NEEDS_INPUT')
        self.assertEqual([x['field']for x in result['question']['fields']],['table'])
        self.assertEqual({c['id']for c in result['question']['fields'][0]['choices']},{'left-table','right-table'})
        result=Resolver(catalog=Catalog(g),model=model,record=Mock()).resolve('Check the export.')
        self.assertEqual([x['field']for x in result['question']['fields']],['table'])
        self.assertEqual(len(result['question']['fields'][0]['choices']),2)

    def test_each_native_comparison_exception_has_generic_reproduction(self):
        # Public receipt IDs only; no held-out wording or expectation enters this test.
        receipts = ['v4-application-baseline-3', 'v4-application-baseline-2', 'v4-fixture-quantity-3', 'v4-record-absent-everywhere-1', 'v4-record-absent-everywhere-2', 'v4-record-absent-everywhere-3', 'v4-record-repeated-gold-2', 'v4-record-repeated-gold-3', 'v4-warehouse-scope-2', 'v4-warehouse-scope-3']
        for receipt in receipts:
            for kind in ("SOURCE_SYSTEM", "ANOTHER_REPORT", "EXPECTED_NUMBER"):
                with self.subTest(native_receipt=receipt, comparison_kind=kind):
                    value = request(); value["compared_with"] = {"kind": kind}
                    result = admit_or_question(value, Catalog(graph()))
                    self.assertEqual(result["status"], "READY")
                    self.assertEqual(result["visual"], "card")
                    self.assertTrue(result["format_warnings"])

    def test_empty_or_nontext_free_text_asks_without_model_or_exception(self):
        from unittest.mock import Mock
        from investigator.guided_text_resolver import Resolver
        model = Mock()
        resolver = Resolver(catalog=Catalog(graph()), model=model, record=Mock())
        for value in (None, '', ' ', [], {}, True):
            self.assertEqual(resolver.resolve(value)['status'], 'NEEDS_INPUT')
        model.complete.assert_not_called()
    def test_public_boundary_fuzz_has_no_unhandled_shape_errors(self):
        catalog = Catalog(graph())
        forms = [None, [], '', 1, True, {}, request()]
        for field in request():
            missing = request(); del missing[field]; forms.append(missing)
            for malformed in (None, '', [], {}, 0, True):
                value = request(); value[field] = malformed; forms.append(value)
        for kind in ('NOTHING', 'SOURCE_SYSTEM', 'ANOTHER_REPORT', 'EXPECTED_NUMBER'):
            for field in ('target', 'source', 'figure'):
                for value in (None, {}, [], '', 'unknown', {'report': 'other'}):
                    form = request(); form['compared_with'] = {'kind': kind, field: value}; forms.append(form)
        for value in forms:
            with self.subTest(form=value):
                result = admit_or_question(value, catalog)
                self.assertIn(result['status'], ('READY', 'NEEDS_INPUT'))

    def test_malformed_figure_does_not_reask_known_report_page_or_visual(self):
        value = request(); value['reported_figure'] = {'state': 'NUMBER', 'value': '2'}
        result = admit_or_question(value, Catalog(graph()))
        self.assertEqual([f['field'] for f in result['question']['fields']], ['intake_details'])
        self.assertEqual(result['prefilled']['visual'], 'card')

    def test_unknown_id_choices_are_catalog_names(self):
        value = request(); value['visual'] = 'invented'
        result = admit_or_question(value, Catalog(graph()))
        self.assertEqual(result['question']['fields'][0]['choices'], [{'id': 'card', 'name': 'Card'}])

    def test_missing_details_preserve_target_and_reach_recreation(self):
        for kind in ('SOURCE_SYSTEM', 'ANOTHER_REPORT', 'EXPECTED_NUMBER'):
            value = request()
            value['compared_with'] = {'kind': kind}
            original = deepcopy(value)
            result = admit(value, Catalog(graph()))
            self.assertEqual(value, original)
            self.assertEqual(result['status'], 'READY')
            self.assertEqual(result['visual'], 'card')
            self.assertEqual(result['compared_with'], {'kind': 'NOTHING'})
            self.assertEqual(result['comparison_context'], {'kind': kind})
            self.assertTrue(result['format_warnings'])

    def test_fallback_uses_only_explicit_single_source_declaration(self):
        value = request()
        value['compared_with'] = {'kind': 'EXPECTED_NUMBER'}
        g = graph()
        source = next(n for n in g['nodes'] if n['id'] == 'source')
        source['properties'] = {'system_of_record': True}
        result = admit(value, Catalog(g))
        self.assertEqual(result['compared_with'], {'kind': 'SOURCE_SYSTEM', 'source': 'source'})
        g['nodes'].append({'id': 'second', 'kind': 'SOURCE', 'label': 'Second',
                           'properties': {'system_of_record': True}})
        self.assertEqual(admit(value, Catalog(g))['compared_with'], {'kind': 'NOTHING'})

    def test_supporting_fields_do_not_crash_or_replace_selected_target(self):
        value = request()
        value['compared_with']['figure'] = {'state': 'NUMBER', 'value': '7', 'precision': 'EXACT'}
        result = admit(value, Catalog(graph()))
        self.assertEqual(result['compared_with'], {'kind': 'NOTHING'})
        self.assertEqual(result['comparison_context']['figure']['value'], '7')

    def test_competing_target_remains_explicit_ambiguity(self):
        value = request()
        value['compared_with'] = {'kind': 'SOURCE_SYSTEM', 'source': 'source', 'target': {'report': 'other'}}
        with self.assertRaisesRegex(ValueError, 'CONFLICTING_COMPARISON_TARGET'):
            admit(value, Catalog(graph()))
        del value['compared_with']['source']
        with self.assertRaisesRegex(ValueError, 'CONFLICTING_COMPARISON_TARGET'):
            admit(value, Catalog(graph()))
