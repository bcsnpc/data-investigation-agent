"""Owner question-only blocking profile; native code guards remain independent."""
from copy import deepcopy
from unittest import TestCase,main
from unittest.mock import Mock
from types import SimpleNamespace
from investigator.delivery_evaluator import CHECKS,evaluate,evaluate_native
from investigator.ai_investigation import Investigator
from investigator.regression_features import configured
from test_round23_reasoning import tool

def checks(*failed):
 return {k:{'passed':k not in failed,'reason':'The answer addresses a different question.' if k=='question' else 'Unsupported or incomplete detail.',
  'severity':'hard','failure_kind':'wrong_question' if k=='question' else 'unsupported_claim'} for k in CHECKS}

def loop(result):
 v=object.__new__(Investigator);v.state={'model_calls':0};v.context={'intake':{'text':'Why is this card8765?'}}
 v.case_view=Mock(return_value={'queries':[],'evidence':{}});v.save=Mock();v.clock=Mock(return_value=0)
 v.model_seconds=0;v.evidence=Mock();v.repair_delivery=Mock(side_effect=AssertionError('Advisory checks must not force rewrites'))
 v.evaluator_model=Mock();v.evaluator_model.complete.return_value=tool('evaluate_delivery',result)
 return v

def native_outcome():
 return {'status':'ANSWERED','business':'Original delivered native answer.', 'model_calls':0,
  'technical':{'verdict':'failed job','operational_fact':{'id':'f1','subject':'load','value':{'status':'FAILED','run_id':'native-run-123'}}}}

def repaired():
 return {'direct_answer':'The named run is native-run-123. Its recorded status is FAILED.',
  'verdict_class':'DEVIATION','calculation_explanation':'Native status only; no quantity calculation.',
  'undecided':[],'routing':'ENGINEER','context_gap':{'type':'other','note':'No missing status fact.'}}

