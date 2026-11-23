"""Incidental native differences do not replace the user's primary comparison."""
from copy import deepcopy
import unittest
from investigator.primary_verification import recreation
from investigator.conclusion_contract import validate
from investigator.grounded_answers import finding
from investigator.regression_features import configured

class PrimaryVerificationTests(unittest.TestCase):
 def case(self):
  return {'intake':{'issue_type':'NUMBER_LOOKS_WRONG','compared_with':{'kind':'NOTHING'},
                   'details':{'measure':'m'},'reported_figure':{'state':'NUMBER','value':'12','precision':'EXACT'}},
          'context':{'layers':{'semantic':{'dialect':'DAX','label':'Semantic'}},
                     'path':{'nodes':[{'id':'m','kind':'MEASURE','label':'Units','properties':{'asset_id':'native-measure'}}]},
                     'system_of_record':{'declared':True,'reachable':False}},
          'queries':[{'id':'q','layer':'semantic','asset_ids':['native-measure'],'purpose':'recreate',
                      'status':'SUCCEEDED','time':'2026-01-01T00:00:00Z','result':{'rows':[{'value':12}]}}],
          'evidence':{'def':{'tool':'get_definition','result':{'content':'SUM(Items[units])','provenance':{'source':'STATIC_DEFINITION'}}}},'triage':{}}
 def args(self):
  return {'direct_answer':'The displayed total follows the implemented sum.','verdict_class':'DEVIATION',
          'verdict':'transformation logic','calculation_explanation':'The retained definition sums units.',
          'undecided':[],'routing':'ENGINEER','context_gap':{'type':'other','note':'No comparison was supplied.'},
          'cause':'The retained measure sums units.','numbers':['12'],'checked':['semantic'],'evidence_ids':['q','def']}
 def test_matching_named_measure_cannot_be_replaced_by_incidental_deviation(self):
  c=self.case();c['queries'].append({'id':'other','layer':'upstream','asset_ids':['different-table'],
       'purpose':'compare','status':'SUCCEEDED','result':{'rows':[{'value':9}]}})
  a=self.args();a['evidence_ids'].append('other')
  self.assertEqual(recreation(c,a),'MATCH')
  with self.assertRaisesRegex(ValueError,'PRIMARY_QUESTION_IS_DISPLAY_VERIFICATION'):validate(a,c)
 def test_unrelated_measure_or_uncited_result_does_not_bind_the_target(self):
  for mode in ['other-measure','uncited','truncated','failed','multi-column']:
   c=self.case();a=self.args()
   if mode=='other-measure':c['queries'][0]['asset_ids']=['other-measure']
   if mode=='uncited':a['evidence_ids']=['def']
   if mode=='truncated':c['queries'][0]['truncated']=True
   if mode=='failed':c['queries'][0]['status']='ERROR'
   if mode=='multi-column':c['queries'][0]['result']['rows']=[{'x':12,'y':1}]
   with self.subTest(mode=mode):self.assertEqual(recreation(c,a),'UNESTABLISHED')
 def test_only_saved_native_query_references_can_supply_recreation(self):
  for record in [{'kind':'MODEL_RESPONSE','result':{'id':'q'}},
                 {'tool':'get_evidence','result':{'record':'q'}},
                 {'tool':'row_layer_diff','result':{'query_ids':'q'}}]:
   c=self.case();c['evidence']['wrapper']=record;a=self.args();a['evidence_ids']=['wrapper','def']
   with self.subTest(record=record):self.assertEqual(recreation(c,a),'UNESTABLISHED')
  c=self.case();c['evidence']['wrapper']={'tool':'run_dax','result':{'record':c['queries'][0]}}
  a=self.args();a['evidence_ids']=['wrapper','def'];self.assertEqual(recreation(c,a),'MATCH')
 def test_actual_target_mismatch_or_supplied_comparison_is_not_relabelled(self):
  c=self.case();c['queries'][0]['result']['rows']=[{'value':9}]
  self.assertEqual(recreation(c,self.args()),'DIFFERS');validate(self.args(),c)
  c=self.case();c['intake']['compared_with']={'kind':'SOURCE_SYSTEM','source':'source'}
  validate(self.args(),c)
 def test_definition_without_a_stated_value_does_not_invent_a_reproduced_display(self):
  from investigator.primary_verification import is_display_verification
  c=self.case();c['intake']['issue_type']='HOW_IS_THIS_CALCULATED';c['intake'].pop('reported_figure')
  self.assertFalse(is_display_verification(c,self.args()))
  a=self.args();a.update(verdict='different question',direct_answer='The two retained definitions include different rows.')
  validate(a,c)
  c['intake']['reported_figure']={'state':'NUMBER','value':'12','precision':'EXACT'}
  self.assertTrue(is_display_verification(c,a))
  with self.assertRaisesRegex(ValueError,'PRIMARY_QUESTION_IS_DISPLAY_VERIFICATION'):validate(a,c)
 def test_unresolved_comparison_context_is_not_discarded_as_no_comparison(self):
  from investigator.primary_verification import no_comparison
  c=self.case();c['intake']['comparison_context']={'kind':'EXPECTED_NUMBER'}
  self.assertFalse(no_comparison(c['intake']));validate(self.args(),c)
 def test_valid_native_calculation_can_answer_without_claiming_source_agreement(self):
  c=self.case();a=self.args();a.update(verdict='as designed',verdict_class='AS DESIGNED')
  value=finding(a,c)
  self.assertIn('as designed',value['business'])
  self.assertFalse(c['context']['system_of_record']['reachable'])
 def test_definition_explained_still_needs_definition_evidence(self):
  c=self.case();a=self.args();a.update(verdict='definition explained',verdict_class='AS DESIGNED')
  self.assertIn('definition explained',finding(a,c)['business'])
  a['evidence_ids']=['q']
  with self.assertRaisesRegex(ValueError,'CALCULATION_EXPLANATION_NEEDS_RETAINED_DEFINITION'):finding(a,c)
 def test_definition_uses_a_newer_completed_run_instead_of_superseded_triage_fault(self):
  c=self.case();a=self.args();a.update(verdict='definition explained',verdict_class='AS DESIGNED')
  c['triage']={'facts':[{'check':'JOB_RUNS','source':'native-job-history','state':'OBSERVED',
      'observed_at':'2026-01-01T00:00:00Z','value':{'subject':'job','status':'RUNNING','run_id':'run1'}}]}
  with self.assertRaisesRegex(ValueError,'CURRENT_OPERATIONAL_FAULT'):
   finding(a,c)
  c['evidence']['fresh-job']={'tool':'get_job_runs','result':{'status':'OBSERVED','source':'native-job-history',
      'observed_at':'2026-01-01T00:01:00Z','facts':[{'subject':'job','kind':'JOB_RUN','state':'OBSERVED',
      'value':{'status':'Completed','run_id':'run1'}}]}}
  self.assertIn('definition explained',finding(a,c)['business'])
  c['evidence']['fresh-job']['result']['facts'][0]['value']['status']='Failed'
  with self.assertRaisesRegex(ValueError,'CURRENT_OPERATIONAL_FAULT'):
   finding(a,c)
 def test_calculation_only_keeps_its_answer_and_reports_the_unresolved_job_separately(self):
  c=self.case();c['intake']['issue_type']='HOW_IS_THIS_CALCULATED'
  c['context']['path']['nodes'].append({'id':'job','kind':'PIPELINE','label':'Load orders'})
  c['triage']={'facts':[{'check':'JOB_RUNS','source':'native-job-history','state':'OBSERVED',
      'observed_at':'2026-01-01T00:00:00Z','value':{'subject':'job','status':'RUNNING','run_id':'run1'}}]}
  a=self.args();a.update(verdict='as designed',verdict_class='AS DESIGNED')
  result=finding(a,c)
  self.assertIn('as designed',result['business'])
  self.assertIn('Load orders run run1 is RUNNING',result['business'])
  self.assertIn('does not establish freshness',result['business'])
  # A status/comparison request cannot use this narrow calculation scope.
  c['intake']['compared_with']={'kind':'SOURCE_SYSTEM','source':'source'}
  with self.assertRaisesRegex(ValueError,'CURRENT_OPERATIONAL_FAULT'):
   finding(a,c)
  c['intake']['compared_with']={'kind':'NOTHING'};a['evidence_ids']=['q']
  with self.assertRaisesRegex(ValueError,'RETAINED_DEFINITION'):
   finding(a,c)
 def test_unreproduced_number_keeps_source_consistency_requirement(self):
  c=self.case();c['queries'][0]['result']['rows']=[{'value':9}]
  a=self.args();a.update(verdict='as designed',verdict_class='AS DESIGNED')
  with self.assertRaisesRegex(ValueError,'SOURCE_CONSISTENCY_UNESTABLISHED'):finding(a,c)
 def test_flag_is_independent_and_existing_target_check_stays_on(self):
  with configured({'r27_primary_verification_scope':False}):validate(self.args(),self.case())
  c=self.case();c['context']['explicit_target']={'visual':'named'};c['intake']['visual']='other'
  a=self.args();a.update(verdict='as designed',verdict_class='AS DESIGNED')
  with self.assertRaisesRegex(ValueError,'EXPLICIT_TARGET_CHANGED'):validate(a,c)
 def multi_column_case(self):
  c=self.case();c['context']['layers']['semantic']['objects']=[
   {'id':'table','kind':'SemanticTable','name':'Items'},
   {'id':'native-measure','kind':'Measure','name':'Units','parent_id':'table'},
   {'id':'other-measure','kind':'Measure','name':'Other','parent_id':'table'}]
  q=c['queries'][0];q.update(text='EVALUATE ROW("quantity",[Units],"entries",COUNTROWS(Items))',asset_ids=['native-measure','table'],result={'rows':[{'[quantity]':12,'[entries]':406}]})
  return c
 def test_parsed_measure_projection_survives_extra_diagnostic_columns(self):
  c=self.multi_column_case();self.assertEqual(recreation(c,self.args()),'MATCH')
  with self.assertRaisesRegex(ValueError,'PRIMARY_QUESTION_IS_DISPLAY_VERIFICATION'):validate(self.args(),c)
 def test_other_column_matching_figure_is_never_used_as_selected_measure(self):
  c=self.multi_column_case();c['queries'][0]['result']['rows']=[{'[quantity]':9,'[entries]':12}]
  self.assertEqual(recreation(c,self.args()),'DIFFERS');validate(self.args(),c)
 def test_expression_aliases_and_native_asset_binding_not_value_search(self):
  for text,assets in [
   ('EVALUATE ROW("quantity",[Other],"entries",[Units])',['native-measure','other-measure']),
   ('EVALUATE ROW("quantity",[Units]*2,"entries",COUNTROWS(Items))',['native-measure','table']),
   ('EVALUATE ROW("quantity",[Units],"QUANTITY",COUNTROWS(Items))',['native-measure','table']),
   ('EVALUATE CALCULATETABLE(ROW("quantity",[Units],"entries",COUNTROWS(Items)))',['native-measure','table'])]:
   c=self.multi_column_case();c['queries'][0].update(text=text,asset_ids=assets)
   # In the first case the native Units projection is entries=406, not quantity=12.
   expected='DIFFERS' if '[Other]' in text else 'UNESTABLISHED'
   with self.subTest(text=text):self.assertEqual(recreation(c,self.args()),expected)
 def test_missing_or_ambiguous_result_alias_does_not_bind(self):
  for row in [{'[not_quantity]':12,'[entries]':406},{'quantity':12,'[quantity]':12,'[entries]':406}]:
   c=self.multi_column_case();c['queries'][0]['result']['rows']=[row]
   with self.subTest(row=row):self.assertEqual(recreation(c,self.args()),'UNESTABLISHED')

if __name__=='__main__':unittest.main()
