from contextlib import closing
from decimal import Decimal
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import duckdb
from defect_lab import ROOT,initialize,validate,mutate,evidence


class LabTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'lab.duckdb';initialize(self.path)

    def test_inject_impact_and_reset_against_separate_truth(self):
        truth=json.loads((ROOT/'infra/lab/evaluation_expected.json').read_text())
        before=evidence(self.path)
        self.assertEqual(sum(r['gold_net_cash'] for r in before['rows']),Decimal(truth['baseline_usd_net_cash']))
        self.assertEqual(mutate(self.path,'inject')['changed_tables'],['g_order_line_summary'])
        after=evidence(self.path)
        self.assertEqual(sum(r['gold_net_cash'] or 0 for r in after['rows']),Decimal(truth['injected_usd_net_cash']))
        self.assertEqual([r['order_id'] for r in after['rows'] if r['gold_net_cash'] is None],truth['affected_orders'])
        self.assertEqual(sum(r['silver_net_cash']-(r['gold_net_cash'] or 0) for r in after['rows']),Decimal(truth['understatement']))
        self.assertEqual(mutate(self.path,'reset')['status'],'READY')
        self.assertEqual(evidence(self.path),before)
        self.assertEqual(mutate(self.path,'reset')['status'],'READY')

    def test_no_overwrite_or_stacked_injection(self):
        with self.assertRaises(ValueError):initialize(self.path)
        mutate(self.path,'inject')
        with self.assertRaises(ValueError):mutate(self.path,'inject')
        self.assertEqual(validate(self.path)['status'],'NOT_READY')

    def test_source_drift_blocks_reset_and_is_preserved(self):
        with closing(duckdb.connect(str(self.path))) as db:db.execute("UPDATE s_fact_order SET captured_amount=999 WHERE order_id='ORD-000001'")
        with self.assertRaises(ValueError):mutate(self.path,'reset')
        self.assertIn('s_fact_order',validate(self.path)['changed_tables'])

    def test_transform_drift_blocks_reset(self):
        with patch('defect_lab.query',return_value='SELECT 1'):
            with self.assertRaises(ValueError):mutate(self.path,'reset')
            self.assertTrue(validate(self.path)['transformation_changed'])

    def test_failed_reset_rolls_back(self):
        mutate(self.path,'inject');before=evidence(self.path)
        from defect_lab import inspect
        calls=[]
        def reject(db):
            calls.append(1)
            return inspect(db) if len(calls)==1 else {'status':'NOT_READY'}
        with patch('defect_lab.inspect',side_effect=reject),self.assertRaises(ValueError):mutate(self.path,'reset')
        self.assertEqual(evidence(self.path),before)

    def test_evidence_excludes_evaluation_and_control(self):
        mutate(self.path,'inject');result=evidence(self.path)
        self.assertEqual(set(result),{'mode','rows'})
        self.assertNotIn('scenario',json.dumps(result,default=str))
        self.assertNotIn('expected',json.dumps(result,default=str))


if __name__=='__main__':unittest.main()