class SlimEvaluatorTests(TestCase):
 def test_raw_all_checks_preserved_but_only_question_blocks(self):
  raw=checks(*CHECKS);model=Mock();model.complete.return_value=tool('evaluate_delivery',raw)
  with configured({'r27_slim_evaluator':True,'r27_evaluator_advisory':True}):review=evaluate(model,{})
  self.assertEqual(review['checks'],raw);self.assertFalse(review['approved']);self.assertTrue(review['would_reject'])
  self.assertEqual(review['blocking_failures'],['question']);self.assertEqual(review['advisory_failures'],['support','target','claims'])
  self.assertIn('question-only blocking',model.complete.call_args.kwargs['system'])
 def test_nonquestion_failures_deliver_without_rewrite_or_downgrade(self):
  for failed in ('support','target','claims'):
   with self.subTest(check=failed),configured({'r27_slim_evaluator':True,'r27_evaluator_advisory':False}):
    v=loop(checks(failed));review=v.evaluate_draft({'evidence_ids':[]})
    self.assertFalse(review['approved']);self.assertEqual(review['blocking_failures'],[]);self.assertTrue(review['delivered_with_warning'])
    self.assertNotIn('outcome',v.state);v.repair_delivery.assert_not_called();self.assertEqual(v.state['model_calls'],1)
 def test_wrong_question_two_retries_then_safe_handoff_even_with_advisory_flag(self):
  v=loop(checks('question','claims'))
  with configured({'r27_slim_evaluator':True,'r27_evaluator_advisory':True}):
   for _ in range(2):
    with self.assertRaisesRegex(ValueError,'DELIVERY_EVALUATOR_REJECTED: question:'):v.evaluate_draft({'evidence_ids':[]})
   self.assertIsNone(v.evaluate_draft({'evidence_ids':[]}))
   with self.assertRaisesRegex(ValueError,'RETRIES_EXHAUSTED'):v.evaluate_draft({'evidence_ids':[]})
  self.assertEqual(v.state['outcome']['status'],'UNRESOLVED');self.assertIn('AFTER_TWO_RETRIES',v.state['outcome']['stop'])
  self.assertEqual(v.evaluator_model.complete.call_count,3);self.assertEqual([x['retry'] for x in v.state['delivery_evaluations']],[0,1,2])
 def test_corrected_question_passes_while_unsupported_claim_stays_advisory(self):
  v=loop(checks('question'));v.evaluator_model.complete.side_effect=[tool('evaluate_delivery',checks('question')),tool('evaluate_delivery',checks('claims'))]
  with configured({'r27_slim_evaluator':True}):
   with self.assertRaises(ValueError):v.evaluate_draft({'evidence_ids':[]})
   review=v.evaluate_draft({'evidence_ids':[]})
  self.assertEqual(review['blocking_failures'],[]);self.assertTrue(review['delivered_with_warning']);self.assertNotIn('outcome',v.state)
 def test_incomplete_evaluator_is_not_a_semantic_wrong_question(self):
  v=loop(checks());v.evaluator_model.complete.return_value={'content':[],'stop_reason':'max_tokens'}
  with configured({'r27_slim_evaluator':True}):review=v.evaluate_draft({'evidence_ids':[]})
  self.assertIsNotNone(review['format_error']);self.assertEqual(review['blocking_failures'],[]);self.assertNotIn('outcome',v.state)
 def test_native_advisory_support_failure_preserves_answer_and_fact(self):
  original=native_outcome();model=Mock();model.complete.return_value=tool('evaluate_delivery',checks('support','claims'))
  with configured({'r27_slim_evaluator':True,'r27_evaluator_advisory':False}):out=evaluate_native(model,{'text':'Which run failed?'},original)
  self.assertEqual(out['status'],'ANSWERED');self.assertEqual(out['technical']['operational_fact'],original['technical']['operational_fact'])
  self.assertEqual(model.complete.call_count,1);self.assertFalse(out['delivery_evaluation']['approved'])
 def test_native_wrong_question_rewrites_twice_then_downgrades(self):
  original=native_outcome();model=Mock();model.complete.side_effect=[tool('evaluate_delivery',checks('question')),tool('repair_delivery',repaired()),tool('evaluate_delivery',checks('question')),tool('repair_delivery',repaired()),tool('evaluate_delivery',checks('question'))]
  with configured({'r27_slim_evaluator':True}):out=evaluate_native(model,{'text':'Which run failed?'},original)
  self.assertEqual(model.complete.call_count,5);self.assertEqual(out['status'],'UNRESOLVED')
  self.assertNotIn('Original delivered native answer',out['business']);self.assertEqual(out['technical']['operational_fact'],original['technical']['operational_fact'])
  self.assertEqual(len(out['delivery_evaluations']),3);self.assertEqual([x['kind'] for x in out['delivery_repairs']],['question','question'])
 def test_native_corrected_exact_answer_can_deliver_with_other_checks_failed(self):
  model=Mock();model.complete.side_effect=[tool('evaluate_delivery',checks('question')),tool('repair_delivery',repaired()),tool('evaluate_delivery',checks('claims','support'))]
  with configured({'r27_slim_evaluator':True}):out=evaluate_native(model,{'text':'Which run failed?'},native_outcome())
  self.assertEqual(out['status'],'ANSWERED');self.assertEqual(model.complete.call_count,3)
  self.assertIn('native-run-123',out['business']);self.assertEqual(out['delivery_evaluation']['blocking_failures'],[])
 def test_slim_never_bypasses_native_reference_and_unique_target_code_checks(self):
  v=object.__new__(Investigator);v.refresh_tools=lambda:None;v.schemas={'submit_finding':Mock()}
  v.context={'candidate_inventory':{}};v.queries=SimpleNamespace(records=[]);v.state={'evidence':{}}
  v.evaluate_draft=Mock(side_effect=AssertionError('Code checks must precede evaluator'))
  with configured({'r27_slim_evaluator':True}):
   with self.assertRaisesRegex(ValueError,'UNKNOWN_EVIDENCE_REFERENCE'):v.dispatch('submit_finding',{'evidence_ids':['invented']})
   v.context['candidate_inventory']={'candidates':[{'id':'one'},{'id':'two'}]}
   v.state['evidence']={'check':{'tool':'check_target_candidates','result':{'selected':'one'}}}
   with self.assertRaisesRegex(ValueError,'TARGET_NOT_A_UNIQUE_OBSERVED_MATCH'):v.dispatch('submit_finding',{'evidence_ids':[],'selected_target':'two'})
  v.evaluate_draft.assert_not_called()
 def test_slim_flag_off_preserves_full_hard_rejection(self):
  v=loop(checks('claims'))
  with configured({'r27_slim_evaluator':False,'r27_evaluator_advisory':False}):
   with self.assertRaisesRegex(ValueError,'DELIVERY_EVALUATOR_REJECTED'):v.evaluate_draft({'evidence_ids':[]})

if __name__=='__main__':main()
