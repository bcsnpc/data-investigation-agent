"""Causal coverage regression, synthetic records only; no model/data calls."""
import importlib.util,sys,unittest
from pathlib import Path
sys.path.insert(0,'scripts')
import test_question_account as fixtures
from investigator import question_account as account

class CausalCoverageTests(unittest.TestCase):
 def state(self,text):
  state=fixtures.QuestionAccountTests().state(text)
  state['envelope']['question_kind']={'kind':'FIGURE_DIFFERENCE','source':{'quote':text,'start':0,'end':len(text)}}
  state['assessment']['classification']='CONSISTENT_TO_BOUNDARY'
  state['observations']=[{'id':'equal','status':'COMPLETED','comparison_status':'CROSS_SURFACE_VERIFIED'}]
  return state
 def test_discrepancy_kind_cannot_replace_requested_explanation_with_equality(self):
  state=self.state("Quantity seems overstated. Investigate the card's current value, upstream data and transformation definitions to identify a supported explanation.")
  result=account.build(state);self.assertEqual(result['status'],'NOT_ANSWERED');self.assertEqual([s['subject'] for s in result['subjects']],['mechanism'])
  self.assertIn('agreement does not establish the requested mechanism',result['subjects'][0]['reason'])
 def test_compound_explicit_comparison_remains_separately_partial(self):
  state=self.state('Compare Quantity with the application, and identify a supported explanation.')
  result=account.build(state);self.assertEqual(result['status'],'PARTLY_ANSWERED');self.assertEqual([x['status'] for x in result['subjects']],['PARTLY_ANSWERED','NOT_ANSWERED'])
 def test_supported_transformation_can_cover_required_mechanism(self):
  state=self.state('Find the cause of the Quantity discrepancy.')
  state['assessment']['classification']='TRANSFORMATION_LOGIC';state['observations'].append({'id':'mechanism','status':'COMPLETED','process_roles':['mechanism','transformation_definition']})
  self.assertEqual(account.build(state)['status'],'PARTLY_ANSWERED')
 def test_unadorned_comparison_does_not_acquire_a_mechanism_obligation(self):
  result=account.build(self.state('Compare Quantity with the application.'))
  self.assertEqual(result['status'],'PARTLY_ANSWERED');self.assertEqual(result['subjects'][0]['subject'],'comparison')
 def test_business_primary_is_not_replaced_by_explanation_guard(self):
  state=self.state('Find an explanation: should void entries count?')
  self.assertEqual(account.build(state)['status'],'NOT_ANSWERED')
 def test_currency_obligation_survives_required_mechanism(self):
  state=self.state('Is Quantity current? Identify a supported explanation of the discrepancy.')
  state['envelope']['question_kind']['kind']='FRESHNESS'
  result=account.build(state)
  self.assertEqual([s['subject'] for s in result['subjects']],['currency','mechanism'])
  self.assertEqual([s['status'] for s in result['subjects']],['NOT_ANSWERED','NOT_ANSWERED'])
 def test_definitions_obligation_survives_required_mechanism(self):
  state=self.state('Inspect the components of Quantity and identify a supported explanation of the discrepancy.')
  state['envelope']['question_kind']['kind']='METRIC_COMPONENTS'
  state['observations'].append({'id':'definition','status':'COMPLETED','process_roles':['transformation_definition']})
  result=account.build(state)
  self.assertEqual([s['subject'] for s in result['subjects']],['definitions','mechanism'])
  self.assertEqual([s['status'] for s in result['subjects']],['PARTLY_ANSWERED','NOT_ANSWERED'])
 def test_delivery_obligation_survives_required_mechanism(self):
  state=self.state('Check delivery of Quantity and identify a supported explanation of the discrepancy.')
  state['envelope']['question_kind']['kind']='SOURCE_CORRECTNESS'
  result=account.build(state)
  self.assertEqual([s['subject'] for s in result['subjects']],['delivery','mechanism'])
 def test_typed_mechanism_obligation_not_duplicated(self):
  state=self.state('Identify a supported explanation of the discrepancy.')
  state['envelope']['question_kind']['kind']='TRANSFORMATION_MECHANISM'
  result=account.build(state)
  self.assertEqual([s['subject'] for s in result['subjects']],['mechanism'])
 def test_parenthesized_business_obligation_remains_named(self):
  state=self.state('Identify a supported explanation of Quantity (should void entries count?).')
  result=account.build(state)
  self.assertIn('meaning',[s['subject'] for s in result['subjects']])
if __name__=='__main__':unittest.main()
