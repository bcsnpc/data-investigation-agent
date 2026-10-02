from investigator.reported_figure import from_candidates

def exact(value):
 text=str(value)
 return from_candidates([{"start":0,"end":len(text),"quote":text}],text)

import copy
import unittest

from investigator import declared_reproduction as reproduction, process_outcomes
from investigator.process_debugging import Probe, vertical
from investigator.synthesis_digest import _process_evidence
from investigator import narrative_form
from test_process_debugging import Adapter


class NeutralAdapter(Adapter):
    def __init__(self, reported_value=3, **kwargs):
        super().__init__(['top', 'lower'], {'top': 8, 'lower': 9}, **kwargs)
        self.declared_value = reported_value
        self.restrictions = [
            {'field_id': 'field-a', 'operator': 'IN', 'values': ['x', 'y']},
            {'field_id': 'field-a', 'operator': 'IN', 'values': ['y', 'z']}]
        self.read_scopes = []
        self.events = []
        self.identity = 'reader'
        self.object = 'top'
        self.report = True
        self.applied = True

    def capabilities(self):
        return super().capabilities() | {reproduction.CAPABILITY}

    def declared_context(self, layer, measure_id, scope):
        from investigator.declaration_inventory import identity
        source={'location':'definition/selection','content_hash':'a'*64}
        return {'status': 'DECLARED', 'restrictions': copy.deepcopy(self.restrictions),
                'inventory':{'discovered':[source], 'entries':[{'id':identity(source),'source':source,
                    'disposition':'ACTIVE','volatility':'FIXED','assumption':'NONE','opaque_provenance':'opaque',
                    'restrictions':copy.deepcopy(self.restrictions)}]},
                'evidence': {'id': 'declaration', 'tool': 'context', 'completeness': 'COMPLETE_RESPONSE',
                    'declaration_provenance': 'DECLARED_BY_DEFINITION',
                    'declared_restrictions': copy.deepcopy(self.restrictions),
                    'metadata': {'context_version': 'context'}}}

    def evaluate_declared_context(self, layer, measure_id, scope):
        self.read_scopes.append(copy.deepcopy(scope)); self.events.append('reproduction')
        n = len(self.read_scopes)
        value = 8 if n == 1 else self.declared_value
        identity = 'reader' if n == 1 else self.identity
        obj = 'top' if n == 1 else self.object
        surface = {'engine': 'synthetic', 'connection': 'connection', 'object': obj, 'identity': identity}
        return Probe('OBSERVED', layer['id'], evidence={
            'id': 'reproduction-read-' + str(n), 'tool': 'probe',
            'completeness': 'COMPLETE_RESPONSE', 'measure_id': measure_id,
            'applied_restrictions': copy.deepcopy(scope['restrictions']) if self.applied else []},
            value={'quantity': value}, execution_surface=surface,
            surface_report={'identity': identity, 'object': obj} if self.report else None,
            surface_reportable=('identity', 'object'))

    def evaluate(self, layer, measure_id, scope):
        self.events.append('vertical-' + layer['id'])
        return super().evaluate(layer, measure_id, scope)

    def presentation_context(self, boundary, scope):
        return {'status': 'INCONCLUSIVE', 'explains': None, 'reason': 'Active selection unknown.'}


SCOPE = {'filters': [{'column_id': 'field-a', 'values': ['y']}], 'reported_figure': exact(3)}


