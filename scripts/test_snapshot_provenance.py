import unittest
from snapshot_provenance import marker, continuity

SILVER = '55cdeeb3-0772-494a-8e7f-f0df4da03353'
GOLD = 'f4e5f3e9-455b-4f99-9a55-408268444b8c'


def result(name, run, **changes):
    values = {'provenance_rows': '100', name: run, name+'_count': '1', name+'_nulls': '0'}
    values.update(changes)
    return {'values': values}


class SnapshotTests(unittest.TestCase):
    def test_aligned_runs_never_become_snapshot_proof(self):
        gold = result('gold_run', GOLD)
        gold['values'].update(result('silver_run', SILVER)['values'])
        output = continuity({'silver': result('silver_run', SILVER), 'gold': gold, 'semantic': result('gold_run', GOLD)})
        self.assertEqual([x['status'] for x in output['checks']], ['RUN_ALIGNED', 'RUN_ALIGNED'])
        self.assertIsNone(output['source_snapshot'])
        self.assertEqual(output['classification'], 'UNRESOLVED')
        self.assertEqual(len(output['gaps']), 3)

    def test_new_gold_old_semantic(self):
        output = continuity({'gold': result('gold_run', GOLD), 'semantic': result('gold_run', SILVER)})
        self.assertEqual(output['checks'][1]['status'], 'RUN_MISMATCH')

    def test_nulls_and_mixed_run_ids_rejected(self):
        for changes in ({'gold_run_count':'2'}, {'gold_run_nulls':'1'}, {'gold_run_count':'0'}):
            self.assertEqual(marker(result('gold_run', GOLD, **changes), 'gold_run')['status'], 'MIXED_OR_MISSING')

    def test_empty_scope_does_not_borrow_global_run(self):
        self.assertEqual(marker(result('gold_run', None, provenance_rows='0', gold_run_count='0'), 'gold_run')['status'], 'UNKNOWN')

    def test_invalid_counts_and_ids(self):
        for changes in ({'provenance_rows':True}, {'gold_run_count':'-1'}, {'gold_run_nulls':'101'}, {'gold_run':'bad'}, {'gold_run_count':None}, {'gold_run_count':'1.0'}):
            with self.subTest(changes=changes):
                self.assertEqual(marker(result('gold_run', GOLD, **changes), 'gold_run')['status'], 'UNKNOWN')

    def test_unavailable_and_legacy_observations(self):
        for item in ({}, {'values':{}}, {'error':'QUERY_UNAVAILABLE'}):
            self.assertEqual(marker(item, 'gold_run')['status'], 'UNKNOWN')


if __name__ == '__main__':
    unittest.main()
