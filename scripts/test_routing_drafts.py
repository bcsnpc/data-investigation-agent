from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from defect_lab import initialize,mutate,evidence
from investigation_evidence_api import EvidenceStore
from lab_investigator import investigate
from lab_filter_cause import verify
from routing_drafts import prepare,save
from ticket_workflow import TicketStore


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        path=Path(self.temp.name)/'lab.duckdb';initialize(path);mutate(path,'inject-filter')
        database=Path(self.temp.name)/'evidence.sqlite'
        result=investigate(evidence(path),database,cause_verifier=lambda p,r:verify(path,p,r))
        self.item=EvidenceStore(database).get(result['id'])
        self.policy={'version':1,'owners':[{'kind':'lab_record_reconciliation','upstream':'silver','downstream':'gold','team':'Fixture Data Team'}]}

    def test_owned_verified_draft_is_bound_idempotent_and_not_sent(self):
        store=TicketStore(Path(self.temp.name)/'workflow.sqlite')
        first=save(store,self.item,self.policy);self.assertEqual(first,save(store,self.item,self.policy))
        self.assertEqual(first['status'],'DRAFT_REQUIRES_REVIEW');self.assertFalse(first['automatic_delivery'])
        self.assertEqual(first['draft']['impact_by_currency']['USD']['downstream_minus_upstream'],'-99.0000')
        changed=deepcopy(self.policy);changed['owners'][0]['team']='Another Fixture Team'
        self.assertNotEqual(save(store,self.item,changed)['id'],first['id'])

    def test_missing_owner_and_ambiguous_owner(self):
        self.assertEqual(prepare(self.item,{'version':1,'owners':[]})['status'],'NEEDS_OWNER')
        self.policy['owners']*=2
        with self.assertRaises(ValueError):prepare(self.item,self.policy)

    def test_other_classifications_never_prepare_bug(self):
        for classification in ('EXPECTED_BEHAVIOR','REFRESH_FRESHNESS','UNRESOLVED','BUSINESS_REVIEW_REQUIRED','SOURCE_OR_DATA_ISSUE'):
            item=deepcopy(self.item);item['classification']=classification
            item['result']['classification']=classification
            result=prepare(item,self.policy)
            self.assertEqual(result['status'],'NO_BUG' if classification=='EXPECTED_BEHAVIOR' else 'HUMAN_TRIAGE')
            self.assertNotIn('draft',result)

    def test_changed_cause_or_impact_is_held(self):
        for field in ('cause','impact','evidence'):
            item=deepcopy(self.item)
            if field=='cause':item['result']['root_cause']='Invented'
            elif field=='impact':item['result']['impact_by_currency']['USD']['gold_total']='1'
            else:item['request']['lab_evidence']['rows'][0]['silver_net_cash']='100'
            self.assertEqual(prepare(item,self.policy)['status'],'HUMAN_TRIAGE')


if __name__=='__main__':unittest.main()