class ReproductionTests(unittest.TestCase):
    def test_upstream_refusal_owns_reason_without_inventory_validation(self):
        from unittest.mock import patch
        from investigator import declaration_inventory
        for status in ('UNDECLARED', 'UNAVAILABLE'):
            for unused in (None, {'broken': 'unused input'}):
                class Refused(NeutralAdapter):
                    def declared_context(inner, *args):
                        return {'status': status, 'reason': 'Ambiguous definition target: first, second',
                                'unsupported_form': 'TARGET_AMBIGUITY', 'inventory': unused}
                adapter = Refused()
                with patch.object(declaration_inventory, 'validate', side_effect=AssertionError('Validated refused input')):
                    result = self.run_check(adapter)
                self.assertEqual(result['reason'], 'Ambiguous definition target: first, second')
                self.assertEqual(result['status'], status)
                self.assertEqual(result['unsupported_form'], 'TARGET_AMBIGUITY')
                self.assertEqual(adapter.read_scopes, [])

    def test_malformed_inventory_is_not_mistaken_for_upstream_refusal(self):
        class Malformed(NeutralAdapter):
            def declared_context(inner, *args):
                d = super().declared_context(*args); d['inventory'] = {'broken': 'inventory'}
                return d
        adapter = Malformed(); result = self.run_check(adapter)
        self.assertEqual(result['reason'], 'Declaration inventory is malformed')
        self.assertEqual(result['unsupported_form'], 'DECLARATION_INVENTORY_CONTRACT')
        self.assertEqual(adapter.read_scopes, [])

    def test_absent_inventory_is_not_reported_as_malformed(self):
        class Absent(NeutralAdapter):
            def declared_context(inner, *args):
                d = super().declared_context(*args); d.pop('inventory'); return d
        adapter = Absent(); result = self.run_check(adapter)
        self.assertEqual(result['reason'], 'Required declaration inventory was not supplied')
        self.assertEqual(result['unsupported_form'], 'DECLARATION_INVENTORY_ABSENT')
        self.assertEqual(adapter.read_scopes, [])

    def test_invalid_declaration_or_refusal_state_is_not_an_inventory_error(self):
        for response in (None, {}, {'status': 'DECLARED_UNKNOWN'}, {'status': 'UNDECLARED', 'reason': ''}):
            class Invalid(NeutralAdapter):
                def declared_context(inner, *args): return response
            adapter = Invalid(); result = self.run_check(adapter)
            self.assertEqual(result['unsupported_form'], 'DECLARATION_RESPONSE_CONTRACT')
            self.assertEqual(adapter.read_scopes, [])

    def run_check(self, adapter=None, scope=None):
        return reproduction.run(adapter or NeutralAdapter(), {'id': 'top'}, 'measure',
                                copy.deepcopy(SCOPE if scope is None else scope))

    def test_repeated_restrictions_intersect_at_execution_and_receipt(self):
        adapter = NeutralAdapter(); result = self.run_check(adapter)
        expected = [{'field_id': 'field-a', 'operator': 'IN', 'values': ['y']}]
        self.assertEqual(adapter.read_scopes, [
            {'restrictions': [], 'dimension_ids': []}, {'restrictions': expected, 'dimension_ids': []}])
        self.assertEqual(result['finding']['composed_restrictions'], expected)
        self.assertEqual(result['finding']['label'], 'REPRODUCED')
        observations = {o['id']: o for o in result['observations']}
        observations['declaration']['declared_restrictions'].pop(0)
        with self.assertRaisesRegex(ValueError, 'coverage|intersection'):
            reproduction.validate(result['finding'], observations)

    def test_empty_intersection_is_preserved_not_dropped(self):
        restrictions = [{'field_id': 'f', 'operator': 'IN', 'values': [True]},
                        {'field_id': 'f', 'operator': 'IN', 'values': [1]}]
        self.assertEqual(reproduction.compose(restrictions), [{'field_id': 'f', 'operator': 'IN', 'values': []}])

    def test_empty_restriction_reaches_evaluation_and_returns_empty_result(self):
        class ScopeEvaluatingAdapter(NeutralAdapter):
            def evaluate_declared_context(self, layer, measure_id, scope):
                probe = super().evaluate_declared_context(layer, measure_id, scope)
                # Calculate from the applied restriction, not the call ordinal.
                from dataclasses import replace
                return replace(probe, value={'quantity': 0 if scope['restrictions'] and
                               any(r['values'] == [] for r in scope['restrictions']) else 8})
        adapter = ScopeEvaluatingAdapter()
        adapter.restrictions[0]['values'] = ['x']; adapter.restrictions[1]['values'] = ['y']
        result = self.run_check(adapter, {**SCOPE, 'reported_figure': exact(0)})
        empty = [{'field_id': 'field-a', 'operator': 'IN', 'values': []}]
        self.assertEqual(adapter.read_scopes[0]['restrictions'], [])
        self.assertEqual(adapter.read_scopes[1]['restrictions'], empty)
        self.assertEqual(result['observations'][2]['applied_restrictions'], empty)
        self.assertEqual(result['finding']['undeclared_context_value'], '8')
        self.assertEqual(result['finding']['reproduced_value'], '0')
        self.assertEqual(result['finding']['label'], 'REPRODUCED')

    def test_same_named_columns_in_distinct_tables_keep_distinct_resolved_identities(self):
        columns = [{'id': 'catalog/table-one/column-code', 'name': 'Code'},
                   {'id': 'catalog/table-two/column-code', 'name': 'Code'}]
        adapter = NeutralAdapter()
        adapter.restrictions = [
            {'field_id': columns[0]['id'], 'operator': 'IN', 'values': ['x']},
            {'field_id': columns[1]['id'], 'operator': 'IN', 'values': ['y']}]
        result = self.run_check(adapter, {'reported_figure':exact(3),'dimension_ids': [c['id'] for c in columns]})
        self.assertEqual(len(result['finding']['composed_restrictions']), 2)
        self.assertEqual(adapter.read_scopes[1]['restrictions'], adapter.restrictions)
        self.assertTrue(all(r['values'] for r in adapter.read_scopes[1]['restrictions']))

    def test_empty_intersection_can_return_native_blank_without_becoming_zero(self):
        adapter=NeutralAdapter(None)
        adapter.restrictions[0]['values']=['x'];adapter.restrictions[1]['values']=['y']
        result=self.run_check(adapter,{**SCOPE,'reported_figure':exact(0)})
        self.assertIsNone(result['finding']['reproduced_value'])
        self.assertEqual(result['finding']['label'],'NOT_REPRODUCED')
        self.assertIn('produced blank',result['business_output'])
        by_id={o['id']:o for o in result['observations']}
        _process_evidence(result['finding'],by_id,{'reproduction-read-1':{'quantity':8},'reproduction-read-2':{'quantity':None}})

    def test_empty_reported_state_can_reproduce_native_blank(self):
        result=self.run_check(NeutralAdapter(None),{'filters':SCOPE['filters'],
            'reported_figure':{'state':'EMPTY','source':{'start':0,'end':5,'quote':'empty'}}})
        self.assertIsNone(result['finding']['reproduced_value'])
        self.assertEqual(result['finding']['label'],'REPRODUCED')

    def test_unspecified_figure_refuses_before_target_and_inventory(self):
        adapter=NeutralAdapter()
        with unittest.mock.patch.object(adapter,'declared_context',side_effect=AssertionError('Extraction must not run')):
            result = self.run_check(adapter,scope={'filters': SCOPE['filters'],'reported_figure':{'state':'UNSPECIFIED'}})
        self.assertEqual(result['reason'],reproduction.NO_FIGURE)
        self.assertNotIn('finding',result)
        self.assertEqual(adapter.read_scopes,[])

    def test_mismatch_is_possible_and_does_not_certify_cause(self):
        result = self.run_check(scope={**SCOPE, 'reported_figure': exact(4)})
        self.assertEqual(result['finding']['label'], 'NOT_REPRODUCED')
        self.assertIn(reproduction.OPEN_LIMIT, result['finding']['limitations'])

    def test_match_does_not_require_difference_from_undeclared_value(self):
        result = self.run_check(NeutralAdapter(8), {**SCOPE, 'reported_figure': exact(8)})
        self.assertEqual(result['finding']['label'], 'REPRODUCED')
        self.assertTrue(result['finding']['values_equal'])

    def test_undeclared_or_irrelevant_predicates_issue_no_reads(self):
        adapter = NeutralAdapter()
        result = self.run_check(adapter, {'reported_figure':exact(3),'filters': [{'column_id': 'other'}]})
        self.assertEqual(result['status'], 'UNDECLARED'); self.assertEqual(adapter.read_scopes, [])
        with unittest.mock.patch.object(adapter, 'capabilities', return_value=set()):
            with unittest.mock.patch.object(adapter, 'declared_context', side_effect=AssertionError):
                self.assertEqual(self.run_check(adapter)['status'], 'UNDECLARED')

    def test_unsupported_operator_fails_before_any_read(self):
        adapter = NeutralAdapter(); adapter.restrictions[0]['operator'] = 'UNKNOWN'
        result = self.run_check(adapter)
        self.assertEqual(result['status'], 'UNDECLARED')
        self.assertEqual(result['unsupported_form'], 'UNKNOWN')
        self.assertEqual(adapter.read_scopes, [])

    def test_non_enumerable_forms_refuse_whole_set_in_either_order(self):
        for form in ('RANGE', 'NEGATION', 'RELATIVE_DATE', 'MEASURE_CONDITION', 'TOP_N'):
            for index in (0, 1):
                with self.subTest(form=form, index=index):
                    adapter = NeutralAdapter(); adapter.restrictions[index]['operator'] = form
                    result = self.run_check(adapter)
                    self.assertEqual(result['status'], 'UNDECLARED')
                    self.assertEqual(result['unsupported_form'], form)
                    self.assertIn(form, result['reason'])
                    self.assertNotIn('finding', result)
                    self.assertEqual(adapter.read_scopes, [])

    def test_disguised_non_enumerated_forms_are_not_coerced(self):
        for change in ({'negated': True}, {'values': [{'range': [1, 3]}]}):
            adapter = NeutralAdapter(); adapter.restrictions[0].update(change)
            result = self.run_check(adapter)
            self.assertEqual(result['status'], 'UNDECLARED')
            self.assertIn('form', result['reason'])
            self.assertEqual(adapter.read_scopes, [])

    def test_surface_or_identity_change_is_unavailable(self):
        for field in ('identity', 'object'):
            adapter = NeutralAdapter(); setattr(adapter, field, 'different')
            result = self.run_check(adapter)
            self.assertEqual(result['status'], 'UNAVAILABLE')
            self.assertNotIn('finding', result)

    def test_missing_surface_self_report_cannot_produce_finding(self):
        adapter = NeutralAdapter(); adapter.report = False
        result = self.run_check(adapter)
        self.assertEqual(result['status'], 'UNAVAILABLE')
        self.assertEqual(result['reason'], 'SURFACE_SELF_REPORT_MISSING')

    def test_compiler_must_attest_applied_intersection(self):
        adapter = NeutralAdapter(); adapter.applied = False
        with self.assertRaisesRegex(ValueError, 'scope/measure/completeness'):
            self.run_check(adapter)

    def test_original_surface_attestation_is_rechecked(self):
        result = self.run_check(); obs = {o['id']: o for o in result['observations']}
        obs['reproduction-read-2']['surface_report']['identity'] = 'administrator'
        with self.assertRaisesRegex(ValueError, 'attestation'):
            reproduction.validate(result['finding'], obs)

    def test_synthesis_uses_whole_original_and_sealed_quantities(self):
        result = self.run_check(); obs = {o['id']: o for o in result['observations']}
        quantities = {'reproduction-read-1': {'quantity': '8'}, 'reproduction-read-2': {'quantity': '3'}}
        self.assertEqual(_process_evidence(result['finding'], obs, quantities), result['finding'])
        quantities['reproduction-read-2']['quantity'] = '4'
        with self.assertRaisesRegex(ValueError, 'sealed quantity'):
            _process_evidence(result['finding'], obs, quantities)

    def test_synthesis_preserves_future_fields_without_aliasing_original_evidence(self):
        result=self.run_check();obs={o['id']:o for o in result['observations']}
        result['finding']['future_evidence']={'nested':['retained']}
        projected=_process_evidence(result['finding'],obs)
        self.assertEqual(projected,result['finding'])
        projected['future_evidence']['nested'].append('changed')
        self.assertEqual(result['finding']['future_evidence'],{'nested':['retained']})

    def test_reproduction_cannot_be_retagged_as_boundary_support(self):
        result = self.run_check(); obs = {o['id']: o for o in result['observations']}
        result['finding']['process_roles'].append('comparison')
        with self.assertRaisesRegex(ValueError, 'boundary'):
            reproduction.validate(result['finding'], obs)

    def test_both_outputs_state_within_layer_and_bounded_baseline(self):
        result = self.run_check()
        self.assertIn('WITHIN_LAYER_CHECK', result['technical_output'])
        self.assertIn('Within', result['business_output'])
        for key in ('business_output', 'technical_output'):
            self.assertIn('undeclared-context', result[key])
            self.assertIn('not', result[key])
            narrative_form.validate(result[key], key == 'business_output')

    def test_no_native_platform_terms_in_engine_interface(self):
        import inspect
        source = inspect.getsource(reproduction)
        for term in ('DAX', 'Microsoft', 'bookmark', 'visual.json', 'page.json'):
            self.assertNotIn(term, source)

    def test_invalid_reported_figure_consumes_no_value_read(self):
        for value in (True, 'unknown', float('inf'), '1e1000000'):
            adapter=NeutralAdapter()
            with self.assertRaises(ValueError):self.run_check(adapter,{**SCOPE,'reported_figure':value})
            self.assertEqual(adapter.read_scopes,[])

    def test_numeric_comparison_does_not_round_high_precision_figures(self):
        value='1.123456789012345678901234567890123'
        self.assertEqual(reproduction.number(value),value)

    def test_declared_values_cannot_exceed_compiler_consumer_bounds(self):
        from investigator import proposal_limits as limits
        for values in (['x'*(limits.FILTER_STRING+1)],list(range(limits.FILTER_VALUES+1)),[limits.EXACT_INTEGER+1]):
            with self.assertRaises(ValueError):
                reproduction.compose([{'field_id':'f','operator':'IN','values':values}])


