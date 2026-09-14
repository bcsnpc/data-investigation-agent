from contextlib import closing
from pathlib import Path
import tempfile
import unittest
import duckdb
from defect_lab import initialize,mutate,evidence
from lab_filter_cause import verify
from lab_investigator import investigate


class FreshnessTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'lab.duckdb';initialize(self.path)
        self.database=Path(self.temp.name)/'evidence.sqlite'

    def run_case(self):return investigate(evidence(self.path),self.database,cause_verifier=lambda p,r:verify(self.path,p,r))

    def test_stale_snapshot_classified_and_reset(self):
        mutate(self.path,'inject-stale');result=self.run_case()
        self.assertEqual(result['classification'],'REFRESH_FRESHNESS')
        self.assertEqual(result['impact_by_currency']['USD']['downstream_minus_upstream'],'99.0000')
        self.assertFalse(result['automatic_defect_routing'])
        self.assertEqual(mutate(self.path,'reset')['status'],'READY')
        self.assertEqual(self.run_case()['classification'],'UNRESOLVED')

    def test_filter_defect_is_not_freshness(self):
        mutate(self.path,'inject-filter');self.assertEqual(self.run_case()['classification'],'TECHNICAL_DEFECT')

    def test_missing_receipt_and_drift_are_not_classified(self):
        for sql in ['DROP TABLE gold_snapshot_receipt',"UPDATE gold_snapshot_receipt SET query_hash='changed'",
                    'UPDATE g_order_line_summary SET net_cash_amount=0',
                    "UPDATE s_fact_order SET captured_amount=200 WHERE order_id='ORD-000001'"]:
            with self.subTest(sql=sql),tempfile.TemporaryDirectory() as folder:
                path=Path(folder)/'lab.duckdb';initialize(path);mutate(path,'inject-stale')
                with closing(duckdb.connect(str(path))) as db:db.execute(sql)
                result=investigate(evidence(path),self.database,cause_verifier=lambda p,r:verify(path,p,r))
                self.assertEqual(result['classification'],'UNRESOLVED')


if __name__=='__main__':unittest.main()
