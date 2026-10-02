"""Item 2b: the declared-source quantity read on an independent surface, faithfully or not at all."""
import copy
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from investigator import flexible_tools, process_outcomes
from investigator.onboarding import Conflict
from investigator.process_debugging import Probe, vertical

ROOT = Path(__file__).resolve().parents[1]
REFUSAL = 'Declared source comparison does not yet translate filtered scope faithfully.'
WS = '00000000-0000-0000-0000-000000000001'


class Store:
    def __init__(self, model):
        self.model = model
        self.path = os.path.join(tempfile.mkdtemp(), 'catalog.sqlite')

    def get(self, identity):
        return self.model

    def connect(self):
        return sqlite3.connect(self.path)


def declared_layer(**changes):
    binding = {'status': 'RESOLVED', 'provenance': 'DECLARED_BY_DEFINITION', 'declared_connection_asset_id': 'endpoint-1',
               'declared_partition': {'schema_name': 'sch', 'entity_name': 'ent', 'source_type': 'entity',
                                      'mode': 'directLake', 'partition_count': 1},
               'declared_role_count': 0, 'definition_asset_id': 'def'}
    layer = {'id': 'lower-asset', 'kind': 'declared_source', 'semantic_table': 'T', 'semantic_column': 'c',
             'declared_columns': [{'name': 'c', 'sourceColumn': 'src_c', 'dataType': 'int64'},
                                  {'name': 'd', 'sourceColumn': 'src_d', 'dataType': 'string'}],
             'binding': binding, 'definition_asset_id': 'def'}
    for key, value in changes.items():
        if key in binding or key in ('declared_partition',):
            binding[key] = value
        else:
            layer[key] = value
    return layer


class Harness:
    CONTEXT = {'assets': [{'id': 'endpoint-1', 'kind': 'SQLEndpoint', 'name': 'lower_db'}]}

    def __init__(self, lower_surface=True, response=None):
        from investigator.adapters.microsoft_process import MicrosoftProcessAdapter
        self.model = {'id': 'm', 'revision': 1, 'context_id': 'c', 'workspace': WS, 'native_id': 'n', 'name': 'M',
                      'enabled': True, 'context': {}}
        self.config = {'fabric': {'workspace_id': WS, 'native_reader': {'account': 'reader@example.com'},
                                  'sql_reader': {'account': 'reader@example.com', 'server': 'lower.example.invalid'}}}
        self.store = Store(self.model); self.lower_calls = []
        self.response = response or {'rows': [{'quantity': '10'}], 'column_types': {'quantity': 'Int64'},
                                     'read_only_verified': True,
                                     'surface_report': {'identity': 'reader@example.com', 'object': 'lower_db'},
                                     'execution_identity': {'principal': 'reader@example.com'}}
        def execute_lower(database, request):
            self.lower_calls.append((database, request))
            return self.response
        self.adapter = MicrosoftProcessAdapter(self.store, self.config, self.model, None, None,
            lower_surface={'status': 'READY'} if lower_surface else None,
            execute_lower=execute_lower if lower_surface else None)

    def evaluate(self, layer, scope=None, dax=None):
        dax_result = dax or {'id': 'dax-1', 'status': 'COMPLETED', 'request_hash': 'h',
                             'result': {'rows': [{'[baseline]': {'type': 'decimal', 'value': '10'}}],
                                        'completeness': 'COMPLETE_RESPONSE',
                                        'surface_report': {'identity': 'reader@example.com'}}}
        real_run = flexible_tools.run
        def run_query(store, plan, config, tool, execute, **kwargs):
            if tool == 'bounded_dax':
                self.dax_query = plan['query']
                return dax_result
            return real_run(store, plan, config, tool, execute, **kwargs)
        with patch('investigator.adapters.microsoft_process.assets', return_value=[{'id': 'q', 'name': 'Q'}]), \
             patch('investigator.adapters.microsoft_process.context_search.latest', return_value=self.CONTEXT), \
             patch('investigator.adapters.microsoft_process.run_query', side_effect=run_query):
            return self.adapter.evaluate(layer, 'q', scope or {})