class PlacementAndGatingTests(unittest.TestCase):
    def test_named_unsupported_refusal_survives_vertical_and_synthesis(self):
        adapter = NeutralAdapter(not_comparable=['lower'])
        adapter.restrictions[1]['operator'] = 'RELATIVE_DATE'
        result = vertical(adapter, 'measure', copy.deepcopy(SCOPE))
        refusal = next(o for o in result['_observations']
                       if o.get('check_kind') == 'DECLARED_CONTEXT_REPRODUCTION_UNAVAILABLE')
        self.assertEqual(refusal['capability_status'], 'UNDECLARED')
        self.assertEqual(refusal['unsupported_form'], 'RELATIVE_DATE')
        self.assertEqual(adapter.read_scopes, [])
        self.assertEqual(result['classification'], 'NO_COMPARABLE_PATH')
        projected = _process_evidence(refusal, {})
        self.assertEqual(projected, refusal)
        projected['unsupported_form'] = 'changed'
        self.assertEqual(refusal['unsupported_form'], 'RELATIVE_DATE')

    def test_reproduction_is_callable_when_no_lower_layer_is_executable(self):
        adapter=NeutralAdapter();adapter.layers=[{'id':'top'}]
        result=vertical(adapter,'measure',copy.deepcopy(SCOPE))
        self.assertEqual(result['classification'],'NO_COMPARABLE_PATH')
        self.assertEqual(result['business_output']['declared_context_reproductions'][0]['label'],'REPRODUCED')
        self.assertEqual(adapter.events,['vertical-top','reproduction','reproduction'])

    def test_reproduction_precedes_unavailable_lower_read_without_bypassing_it(self):
        adapter = NeutralAdapter(not_comparable=['lower'])
        result = vertical(adapter, 'measure', copy.deepcopy(SCOPE))
        self.assertEqual(adapter.events, ['vertical-top', 'reproduction', 'reproduction', 'vertical-lower'])
        self.assertEqual(result['classification'], 'NO_COMPARABLE_PATH')
        self.assertEqual(result['technical_output']['boundary_summary']['comparisons_executed'], 0)
        self.assertEqual(result['technical_output']['boundary_summary']['within_layer_checks'], 1)
        for key in ('business_output', 'technical_output'):
            self.assertEqual(result[key]['declared_context_reproductions'][0]['label'], 'REPRODUCED')
        process_outcomes.validate(result, {o['id']: o for o in result['_observations']})

    def test_reproduction_does_not_satisfy_defect_gate(self):
        result = vertical(NeutralAdapter(), 'measure', copy.deepcopy(SCOPE))
        self.assertEqual(result['classification'], 'NO_KNOWN_PATTERN')
        self.assertIn('presentation_context', result['support']['process']['missing_capability'])
        obs = {o['id']: o for o in result['_observations']}
        process_outcomes.validate(result, obs)
        result['classification'] = 'DEFECT'
        result['support']['process']['recommended_action'] = process_outcomes.ACTIONS['DEFECT']
        with self.assertRaisesRegex(ValueError, 'competing'):
            process_outcomes.validate(result, obs)

    def test_reproduction_does_not_satisfy_existing_presentation_or_consistency_contracts(self):
        result = vertical(NeutralAdapter(not_comparable=['lower']), 'measure', copy.deepcopy(SCOPE))
        for outcome in ('PRESENTATION_LOGIC', 'CONSISTENT_TO_BOUNDARY'):
            candidate = copy.deepcopy(result); candidate['classification'] = outcome
            candidate['support']['process']['recommended_action'] = process_outcomes.ACTIONS[outcome]
            with self.assertRaises(ValueError):
                process_outcomes.validate(candidate, {o['id']: o for o in candidate['_observations']})

    def test_final_narratives_include_finding_without_boundary_masquerade(self):
        result = vertical(NeutralAdapter(not_comparable=['lower']), 'measure', copy.deepcopy(SCOPE))
        finding = result['business_output']['declared_context_reproductions'][0]
        payload = {'scope': {'measure_name': 'quantity'}, 'evidence': [{'id': finding['id'], 'tool': 'process', 'result': finding}]}
        business = narrative_form.business('Recommended action: Ask the owner.', payload)
        technical = narrative_form.technical('The declared selections determine the calculation.', payload,
                                            result, {'text': 'Ask the owner.'})
        self.assertIn('reproduce the reported figure of 3', business)
        self.assertIn('WITHIN_LAYER_CHECK', technical)
        self.assertIn('No independently compared boundary', technical)
        self.assertEqual(technical.count('Unattested connection, engine on L0'),1)
        self.assertIn('receipts reproduction-read-1, reproduction-read-2',technical)

    def test_validation_refuses_missing_side_finding_and_limits(self):
        result = vertical(NeutralAdapter(not_comparable=['lower']), 'measure', copy.deepcopy(SCOPE))
        obs = {o['id']: o for o in result['_observations']}
        for change in ('output', 'limits'):
            candidate = copy.deepcopy(result)
            if change == 'output': del candidate['business_output']['declared_context_reproductions']
            else: candidate['limits'].remove(reproduction.ACTIVE_LIMIT)
            with self.assertRaisesRegex(ValueError, 'Reproduction'):
                process_outcomes.validate(candidate, obs)

    def test_production_synthesis_preserves_side_finding_and_validates_originals(self):
        from test_synthesis_narrative import NarrativeContractTests
        from investigator import synthesis_narrative
        fixtures=NarrativeContractTests()
        state,payload=fixtures.source('NO_COMPARABLE_PATH')
        result=reproduction.run(NeutralAdapter(),{'id':'top'},'measure',copy.deepcopy(SCOPE))
        state['observations'].extend(result['observations'])
        state['assessment']['evidence_ids'].extend(o['id'] for o in result['observations'])
        state['assessment']['limits'].extend(result['finding']['limitations'])
        from investigator.process_debugging import unattested_surface_fields,surface_limit
        unattested=unattested_surface_fields(result['observations'])
        state['assessment']['limits'].extend(surface_limit(row) for row in unattested)
        for key in ('business_output','technical_output'):
            state['assessment'].setdefault(key,{})['declared_context_reproductions']=[result['finding']]
            state['assessment'][key]['unattested_surface_fields']=unattested
        payload['evidence'].extend({'id':o['id'],'tool':o['tool'],
            'result':o if o.get('check_kind')==reproduction.KIND else {}} for o in result['observations'])
        _,outputs=synthesis_narrative.assemble(synthesis_narrative.Response(fixtures.response(payload)),payload,state)
        self.assertIn('Within-layer check',outputs['business_output']['explanation']['text'])
        self.assertIn('WITHIN_LAYER_CHECK',outputs['technical_output']['explanation']['text'])
        self.assertEqual(outputs['business_output']['question_account']['status'],'PARTLY_ANSWERED')
        state['observations'][-2]['applied_restrictions']=[]
        with self.assertRaisesRegex(ValueError,'coverage|intersection'):
            synthesis_narrative.assemble(synthesis_narrative.Response(fixtures.response(payload)),payload,state)

    def test_question_account_names_missing_figure_without_claiming_an_answer(self):
        from investigator.question_account import build
        result=vertical(NeutralAdapter(not_comparable=['lower']),'measure',{'filters':SCOPE['filters'],'reported_figure':{'state':'UNSPECIFIED'}})
        state={'envelope':{'symptom':'Explain the difference.'},'observations':result['_observations'],'assessment':{}}
        account=build(state)
        self.assertEqual(account['status'],'NOT_ANSWERED')
        self.assertIn('no reported figure',account['subjects'][0]['reason'])


if __name__ == '__main__':
    unittest.main()
