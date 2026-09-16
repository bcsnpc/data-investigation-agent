import copy
from decimal import Decimal
import json
import unittest
from unittest.mock import MagicMock, patch

from investigator.dependency_context import edges, compile_path, Unsupported
from investigator.semantic_graph import analyze
from investigator.onboarding import digest
from investigator.native_diagnostics import build, run
from investigator.adaptive_candidates import catalog, available, observation, diagnostic_pairs
from investigator.adaptive_runtime import AdaptiveRuntime
from investigator.runtime import Runtime
from investigator.workspace import Workspace
import test_source_diagnostics as store_fixture
from test_adaptive_investigation import decision
from test_native_diagnostics import response


def fixture():
    expressions = {'Base': 'COUNTROWS(Activity)',
        'Replaced': 'CALCULATE([Base],Activity[Flag]=TRUE())',
        'Kept': 'CALCULATE([Base],KEEPFILTERS(Activity[Flag]=TRUE()))',
        'Ratio': 'DIVIDE([Replaced],[Base])', 'Combined': '[Replaced]+[Kept]+[Base]',
        'Outer': 'CALCULATE([Replaced],Activity[Flag]=FALSE())',
        'Unsupported': 'CALCULATE([Base],ALL(Activity))'}
    assets = [{'id': 't', 'name': 'Activity', 'kind': 'SemanticTable', 'metadata': {}}]
    for cid, name, kind in [('f', 'Flag', 'boolean'), ('r', 'Region', 'string'), ('i', 'Id', 'int64')]:
        assets.append({'id': cid, 'name': name, 'kind': 'SemanticColumn', 'parent_id': 't', 'metadata': {'dataType': kind}})
    for name, expression in expressions.items():
        assets.append({'id': name, 'name': name, 'kind': 'Measure', 'parent_id': 't', 'metadata': {'expression': expression}})
    for a in assets: a['content_hash'] = digest(a)
    model = {'id': 'model', 'revision': 3, 'context_id': 'ctx', 'enabled': True, 'workspace': 'workspace', 'native_id': 'native',
             'name': 'Context checks', 'context': {'id': 'ctx', 'reports': [{'model_assets': assets}],
              'measures': [{'id': name, 'name': name} for name in expressions], 'semantic_graph': analyze(assets)}}
    return model


