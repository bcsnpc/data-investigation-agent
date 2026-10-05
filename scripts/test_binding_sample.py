"""Typed witnesses catch wrong bindings even when the old SUM agrees."""
import copy
import hashlib
import sqlite3
import unittest
from investigator.binding_sample import verify, sample_address, validate_address
from investigator.process_debugging import attest_surface
from investigator.transformation_sql import compile_quantity
from investigator.verification_budget import VerificationBudget
from investigator.usage_governance import UsageHold
from test_lineage_binding import proposal


class BindingSampleTests(unittest.TestCase):
    sample = {'kind': 'KEY_RANGE', 'column': 'key', 'lower': 1, 'upper': 20,
              'provenance': 'synthetic-explicit-key-range'}

    def trial(self, profile, source, target):
        with sqlite3.connect(':memory:') as db:
            db.executescript("CREATE TABLE source_data(k INT, v); CREATE TABLE target_data(k INT, v);")
            db.executemany('INSERT INTO source_data VALUES (?,?)', enumerate(source, 1))
            db.executemany('INSERT INTO target_data VALUES (?,?)', enumerate(target, 1))
            db.create_function('stable_hash', 1, lambda v: int.from_bytes(hashlib.sha256(v.encode('utf-8')).digest()[:4], 'big'))
            statements = []

            def compiler(binding, side, context, address):
                columns = {'NUMERIC': 'SUM(v) AS sum, COUNT(*) AS count',
                           'STRING': 'COUNT(*) AS count, COUNT(DISTINCT v) AS distinct_count, SUM(CASE WHEN v IS NOT NULL THEN stable_hash(v) END) AS hash_sum',
                           'TEMPORAL': 'MIN(v) AS min, MAX(v) AS max, COUNT(*) AS count',
                           'BOOLEAN': 'COUNT(CASE WHEN v=1 THEN 1 END) AS true_count, COUNT(*) AS count'}
                table = 'source_data' if side == 'SOURCE' else 'target_data'
                query = 'SELECT ' + columns[profile] + ' FROM ' + table + ' WHERE k BETWEEN 1 AND 20'
                statements.append((side, query))
                return {'query':query, 'address':address, 'normalization':{
                    'status':'DECLARED','collation':'ordinal','trim':False,'case_fold':False,
                    'evidence':'synthetic-sqlite-binary-declaration'}}

            def execute(side, plan):
                query, address = plan['query'], plan['address']
                cursor = db.execute(query)
                values = dict(zip([c[0] for c in cursor.description], cursor.fetchone()))
                surface = {'engine': 'sqlite', 'connection': 'test', 'object': side, 'identity': 'synthetic-reader'}
                evidence = {'id': side, 'execution_surface': surface, 'surface_report': surface,
                            'surface_report_binding': 'VALUE_QUERY', 'surface_report_receipt_id': side,
                            'surface_report_types': {'engine': 'ENGINE_PRODUCT', 'object': 'DATABASE'},
                            'read_address': address, 'values':[copy.deepcopy(values)], 'context_id':'synthetic'}
                evidence['surface_attestation'] = attest_surface(surface, surface, tuple(surface))
                return {'status': 'COMPLETED', 'context': 'synthetic', 'address': address,
                        'quantities': values, 'evidence': evidence}

            result = verify(proposal(), context='synthetic', sample=self.sample, profile=profile,
                            compiler=compiler, execute=execute)
            self.assertEqual(len(statements), 2)
            return result

    def test_every_type_correct_binding_verifies_and_wrong_binding_falsifies(self):
        cases = [('NUMERIC', [2, 4], [1, 5], [3, 4]),
                 ('STRING', ['a', 'b'], ['b', 'a'], ['a', 'c']),
                 ('TEMPORAL', ['2026-01-01', '2026-01-02'], ['2026-01-02', '2026-01-01'], ['2026-01-01', '2026-01-03']),
                 ('BOOLEAN', [1, 0, 1], [0, 1, 1], [1, 0, 0])]
        for kind, source, good, bad in cases:
            with self.subTest(profile=kind):
                good_result = self.trial(kind, source, good)
                self.assertEqual(good_result['status'], 'VERIFIED')
                self.assertEqual(good_result['snapshot_status'], 'SNAPSHOT_UNVERIFIED')
                self.assertTrue(good_result['requires_reverification'])
                self.assertEqual(self.trial(kind, source, bad)['status'], 'FALSIFIED')

    def test_equal_sum_but_different_count_falsifies(self):
        self.assertEqual(self.trial('NUMERIC', [2, 2], [4])['status'], 'FALSIFIED')
        self.assertEqual(self.trial('NUMERIC', [None, None], [None])['status'], 'FALSIFIED')

    def test_hash_detects_changed_string_content_with_equal_cardinality(self):
        self.assertEqual(self.trial('STRING', ['Sales', 'Customers'], ['Sales', 'Orders'])['status'], 'FALSIFIED')

    def test_verdict_recomputed_from_original_complete_profile(self):
        from investigator.lineage_binding import revalidate_verification
        original=self.trial('NUMERIC',[2,4],[4,2])
        self.assertEqual(revalidate_verification(original),original)
        changed=copy.deepcopy(original)
        changed['observations'][1]['quantities']['count']=3
        with self.assertRaisesRegex(ValueError,'differs'):
            revalidate_verification(changed)

    def test_original_values_cannot_be_replaced_by_consistent_forged_profile(self):
        from investigator.lineage_binding import revalidate_verification
        original=self.trial('NUMERIC',[2,4],[4,2])
        for observation in original['observations']:
            observation['quantities']['count']=123
        with self.assertRaisesRegex(ValueError,'differs'):
            revalidate_verification(original)

    def test_stable_standalone_metadata_does_not_verify_snapshot(self):
        from investigator.lineage_binding import revalidate_verification
        original=self.trial('NUMERIC',[2,4],[4,2])
        for observation in original['observations']:
            observation['evidence']['standalone_metadata']={'version':'stable','modified':'2026-10-05'}
        checked=revalidate_verification(original)
        self.assertEqual(checked['snapshot_status'],'SNAPSHOT_UNVERIFIED')
        self.assertTrue(checked['requires_reverification'])

    def test_declared_to_proposal_round_trip_uses_compiled_vector(self):
        from contextlib import closing
        from types import SimpleNamespace
        from investigator.adapters.binding_verification import BindingVerificationRoute
        import sqlglot
        p=proposal()
        objects={name:{'asset_id':name,'connection':'endpoint','database':side,
            'catalog':{'id':name,'metadata':{'schema_name':side,'name':'items','type_desc':'USER_TABLE',
                'columns':[{'name':'amount','data_type':'int'},{'name':'key','data_type':'bigint'}]}}}
            for name,side in [('input-table','lower_data'),('output-table','upper_data')]}
        p['expression']['relation']['columns'].append('key')
        p['sources'][0]['columns'].append('key')
        process=SimpleNamespace(model={'context_id':'synthetic'},config={'fabric':{'sql_reader':{'server':'endpoint'}}})
        route=BindingVerificationRoute(process,objects=objects,context='synthetic')
        with closing(sqlite3.connect(':memory:')) as db:
            db.executescript("ATTACH DATABASE ':memory:' AS lower_data; ATTACH DATABASE ':memory:' AS upper_data; CREATE TABLE lower_data.items(amount INT,key INT); CREATE TABLE upper_data.items(amount INT,key INT); INSERT INTO lower_data.items VALUES (3,1),(3,2),(4,3); INSERT INTO upper_data.items SELECT * FROM lower_data.items;")
            statements=[]
            def execute(side,plan):
                statements.append(plan['compiled']['query'])
                cursor=db.execute(sqlglot.transpile(plan['compiled']['query'],read='tsql',write='sqlite')[0])
                values=dict(zip([c[0] for c in cursor.description],cursor.fetchone()))
                surface={'engine':'sqlite','connection':'memory','object':side,'identity':'reader'}
                evidence={'id':side,'values':[values],'context_id':'synthetic','read_address':plan['address'],
                    'execution_surface':surface,'surface_report':surface,'surface_report_binding':'VALUE_QUERY',
                    'surface_report_receipt_id':side,'surface_report_types':{'engine':'ENGINE_PRODUCT','object':'DATABASE'}}
                evidence['surface_attestation']=attest_surface(surface,surface,tuple(surface))
                return {'status':'COMPLETED','context':'synthetic','address':plan['address'],'quantities':values,'evidence':evidence}
            options={'context':'synthetic','sample':self.sample,'profile':route.target_profile(p),'compiler':route.compile,'execute':execute}
            declared=verify(p,**options)
            p.update(extractor='MODEL',confidence=0.1)
            inferred=verify(p,**options)
            self.assertEqual(declared['status'],'VERIFIED')
            self.assertEqual(inferred['status'],'VERIFIED')
            self.assertEqual(declared['address'],inferred['address'])
            self.assertEqual(statements[:2],statements[2:])
            self.assertEqual(declared['observations'],inferred['observations'])

    def test_declared_copy_tape_cannot_supply_unrecorded_count(self):
        import json
        from pathlib import Path
        record=json.loads((Path(__file__).parent/'fixtures/round-six-declared-copy-verification.json').read_text(encoding='utf-8'))
        original=record['verification']
        p=copy.deepcopy(original['proposal']);p.update(extractor='MODEL',confidence=0.1)
        observations=iter(original['observations'])
        result=verify(p,context=original['context'],sample=self.sample,profile='NUMERIC',
            compiler=lambda *args:None,execute=lambda *args:next(observations))
        self.assertEqual(result['status'],'UNVERIFIED')
        self.assertNotIn('quantities',original['observations'][0])
        # Do not backfill addresses or counts into a pre-contract receipt.
        self.assertEqual(result['observations'][0],original['observations'][0])

    def test_complete_profile_is_required_legacy_sum_is_not_backfilled(self):
        from investigator.binding_sample import _quantities
        with self.assertRaisesRegex(ValueError, 'Complete'):
            _quantities({'sum': '7661'}, 'NUMERIC')

    def test_date_window_address_and_tampered_identity(self):
        sample = {'kind': 'DATE_WINDOW', 'column': 'event_date', 'lower': '2026-09-15',
                  'upper': '2026-09-16', 'provenance': 'retained-predicate'}
        address = sample_address(proposal(), sample, 'TEMPORAL')
        self.assertEqual(validate_address(address), address)
        address['sample']['upper'] = '2026-09-17'
        with self.assertRaisesRegex(ValueError, 'identity'):
            validate_address(address)

    def test_declared_and_model_provenance_do_not_change_quantity_address(self):
        p=proposal();a=sample_address(p,self.sample,'NUMERIC')
        p.update(extractor='MODEL',confidence=0.3)
        self.assertEqual(sample_address(p,self.sample,'NUMERIC'),a)

    def test_compile_integral_profile_one_statement_and_explicit_sample(self):
        relation = {'kind': 'SCAN', 'table': 't', 'columns': ['key', 'amount']}
        catalog = {'t': {'id': 't', 'metadata': {'schema_name': 'dbo', 'name': 'items',
                         'type_desc': 'USER_TABLE', 'columns': [{'name': 'key', 'data_type': 'bigint'},
                                                               {'name': 'amount', 'data_type': 'int'}]}}}
        text = compile_quantity(relation, 'amount', catalog, profile='NUMERIC', sample=self.sample)
        self.assertIn('SUM(', text)
        self.assertIn('COUNT(', text)
        self.assertIn('>= 1', text)
        self.assertIn('<= 20', text)

    def test_text_named_date_is_not_implicitly_cast_or_compared(self):
        relation = {'kind': 'SCAN', 'table': 't', 'columns': ['event_date', 'amount']}
        catalog = {'t': {'id': 't', 'metadata': {'schema_name': 'dbo', 'name': 'items',
                         'type_desc': 'USER_TABLE', 'columns': [{'name': 'event_date', 'data_type': 'nvarchar'},
                                                               {'name': 'amount', 'data_type': 'int'}]}}}
        sample = {'kind': 'DATE_WINDOW', 'column': 'event_date', 'lower': '2026-09-15',
                  'upper': '2026-09-16', 'provenance': 'retained'}
        with self.assertRaisesRegex(ValueError, 'SAMPLE_TYPE_UNSUPPORTED'):
            compile_quantity(relation, 'amount', catalog, profile='NUMERIC', sample=sample)

    def test_verification_budget_does_not_change_investigation_cap(self):
        budgets = {'diagnostic_reads_per_run': 12,
                   'binding_verification': {'probes_per_binding': 2, 'metadata_probes': 3, 'session_cap': 33}}
        events = []
        budget = VerificationBudget(budgets, 15, record=events.append)
        for _ in range(33):
            budget.read('TARGET', lambda: None)
        with self.assertRaises(UsageHold):
            budget.read('SOURCE', lambda: self.fail('must not execute'))
        self.assertEqual(budgets['diagnostic_reads_per_run'], 12)
        self.assertEqual(budget.count, 33)
        self.assertEqual(events[-1]['decision'], 'REFUSED')


if __name__ == '__main__':
    unittest.main()
