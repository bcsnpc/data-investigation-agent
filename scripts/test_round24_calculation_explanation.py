import unittest
from unittest.mock import patch
from investigator.grounded_answers import finding
class CalculationTests(unittest.TestCase):
 def setUp(self):
  self.case={'intake':{'issue_type':'HOW_IS_THIS_CALCULATED','compared_with':{'kind':'NOTHING'}},'context':{'path':{'nodes':[]},'layers':{}},'queries':[],'evidence':{},'triage':{'facts':[]}}
  self.args={'verdict':'as designed','cause':'The retained measure sums observed inputs.','numbers':[],'checked':[],'evidence_ids':['e']}
  self.support=[{'content':'SUM(Items[amount])','provenance':'native definition'},{'subject':'model','native_result':{'rows':[{'n':600}]}}]
 def test_definition_question_is_not_refused_for_absent_source_declaration(self):
  with patch('investigator.grounded_answers.cited',return_value=self.support):r=finding(self.args,self.case)
  self.assertIn('does not establish',r['business']);self.assertEqual(r['technical']['verdict'],'as designed')
 def test_source_comparison_still_requires_declared_source_and_reads(self):
  self.case['intake']['compared_with']={'kind':'SOURCE_SYSTEM'}
  with patch('investigator.grounded_answers.cited',return_value=self.support),self.assertRaisesRegex(ValueError,'SOURCE_CONSISTENCY_UNESTABLISHED'):finding(self.args,self.case)
 def test_no_native_recreation_or_current_failed_run_cannot_be_as_designed(self):
  with patch('investigator.grounded_answers.cited',return_value=self.support[:1]),self.assertRaisesRegex(ValueError,'NATIVE_RECREATION'):finding(self.args,self.case)
  self.case['triage']={'facts':[{'check':'JOB_RUNS','state':'OBSERVED','source':'native','value':{'subject':'job','status':'Failed','run_id':'r'}}]}
  with patch('investigator.grounded_answers.cited',return_value=self.support),self.assertRaisesRegex(ValueError,'CURRENT_OPERATIONAL_FAULT'):finding(self.args,self.case)
if __name__=='__main__':unittest.main()
