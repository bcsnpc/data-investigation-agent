from copy import deepcopy
from unittest.mock import Mock
import unittest
from investigator.delivery_evaluator import CHECKS,INSTRUCTIONS,evaluate,payload
from test_round23_reasoning import tool


class DeliveryEvaluatorTests(unittest.TestCase):
    def test_soft_presentation_issue_is_not_a_hard_evidence_failure(self):
        checks={k:{'passed':k!='claims','reason':'Citation label format only; native q1 supports the statement.',
                   'severity':'soft'} for k in CHECKS}
        model=Mock();model.complete.return_value=tool('evaluate_delivery',checks)
        result=evaluate(model,{})
        self.assertEqual(result['hard_failures'],[])
        self.assertEqual(result['soft_failures'],['claims'])
        self.assertEqual(result['rejection_level'],'soft')

    def test_wrong_question_target_and_unsupported_claim_remain_hard(self):
        for failure in ('question','target','support','claims'):
            checks={k:{'passed':k!=failure,'reason':'Substantive evidence mismatch.', 'severity':'hard'} for k in CHECKS}
            model=Mock();model.complete.return_value=tool('evaluate_delivery',checks)
            result=evaluate(model,{})
            self.assertEqual(result['hard_failures'],[failure])

    def test_wrong_question_and_explicit_target_cannot_be_labelled_soft(self):
        for failure in ('question','target'):
            checks={k:{'passed':k!=failure,'reason':'Explicit target overridden.', 'severity':'soft'} for k in CHECKS}
            model=Mock();model.complete.return_value=tool('evaluate_delivery',checks)
            self.assertEqual(evaluate(model,{})['hard_failures'],[failure])

    def test_aws_disabled_before_dispatch_without_changing_keys(self):
        from investigator.provider_budget import check_credit
        from investigator.model_spend import SpendHold
        with self.assertRaisesRegex(SpendHold,'PROVIDER_DISABLED_BY_OWNER:bedrock'):
            check_credit('bedrock',1795219200,owner='round27-grading',purpose='GRADING')

    def test_evaluator_truncation_is_format_failure_not_four_false_claims(self):
        model=Mock();model.complete.return_value={'content':[],'stop_reason':'max_tokens'}
        result=evaluate(model,{})
        self.assertEqual(result['hard_failures'],[])
        self.assertEqual(result['rejection_level'],'soft')

    def test_only_ticket_draft_and_cited_native_records_are_sent(self):
        case={'messages':['private reasoning'], 'context':{'hidden':'uncited catalog'},
              'queries':[{'id':'q1','result':{'rows':[{'value':7}]}}, {'id':'q2','result':'uncited'}],
              'evidence':{'e1':{'tool':'check_target_candidates','result':{'observations':[{'evidence_id':'q1'}]}},
                          'model':{'kind':'MODEL_RESPONSE','response':'private reasoning'}}}
        packet=payload({'description':'Why seven?'},{'direct_answer':'Seven because ...','evidence_ids':['e1']},case)
        self.assertEqual(set(packet),{'ticket','draft','cited_evidence'})
        self.assertEqual(set(packet['cited_evidence']),{'q1','e1'})
        self.assertNotIn('private reasoning',str(packet))
        with self.assertRaisesRegex(ValueError,'NATIVE_EVIDENCE'):
            payload({}, {'evidence_ids':['model']},case)

    def test_each_failed_check_refuses_confident_delivery_with_specific_reason(self):
        for failed in CHECKS:
            with self.subTest(check=failed):
                checks={k:{'passed':k!=failed,'reason':'Wrong target: explicit Card was replaced.' if k==failed else 'Supported.'} for k in CHECKS}
                model=Mock();model.complete.return_value={**tool('evaluate_delivery',checks),'cost_microdollars':1900,'usage':{'input_tokens':100}}
                result=evaluate(model,{'ticket':{},'draft':{},'cited_evidence':{}})
                self.assertFalse(result['approved']);self.assertEqual(result['checks'],checks)
                self.assertEqual(result['cost_microdollars'],1900)

    def test_harmful_patterns_explicitly_in_evaluator_prompt(self):
        self.assertIn('Silver/Gold',INSTRUCTIONS)
        self.assertIn('sum-versus-count',INSTRUCTIONS)
        self.assertIn('overridden explicit target',INSTRUCTIONS)

    def test_malformed_evaluator_is_a_recordable_rejection_not_approval(self):
        model=Mock();model.complete.return_value={'content':[{'type':'text','text':'looks fine'}],'usage':{'input_tokens':8}}
        result=evaluate(model,{})
        self.assertFalse(result['approved']);self.assertEqual(result['usage'],{'input_tokens':8})

    def test_truncated_evaluator_names_missing_check_without_false_claim_diagnosis(self):
        checks={k:{'passed':True,'reason':'Supported.'}for k in CHECKS if k!='claims'}
        model=Mock();model.complete.return_value={**tool('evaluate_delivery',checks),'stop_reason':'max_tokens'}
        result=evaluate(model,{})
        self.assertFalse(result['approved'])
        self.assertEqual(result['format_error']['missing_checks'],['claims'])
        self.assertEqual(result['format_error']['stop_reason'],'max_tokens')
        self.assertIn('output-token limit',result['checks']['claims']['reason'])
        self.assertEqual(model.complete.call_args.kwargs['max_tokens'],3200)

    def test_approval_needs_all_four_checks(self):
        model=Mock();model.complete.return_value=tool('evaluate_delivery',{k:{'passed':True,'reason':'Supported by q1.'} for k in CHECKS})
        self.assertTrue(evaluate(model,{})['approved'])

    def test_native_fastpath_rejection_retains_fact_but_removes_confident_answer(self):
        from investigator.delivery_evaluator import evaluate_native
        model=Mock();model.complete.return_value=tool('evaluate_delivery',{k:{'passed':k!='question',
            'reason':'The named run is a different run.' if k=='question' else 'Native fact supported.'} for k in CHECKS})
        fact={'id':'f1','subject':'load','value':{'status':'FAILED','run_id':'native-run-123'}}
        result=evaluate_native(model,{'text':'Which run failed?'},{'status':'ANSWERED','business':'Confident wrong run answer.',
            'technical':{'verdict':'failed job','operational_fact':fact},'model_calls':0})
        self.assertEqual(result['status'],'UNRESOLVED')
        self.assertNotIn('Confident wrong run answer',result['business'])
        self.assertEqual(result['technical']['operational_fact'],fact)
        self.assertEqual(result['model_calls'],1)
        self.assertEqual(result['conclusion']['verdict_class'],'UNRESOLVED')


if __name__=='__main__':unittest.main()
