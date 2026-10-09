import copy
import unittest
from investigator import ticket_findings as findings, process_outcomes
from investigator.onboarding import Conflict
import test_process_debugging as outcome_fixture


class TicketFindingsTests(unittest.TestCase):
    def state(self,classification='CONSISTENT_TO_SOURCE'):
        assessment,observations=outcome_fixture.OutcomeContractTests().valid(classification)
        return {'id':'session','observations':list(observations.values()),
            'synthesis':{'status':'COMPLETED','assessment':assessment,'source_hash':'sealed-state-hash',
                'outputs':{'business_output':{'text':'Retained qualified business explanation.'},
                    'technical_output':{'text':'Retained qualified technical explanation.'}}}}

    def test_all_outcomes_revalidate_against_original_observations(self):
        for outcome in process_outcomes.OUTCOMES:
            with self.subTest(outcome=outcome):
                state=self.state(outcome);before=copy.deepcopy(state)
                result=findings.from_state(state)
                self.assertEqual(result['classification'],outcome)
                self.assertEqual(result['outputs'],state['synthesis']['outputs'])
                self.assertEqual(result['observations'],state['observations'])
                self.assertEqual(state,before)

    def test_missing_evidence_is_not_defaulted_or_projected_away(self):
        state=self.state();state['observations']=[o for o in state['observations'] if o['id']!='flow_consistency']
        with self.assertRaises((ValueError,Conflict)):findings.from_state(state)

    def test_failed_or_absent_synthesis_cannot_be_shared(self):
        for change in ({'status':'FAILED'},{'outputs':None},{'assessment':None}):
            state=self.state();state['synthesis'].update(change)
            with self.subTest(change=change),self.assertRaises(Conflict):findings.from_state(state)

    def test_handoff_retains_scope_limits_and_never_sends(self):
        state=self.state('CONSISTENT_TO_BOUNDARY')
        result=findings.from_state(state)
        package=findings.package(result,'BUSINESS_VALIDATION','configured-business-owner')
        self.assertEqual(package['classification'],'CONSISTENT_TO_BOUNDARY')
        self.assertEqual(package['assessment'],result['assessment'])
        self.assertEqual(package['delivery'],'RECORDED_NOT_SENT')
        with self.assertRaises(Conflict):findings.package(result,'BUSINESS_VALIDATION','')
        technical=findings.from_state(self.state('TRANSFORMATION_LOGIC'))
        with self.assertRaises(Conflict):findings.package(technical,'BUSINESS_VALIDATION','owner')
