import copy
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock
from investigator import translation_proposer as t
from investigator.process_debugging import attest_surface
from investigator.verification_budget import VerificationBudget
from investigator.onboarding import digest


def case(kind='FILTER', relative=False):
    definition = {'form': 'relative-window' if relative else 'top-ranked'} if kind == 'FILTER' else {'form': 'remove-restriction'}
    cells = []
    for i in range(4):
        c = {'measure_id': 'm', 'target_id': 'v', 'mode': 'KEYED', 'grouping_columns': ['k'],
             'key_restrictions': [{'field_id': 'k', 'operator': 'IN', 'values': [str(i)]}]}
        c['id'] = digest(c); cells.append(c)
    request = {'kind': kind, 'definition': definition, 'definition_hash': t.seal(definition),
               'target_engine': 'sqlite', 'grouping': [], 'relative': relative,
               'evaluation_timestamp': '2026-10-06T15:00:00-05:00' if relative else None,
               'context': 'synthetic', 'available_cells': cells, 'precision': {'state': 'EXACT'},
               'metadata': {'objects': {'items': 'TABLE'}, 'normalization': {'encoding': 'typed-json-utf8', 'case_fold': False, 'trim': False}}}
    proposal = {k: copy.deepcopy(request[k]) for k in ('kind', 'definition_hash', 'target_engine', 'grouping', 'evaluation_timestamp')}
    proposal.update(objects=[{'id': 'items', 'kind': 'TABLE'}], expression='k in (2,3)' if not relative else "day >= '2026-10-01' and day <= '2026-10-06'")
    if kind == 'MEASURE': proposal['expression'] = 'sum(v)'
    return request, proposal