class CompileTests(unittest.TestCase):
    def test_quantity_is_compiled_from_declarations_through_the_admission_path(self):
        h = Harness()
        probe = h.evaluate(declared_layer())
        self.assertEqual(probe.status, 'OBSERVED')
        database, request = h.lower_calls[0]
        self.assertEqual(database, 'lower_db')
        # Compiled (and re-qualified) by the SQL compiler against the declared catalog.
        self.assertEqual(request['tool'], 'bounded_fabric_sql')
        self.assertIn('SUM(', request['query']); self.assertIn('[src_c]', request['query'])
        self.assertIn('[sch].[ent]', request['query'])
        self.assertEqual(request['read_only_objects'], ['[sch].[ent]'])
        self.assertTrue(request['require_read_only'])
        self.assertEqual(probe.value, {'quantity': '10'})
        self.assertEqual(probe.execution_surface, {'engine': 'FABRIC_SQL', 'connection': 'sql://lower.example.invalid',
                                                   'object': 'lower_db', 'identity': 'reader@example.com'})
        self.assertEqual(probe.surface_report, {'identity': 'reader@example.com', 'object': 'lower_db'})
        self.assertEqual(probe.surface_reportable, ('identity', 'object'))
        self.assertEqual(probe.evidence['binding_provenance'], 'DECLARED_BY_DEFINITION')

    def test_compiled_presentation_and_source_reads_record_context_explicitly(self):
        from investigator.refresh_comparison import whole_entity_context
        h=Harness()
        self.assertEqual(h.evaluate({'id':'top'}).evidence['declared_context'],whole_entity_context())
        self.assertEqual(h.evaluate(declared_layer()).evidence['declared_context'],whole_entity_context())
        self.assertIsNone(h.evaluate({'id':'top'},scope={'dimension_ids':['unknown']}).evidence['declared_context'])

    def test_the_read_leaves_a_sealed_receipt(self):
        from investigator.receipt_integrity import verify
        h = Harness(); probe = h.evaluate(declared_layer())
        with h.store.connect() as db:
            self.assertEqual(verify(db, 'bounded_fabric_sql', probe.evidence['id'])['state'], 'SEALED')

    def test_filtered_scope_refusal_is_unchanged_and_nothing_is_read(self):
        h = Harness()
        probe = h.evaluate(declared_layer(), scope={'filters': [{'column': 'x'}]})
        self.assertEqual((probe.status, probe.reason), ('NOT_COMPARABLE', REFUSAL))
        self.assertEqual(h.lower_calls, [])

    def test_unfaithful_mappings_are_refused_and_fall_back_to_the_within_layer_check(self):
        cases = {'roles': declared_layer(declared_role_count=1),
                 'omitted source type': declared_layer(declared_partition={'schema_name':'sch','entity_name':'ent','partition_count':1}),
                 'partitions': declared_layer(declared_partition={'schema_name': 'sch', 'entity_name': 'ent',
                                                                  'source_type': 'entity', 'partition_count': 2}),
                 'query partition': declared_layer(declared_partition={'schema_name': 'sch', 'entity_name': 'ent',
                                                                       'source_type': 'm', 'partition_count': 1}),
                 'calculated column': declared_layer(declared_columns=[{'name': 'c', 'type': 'calculated',
                                                                        'expression': 'x', 'dataType': 'int64'}]),
                 'no source column': declared_layer(declared_columns=[{'name': 'c', 'dataType': 'int64'}]),
                 'no endpoint': declared_layer(declared_connection_asset_id='missing'),
                 'unresolved': declared_layer(status='AMBIGUOUS')}
        for name, layer in cases.items():
            with self.subTest(name):
                h = Harness(); probe = h.evaluate(layer)
                self.assertEqual(h.lower_calls, [])
                self.assertEqual((probe.status, probe.reason), ('NOT_COMPARABLE', 'NO_INDEPENDENT_LOWER_READ'))
                self.assertTrue(probe.evidence['independent_read_refused'])

    def test_without_an_independent_surface_the_within_layer_check_still_fires(self):
        h = Harness(lower_surface=False)
        probe = h.evaluate(declared_layer())
        self.assertEqual((probe.status, probe.reason), ('NOT_COMPARABLE', 'NO_INDEPENDENT_LOWER_READ'))
        self.assertEqual(probe.execution_surface['engine'], 'POWER_BI_DAX')
        self.assertIn("SUM('T'[c])", h.dax_query)

    def test_failed_lower_read_is_unavailable_not_observed(self):
        h = Harness(response={'error': 'x'})
        probe = h.evaluate(declared_layer())
        self.assertEqual(probe.status, 'UNAVAILABLE')
        self.assertEqual(probe.failure['interface'], 'FABRIC_SQL')

    def test_engine_values_compare_across_representations(self):
        from investigator.adapters.microsoft_process import _quantity
        self.assertEqual(_quantity([{'[baseline]': {'type': 'decimal', 'value': '8765'}}]),
                         _quantity([{'quantity': {'type': 'decimal', 'value': '8765.00'}}]))
        self.assertEqual(_quantity([{'a': None}]), {'quantity': None})
        self.assertEqual(_quantity([{'a': 1}, {'a': 2}]), [{'a': 1}, {'a': 2}])  # not a scalar: kept as is

    def test_no_estate_names_in_adapter_or_engine(self):
        for path in ('scripts/investigator/adapters/microsoft_process.py', 'scripts/investigator/process_debugging.py',
                     'scripts/investigator/flexible_tools.py'):
            source = (ROOT/path).read_text(encoding='utf-8').lower()
            for name in ('movement_values', 'warehouse_gold', 'handled quantity', "'activity'", 'e1b8e1'):
                self.assertNotIn(name, source, path)

    def test_declared_surface_columns_never_enter_compared_quantity(self):
        from investigator.adapters.microsoft_process import _quantity
        import copy
        for label in ('surface_identity','arbitrary_report_label'):
            for column in (label,'['+label+']'):
                rows=[{'[baseline]':{'type':'decimal','value':'12.00'},
                       column:{'type':'string','value':'reader@example.com'}}]
                original=copy.deepcopy(rows)
                self.assertEqual(_quantity(rows,{'identity':label}),{'quantity':'12'})
                self.assertEqual(rows,original)  # receipt/attestation untouched
                self.assertEqual(_quantity(rows),original)  # no name-based stripping
                rows[0]['other_measure']={'type':'decimal','value':'5'}
                projected=_quantity(rows,{'identity':label})
                self.assertEqual(set(projected[0]),{'[baseline]','other_measure'})

    def test_the_fabric_sql_tool_requires_a_declared_catalog_and_is_not_offered_to_planners(self):
        h = Harness()
        plan = {'model_id': 'm', 'revision': 1, 'context_id': 'c', 'query': 'SELECT 1 AS x', 'max_rows': 20}
        with self.assertRaises(Conflict):
            flexible_tools.build(h.store, plan, h.config, 'bounded_fabric_sql')
        source = (ROOT/'scripts/investigator/flexible_tools.py').read_text(encoding='utf-8')
        capabilities = source[source.index('def capabilities'):source.index('def surface_columns')]
        self.assertNotIn('bounded_fabric_sql', capabilities)


