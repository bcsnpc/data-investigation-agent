from contextlib import closing
from pathlib import Path
import tempfile
import unittest
import duckdb
from defect_lab import initialize,mutate,evidence
from lab_filter_cause import verify
from lab_investigator import investigate
from investigation_evidence_api import EvidenceStore
from routing_drafts import prepare


class ArithmeticTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'lab.duckdb';initialize(self.path)
        self.database=Path(self.temp.name)/'evidence.sqlite'
    def run_case(self):return investigate(evidence(self.path),self.database,cause_verifier=lambda p,r:verify(self.path,p,r))

    def test_double_refund_proved_and_reset(self):
        mutate(self.path,'inject-double-refund');result=self.run_case()
        self.assertEqual(result['classification'],'TECHNICAL_DEFECT')
        self.assertEqual(result['root_cause'],'Gold build subtracts refund amount twice')
        self.assertEqual(result['impact_by_currency']['USD']['downstream_minus_upstream'],'-99.0000')
        self.assertEqual(result['affected_records'][0]['order_id'],'ORD-000001')
        self.assertFalse(result['automatic_defect_routing'])
        self.assertEqual(mutate(self.path,'reset')['status'],'READY')
        self.assertFalse(self.run_case()['root_cause_verified'])

    def test_missing_or_forged_receipt_never_promotes(self):
        mutate(self.path,'inject-double-refund')
        with closing(duckdb.connect(str(self.path))) as db:db.execute("UPDATE gold_arithmetic_receipt SET query_text='DROP TABLE s_fact_order'")
        self.assertEqual(self.run_case()['classification'],'UNRESOLVED')
        with closing(duckdb.connect(str(self.path))) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM s_fact_order').fetchone()[0],3)
            db.execute('DROP TABLE gold_arithmetic_receipt')
        self.assertEqual(self.run_case()['classification'],'UNRESOLVED')

    def test_source_or_output_drift_blocks_proof(self):
        for sql in ("UPDATE s_fact_order SET captured_amount=56 WHERE order_id='ORD-000002'",'UPDATE g_order_line_summary SET net_cash_amount=0'):
            with tempfile.TemporaryDirectory() as folder:
                path=Path(folder)/'lab.duckdb';initialize(path);mutate(path,'inject-double-refund')
                with closing(duckdb.connect(str(path))) as db:db.execute(sql)
                result=investigate(evidence(path),self.database,cause_verifier=lambda p,r:verify(path,p,r))
                self.assertEqual(result['classification'],'UNRESOLVED')

    def test_routing_contract_does_not_assume_filter_cause(self):
        mutate(self.path,'inject-double-refund');result=self.run_case()
        item=EvidenceStore(self.database).get(result['id'])
        self.assertEqual(prepare(item,{'version':1,'owners':[]})['status'],'HUMAN_TRIAGE')


if __name__=='__main__':unittest.main()
