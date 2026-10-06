"""Actual governed DAX compiler/receipt path, with an injected native transport."""
import copy
import unittest
from unittest.mock import Mock
import test_declared_predicate_adapter as fixture
from investigator import translation_proposer as t, native_identity
from investigator.adapters.translation_native import FilterRoute
from investigator.verification_budget import VerificationBudget


class NativeTranslationTests(unittest.TestCase):
    setUp = fixture.DeclaredPredicateAdapterTests.setUp
    part = fixture.DeclaredPredicateAdapterTests.part

    def route_case(self, values, *, partial=False):
        query = 'EVALUATE SELECTCOLUMNS(FILTER(Customers,Customers[Region]="North"),"translation_key_0",Customers[Region])'
        request = {'kind': 'FILTER', 'definition': {'retained': 'independently compiled filter'},
            'definition_hash': t.seal({'retained': 'independently compiled filter'}),
            'target_engine': 'OLAP Server', 'grouping': [], 'relative': False,
            'evaluation_timestamp': None, 'context': self.model['context_id'], 'scope': {'restrictions': []},
            'metadata': {'objects': {self.dimension['id']: 'TABLE', self.column['id']: 'COLUMN'},
                'native_key_columns': [self.column['id']],
                'normalization': {'encoding': 'typed-json-utf8', 'case_fold': False, 'trim': False}}}
        proposal = {key: request[key] for key in ('kind', 'definition_hash', 'target_engine', 'grouping', 'evaluation_timestamp')}
        proposal.update(expression=query, objects=[{'id': self.dimension['id'], 'kind': 'TABLE'},
                                                  {'id': self.column['id'], 'kind': 'COLUMN'}])
        def execute(compiled):
            self.requests.append(copy.deepcopy(compiled))
            rows = [{'translation_key_0': value, 'translation_marker': False} for value in values]
            rows.append({'translation_key_0': None, 'translation_marker': True})
            if partial: rows = rows * 64
            for row in rows:
                row.update(surface_identity=self.reader['account'], surface_engine='OLAP Server', surface_object=self.model['native_id'])
            response = {'results': [{'tables': [{'rows': rows}]}]}
            response[native_identity.KEY] = native_identity.make(response, compiled, self.reader)
            return response
        self.adapter.execute_native = execute
        self.native_compiler = Mock(return_value=query)
        self.verification_meter = Mock(side_effect=lambda tool, execute: execute())
        route = FilterRoute(self.adapter, native_compiler=self.native_compiler, verification_meter=self.verification_meter)
        return request, proposal, route

    def test_empty_selected_set_still_has_same_statement_surface_attestation(self):
        request, proposal, route = self.route_case([])
        budget = VerificationBudget({}, 1, record=lambda _: None)
        result = t.verify(proposal, request, cells=[None], compiler=route.compile, execute=route.execute, budget=budget)
        self.assertEqual(result['status'], 'VERIFIED')
        self.assertEqual(result['key_sets'][0][0]['count'], 0)
        self.assertEqual(len(self.requests), 2)
        self.assertEqual(self.adapter.meters if hasattr(self.adapter, 'meters') else self.meters, [])
        self.assertEqual(self.verification_meter.call_count, 2)
        for observation in result['observations']:
            self.assertEqual(observation['evidence']['surface_attestation']['consistency'], 'MATCHED')
            self.assertEqual(observation['evidence']['surface_report_binding'], 'VALUE_QUERY')
        self.assertEqual(t.revalidate(result), result)

    def test_complete_keys_preserved_without_attestation_sentinel_as_a_key(self):
        request, proposal, route = self.route_case(['North'])
        result = t.verify(proposal, request, cells=[None], compiler=route.compile, execute=route.execute,
                          budget=VerificationBudget({}, 1, record=lambda _: None))
        self.assertEqual(result['status'], 'VERIFIED')
        self.assertEqual(result['observations'][0]['keys'], [['North']])
        self.assertIn('translation_marker', self.requests[0]['query'])
        self.assertEqual(result['key_sets'][0][0]['count'], 1)

    def test_truncated_keys_never_verify_even_if_both_truncated_answers_agree(self):
        request, proposal, route = self.route_case(['North'], partial=True)
        result = t.verify(proposal, request, cells=[None], compiler=route.compile, execute=route.execute,
                          budget=VerificationBudget({}, 1, record=lambda _: None))
        self.assertEqual(result['status'], 'UNVERIFIED'); self.assertEqual(len(self.requests), 1)

    def test_model_cannot_omit_actual_compiler_object_reference(self):
        request, proposal, route = self.route_case(['North'])
        proposal['objects'] = proposal['objects'][:1]
        result = t.verify(proposal, request, cells=[None], compiler=route.compile, execute=route.execute, budget=Mock())
        self.assertEqual(result['status'], 'UNVERIFIED')
        self.assertIn('compiler-resolved references', result['reason']); self.assertEqual(self.requests, [])


if __name__ == '__main__': unittest.main()
