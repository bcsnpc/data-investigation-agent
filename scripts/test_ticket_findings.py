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

    def test_delivery_rejects_coverage_overclaim_even_when_outcome_is_valid(self):
        from investigator import question_account
        state=self.state('TRANSFORMATION_LOGIC')
        state['envelope']={'symptom':'What does this adjustment mean, and should it count?','question_kind':{'kind':'BUSINESS_MEANING'}}
        state['assessment']=state['synthesis']['assessment']
        state['synthesis']['outputs']={key:{'explanation':{'text':'The retained operation repeats matching entries.'}}
            for key in ('business_output','technical_output')}
        question_account.attach(state['synthesis']['outputs'],state)
        result=findings.from_state(state)
        self.assertEqual(result['classification'],'TRANSFORMATION_LOGIC')
        self.assertEqual(result['outputs']['business_output']['question_account']['status'],'NOT_ANSWERED')
        for key in ('business_output','technical_output'):
            changed=copy.deepcopy(state)
            changed['synthesis']['outputs'][key]['question_account']['status']='PARTLY_ANSWERED'
            with self.assertRaisesRegex(Conflict,'question/answer account'):findings.from_state(changed)
        changed=copy.deepcopy(state)
        for entry in changed['synthesis']['outputs'].values():entry.pop('question_account')
        with self.assertRaisesRegex(Conflict,'question/answer account'):findings.from_state(changed)

    def test_failed_or_absent_synthesis_cannot_be_shared(self):
        for change in ({'status':'FAILED'},{'outputs':None},{'assessment':None}):
            state=self.state();state['synthesis'].update(change)
            with self.subTest(change=change),self.assertRaises(Conflict):findings.from_state(state)

    def test_registered_refusal_can_be_shared_without_manufacturing_assessment(self):
        from investigator.process_receipts import refusal
        from investigator.refusal_synthesis import render
        state={'id':'session','envelope':{'symptom':'Why does the number differ?'},'observations':[]}
        # The producer's receipt validator owns the failure shape; use the
        # registered boundary refusal for this delivery-contract regression.
        state['observations']=[refusal('UNIMPLEMENTED_ROUTE','This route is not implemented.','refused')]
        outputs=render(state)
        state['synthesis']={'status':'COMPLETED','validation':'REGISTERED_REFUSAL_DELIVERY','assessment':None,'outputs':outputs}
        result=findings.from_state(state)
        self.assertEqual(result['classification'],'HELD');self.assertIsNone(result['assessment'])
        self.assertEqual(result['outputs'],outputs)
        from investigator.smart_intake import SmartIntake
        ticket={'state':'FINDINGS_SHARED','findings':result,'history':[]}
        retained=SmartIntake._handoff(None,ticket,'TECH_HANDOFF')
        self.assertEqual(retained['state'],'FINDINGS_SHARED')
        self.assertEqual(retained['history'][-1]['detail']['handoff_unavailable'],
                         'REGISTERED_REFUSAL_NO_TECHNICAL_FINDING')
        state['synthesis']['outputs']['refusal']['text']='A different blocker.'
        with self.assertRaises(Conflict):findings.from_state(state)

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