class TranslationTests(unittest.TestCase):
    def run_case(self, kind='FILTER', *, relative=False, wrong=False, mutate=None, cross=False, cells=None, extension=False):
        request, proposal = case(kind, relative)
        self.request = request; self.proposal = proposal; self.events = []
        db = sqlite3.connect(':memory:')
        self.addCleanup(db.close)
        db.execute('create table items(k integer, v integer, day text)')
        db.executemany('insert into items values(?,?,?)', [(1, 10, '2026-09-30'), (2, 40, '2026-10-01'), (3, 30, '2026-10-06'), (4, 20, '2026-10-07')])
        if wrong: proposal['expression'] = 'k in (1,2)' if kind == 'FILTER' else 'sum(v)+1'
        if relative and wrong: proposal['expression'] = "day >= '2026-10-02'"
        def compile(proposal, side, request, address):
            # This fixture compiler has no network/estate route. Native queries
            # are independently authored, not copied from proposed expressions.
            if kind == 'FILTER':
                native = "select k from items where day >= '2026-10-01' and day <= '2026-10-06'" if relative else 'select k from items order by v desc, k asc limit 2'
                query = native if side == 'NATIVE' else 'select k from items where ' + proposal['expression']
            else:
                native = 'select sum(v) from items'  # ALL removes the keyed restriction.
                query = native if side == 'NATIVE' else 'select ' + proposal['expression'] + ' from items'
            return {'query': query, 'address': address}
        def execute(side, plan):
            self.events.append(side)
            surface = {'engine': 'sqlite', 'connection': 'test', 'object': side if cross else 'items', 'identity': 'synthetic-reader'}
            evidence = {'id': 'receipt-' + str(len(self.events)), 'context_id': request['context'],
                        'read_address': plan['address'], 'execution_surface': surface, 'surface_report': surface,
                        'surface_report_binding': 'VALUE_QUERY', 'surface_report_types': {'engine': 'ENGINE_PRODUCT', 'object': 'DATABASE'}}
            evidence['surface_report_receipt_id'] = evidence['id']
            evidence['surface_attestation'] = attest_surface(surface, surface, tuple(surface))
            rows = db.execute(plan['query']).fetchall()
            o = {'status': 'COMPLETED', 'evidence': evidence}
            if kind == 'FILTER': o.update(keys=[list(r) for r in rows], complete=True, normalization=request['metadata']['normalization'])
            else: o['quantity'] = {'state': 'NUMBER', 'value': str(rows[0][0])}
            evidence['translation_result'] = copy.deepcopy({k: o[k] for k in ('quantity', 'keys', 'complete', 'normalization') if k in o})
            if mutate: mutate(o, side)
            return o
        selected = cells if cells is not None else (request['available_cells'][:3] if kind == 'MEASURE' else [None])
        self.compiler = compile; self.execute = execute
        self.budget_events = []
        self.budget = VerificationBudget({'binding_verification': {'metadata_probes': 0}}, 3, record=self.budget_events.append)
        return t.verify(proposal, request, cells=selected, compiler=compile, execute=execute, budget=self.budget, cross_boundary=cross, extension=extension)

    def test_top_n_matches_independently_evaluated_native_keys(self):
        r = self.run_case(); self.assertEqual(r['status'], 'VERIFIED')
        self.assertEqual(r['key_sets'][0][0]['count'], 2); self.assertEqual(self.budget.count, 2)

    def test_relative_date_pinned_in_every_probe_address(self):
        r = self.run_case(relative=True); self.assertEqual(r['status'], 'VERIFIED')
        for o in r['observations']: self.assertEqual(o['evidence']['read_address']['evaluation_timestamp'], self.request['evaluation_timestamp'])

    def test_all_like_measure_verifies_three_distinct_cell_addresses(self):
        r = self.run_case('MEASURE', cross=True)
        self.assertEqual(r['status'], 'VERIFIED'); self.assertEqual(len(r['cells']), 3)
        self.assertEqual(self.budget.count, 6); self.assertEqual(r['snapshot_status'], 'SNAPSHOT_UNVERIFIED')

    def test_deliberately_wrong_top_n_relative_date_and_measure_falsify(self):
        for kind, relative in [('FILTER', False), ('FILTER', True), ('MEASURE', False)]:
            with self.subTest(kind=kind, relative=relative):
                r = self.run_case(kind, relative=relative, wrong=True, cross=kind == 'MEASURE')
                self.assertEqual(r['status'], 'FALSIFIED'); self.assertEqual(len(r['observations']), 2)

    def test_undiscovered_object_rejected_before_compiler_or_reads(self):
        request, p = case(); p['objects'][0]['id'] = 'other'; compiler = Mock(); execute = Mock()
        with self.assertRaisesRegex(ValueError, 'absent from metadata'):
            t.verify(p, request, cells=[None], compiler=compiler, execute=execute, budget=Mock())
        compiler.assert_not_called(); execute.assert_not_called()

    def test_model_cannot_emit_verdict_or_omit_grouping(self):
        request, p = case()
        for bad in [{**p, 'status': 'VERIFIED'}, {k: v for k, v in p.items() if k != 'grouping'}]:
            with self.assertRaises(Exception): t.validate(bad, request)

    def test_relative_time_cannot_be_changed_or_naive(self):
        request, p = case(relative=True)
        p['evaluation_timestamp'] = '2026-10-07T15:00:00-05:00'
        with self.assertRaisesRegex(ValueError, 'timestamp differs'): t.validate(p, request)
        p['evaluation_timestamp'] = request['evaluation_timestamp'] = '2026-10-06T15:00:00'
        with self.assertRaisesRegex(ValueError, 'timezone'): t.validate(p, request)

    def test_complete_normalized_set_required_not_aggregate_count_alone(self):
        for mutation in [lambda o, s: o.update(complete=False), lambda o, s: o.update(normalization={'other': True})]:
            self.assertEqual(self.run_case(mutate=mutation)['status'], 'UNVERIFIED')
        self.assertNotEqual(t.key_fingerprint([[1], [2]], {'encoding': 'typed'}), t.key_fingerprint([[3], [4]], {'encoding': 'typed'}))

    def test_binary_fingerprint_preserves_type_order_and_tuple_boundaries(self):
        norm = {'encoding': 'typed'}
        self.assertEqual(t.key_fingerprint([[1], [2]], norm), t.key_fingerprint([[2], [1]], norm))
        self.assertNotEqual(t.key_fingerprint([[1]], norm), t.key_fingerprint([['1']], norm))
        self.assertNotEqual(t.key_fingerprint([['ab', 'c']], norm), t.key_fingerprint([['a', 'bc']], norm))
        with self.assertRaises(ValueError): t.key_fingerprint([[1], [1]], norm)

    def test_tampered_attestation_context_or_address_never_verifies(self):
        for field in ('context_id', 'read_address', 'surface_attestation', 'surface_report_binding'):
            def mutation(o, side, field=field): o['evidence'][field] = 'tampered'
            # malformed evidence is a refusal, never a successful witness
            r = self.run_case(mutate=mutation); self.assertEqual(r['status'], 'UNVERIFIED')

    def test_distinct_measure_cell_without_retained_address_refuses(self):
        request, p = case('MEASURE'); cells = request['available_cells'][:2]
        with self.assertRaisesRegex(ValueError, 'three bounded cells'):
            t.verify(p, request, cells=cells, compiler=Mock(), execute=Mock(), budget=Mock(), cross_boundary=True)

    def test_cross_boundary_filters_need_verified_key_binding(self):
        r = self.run_case(cross=True); self.assertEqual(r['status'], 'UNVERIFIED')
        self.assertIn('verified binding', r['reason'])

    def test_ledger_cache_is_scope_and_cell_specific_and_marks_changes_stale(self):
        r = self.run_case('MEASURE', cross=True)
        with tempfile.TemporaryDirectory() as d:
            ledger = t.Ledger(Path(d)/'translations.jsonl'); ledger.append(r)
            self.assertIsNotNone(ledger.reusable(self.request, self.request['available_cells'][0]))
            self.assertIsNone(ledger.reusable(self.request, self.request['available_cells'][3]))
            changed = copy.deepcopy(self.request); changed['context'] = 'new'
            self.assertEqual(ledger.view(changed)[0]['status'], 'STALE')
            original = ledger.path.read_bytes()
            ledger.view(changed); self.assertEqual(ledger.path.read_bytes(), original)

    def test_mechanism_uses_metered_provider_contract(self):
        request, p = case(); proposer = Mock(); proposer.propose.return_value = p
        meter = Mock(side_effect=lambda request, execute: execute())
        self.assertEqual(t.propose(request, proposer, meter), p)
        meter.assert_called_once(); self.assertEqual(proposer.propose.call_args.args[1], t.SCHEMA)

    def test_extension_reuses_original_native_cell_and_charges_one_probe(self):
        r = self.run_case('MEASURE', cross=True)
        cell = self.request['available_cells'][3]
        baseline = copy.deepcopy(r['observations'][0])
        baseline['evidence']['read_address'] = {'kind': 'CELL', 'cell': cell}
        budget = VerificationBudget({'binding_verification': {'metadata_probes': 0}}, 1, record=lambda e: None)
        extended = t.verify(self.proposal, self.request, cells=[cell], compiler=self.compiler, execute=self.execute,
                            budget=budget, cross_boundary=True, extension=True, native_observation=baseline)
        self.assertEqual(extended['status'], 'VERIFIED'); self.assertEqual(budget.count, 1)
        self.assertEqual(t.revalidate(extended), extended)

    def test_failed_or_unaddressed_extension_baseline_cannot_be_rebound(self):
        r = self.run_case('MEASURE', cross=True)
        cell = self.request['available_cells'][3]
        budget = VerificationBudget({'binding_verification': {'metadata_probes': 0}}, 1, record=lambda e: None)
        bad = t.verify(self.proposal, self.request, cells=[cell], compiler=self.compiler, execute=self.execute,
                       budget=budget, cross_boundary=True, extension=True, native_observation=r['observations'][0])
        self.assertEqual(bad['status'], 'UNVERIFIED'); self.assertEqual(budget.count, 0)

    def test_budget_hold_retains_failed_verification_not_a_clean_verdict(self):
        from investigator.lineage_binding import VerificationHold
        self.run_case()
        budget = VerificationBudget({'binding_verification': {'metadata_probes': 0, 'session_cap': 1}}, 1, record=lambda e: None)
        with self.assertRaises(VerificationHold) as raised:
            t.verify(self.proposal, self.request, cells=[None], compiler=self.compiler, execute=self.execute, budget=budget)
        self.assertEqual(len(raised.exception.verification['observations']), 1)
        self.assertEqual(raised.exception.verification['status'], 'UNVERIFIED')

    def test_producer_cannot_replace_receipted_keys_with_an_equal_set(self):
        r = self.run_case(mutate=lambda o, side: o.update(keys=[[99]]))
        self.assertEqual(r['status'], 'UNVERIFIED'); self.assertIn('original probe receipt', r['reason'])

    def test_latest_failed_reverification_invalidates_older_cache(self):
        success = self.run_case()
        with tempfile.TemporaryDirectory() as d:
            ledger = t.Ledger(Path(d)/'translations.jsonl'); ledger.append(success)
            failed = copy.deepcopy(success)
            failed.update(status='UNVERIFIED', reason='New comparison could not execute')
            ledger.append(failed); self.assertIsNone(ledger.reusable(self.request))

    def test_receipt_cannot_relabel_a_falsification_as_verified(self):
        failed = self.run_case(wrong=True); failed['status'] = 'VERIFIED'
        with tempfile.TemporaryDirectory() as d:
            ledger = t.Ledger(Path(d)/'translations.jsonl')
            with self.assertRaisesRegex(ValueError, 'original observations'): ledger.append(failed)

    def test_uncompilable_expression_refuses_before_any_probe(self):
        request, p = case(); execute = Mock()
        r = t.verify(p, request, cells=[None], compiler=Mock(side_effect=NotImplementedError('Unsupported native expression')),
                     execute=execute, budget=Mock())
        self.assertEqual(r['status'], 'UNVERIFIED'); execute.assert_not_called()

    def test_blank_is_not_zero_or_failed_query(self):
        self.assertNotEqual(t._quantity({'state': 'BLANK'}, {'state': 'EXACT'}), t._quantity({'state': 'NUMBER', 'value': '0'}, {'state': 'EXACT'}))
        with self.assertRaises(ValueError): t._quantity(None, {'state': 'EXACT'})


if __name__ == '__main__': unittest.main()
