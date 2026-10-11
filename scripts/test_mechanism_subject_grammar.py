"""Regression: synthetic extraction, no provider or estate calls."""
import importlib.util,sys,unittest
from pathlib import Path
sys.path.insert(0,'scripts')
from test_intake_extraction import fixture
from investigator.ticket_clarification import settings
from investigator import ticket_route as route

class MechanismAskTests(unittest.TestCase):
 def test_noun_and_verb_mechanism_asks_preserve_the_declared_subject(self):
  for phrase in ('identify a supported explanation','explain','seek explanations','explaining'):
   text="In Report, Quantity seems overstated. Investigate the Value card's current value and transformation definitions to "+phrase+'.'
   raw,payload=fixture(text,kind='TRANSFORMATION_MECHANISM')
   result=route.settlement(raw,payload['text'],settings(),code_gate=True)
   self.assertEqual(result['route'],'DECLARED_SUBJECT');self.assertEqual(result['kind'],'TRANSFORMATION_MECHANISM')
   self.assertEqual(result['source']['quote'],raw['primary'])
 def test_nomination_alone_does_not_manufacture_mechanism_ask(self):
  raw,payload=fixture('In Report, Quantity is 16.',kind='TRANSFORMATION_MECHANISM')
  self.assertIsNone(route.settlement(raw,payload['text'],settings(),code_gate=True))
 def test_explanation_does_not_erase_explicit_external_comparator(self):
  for extra in ('against another report','versus yesterday','against the application'):
   raw,payload=fixture('In Report, seek an explanation of Quantity '+extra+'.',kind='TRANSFORMATION_MECHANISM')
   self.assertIsNone(route.settlement(raw,payload['text'],settings(),code_gate=True))
 def test_explanation_does_not_route_business_rule_decision(self):
  raw,payload=fixture('In Report, explain whether Quantity should include void entries.',kind='BUSINESS_MEANING')
  self.assertIsNone(route.settlement(raw,payload['text'],settings(),code_gate=True))
 def test_confirmed_comparison_policy_is_not_overridden(self):
  raw,payload=fixture('In Report, identify a supported explanation of Quantity.',kind='TRANSFORMATION_MECHANISM')
  self.assertIsNone(route.settlement(raw,payload['text'],{**settings(),'must_confirm':['COMPARISON']},code_gate=True))
if __name__=='__main__':unittest.main()
