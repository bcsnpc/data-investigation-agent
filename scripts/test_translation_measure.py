"""Governed native and lower SQL route integration; transports are injected."""
import copy
import unittest
from unittest.mock import Mock
import test_declared_predicate_adapter as fixture
from investigator import translation_proposer as t
from investigator.onboarding import digest
from investigator.adapters.translation_measure import MeasureRoute
from investigator.verification_budget import VerificationBudget


class MeasureTranslationTests(unittest.TestCase):
    setUp = fixture.DeclaredPredicateAdapterTests.setUp
    part = fixture.DeclaredPredicateAdapterTests.part

    def build(self, value='3'):
        self.config['fabric']['sql_reader'] = {'server': 'declared.example', 'account': self.reader['account']}
        table = {'id': 'declared/source', 'provenance': 'DECLARED_BY_DEFINITION', 'metadata': {
            'schema_name': 'dbo', 'name': 'Source', 'type_desc': 'USER_TABLE',
            'columns': [{'name': 'Value', 'data_type': 'bigint'}]}}
        objects = {table['id']: {'catalog': table, 'connection': 'declared.example', 'database': 'declared-db'}}
        self.sql_requests = []
        def execute(database, compiled):
            self.sql_requests.append((database, copy.deepcopy(compiled)))
            return {'rows': [{'quantity': value}], 'column_types': {'quantity': 'Int64'},
                'read_only_verified': True, 'surface_report_binding': 'VALUE_QUERY',
                'surface_report': {'identity': self.reader['account'], 'engine': 'Microsoft Azure SQL Data Warehouse', 'object': database}}
        self.adapter.execute_lower = execute
        cells = []
        for mode, keys in [('UNGROUPED', []), ('TOTAL', []), ('KEYED', [{'field_id': self.column['id'], 'operator': 'IN', 'values': ['North']}])]:
            cell = {'measure_id': self.measure['id'], 'target_id': self.visual['id'], 'mode': mode,
                'grouping_columns': [] if mode == 'UNGROUPED' else [self.column['id']], 'key_restrictions': keys}
            cell['id'] = digest(cell); cells.append(cell)
        definition = {'measure_id': self.measure['id'], 'expression': self.measure['metadata']['expression']}
        request = {'kind': 'MEASURE', 'definition': definition, 'definition_hash': t.seal(definition),
            'target_engine': 'Microsoft Azure SQL Data Warehouse', 'grouping': [], 'relative': False,
            'evaluation_timestamp': None, 'context': self.model['context_id'], 'scope': {'restrictions': []},
            'available_cells': cells, 'precision': {'state': 'EXACT'}, 'metadata': {'objects': {table['id']: 'TABLE'}}}
        proposal = {key: request[key] for key in ('kind', 'definition_hash', 'target_engine', 'grouping', 'evaluation_timestamp')}
        proposal.update(expression='SELECT SUM(s.[Value]) AS quantity FROM dbo.Source AS s', objects=[{'id': table['id'], 'kind': 'TABLE'}])
        route = MeasureRoute(self.adapter, measure_id=self.measure['id'], objects=objects,
            verification_meter=lambda tool, execute: execute())
        return request, proposal, route, cells

    def test_keyed_sample_without_source_scope_binding_refuses_before_any_read(self):
        request, proposal, route, cells = self.build()
        budget = VerificationBudget({}, 3, record=lambda _: None)
        result = t.verify(proposal, request, cells=cells, compiler=route.compile, execute=route.execute,
                          budget=budget, cross_boundary=True)
        self.assertEqual(result['status'], 'UNVERIFIED', result['reason'])
        self.assertIn('verified column bindings', result['reason'])
        self.assertEqual(budget.count, 0); self.assertEqual(len(self.requests), 0); self.assertEqual(len(self.sql_requests), 0)
        self.assertEqual(self.meters, [])
        with self.assertRaisesRegex(ValueError, 'no observation proof'): t.revalidate(result)

    def test_unrestricted_native_and_source_probes_preserve_differing_original_values(self):
        request, proposal, route, cells = self.build('4')
        address = {'kind':'TRANSLATION', 'proposal_hash':t.seal(proposal), 'cell':cells[0], 'evaluation_timestamp':None}
        observations = [route.execute(side, route.compile(proposal,side,request,address)) for side in ('NATIVE','PROPOSED')]
        self.assertEqual([o['quantity']['value'] for o in observations], ['3', '4'])
        self.assertEqual([o['status'] for o in observations], ['COMPLETED','COMPLETED'])
        self.assertEqual([o['evidence']['read_address'] for o in observations], [address,address])

    def test_definition_not_identical_to_pinned_measure_refuses_before_any_read(self):
        request, proposal, route, cells = self.build()
        request['definition']['expression'] = 'different measure'; proposal['definition_hash'] = request['definition_hash'] = t.seal(request['definition'])
        result = t.verify(proposal, request, cells=cells, compiler=route.compile, execute=route.execute,
            budget=Mock(), cross_boundary=True)
        self.assertEqual(result['status'], 'UNVERIFIED'); self.assertEqual(self.requests, []); self.assertEqual(self.sql_requests, [])


if __name__ == '__main__': unittest.main()
