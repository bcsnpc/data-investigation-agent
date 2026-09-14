from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from defect_lab import initialize,mutate,evidence
from lab_investigator import investigate
from investigation_evidence_api import EvidenceStore


class ExpectedTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'lab.duckdb';initialize(self.path)
        self.database=Path(self.temp.name)/'evidence.sqlite'
        self.payload,self.context=evidence(self.path,True)

    def run_case(self,context=None,payload=None):return investigate(payload or self.payload,self.database,self.context if context is None else context)

    def test_verified_refunds_classify_and_persist_exact_business_evidence(self):
        result=self.run_case();self.assertEqual(result['classification'],'EXPECTED_BEHAVIOR')
        totals=result['business_verification']['by_currency']['USD']
        self.assertEqual((totals['captured'],totals['refunded'],totals['net_cash']),('253.0000','99.0000','154.0000'))
        self.assertFalse(result['automatic_defect_routing'])
        self.assertIn('business_context',EvidenceStore(self.database).get(result['id'])['request'])

    def test_omission_never_becomes_expected(self):
        mutate(self.path,'inject');payload,context=evidence(self.path,True)
        self.assertEqual(self.run_case(context,payload)['classification'],'UNRESOLVED')

    def test_missing_and_different_scope_block_classification(self):
        for mode in ('missing','different','arithmetic','excess_refund','question'):
            context=deepcopy(self.context)
            if mode=='missing':context['records'].pop()
            if mode=='different':context['records'][0]['currency']='EUR'
            if mode=='arithmetic':context['records'][0]['captured_amount']='200'
            if mode=='excess_refund':context['records'][0]['refunded_amount']='999'
            if mode=='question':context['question']='why_revenue_fell_this_month'
            with self.subTest(mode=mode):self.assertEqual(self.run_case(context)['classification'],'UNRESOLVED')

    def test_duplicate_or_invalid_driver_rejected(self):
        context=deepcopy(self.context);context['records'].append(context['records'][0])
        with self.assertRaises(ValueError):self.run_case(context)
        for value in ('NaN',True,-1,'0.00001'):
            context=deepcopy(self.context);context['records'][0]['refunded_amount']=value
            with self.subTest(value=value),self.assertRaises(ValueError):self.run_case(context)

    def test_matching_without_business_context_remains_unresolved(self):
        self.assertEqual(investigate(self.payload,self.database)['classification'],'UNRESOLVED')


if __name__=='__main__':unittest.main()
