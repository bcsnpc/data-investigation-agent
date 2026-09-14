from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from defect_lab import initialize,mutate,evidence,filter_query
from lab_filter_cause import verify
from lab_investigator import investigate
from investigation_evidence_api import EvidenceStore
from routing_drafts import prepare,save,digest
from routing_review import RoutingReview
from routing_delivery_rehearsal import DeliveryRehearsal
from ticket_workflow import TicketStore,Conflict


class ArithmeticRoutingTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);folder=Path(self.temp.name)
        path=folder/'lab.duckdb';initialize(path);mutate(path,'inject-double-refund')
        run=investigate(evidence(path),folder/'evidence.sqlite',cause_verifier=lambda p,r:verify(path,p,r))
        self.item=EvidenceStore(folder/'evidence.sqlite').get(run['id'])
        self.policy={'version':1,'owners':[{'kind':'lab_record_reconciliation','upstream':'silver','downstream':'gold','team':'Fixture Data Team'}]}
        self.store=TicketStore(folder/'workflow.sqlite')

    def test_owned_arithmetic_prepares_idempotently_with_exact_impact(self):
        record=save(self.store,self.item,self.policy)
        self.assertEqual(record['status'],'DRAFT_REQUIRES_REVIEW');self.assertEqual(record,save(self.store,self.item,self.policy))
        self.assertIn('subtracts refund amount twice',record['draft']['title'])
        self.assertEqual(record['draft']['impact_by_currency']['USD']['downstream_minus_upstream'],'-99.0000')
        self.assertFalse(record['automatic_delivery'])

    def test_mixed_query_flags_and_classification_rejected_even_with_rehashed_payload(self):
        for field in ('query','flag','classification','cause'):
            item=deepcopy(self.item);cause=item['request']['cause_evidence']
            if field=='query':cause['query_text']=filter_query()
            elif field=='flag':cause['faulty_replay_matches']=False
            elif field=='classification':cause['classification']='REFRESH_FRESHNESS'
            else:cause['cause']='Unknown cause';item['result']['root_cause']='Unknown cause'
            item['request']['evidence_hash']=digest({k:item['request'].get(k) for k in ('lab_evidence','business_context','cause_evidence')})
            self.assertEqual(prepare(item,self.policy)['status'],'HUMAN_TRIAGE')

    def test_changed_impact_cannot_route(self):
        item=deepcopy(self.item);item['result']['impact_by_currency']['USD']['downstream_minus_upstream']='-1.0000'
        self.assertEqual(prepare(item,self.policy)['status'],'HUMAN_TRIAGE')

    def test_approval_and_rehearsal_revalidate_arithmetic_evidence(self):
        record=save(self.store,self.item,self.policy)
        review=RoutingReview(self.store,SimpleNamespace(get=lambda _:self.item),lambda:self.policy)
        review.approve(record['id'],review.detail(record['id'])['draft_hash'])
        rehearsal=DeliveryRehearsal(review);rehearsal.enqueue(record['id'])
        rehearsal.advance(record['id']);self.assertTrue(rehearsal.advance(record['id'])['complete'])
        self.item['request']['cause_evidence']['corrected_replay_reconciles']=False
        with self.assertRaises(Conflict):rehearsal.advance(record['id'])


if __name__=='__main__':unittest.main()