class ResolvedLayerTests(unittest.TestCase):
    def test_declared_columns_come_from_the_referenced_semantic_column_assets(self):
        from investigator.adapters.microsoft_process import MicrosoftProcessAdapter
        metadata = {'measure': {'id': 'q', 'parent_id': 'table', 'metadata': {'expression': "SUM('T'[c])"}},
                    'assets': [{'kind': 'SemanticTable', 'name': 'T', 'metadata': {'partitions': []}},
                               {'kind': 'SemanticColumn', 'name': 'c', 'parent_id': 'table',
                                'metadata': {'sourceColumn': 'src_c', 'dataType': 'int64'}}], 'gaps': []}
        binding = {'status': 'RESOLVED', 'asset': {'id': 'lower-asset'}, 'definition_asset_id': 'def', 'provenance':
                   'DECLARED_BY_DEFINITION'}
        adapter = MicrosoftProcessAdapter(object(), {'fabric': {}}, {'context': {}}, None, None)
        with patch('investigator.adapters.microsoft_process.context_search.measure_path', return_value=metadata),              patch.object(MicrosoftProcessAdapter, '_partition_binding', return_value=binding),              patch('investigator.adapters.microsoft_process.context_search.latest', return_value={}):
            layer = adapter.resolve_path('q')['layers'][1]
        self.assertEqual(layer['declared_columns'], [{'name': 'c', 'sourceColumn': 'src_c', 'dataType': 'int64'}])


