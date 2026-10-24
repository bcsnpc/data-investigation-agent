import unittest
from investigator.investigator_case import CaseFile


class CaseTests(unittest.TestCase):
    def test_model_view_omits_correlation_label_but_durable_case_preserves_it(self):
        case=CaseFile({'id':'expected-latency-experiment','text':'Where is the record?'})
        self.assertNotIn('ticket_id',case.model_view())
        self.assertEqual(case.snapshot()['ticket_id'],'expected-latency-experiment')
        self.assertEqual(CaseFile.loads(case.dumps()).snapshot()['ticket_id'],'expected-latency-experiment')

    def test_round_trip_preserves_every_code_owned_field(self):
        case = CaseFile({'id': 'ticket-1', 'text': 'Did the load fail?'})
        case.advance('quick_facts')
        case.evidence([{'id': 'e1', 'kind': 'FACT', 'observation': {'status': 'FAILED'}}])
        self.assertTrue(case.propose({'note': 'Check the failed load.', 'evidence_ids': ['e1']}))
        case.observe({'event': 'INVESTIGATOR_CALL_BLOCKED', 'tool': 'last_run', 'arguments': {'job': 'j'}})
        case.observe({'event': 'INVESTIGATOR_REJECTED', 'reason': 'EVIDENCE_MISSING'})
        case.finish({'verdict': 'failed job', 'status': 'answered', 'stop_reason': 'EVIDENCE_PROVEN'})
        self.assertEqual(CaseFile.loads(case.dumps()).snapshot(), case.snapshot())

    def test_model_cannot_rewrite_step_evidence_or_outcome_and_rejection_is_logged(self):
        case = CaseFile({'id': 'ticket-1'})
        for proposal in ({'current_step': 'deliver'}, {'final_outcome': {'verdict': 'as designed'}},
                         {'note': 'Invent support.', 'evidence_ids': ['not-obtained']}):
            self.assertFalse(case.propose(proposal))
        value = case.snapshot()
        self.assertEqual(value['current_step'], 'recreate')
        self.assertIsNone(value['final_outcome'])
        self.assertEqual(len(value['errors']), 3)


class RecitationTests(unittest.TestCase):
    def test_matching_recitation_is_silent_mismatch_is_logged_and_cannot_advance(self):
        case=CaseFile({'id':'ticket-1'})
        self.assertIsNone(case.recite({'plan':case.snapshot()['plan'],'current_step':'recreate'}))
        self.assertEqual(case.snapshot()['errors'],[])
        event=case.recite({'plan':['invented'],'current_step':'deliver'})
        self.assertEqual(event['reason'],'CODE_CASE_FILE_WINS')
        self.assertEqual(case.snapshot()['current_step'],'recreate')
        self.assertEqual(case.snapshot()['errors'],[event])

if __name__ == '__main__':
    unittest.main()
