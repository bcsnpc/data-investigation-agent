"""An existing scope-explanation verdict has a compatible question disposition."""
import unittest
from investigator.conclusion_contract import validate,fields
from investigator.grounded_answers import finding
from investigator.regression_features import configured
def case_fixture():
 from test_round27_consistency_feedback import ConsistencyFeedbackTests
 return ConsistencyFeedbackTests().fixture()

class ScopeVerdictTests(unittest.TestCase):
 def arguments(self):
  return {'verdict':'different question','verdict_class':'AS DESIGNED','direct_answer':'The two declared selections use different site restrictions.','calculation_explanation':'The retained measure adds units under each selection.','undecided':[],'routing':'ENGINEER'}
 def test_existing_technical_scope_verdict_has_a_valid_question_disposition(self):
  self.assertEqual(validate(self.arguments(),{'intake':{}})['verdict_class'],'AS DESIGNED')
 def test_scope_mapping_is_documented_only_when_enabled(self):
  self.assertIn('different question technical detail',fields()['verdict_class']['description'])
 def test_explicit_target_check_still_rejects_other_visual(self):
  c={'intake':{'visual':'other'},'context':{'explicit_target':{'visual':'named'}}}
  with self.assertRaisesRegex(ValueError,'EXPLICIT_TARGET_CHANGED'):validate(self.arguments(),c)
 def test_different_cited_values_can_explain_two_declared_scopes(self):
  c,a=case_fixture();c['queries'][1]['result']['rows']=[{'quantity':9}]
  c['intake']={'selected_site':1,'comparison_site':2};c['context']['conclusion_contract']='question-first-v1'
  a.update(self.arguments());a.update(numbers=[7,9],cause='The declared site restrictions differ; the native values are7and9.')
  validate(a,c);result=finding(a,c);self.assertIn('different question',result['business'])
  a['verdict']='as designed'
  with self.assertRaisesRegex(ValueError,'compared native values differ'):finding(a,c)
 def test_scope_label_does_not_turn_failed_queries_into_evidence(self):
  c,a=case_fixture();a.update(self.arguments());c['queries'][1].update(status='ERROR',error='native read failed')
  with self.assertRaisesRegex(ValueError,'FAILED_QUERY'):finding(a,c)
