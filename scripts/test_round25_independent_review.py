import unittest
from copy import deepcopy
from round25_independent_review import packet,exact_deduplicate,differs,schema,metric_winner,saved_evidence
from jsonschema import Draft202012Validator
class IndependentReviewTests(unittest.TestCase):
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