class ProcedureAdapter:
    """Presentation on one surface and the declared source on another."""
    def __init__(self, upper, lower, capabilities=(), definition=None, jobs=None, provenance='DECLARED_BY_DEFINITION'):
        self.upper, self.lower, self.extra = upper, lower, set(capabilities)
        self.definition, self.jobs, self.provenance = definition, jobs, provenance
        self.definition_calls = 0

    def capabilities(self):
        return {'resolve_measure_path', 'evaluate_scoped_quantity', 'independent_lower_surface'} | self.extra

    def resolve_path(self, measure):
        return {'layers': [{'id': 'presentation'}, {'id': 'declared-source'}], 'stopped_by': 'REACHED',
                'evidence': {'id': 'path', 'tool': 'context'}}

    def evaluate(self, layer, measure, scope):
        if layer['id'] == 'presentation':
            return Probe('OBSERVED', 'presentation', {'id': 'dax', 'tool': 'bounded_dax'}, {'quantity': self.upper},
                         execution_surface={'engine': 'POWER_BI_DAX', 'connection': 'ws', 'object': 'model',
                                            'identity': 'reader'},
                         surface_report={'identity': 'reader','engine':'POWER_BI_DAX','connection':'ws','object':'model'}, surface_reportable=('identity',))
        return Probe('OBSERVED', 'declared-source', {'id': 'sql', 'tool': 'bounded_fabric_sql',
                                                     'binding_provenance': self.provenance},
                     {'quantity': self.lower},
                     execution_surface={'engine': 'FABRIC_SQL', 'connection': 'sql://h', 'object': 'db',
                                        'identity': 'reader'},
                     surface_report={'identity': 'reader', 'object': 'db','engine':'FABRIC_SQL','connection':'sql://h'}, surface_reportable=('identity', 'object'))

    def presentation_context(self, boundary, scope):
        return {'status': 'INCONCLUSIVE', 'explains': None}

    def transformation_definition(self, boundary):
        self.definition_calls += 1
        return self.definition or {'status': 'UNAVAILABLE', 'explains': None}

    def job_history(self, boundary):
        return self.jobs or {'status': 'NOT_APPLICABLE'}

    def ingestion(self, path, scope):
        return {'status': 'CURRENT'}