class ContextTests(unittest.TestCase):
    def setUp(self):
        self.model = fixture()
        self.plan = {'model_id': 'model', 'revision': 3, 'context_id': 'ctx', 'measure_ids': ['Base'],
            'filters': [{'column_id': 'f', 'operator': 'in', 'values': [False]}],
            'dimension_id': None, 'include_dependencies': False, 'context_path': ['Replaced', 'Base']}

    def expression(self, value, name='Replaced'):
        a = next(a for a in self.model['context']['reports'][0]['model_assets'] if a['id'] == name)
        a['metadata']['expression'] = value

    def test_replacement_and_intersection_stay_native(self):
        replaced = compile_path(self.model, ['Replaced', 'Base'], 'Base')
        kept = compile_path(self.model, ['Kept', 'Base'], 'Base')
        self.assertEqual(replaced['steps'][0]['filters'][0]['mode'], 'REPLACE')
        self.assertEqual(kept['steps'][0]['filters'][0]['mode'], 'INTERSECT')
        self.assertEqual(replaced['expression'], "CALCULATE('Activity'[Base],'Activity'[Flag]=TRUE())")
        self.assertIn('KEEPFILTERS(', kept['expression'])
        self.assertFalse(replaced['effective_report_context_verified'])

    def test_nested_wrapper_order_matches_measure_nesting(self):
        result = compile_path(self.model, ['Outer', 'Replaced', 'Base'], 'Base')
        self.assertEqual(result['expression'], "CALCULATE(CALCULATE('Activity'[Base],'Activity'[Flag]=TRUE()),'Activity'[Flag]=FALSE())")

    def test_ratio_neutral_edge_retained_before_transformed_edge(self):
        result = compile_path(self.model, ['Ratio', 'Replaced', 'Base'], 'Base')
        self.assertEqual(result['steps'][0]['filters'], [])
        self.assertEqual(len(result['steps']), 2)

    def test_query_keeps_outer_ticket_filter_and_inner_measure_filter(self):
        request = build(self.model, self.plan)
        self.assertIn("TREATAS({FALSE()},'Activity'[Flag])", request['query'])
        self.assertIn("CALCULATE('Activity'[Base],'Activity'[Flag]=TRUE())", request['query'])
        self.assertEqual(request['dependency_context']['path'], ['Replaced', 'Base'])

    def test_contextual_dimension_uses_same_wrapper(self):
        request = build(self.model, dict(self.plan, dimension_id='r'))
        self.assertIn('SUMMARIZECOLUMNS', request['query'])
        self.assertIn("CALCULATE('Activity'[Base],'Activity'[Flag]=TRUE())", request['query'])

    def test_bounded_typed_literals_and_escaping(self):
        for expr in ['CALCULATE([Base],Activity[Id]=-3)', 'CALCULATE([Base],Activity[Region]="a""b")']:
            self.expression(expr); result = compile_path(self.model, ['Replaced', 'Base'], 'Base')
            self.assertEqual(len(result['steps'][0]['filters']), 1)
        self.assertIn('"a""b"', result['expression'])

    def test_unsupported_expressions_never_guess_context(self):
        for expr in ['CALCULATE([Base],ALL(Activity))', 'CALCULATE([Base],Activity[Flag]=BLANK())',
                     'CALCULATE([Base],Activity[Flag]==TRUE())', 'CALCULATE([Base],[Flag]=TRUE())',
                     'CALCULATE([Base],Activity[Flag]=1)', 'CALCULATE([Base],Activity[Id]>2)',
                     'CALCULATE([Base],Activity[Flag]=TRUE(),Activity[Flag]=FALSE())',
                     'CALCULATE([Base],Activity[Flag]=TRUE()||Activity[Flag]=FALSE())',
                     'CALCULATE([Base],USERELATIONSHIP(Activity[Id],Activity[Id]))',
                     'IF(TRUE(),[Base],[Base])', 'SUMX(Activity,[Base])',
                     'CALCULATE(CALCULATE([Base],Activity[Flag]=TRUE()),Activity[Flag]=FALSE())',
                     '[Base]+CALCULATE([Base],Activity[Flag]=TRUE())']:
            with self.subTest(expr=expr):
                self.expression(expr)
                with self.assertRaises(Unsupported): compile_path(self.model, ['Replaced', 'Base'], 'Base')

    def test_unrelated_cycle_stale_and_multi_measure_paths_rejected(self):
        for change in [{'context_path': ['Kept', 'Ratio', 'Base']}, {'context_path': ['Base', 'Base']},
                       {'context_path': ['Replaced']}, {'context_path': ['Replaced', 'Unknown']},
                       {'include_dependencies': True}, {'measure_ids': ['Base', 'Ratio']}, {'revision': 99}]:
            with self.subTest(change=change), self.assertRaises(ValueError): build(self.model, dict(self.plan, **change))

    def test_same_dependency_multiple_neutral_references_not_ambiguous(self):
        self.expression('DIVIDE(([Base]+[Base])*2,[Base],0)')
        self.assertEqual(edges(self.model, 'Replaced'), [{'child_id': 'Base', 'filters': []}])

    def test_unknown_or_ambiguous_catalog_reference_rejected(self):
        self.expression('CALCULATE([Missing],Activity[Flag]=TRUE())')
        with self.assertRaises(Unsupported): edges(self.model, 'Replaced')
        self.expression('CALCULATE([Base],Activity[Flag]=TRUE())')
        self.model['context']['reports'][0]['model_assets'].append({'id': 'dup', 'kind': 'SemanticColumn', 'name': 'Base', 'parent_id': 't'})
        with self.assertRaises(Unsupported): edges(self.model, 'Replaced')


