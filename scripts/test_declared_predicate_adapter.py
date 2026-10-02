from investigator.reported_figure import from_candidates

def exact(value):
 text=str(value)
 return from_candidates([{"start":0,"end":len(text),"quote":text}],text)

"""Adapter/compiler contracts with synthetic pinned metadata and injected transport."""
import copy
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from uuid import uuid4

from investigator.adapters.microsoft_process import MicrosoftProcessAdapter
from investigator.adapters import report_predicates as predicates
from investigator import declared_reproduction, native_identity, query_dax
from investigator.process_debugging import attest
from investigator.onboarding import Conflict


def field(table='Customers', column='Region', kind='Column'):
    return {kind: {'Expression': {'SourceRef': {'Entity': table}}, 'Property': column}}


def native_filter(values=('North',), table='Customers', column='Region'):
    expression = field(table, column)
    expression['Column']['Expression']['SourceRef'] = {'Source': 'c'}
    return {'Version': 2, 'From': [{'Name': 'c', 'Entity': table, 'Type': 0}],
            'Where': [{'Condition': {'In': {'Expressions': [expression],
                'Values': [[{'Literal': {'Value': "'" + value.replace("'", "''") + "'"}}] for value in values]}}}]}


def filter_config(document):
    return {'filters': [{'type': 'Categorical', 'filter': document}]}


class Store:
    def __init__(self, path, model): self.path, self.model = path, model
    def get(self, identity):
        if identity != self.model['id']: raise KeyError(identity)
        return copy.deepcopy(self.model)
    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path)
        try:
            with db: yield db
        finally: db.close()


class DeclaredPredicateAdapterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        ws, mid = str(uuid4()), str(uuid4())
        self.reader = {'mode': 'isolated_reader', 'tenant_id': str(uuid4()), 'principal_id': str(uuid4()),
                       'account': 'reader@example.com', 'model_ids': [mid]}
        self.config = {'fabric': {'workspace_id': ws, 'native_reader': self.reader}}
        self.parts = []
        self.table = {'id': 'resolved/sales', 'kind': 'SemanticTable', 'name': 'Sales'}
        self.dimension = {'id': 'resolved/customers', 'kind': 'SemanticTable', 'name': 'Customers'}
        self.column = {'id': 'resolved/customers/region', 'parent_id': self.dimension['id'],
                       'kind': 'SemanticColumn', 'name': 'Region', 'metadata': {'dataType': 'string'}}
        self.measure = {'id': 'resolved/sales/revenue', 'parent_id': self.table['id'],
                        'kind': 'Measure', 'name': 'Revenue', 'metadata': {'expression': 'SUM(Sales[Value])'}}
        self.model = {'id': str(uuid4()), 'workspace': ws, 'native_id': mid, 'revision': 4,
            'context_id': str(uuid4()), 'enabled': True, 'context': {
                'model_assets': [self.table, self.dimension, self.column, self.measure], 'reports': [], 'scan_id': 'scan'}}
        self.model['context']['id'] = self.model['context_id']
        self.report = {'report': {'id': 'resolved/report'}, 'model_id': 'fabric://' + ws + '/' + mid,
            'binding_status': 'RESOLVED_EXPLICIT_ID', 'gaps': [], 'report_definitions': self.parts}
        self.model['context']['reports'].append(self.report)
        self.report_doc = self.part('definition/report.json', {})
        self.page = self.part('definition/pages/p/page.json', {'name': 'p',
            'filterConfig': filter_config(native_filter()),
            'visualInteractions': [{'source': 's', 'target': 'v', 'type': 'DataFilter'}]})
        self.visual = self.part('definition/pages/p/visuals/v/visual.json', {'name': 'v',
            'visual': {'visualType': 'card', 'query': {'queryState': {'Values': {'projections': [
                {'field': field('Sales', 'Revenue', 'Measure')}]}}}},
            'filterConfig': filter_config(native_filter(('North', 'West')))})
        self.slicer = self.part('definition/pages/p/visuals/s/visual.json', {'name': 's', 'visual': {
            'visualType': 'slicer', 'query': {'queryState': {'Values': {'projections': [{'field': field()}]}}},
            'objects': {'data': [{'properties': {'mode': {'expr': {'Literal': {'Value': "'Dropdown'"}}}}}],
                        'general': [{'properties': {'filter': {'filter': native_filter()}}}]}}})
        self.bookmark = self.part('definition/bookmarks/b.bookmark.json', {'name': 'b',
            'options': {'suppressData': False}, 'explorationState': {'selection': {'filter': native_filter(('Coastal',))}}})
        self.store = Store(Path(self.tmp.name) / 'receipts.sqlite', self.model)
        self.requests = []; self.meters = []
        def execute(request):
            self.requests.append(copy.deepcopy(request))
            response = {'results': [{'tables': [{'rows': [{'quantity': 3,
                'surface_identity': self.reader['account'],'surface_engine':'OLAP Server','surface_object':self.model['native_id']}]}]}]}
            response[native_identity.KEY] = native_identity.make(response, request, self.reader)
            return response
        def meter(tool, read): self.meters.append(tool); return read()
        self.adapter = MicrosoftProcessAdapter(self.store, self.config, self.model, execute, self.fail, meter_read=meter)
        self.layer = {'id': self.table['id'], 'kind': 'presentation'}
        self.scope = {'filters': [{'column_id': self.column['id'], 'values': ['North']}], 'reported_figure': exact(3)}

    def test_combined_inventory_bound_is_refused_by_engine_before_compilation(self):
        self.modify(self.page, lambda d: d['filterConfig'].update(
            filters=[{'type': 'Categorical', 'filter': native_filter()} for _ in range(33)]))
        declaration = self.adapter.declared_context(self.layer, self.measure['id'], self.scope)
        self.assertEqual(declaration['status'], 'DECLARED')
        self.assertGreater(len(declaration['restrictions']), 32)
        result = self.run_check()
        self.assertEqual(result['status'], 'UNDECLARED')
        self.assertEqual(result['unsupported_form'], 'DECLARATION_INVENTORY_CONTRACT')
        self.assertEqual(self.requests, [])

    def part(self, name, document):
        content = json.dumps(document)
        part = {'id': 'part/' + name, 'kind': 'DefinitionPart', 'name': name,
            'availability': 'CURRENT', 'content_hash': hashlib.sha256(content.encode()).hexdigest(),
            'metadata': {'content': content}}
        self.parts.append(part); return part

    def modify(self, part, change):
        doc = json.loads(part['metadata']['content']); change(doc)
        part['metadata']['content'] = json.dumps(doc)
        part['content_hash'] = hashlib.sha256(part['metadata']['content'].encode()).hexdigest()

    def declaration(self): return self.adapter.declared_context(self.layer, self.measure['id'], self.scope)
    def run_check(self): return declared_reproduction._run_one(self.adapter, self.layer, self.measure['id'], self.scope)

    def assert_inventory_block(self, form):
        declaration = self.declaration()
        self.assertEqual(declaration['status'], 'DECLARED')  # extracted, not eligible
        unsupported = [e for e in declaration['inventory']['entries'] if e['disposition'] == 'UNSUPPORTED']
        self.assertTrue(unsupported)
        self.assertIn(form, ' '.join(e['opaque_provenance'] for e in unsupported))
        result = self.run_check()
        self.assertEqual(result['status'], 'UNDECLARED')
        self.assertEqual(result['unsupported_form'], 'UNSUPPORTED_DECLARATION')
        self.assertEqual(self.requests, [])
        return declaration, result


    def test_bookmark_on_active_column_is_retained_and_excluded_without_changing_intersection(self):
        declaration = self.declaration()
        composed = declared_reproduction.compose(declaration['restrictions'])
        self.assertEqual(composed, [{'field_id': self.column['id'], 'operator': 'IN', 'values': ['North']}])
        excluded = declaration['evidence']['conditional_declarations']
        self.assertEqual(excluded[0]['reason'], 'STORED_BOOKMARK_REQUIRES_INVOCATION')
        self.assertEqual(excluded[0]['alternatives'][0]['restrictions'][0]['values'], ['Coastal'])
        self.assertIn('invocation is unknown', excluded[0]['non_reproduction_limit'])

    def test_pinned_context_only_never_reads_latest_or_cloud_report(self):
        with patch('investigator.context_search.latest', side_effect=AssertionError('unpinned access')):
            declaration = self.declaration()
        evidence = declaration['evidence']
        self.assertEqual(evidence['metadata']['context_version'], self.model['context_id'])
        self.assertEqual(evidence['metadata']['model_revision'], 4)
        self.assertEqual(self.requests, [])

    def test_two_probes_use_compiler_admission_receipts_and_surface_attestation(self):
        result = self.run_check()
        self.assertEqual(result['status'], 'COMPLETED')
        self.assertEqual(result['finding']['comparison_status'], 'WITHIN_LAYER_CHECK')
        self.assertEqual(self.meters, ['bounded_dax', 'bounded_dax'])
        self.assertEqual(len(self.requests), 2)
        for request in self.requests:
            self.assertEqual(request['context_id'], self.model['context_id'])
            self.assertIn('compiled_read', request)
            self.assertEqual(request['requires_native_reader'], True)
            self.assertIn('USERPRINCIPALNAME()', request['query'])
        for observation in result['observations'][1:3]:
            self.assertEqual(observation['surface_attestation']['status'], 'PARTIAL')
            self.assertEqual(observation['surface_attestation']['consistency'], 'MATCHED')
            self.assertEqual(observation['context_id'], self.model['context_id'])
            self.assertEqual(observation['model_revision'], 4)
            self.assertTrue(observation['conditional_declarations'])
        with self.store.connect() as db:
            rows = db.execute('SELECT status,request FROM flexible_diagnostics').fetchall()
            self.assertEqual(len(rows), 2)
            self.assertTrue(all(status == 'COMPLETED' for status, _ in rows))
            self.assertTrue(all(json.loads(request)['plan']['revision'] == 4 for _, request in rows))

    def test_one_filter_argument_per_resolved_native_column_path(self):
        self.run_check()
        query = self.requests[1]['query']
        self.assertEqual(query.count('TREATAS('), 1)
        self.assertEqual(query.count("'Customers'[Region]"), 1)
        self.assertNotIn('Coastal', query)

    def test_empty_intersection_is_compiled_as_empty_relation_not_unfiltered_scope(self):
        self.modify(self.visual, lambda d: d.update(filterConfig=filter_config(native_filter(('Elsewhere',)))))
        result = self.run_check()
        query = self.requests[1]['query']
        self.assertIn("FILTER(VALUES('Customers'[Region]),FALSE())", query)
        self.assertEqual(result['observations'][2]['applied_restrictions'][0]['values'], [])
        self.assertNotEqual(self.requests[0]['compiled_read'], self.requests[1]['compiled_read'])

    def test_duplicate_native_paths_refuse_even_if_caller_bypasses_engine_intersection(self):
        restriction = {'field_id': self.column['id'], 'operator': 'IN', 'values': ['North']}
        with self.assertRaisesRegex(predicates.Refusal, 'DUPLICATE_NATIVE_COLUMN_PATH'):
            predicates.quantity_query(self.model, self.measure['id'], [restriction, restriction])

    def test_same_named_columns_in_different_tables_compile_as_distinct_paths(self):
        column = dict(self.column, id='resolved/sales/region', parent_id=self.table['id'])
        self.model['context']['model_assets'].append(column)
        self.modify(self.visual, lambda d: d.update(filterConfig=filter_config(native_filter(('West',), 'Sales'))))
        self.run_check()
        query = self.requests[1]['query']
        self.assertEqual(query.count('TREATAS('), 2)
        self.assertEqual(query.count("'Customers'[Region]"), 1)
        self.assertEqual(query.count("'Sales'[Region]"), 1)
        self.assertTrue({column['id'], self.column['id']} <= set(self.requests[1]['asset_ids']))

    def test_numeric_and_boolean_membership_is_typed_without_date_or_column_name_branches(self):
        for typ, tokens, expected in (('int64', ['1L', '2L'], [1, 2]),
                                      ('boolean', ['true', 'false'], [True, False]),
                                      ('decimal', ['1.25D'], [1.25])):
            with self.subTest(typ=typ):
                self.column['metadata']['dataType'] = typ
                doc = native_filter()
                doc['Where'][0]['Condition']['In']['Values'] = [[{'Literal': {'Value': t}}] for t in tokens]
                result = predicates.restrictions(self.model, doc)
                self.assertEqual(result[0]['values'], expected)
                query = predicates.quantity_query(self.model, self.measure['id'], result)
                self.assertEqual(query.count('TREATAS('), 1)
                self.assertIn(self.column['id'], query_dax.compile_query(query, self.model['context']['model_assets'])['asset_ids'])

    def test_out_of_bound_literal_and_lossy_decimal_refuse_before_queries(self):
        self.modify(self.page, lambda d: d.update(filterConfig=filter_config(native_filter(('x' * 201,)))))
        self.assert_inventory_block('LITERAL_REPRESENTATION_BOUND')
        self.assertEqual(self.requests, [])
        self.column['metadata']['dataType'] = 'decimal'
        doc = native_filter()
        doc['Where'][0]['Condition']['In']['Values'] = [[{'Literal': {'Value': '1.1234567890123456789D'}}]]
        with self.assertRaisesRegex(predicates.Refusal, 'LOSSY_NUMERIC_LITERAL'):
            predicates.restrictions(self.model, doc)

    def test_oversized_integer_literal_refuses_before_python_conversion_or_reads(self):
        self.column['metadata']['dataType'] = 'int64'
        doc = native_filter()
        doc['Where'][0]['Condition']['In']['Values'] = [[{'Literal': {'Value': '9' * 5000 + 'L'}}]]
        self.modify(self.page, lambda d: d.update(filterConfig=filter_config(doc)))
        self.assert_inventory_block('LITERAL_REPRESENTATION_BOUND')
        self.assertEqual(self.requests, [])

    def test_refused_new_declaration_cannot_reuse_prior_admission(self):
        self.declaration()
        self.modify(self.page, lambda d: d.update(visualInteractions=[]))
        self.assert_inventory_block('SLICER_INTERACTION_APPLICABILITY_UNKNOWN')
        with self.assertRaisesRegex(Conflict, 'No complete pinned declaration'):
            self.adapter.evaluate_declared_context(self.layer, self.measure['id'], {'restrictions': [], 'dimension_ids': []})
        self.assertEqual(self.requests, [])

    def test_incomplete_retained_definition_or_binding_cannot_produce_a_partial_active_set(self):
        for change in ('gap', 'binding', 'parent'):
            with self.subTest(change=change):
                report = copy.deepcopy(self.report)
                if change == 'gap': report['gaps'] = ['REPORT_DEFINITION_UNAVAILABLE']
                elif change == 'binding': report['binding_status'] = 'UNRESOLVED'
                else: report['report_definitions'] = [p for p in report['report_definitions'] if p['name'] != 'definition/report.json']
                self.model['context']['reports'] = [report]
                self.assertEqual(self.declaration()['status'], 'UNDECLARED')
                self.assertEqual(self.requests, [])

    def test_sync_slicers_and_conditional_pages_are_named_refusals(self):
        self.modify(self.slicer, lambda d: d.update(syncGroup={'name': 'shared'}))
        self.assert_inventory_block('SLICER_SYNC_CONTEXT')
        self.modify(self.slicer, lambda d: d.pop('syncGroup'))
        self.modify(self.page, lambda d: d.update(pageBinding={'type': 'Drillthrough'}))
        self.assert_inventory_block('CONDITIONAL_PAGE_CONTEXT')

    def test_unfamiliar_names_values_and_quoted_identifiers_are_catalog_bound(self):
        self.dimension['name'] = "Buyer's Areas"; self.column['name'] = 'Code]Name'
        for part in (self.page, self.visual):
            self.modify(part, lambda d: d.update(filterConfig=filter_config(native_filter(('A"B',), self.dimension['name'], self.column['name']))))
        self.modify(self.page, lambda d: d['visualInteractions'][0].update(type='NoFilter'))
        self.run_check()
        query = self.requests[1]['query']
        self.assertIn("'Buyer''s Areas'[Code]]Name]", query)
        self.assertIn('"A""B"', query)
        self.assertIn(self.column['id'], self.requests[1]['asset_ids'])

    def test_missing_identity_report_on_either_probe_cannot_produce_finding(self):
        for fail_at in (1, 2):
            with self.subTest(fail_at=fail_at):
                self.requests.clear()
                def execute(request):
                    self.requests.append(request)
                    row = {'quantity': 3}
                    if len(self.requests) != fail_at: row['surface_identity'] = self.reader['account']
                    row.update(surface_engine='OLAP Server',surface_object=self.model['native_id'])
                    response = {'results': [{'tables': [{'rows': [row]}]}]}
                    response[native_identity.KEY] = native_identity.make(response, request, self.reader)
                    return response
                self.adapter.execute_native = execute
                result = self.run_check()
                self.assertEqual(result['status'], 'UNAVAILABLE')
                self.assertNotIn('finding', result)

    def test_changed_context_or_revision_refuses_before_reproduction_read(self):
        self.declaration()
        prior = copy.deepcopy(self.store.model)
        for key, value in (('revision', 5), ('context_id', str(uuid4()))):
            self.store.model = dict(prior, **{key: value})
            with self.assertRaises(Conflict):
                self.adapter.evaluate_declared_context(self.layer, self.measure['id'], {'restrictions': [], 'dimension_ids': []})
        self.assertEqual(self.requests, [])

    def test_modified_execution_restrictions_are_refused_not_admitted(self):
        self.declaration()
        with self.assertRaisesRegex(Conflict, 'composed declaration'):
            self.adapter.evaluate_declared_context(self.layer, self.measure['id'], {'restrictions': [
                {'field_id': self.column['id'], 'operator': 'IN', 'values': ['Invented']}], 'dimension_ids': []})
        self.assertEqual(self.requests, [])

    def test_unknown_active_conditions_refuse_whole_set_before_any_value_read(self):
        for form in ('Between', 'Not', 'RelativeDate', 'Comparison', 'TopN'):
            self.modify(self.visual, lambda d: d.update(filterConfig=filter_config({
                'Version': 2, 'From': [], 'Where': [{'Condition': {form: {}}}]})))
            self.assert_inventory_block(form)
            self.assertEqual(self.requests, [])

    def test_native_unsupported_form_stays_opaque_while_engine_names_neutral_gate(self):
        self.modify(self.visual, lambda d: d.update(filterConfig=filter_config({
            'Version': 2, 'From': [], 'Where': [{'Condition': {'Not': {}}}]})))
        self.assert_inventory_block('CONDITION_Not')
        self.assertEqual(self.requests, [])

    def test_measure_level_and_tuple_conditions_refuse_without_dropping_column_restrictions(self):
        for expression in (field('Sales', 'Revenue', 'Measure'), [field(), field('Sales', 'Revenue', 'Measure')]):
            doc = native_filter()
            doc['Where'][0]['Condition']['In']['Expressions'] = expression if isinstance(expression, list) else [expression]
            self.modify(self.visual, lambda d: d.update(filterConfig=filter_config(doc)))
            self.assert_inventory_block('TUPLE_IN' if isinstance(expression, list) else 'FIELD_EXPRESSION_Measure')
            self.assertEqual(self.requests, [])

    def test_unknown_conditional_form_is_retained_but_never_applied(self):
        self.modify(self.bookmark, lambda d: d.update(explorationState={'filter': {
            'Version': 2, 'From': [], 'Where': [{'Condition': {'Not': {}}}]}}))
        declaration = self.declaration()
        self.assertEqual(declaration['status'], 'DECLARED')
        alternative = declaration['evidence']['conditional_declarations'][0]['alternatives'][0]
        self.assertIn('Not', alternative['unsupported_form'])
        self.assertTrue(alternative['declaration'])

    def test_unknown_slicer_applicability_is_not_classified_active(self):
        self.modify(self.page, lambda d: d.update(visualInteractions=[]))
        self.assert_inventory_block('APPLICABILITY_UNKNOWN')

    def test_non_enumerated_slicer_mode_without_predicate_cannot_be_dropped(self):
        self.modify(self.slicer, lambda d: d['visual']['objects'].update(
            general=[], data=[{'properties': {'mode': {'expr': {'Literal': {'Value': "'RelativeDate'"}}}}}]))
        self.assert_inventory_block('NON_ENUMERATED_SLICER_MODE')
        self.assertEqual(self.requests, [])

    def test_predicate_outside_supported_active_location_is_not_silently_dropped(self):
        self.modify(self.page, lambda d: d.update(unknownConditionalState={'filter': native_filter(('Coastal',))}))
        self.assert_inventory_block('FILTER_APPLICABILITY_UNKNOWN')
        self.assertEqual(self.requests, [])

    def test_inverted_selection_modifier_is_not_coerced_to_in_membership(self):
        self.modify(self.page, lambda d: d['filterConfig']['filters'][0].update(objects={
            'general': [{'properties': {'isInvertedSelectionMode': {'expr': {'Literal': {'Value': 'true'}}}}}]}))
        self.assert_inventory_block('INVERTED_SELECTION_MODE')
        self.assertEqual(self.requests, [])

    def test_filter_field_disagreement_refuses_instead_of_guessing(self):
        self.modify(self.page, lambda d: d['filterConfig']['filters'][0].update(field=field('Sales', 'Revenue', 'Measure')))
        self.assert_inventory_block('FIELD_EXPRESSION_Measure')
        self.assertEqual(self.requests, [])

    def test_no_filter_interaction_excludes_selection(self):
        self.modify(self.page, lambda d: d['visualInteractions'][0].update(type='NoFilter'))
        declaration = self.declaration()
        self.assertEqual(len(declaration['restrictions']), 2)
        self.assertIn('DECLARED_NO_FILTER_INTERACTION', [x['reason'] for x in declaration['evidence']['conditional_declarations']])

    def test_multiple_matching_visuals_remain_real_ambiguity_and_side_channel_refuses(self):
        self.part('definition/pages/p/visuals/other/visual.json', json.loads(self.visual['metadata']['content']))
        result = self.declaration()
        self.assertEqual(result['status'], 'UNDECLARED')
        self.assertIn('AMBIGUOUS_OR_MISSING_DECLARATION_TARGET', result['reason'])
        self.scope['definition_target_id'] = self.visual['id']
        self.assertEqual(self.declaration()['status'], 'UNDECLARED')
        self.assertIn('LEGACY_SIDE_CHANNEL_TARGET',self.declaration()['reason'])

    def test_grouped_visual_is_not_silently_coerced_to_scalar_measure(self):
        self.modify(self.visual, lambda d: d['visual']['query']['queryState'].update(Category={}))
        self.assertIn('UNSUPPORTED_PROJECTION_ROLE: Category', self.declaration()['reason'])

    def test_malformed_native_expression_is_named_refusal(self):
        self.modify(self.page, lambda d: d.update(filterConfig=filter_config({'Version': 2, 'From': [None], 'Where': [None]})))
        self.assert_inventory_block('SOURCE_REFERENCE')
        self.assertEqual(self.requests, [])

    def test_missing_render_support_refuses_before_even_undeclared_context_read(self):
        self.column['metadata']['dataType'] = 'dateTime'
        self.assert_inventory_block('LITERAL_TYPE_dateTime')
        self.assertEqual(self.requests, [])

    def test_lower_filtered_refusal_and_active_selection_inconclusive_are_unchanged(self):
        _, refusal = self.adapter._lower_quantity({}, {'filters': [{}]})
        self.assertEqual(refusal, 'Declared source comparison does not yet translate filtered scope faithfully.')
        with patch('report_slicer_context.assess', return_value={}):
            result = self.adapter.presentation_context({}, {})
        self.assertEqual(result['status'], 'INCONCLUSIVE')

    def test_unknown_selection_bearing_visual_is_unsupported_and_blocked_by_engine_validation(self):
        self.modify(self.slicer,lambda d:d['visual'].update(visualType='unknownSelectionVisual'))
        declaration=self.declaration()
        self.assertEqual(declaration['status'],'DECLARED')
        unsupported=[e for e in declaration['inventory']['entries'] if e['disposition']=='UNSUPPORTED']
        self.assertTrue(any('unknownSelectionVisual' in e['opaque_provenance'] for e in unsupported))
        from investigator import declaration_inventory
        with patch.object(declaration_inventory,'validate',wraps=declaration_inventory.validate) as validation:
            result=self.run_check()
        validation.assert_called_once()
        self.assertEqual(result['status'],'UNDECLARED')
        self.assertEqual(result['unsupported_form'],'UNSUPPORTED_DECLARATION')
        self.assertEqual(self.requests,[])

    def test_active_set_is_only_a_flattening_of_active_inventory_entries(self):
        d=self.declaration()
        self.assertEqual(d['restrictions'],[r for e in d['inventory']['entries'] if e['disposition']=='ACTIVE' for r in e['restrictions']])
        self.assertEqual(d['evidence']['declared_restrictions'],d['restrictions'])
        self.assertNotIn('active_declarations',d['evidence']['metadata'])

    def test_every_discovered_declaration_has_exactly_one_explicit_disposition(self):
        d=self.declaration();inv=d['inventory']
        from investigator import declaration_inventory
        self.assertEqual(sorted(declaration_inventory.identity(s) for s in inv['discovered']),sorted(e['id'] for e in inv['entries']))
        self.assertEqual(len(inv['discovered']),sum(e['disposition'] in declaration_inventory.SCHEMA['disposition']['enum'] for e in inv['entries']))
        self.assertTrue(all(type(e['disposition']) is str for e in inv['entries']))
        with patch.object(predicates.ReportDeclarations,'active',return_value=None):
            result=self.run_check()
        self.assertEqual(result['status'],'UNDECLARED')  # forgotten classification is explicit UNSUPPORTED
        self.assertEqual(self.requests,[])

    def test_shuffling_collected_parts_preserves_inventory_and_ids(self):
        before=self.declaration()['inventory']
        self.parts.reverse()
        after=self.declaration()['inventory']
        self.assertEqual(before,after)

    def test_unknown_declaration_container_without_where_is_not_omitted(self):
        self.modify(self.page,lambda d:d.update(unfamiliarSavedState={'values':['Coastal']}))
        self.assert_inventory_block('UNKNOWN_DECLARATION_CONTAINER:unfamiliarSavedState')

    def test_saved_defaults_are_active_volatile_and_qualified_in_both_outputs(self):
        d=self.declaration();entries=d['inventory']['entries']
        selected=[e for e in entries if 'SAVED_SLICER_SELECTION' in e['opaque_provenance']]
        self.assertTrue(selected)
        self.assertTrue(all(e['disposition']=='ACTIVE' and e['volatility']=='VIEWER_CHANGEABLE' and e['assumption']=='SAVED_DEFAULT' for e in selected))
        result=self.run_check()
        for output in ('business_output','technical_output'):
            self.assertIn('assumes saved default',result[output])
            self.assertNotIn('confirmed',result[output].lower())
        self.scope['reported_figure']=exact(4)
        result=self.run_check()
        self.assertEqual(result['finding']['label'],'NOT_REPRODUCED')
        for output in ('business_output','technical_output'):
            self.assertIn('moved slicer',result[output])
            self.assertIn('invoked bookmark',result[output])
            self.assertIn('other selections',result[output])
            self.assertIn('security restrictions',result[output])

    def hostile(self, change, expected='DECLARATION_INVENTORY_CONTRACT'):
        d=copy.deepcopy(self.declaration());change(d)
        class WrongAdapter:
            def capabilities(inner):return {'declared_context_reproduction'}
            def declared_context(inner,*args):return d
            def evaluate_declared_context(inner,*args):self.fail('Hostile producer reached a data read')
        result=declared_reproduction.run(WrongAdapter(),self.layer,self.measure['id'],self.scope)
        self.assertEqual(result['status'],'UNDECLARED')
        self.assertEqual(result['unsupported_form'],expected)
        self.assertEqual(self.requests,[])
        return result

    def test_hostile_producer_active_restriction_without_inventory_entry_is_refused(self):
        self.hostile(lambda d:d['restrictions'].append({'field_id':'untraced','operator':'IN','values':[1]}))

    def test_hostile_producer_active_entry_missing_from_active_set_is_refused(self):
        self.hostile(lambda d:d['restrictions'].pop())

    def test_hostile_producer_missing_or_multiple_dispositions_is_refused(self):
        for value in (None,['ACTIVE','CONDITIONAL']):
            def change(d):
                e=d['inventory']['entries'][0]
                if value is None:del e['disposition']
                else:e['disposition']=value
            with self.subTest(value=value):self.hostile(change)

    def test_hostile_producer_unsupported_entry_blocks_otherwise_complete_active_set(self):
        def change(d):
            from investigator import declaration_inventory
            source={'location':'unrelated-declaration','content_hash':'d'*64}
            d['inventory']['discovered'].append(source)
            d['inventory']['entries'].append({'id':declaration_inventory.identity(source),'source':source,
                'disposition':'UNSUPPORTED','volatility':'UNKNOWN','assumption':'APPLICABILITY_UNKNOWN',
                'opaque_provenance':'unknown-external-kind','restrictions':[]})
        result=self.hostile(change,'UNSUPPORTED_DECLARATION')
        self.assertIn('Unsupported declarations',result['reason'])

    def test_hostile_producer_volatility_or_assumption_outside_consumer_enum_is_refused(self):
        for field in ('volatility','assumption'):
            with self.subTest(field=field):
                result=self.hostile(lambda d:d['inventory']['entries'][0].update({field:'producer-invented-value'}))
                self.assertIn('Invalid declaration '+field,result['reason'])

    def test_hostile_producer_unaccounted_discovered_declaration_is_refused(self):
        self.hostile(lambda d:d['inventory']['entries'].pop())

    def test_unknown_part_is_unsupported_even_without_recognised_predicate(self):
        self.part('definition/unfamiliarDeferredFeature.json',{'selection':['Coastal']})
        self.assert_inventory_block('UNKNOWN_DEFINITION_PART')


if __name__ == '__main__': unittest.main()
