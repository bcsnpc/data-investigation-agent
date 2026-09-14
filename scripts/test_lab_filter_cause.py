from contextlib import closing
from pathlib import Path
import tempfile
import unittest
import duckdb
from defect_lab import initialize,mutate,evidence
from lab_filter_cause import verify
from lab_investigator import investigate
from investigation_evidence_api import EvidenceStore


class CauseTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'lab.duckdb';initialize(self.path)
        self.database=Path(self.temp.name)/'evidence.sqlite'

    def investigate(self,payload=None):
        return investigate(payload or evidence(self.path),self.database,cause_verifier=lambda p,r:verify(self.path,p,r))

    def test_filter_replay_verifies_cause_and_reset_removes_proof(self):
        mutate(self.path,'inject-filter');result=self.investigate()
        self.assertEqual(result['classification'],'TECHNICAL_DEFECT');self.assertTrue(result['root_cause_verified'])
        self.assertFalse(result['automatic_defect_routing'])
        self.assertEqual(result['impact_by_currency']['USD']['downstream_minus_upstream'],'-99.0000')
        self.assertTrue(EvidenceStore(self.database).get(result['id'])['request']['cause_evidence']['filtered_replay_matches'])
        self.assertEqual(mutate(self.path,'reset')['status'],'READY')
        self.assertEqual(self.investigate()['classification'],'UNRESOLVED')

    def test_row_loss_without_build_proof_is_unresolved(self):
        mutate(self.path,'inject');self.assertEqual(self.investigate()['classification'],'UNRESOLVED')

    def test_source_output_and_query_tampering_block_cause(self):
        for sql in ["UPDATE s_fact_order SET captured_amount=200 WHERE order_id='ORD-000001'",
                    "UPDATE g_order_line_summary SET net_cash_amount=54 WHERE order_id='ORD-000002'",
                    "UPDATE gold_build_receipt SET query_text='DROP TABLE s_fact_order'"]:
            with self.subTest(sql=sql):
                path=Path(self.temp.name)/('case'+str(abs(hash(sql)))+'.duckdb');initialize(path);mutate(path,'inject-filter')
                with closing(duckdb.connect(str(path))) as db:db.execute(sql)
                result=investigate(evidence(path),self.database,cause_verifier=lambda p,r:verify(path,p,r))
                self.assertEqual(result['classification'],'UNRESOLVED')

    def test_stale_payload_blocked(self):
        mutate(self.path,'inject-filter');payload=evidence(self.path);payload['rows'][1]['gold_net_cash']='54.0000'
        self.assertEqual(self.investigate(payload)['classification'],'UNRESOLVED')


if __name__=='__main__':unittest.main()
