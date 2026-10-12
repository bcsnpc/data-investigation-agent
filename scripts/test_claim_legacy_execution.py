import copy, unittest
from unittest.mock import Mock, patch
import test_claim_investigations as fixture
from investigator.onboarding import Conflict


class ConfirmedLegacyExecutionTests(unittest.TestCase):
    def setUp(self):
        self.h=fixture.ClaimsExecutionTests();self.h.setUp();self.addCleanup(self.h.doCleanups)
        self.catalog=copy.deepcopy(fixture.CAT)
        for v in self.catalog['models'][0]['visuals']:
            v.update(grouping_columns=[],declared_scopes={'quantity':{'state':'COMPLETE','restrictions':[]}})
        p=patch.object(self.h.workspace.claims,'_catalog',return_value=self.catalog);p.start();self.addCleanup(p.stop)
        self.request=self.h.confirmed(direction='DIFFERENT',examples=[],scope={
            'kind':'VISUALS','report_id':'report','page_id':'page','visual_ids':['card']})
        self.calls=[]
        self.h.agent.create=Mock(side_effect=lambda envelope,key:self.created(envelope,key))
        self.h.agent.run_process=Mock(side_effect=lambda identity:self.calls.append(('run',identity)))
        self.h.agent.synthesize=Mock(side_effect=lambda identity:self.calls.append(('synthesize',identity)))
        self.receipts=[{'id':'physical-read','physical_requests':11}]
        self.h.agent.get=Mock(return_value={'id':'legacy','cloud_calls':4,'physical_calls':11,'process_read_receipts':self.receipts})
        self.finding={'session_id':'legacy','classification':'TRANSFORMATION_LOGIC','assessment':{'limits':['Snapshot versions remain unverified.']},
            'observations':[{'id':'quantity-proof'}],'outputs':{
                'business_output':{'explanation':{'text':'The checked totals differ.'}},
                'technical_output':{'explanation':{'text':'The original comparison and operation receipts establish the checked boundary.'}}}}

    def created(self,envelope,key):
        self.calls.append(('create',key));self.envelope=envelope
        return {'id':'legacy'}

    def test_confirmed_visual_uses_normal_create_walk_synthesis_and_original_findings(self):
        with patch('investigator.ticket_findings.from_state',return_value=self.finding) as consumer:
            result=self.h.controller.run(self.request)
        self.assertEqual([c[0]for c in self.calls],['create','run','synthesize'])
        self.assertEqual(result['classification'],'TRANSFORMATION_LOGIC')
        self.assertEqual(result['status'],'COMPLETED')
        self.assertEqual(result['checks']['validated_findings'],self.finding)
        self.assertEqual(result['reads'],{'diagnostic':4,'physical':11,'receipts':self.receipts})
        self.assertEqual(self.envelope['target_visual']['target_id'],'card')
        self.assertEqual(self.envelope['target_visual']['match_basis']['confirmed_claim']['claim_id'],self.request['id'])
        self.assertEqual(self.h.agent.begun,[]);self.assertEqual(self.h.agent.finalized,[])
        self.assertIn('The checked totals differ.',result['outputs']['business_explanation'])
        consumer.assert_called_once()

    def test_validated_refusal_remains_held_not_completed_check(self):
        finding=copy.deepcopy(self.finding);finding.update(classification='HELD',assessment=None)
        with patch('investigator.ticket_findings.from_state',return_value=finding):result=self.h.controller.run(self.request)
        self.assertEqual(result['status'],'HELD');self.assertEqual(result['classification'],'HELD')
        self.assertEqual(result['reads']['physical'],11)

    def test_synthesis_failure_retains_every_read_and_stops_without_claim_finalization(self):
        self.h.agent.synthesize.side_effect=ValueError('Composition rejected')
        result=self.h.controller.run(self.request)
        self.assertEqual(result['status'],'HELD');self.assertEqual(result['reason'],'CLAIM_EXECUTION_FAILED')
        self.assertEqual(result['reads']['diagnostic'],4);self.assertEqual(result['reads']['physical'],11)
        self.assertEqual(result['reads']['receipts'],self.receipts)
        self.assertEqual(self.h.agent.finalized,[])

if __name__=='__main__':unittest.main()