class AdaptiveContextTests(unittest.TestCase):
    def setUp(self):
        h = store_fixture.SourceTests(); h.setUp(); self.addCleanup(h.doCleanups)
        self.store, self.config = h.store, h.config
        self.model = h.model; self.model.clear(); self.model.update(fixture())
        self.config['fabric']['workspace_id'] = 'workspace'
        self.envelope = {'model_id': 'model', 'revision': 3, 'context_id': 'ctx', 'measure_id': 'Combined',
            'filters': [{'column_id': 'f', 'operator': 'in', 'values': [False]}], 'dimension_ids': ['r'],
            'source_tests': [], 'symptom': 'Why do these figures differ?',
            'limits': {'cloud_calls': 8, 'planner_calls': 6, 'wall_seconds': 900, 'input_characters': 80000, 'max_depth': 3}}

    def test_shared_child_has_distinct_replaced_kept_and_original_candidates(self):
        choices, gaps = catalog(self.store, self.config, self.envelope)
        base = [c for c in choices if c['measure_id'] == 'Base' and c['dimension_id'] is None]
        self.assertEqual(len(base), 3); self.assertEqual(len({c['id'] for c in base}), 3)
        self.assertEqual(sum(bool(c.get('dependency_context')) for c in base), 2)
        self.assertIn('CONTEXTUAL_SOURCE_COMPARISON_UNSUPPORTED', [g['reason'] for g in gaps])

    def test_contextual_child_waits_for_exact_parent_and_dimension_for_own_scalar(self):
        choices, _ = catalog(self.store, self.config, self.envelope)
        child = next(c for c in choices if c.get('dependency_context') and c['dimension_id'] is None)
        other_parent = next(c for c in choices if c['measure_id'] == 'Kept' and c['dimension_id'] is None)
        observed = [{'id': 'x', 'candidate_id': other_parent['id'], 'tool': 'native', 'dimension_id': None,
                     'measure_id': 'Kept', 'status': 'COMPLETED'}]
        if child['parent'] == 'Kept': observed[0]['candidate_id'] = 'wrong-parent'
        self.assertNotIn(child, available(choices, observed, []))
        observed[0]['candidate_id'] = child['parent_candidate_id']
        self.assertIn(child, available(choices, observed, []))
        dimension = next(c for c in choices if c.get('scalar_candidate_id') == child['id'])
        self.assertNotIn(dimension, available(choices, observed, []))
        observed.append({'candidate_id': child['id'], 'tool': 'native', 'dimension_id': None, 'measure_id': child['measure_id'],
                         'status': 'COMPLETED', 'dependency_context': child['dependency_context']})
        self.assertIn(dimension, available(choices, observed, []))

    def test_depth_budget_and_unsupported_context_are_explicit(self):
        self.envelope['limits']['max_depth'] = 1
        choices, gaps = catalog(self.store, self.config, self.envelope)
        self.assertFalse(any(c.get('dependency_context') for c in choices))
        self.assertIn('DEPTH_LIMIT', [g['reason'] for g in gaps])
        self.envelope['measure_id'] = 'Unsupported'
        choices, gaps = catalog(self.store, self.config, self.envelope)
        self.assertEqual({c['measure_id'] for c in choices}, {'Unsupported'})
        self.assertTrue(gaps)

    def test_contextual_observation_not_paired_with_untransformed_source(self):
        choices, _ = catalog(self.store, self.config, self.envelope)
        c = next(c for c in choices if c.get('dependency_context') and c['dimension_id'] is None)
        o = observation(c, {'id': 'run', 'steps': [{'result': {'id': 'receipt', 'status': 'COMPLETED', 'request_hash': 'h',
                         'result': {'rows': [{'[m0]': {'type': 'decimal', 'value': '2'}}]}}}]})
        s = {'id': 'source', 'tool': 'source', 'status': 'COMPLETED', 'measure_id': 'Base',
             'values': [{'type': 'decimal', 'value': '10'}]}
        self.assertEqual(diagnostic_pairs([o, s]), [])

    def test_adaptive_runtime_saves_context_and_sends_it_to_planner(self):
        calls = []; payloads = []
        def execute(request):
            calls.append(request); return response([{'[m0]': 2 if request.get('dependency_context') else 10}])
        def planner(payload):
            payloads.append(payload)
            choices = [c for c in payload['candidates'] if c['dimension_id'] is None]
            selected = next((c for c in choices if c.get('dependency_context')), choices[0] if choices else None)
            return decision(selected['id']) if selected and len(payload['observations']) < 4 else decision(), {}
        agent = AdaptiveRuntime(Runtime(self.store, self.config, execute, None), planner)
        result = agent.run(agent.create(self.envelope, 'context') ['id'])
        self.assertTrue(any(r.get('dependency_context') for r in calls))
        self.assertTrue(any(o.get('dependency_context') for o in result['observations']))
        self.assertTrue(any(c.get('dependency_context') for p in payloads for c in p['candidates']))
        self.assertFalse(result['outcome']['cause_verified'])

    def test_workspace_preview_exposes_context_changes_without_queries(self):
        import test_investigator_workspace as workspace_fixture
        h = workspace_fixture.WorkspaceTests(); h.setUp(); self.addCleanup(h.doCleanups)
        h.model.clear(); h.model.update(fixture()); h.config['fabric']['workspace_id'] = 'workspace'
        request = dict(h.request, measure_id='Combined', filters=self.envelope['filters'])
        preview = h.workspace.preview(request)
        self.assertEqual(len(preview['calculation_contexts']), 2)
        self.assertEqual({c['filters'][0]['mode'] for c in preview['calculation_contexts']}, {'REPLACE', 'INTERSECT'})
        h.native.assert_not_called(); h.planner.assert_not_called()

    def test_changed_parent_definition_holds_active_session(self):
        execute = MagicMock(); planner = MagicMock()
        agent = AdaptiveRuntime(Runtime(self.store, self.config, execute, None), planner)
        saved = agent.create(self.envelope, 'stale-context')
        self.model['context']['reports'][0]['model_assets'][-1]['metadata']['expression'] = '[Base]'
        result = agent.run(saved['id'])
        self.assertEqual(result['status'], 'HELD')
        planner.assert_not_called(); execute.assert_not_called()


if __name__ == '__main__': unittest.main()