class ProcedureTests(unittest.TestCase):
    def test_equal_values_on_different_surfaces_are_an_adjacent_cross_surface_consistency(self):
        result = vertical(ProcedureAdapter('10', '10'), 'measure', {})
        self.assertEqual(result['classification'], 'CONSISTENT_TO_BOUNDARY')
        comparison = next(o for o in result['_observations'] if o.get('comparison_status') == 'CROSS_SURFACE_VERIFIED')
        self.assertEqual((comparison['upper_layer'], comparison['lower_layer']), ('presentation', 'declared-source'))
        self.assertNotEqual(comparison['upper_execution_surface']['engine'], comparison['lower_execution_surface']['engine'])
        named = {(u['layer'], u['field']) for u in result['business_output']['unattested_surface_fields']}
        self.assertEqual(named,set()) # This synthetic producer self-reports all four fields.
        for output in ('business_output', 'technical_output'):
            self.assertEqual(result[output]['compared_bindings'][0]['provenance'], 'DECLARED_BY_DEFINITION')
        process_outcomes.validate(result, {o['id']: o for o in result['_observations']})

    def test_divergence_found_this_way_cannot_become_defect(self):
        profiles = {
            'no definition or job checks': ProcedureAdapter('10', '9'),
            'checks declared but unavailable': ProcedureAdapter('10', '9', {'presentation_context', 'transformation_definition',
                                                                            'job_history', 'ingestion'}),
            'checks declared, nothing explains': ProcedureAdapter('10', '9', {'presentation_context', 'transformation_definition',
                'job_history', 'ingestion'}, definition={'status': 'CURRENT', 'explains': False,
                'evidence': {'id': 'def', 'tool': 'context'}}, jobs={'status': 'NOT_APPLICABLE'}),
        }
        for name, adapter in profiles.items():
            with self.subTest(name):
                result = vertical(adapter, 'measure', {})
                self.assertNotEqual(result['classification'], 'DEFECT')

    def test_divergence_asks_for_the_definition_when_it_is_declared(self):
        adapter = ProcedureAdapter('10', '9', {'transformation_definition'})
        vertical(adapter, 'measure', {})
        self.assertEqual(adapter.definition_calls, 1)

    def test_a_comparison_on_an_inferred_binding_says_so_in_both_outputs(self):
        result = vertical(ProcedureAdapter('10', '10', provenance='INFERRED_FROM_CODE'), 'measure', {})
        self.assertTrue(any('INFERRED_FROM_CODE' in l and 'declared-source' in l for l in result['limits']))
        for output in ('business_output', 'technical_output'):
            self.assertEqual(result[output]['compared_bindings'][0]['provenance'], 'INFERRED_FROM_CODE')
        observations = {o['id']: o for o in result['_observations']}
        process_outcomes.validate(result, observations)
        stripped = copy.deepcopy(result); stripped['limits'] = [l for l in stripped['limits'] if 'INFERRED' not in l]
        with self.assertRaisesRegex(ValueError, 'inferred binding'):
            process_outcomes.validate(stripped, observations)
        for output in ('business_output', 'technical_output'):
            stripped = copy.deepcopy(result); stripped[output]['compared_bindings'] = []
            with self.assertRaisesRegex(ValueError, 'both outputs'):
                process_outcomes.validate(stripped, observations)


class TransportScriptTests(unittest.TestCase):
    def test_script_names_database_self_reports_and_guards_read_only(self):
        source = (ROOT/'infra/scripts/Read-FabricSqlAggregate.ps1').read_text(encoding='utf-8-sig')
        self.assertIn("IsNullOrWhiteSpace($request.database)", source)
        self.assertIn("$builder['Initial Catalog'] = $request.database", source)
        self.assertIn('SUSER_SNAME() AS login_name, DB_NAME() AS database_name', source)
        self.assertIn("fn_my_permissions(NULL,'DATABASE')", source)
        self.assertIn("'access_token,database,max_rows,parameters,query,read_only_objects,result_columns,server'", source)

    def test_transport_forwards_only_the_admitted_request(self):
        import subprocess
        import fabric_sql_surface
        seen = {}
        def run(command, input, **kwargs):
            seen.update(json.loads(input))
            return subprocess.CompletedProcess(command, 0, json.dumps({'rows': [], 'read_only_verified': True}), '')
        config = {'fabric': {'auth': {'tenant_id': WS}, 'sql_reader': {'account': 'r@example.com', 'profile': '.local/p',
                                                                       'server': 'h.example.invalid'}}}
        request = {'query': 'SELECT 1', 'parameters': [], 'read_only_objects': ['[s].[e]'], 'max_rows': 21,
                   'result_columns': ['x'], 'tool': 'bounded_fabric_sql', 'extra': 'dropped'}
        fabric_sql_surface.read(config, 'lower_db', request, token=lambda *a: 't', run=run)
        self.assertEqual(sorted(seen), ['access_token', 'database', 'max_rows', 'parameters', 'query',
                                        'read_only_objects', 'result_columns', 'server'])
        self.assertEqual(seen['database'], 'lower_db')


if __name__ == '__main__':
    unittest.main()
