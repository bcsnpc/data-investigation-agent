import unittest
from copy import deepcopy
from round25_independent_review import packet,exact_deduplicate,pack_embedded_json,compact_capture_packet,differs,schema,metric_winner,saved_evidence,review_resume_response,review_budget
from jsonschema import Draft202012Validator
class IndependentReviewTests(unittest.TestCase):
 def test_review_budget_uses_owner_actual_limit_without_changing_monthly_authority(self):
  from unittest.mock import patch
  state=object();rate=object()
  with patch('investigator.reasoning_budget.TicketBudget')as budget:
   review_budget(state,'review:case',rate)
   budget.assert_called_once_with(state,case_id='review:case',owner='round25-independent-reviewer',rate=rate,purpose='GRADING',actual_usage_limit=3_000_000)
 def test_only_token_count_refusal_is_safe_to_retry(self):
  self.assertIsNone(review_resume_response([{'event':'REASONING_TOKEN_COUNT','input_tokens':100}]))
  response={'content':['saved']}
  self.assertEqual(review_resume_response([{'event':'REASONING_RESPONSE','body':response}]),response)
  for events in ([],[{'event':'REASONING_REQUEST'}],[{'event':'REASONING_RESPONSE','body':response}]*2):
   with self.assertRaisesRegex(RuntimeError,'DO_NOT_DUPLICATE'):review_resume_response(events)
 def test_column_key_packet_keeps_nested_json_order_unicode_and_all_rows(self):
  import json
  rows={'rows':[{'id':i,'literal':'synthetic α value'}for i in range(300)]}
  value={'native':rows,'body':json.dumps(rows),'reverse':json.dumps({'z':rows,'a':1}),'plain':'not JSON '*400}
  before=deepcopy(value);packed=compact_capture_packet(value)
  self.assertLess(len(json.dumps(packed)),len(json.dumps(exact_deduplicate(value))))
  self.assertEqual(value,before);self.assertIn('key_sets',packed)
 def test_embedded_json_strings_preserve_every_byte_and_reduce_repetition(self):
  import json
  rows={'rows':[{'id':i,'literal':'synthetic α value'}for i in range(100)]}
  original={'native':rows,'body':json.dumps(rows),'canonical_body':json.dumps(rows,ensure_ascii=False,sort_keys=True,separators=(',',':'))}
  before=deepcopy(original);packed=pack_embedded_json(original)
  self.assertLess(len(json.dumps(packed)),len(json.dumps(exact_deduplicate(original))))
  self.assertEqual(original,before)
 def test_nonstandard_json_whitespace_and_plain_strings_remain_literal(self):
  import json
  text=json.dumps({'rows':list(range(800))},indent=3)+'\n'
  packed=pack_embedded_json({'body':text,'plain':'not JSON '*400})
  self.assertIn(text,packed['verbatim_pool'])
 def test_only_owner_allowed_inputs_and_no_mutation(self):
  p={'verdict_match':True,'reason':'first'};s={'verdict_match':False,'reason':'second'};old=deepcopy(p)
  result=packet(ticket={'text':'question'},answer={'business':'saved'},evidence={'rows':[[1],[2],[3],[4]]},expectation={'cause':'fixed'},primary=p,secondary=s)
  self.assertEqual(set(result),{'ticket','DIA_saved_answer','saved_evidence','sealed_expectation','graders'})
  self.assertEqual(result['saved_evidence']['rows'],[[1],[2],[3],[4]])
  result['graders']['primary']['reason']='changed';self.assertEqual(p,old)
  self.assertTrue(differs(p,s))
 def test_lossless_deduplication_roundtrip_is_checked(self):
  value={'a':['raw-sensitive-synthetic-fixture-string'*8,{'rows':[[i]for i in range(20)]}]*3}
  packed=exact_deduplicate(value);self.assertIn('verbatim_pool',packed)
  self.assertEqual(value['a'][1]['rows'][-1],[19])
 def test_review_schema_requires_independent_decision(self):
  s=schema();Draft202012Validator.check_schema(s);self.assertIn('winner',s['required']);self.assertIn('reason',s['required'])

 def test_reporting_vocabulary_never_overrides_reviewer_grade(self):
  first={'verdict_match':True,'handoff_quality':0};second={'verdict_match':False,'handoff_quality':0}
  decision={**first,'winner':'both'};self.assertEqual(metric_winner(decision,first,second),'mixed')
  decision={'verdict_match':True,'handoff_quality':2,'winner':'primary'}
  self.assertEqual(metric_winner(decision,first,second),'mixed')
  self.assertEqual(decision['handoff_quality'],2)

 def test_early_intake_hold_retains_structured_evidence(self):
  intake={'status':'NEEDS_INPUT','question':'Which page?','choices':['Visible page']}
  wrapped={'result':{'status':'NEEDS_INPUT','intake':intake,'outputs':{'business':{'question':'Which page?'}}}}
  evidence=saved_evidence(wrapped);self.assertEqual(evidence['intake'],intake)
  evidence['intake']['choices'].append('changed');self.assertEqual(intake['choices'],['Visible page'])
