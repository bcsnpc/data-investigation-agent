from contextlib import closing
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
import duckdb
from defect_lab import initialize,mutate,evidence
from lab_investigator import reconcile,investigate
from investigation_evidence_api import EvidenceStore


class ImpactTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'lab.duckdb';initialize(self.path)

    def test_injected_impact_persists_without_ground_truth(self):
        mutate(self.path,'inject');database=Path(self.temp.name)/'evidence.sqlite'
        result=investigate(evidence(self.path),database)
        self.assertEqual(result['impact_by_currency']['USD']['downstream_minus_upstream'],'-99.0000')
        self.assertEqual(result['affected_records'][0]['order_id'],'ORD-000001')
        self.assertFalse(result['root_cause_verified']);self.assertFalse(result['automatic_defect_routing'])
        saved=EvidenceStore(database).get(result['id']);self.assertEqual(saved['result'],result)
        self.assertEqual(saved['request']['lab_evidence']['rows'][0]['gold_present'],False)
        mutate(self.path,'reset');self.assertEqual(reconcile(evidence(self.path))['comparison_status'],'MATCH')

    def test_extra_gold_key_is_not_lost_by_projection(self):
        with closing(duckdb.connect(str(self.path))) as db:
            db.execute("UPDATE g_order_line_summary SET order_id='ORD-999999' WHERE order_id='ORD-000002'")
        result=reconcile(evidence(self.path))
        self.assertEqual({r['status'] for r in result['affected_records']},{'MISSING_IN_GOLD','EXTRA_IN_GOLD'})
        self.assertEqual(result['impact_by_currency']['USD']['downstream_minus_upstream'],'0.0000')
        self.assertEqual(result['comparison_status'],'MISMATCH')

    def test_currencies_are_separate_and_zero_missing_is_detected(self):
        payload=evidence(self.path);row=payload['rows'][2]
        row.update(currency='EUR',gold_present=False,gold_net_cash=None)
        result=reconcile(payload)
        self.assertEqual(result['impact_by_currency']['EUR']['affected_records'],1)
        self.assertEqual(result['affected_records'][0]['status'],'MISSING_IN_GOLD')
        self.assertEqual(len(result['impact_by_currency']),2)

    def test_invalid_and_duplicate_evidence_rejected(self):
        baseline=evidence(self.path)
        duplicate=deepcopy(baseline);duplicate['rows'].append(duplicate['rows'][0])
        with self.assertRaises(ValueError):reconcile(duplicate)
        for value in (None,True,0.1,'NaN','1.00001'):
            payload=deepcopy(baseline);payload['rows'][0]['gold_net_cash']=value
            with self.subTest(value=value),self.assertRaises(ValueError):reconcile(payload)

    def test_changed_amount_is_exact_and_matching_is_not_expected_behavior(self):
        payload=evidence(self.path);payload['rows'][0]['gold_net_cash']='98.9900'
        result=reconcile(payload)
        self.assertEqual(result['affected_records'][0]['status'],'VALUE_MISMATCH')
        self.assertEqual(result['impact_by_currency']['USD']['downstream_minus_upstream'],'-0.0100')
        self.assertEqual(reconcile(evidence(self.path))['classification'],'UNRESOLVED')


if __name__=='__main__':unittest.main()
