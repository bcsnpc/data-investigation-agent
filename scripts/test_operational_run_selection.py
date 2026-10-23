import copy,unittest
from investigator.operational_run_selection import from_text,select
from investigator.evidence_verdicts import explicit_operational_fact
from investigator.adapters.runtime_facts_microsoft import producer_time

class ExplicitRunTests(unittest.TestCase):
 def fact(self):
  old={'run_id':'old','start':'2026-10-20T01:02:03.1234567Z','end':'2026-10-20T01:03:00Z','status':'FAILED'}
  new={'run_id':'new','start':'2026-10-21T01:02:03Z','end':'2026-10-21T01:03:00Z','status':'SUCCEEDED'}
  return {'id':'original-fact-hash','subject':'job','kind':'JOB_RUN','state':'OBSERVED','freshness':'CURRENT','observed_at':'2026-10-23T00:00:00Z','collected_at':'2026-10-23T00:00:00Z','value':{**new,'recent_runs':[new,old]}}
 def test_named_historical_run_is_selected_instead_of_latest_and_original_remains_exact(self):
  text='Did pipeline Example complete the run on 2026-10-20 at 01:02:03 UTC?';selector=from_text(text);original=self.fact();before=copy.deepcopy(original)
  result=explicit_operational_fact({'kind':'FACT','subject':'job','question':'RUN_STATUS','source':{'start':0,'end':len(text),'quote':text},'run_selector':selector},[{'kind':'FACT','value':original}],'2026-10-23T01:00:00Z',text)
  self.assertEqual(result['value']['run_id'],'old');self.assertEqual(result['value']['status'],'FAILED');self.assertEqual(original,before);self.assertNotIn('id',result);self.assertEqual(result['selection']['source_fact_id'],'original-fact-hash');self.assertEqual(result['selection']['timestamp_fraction_digits'],0)
 def test_missing_named_run_refuses_without_substituting_latest(self):
  text='Did the pipeline run on 2026-10-19T01:02:03Z fail?'
  with self.assertRaisesRegex(ValueError,'NOT_IN_RETAINED_HISTORY'):select(from_text(text),[self.fact()],text)
 def test_same_second_two_runs_are_ambiguous_at_stated_precision(self):
  text='Did pipeline Example run at 2026-10-20T01:02:03Z fail?';fact=self.fact();fact['value']['recent_runs'].append({'run_id':'other','start':'2026-10-20T01:02:03.9Z','status':'SUCCEEDED'})
  with self.assertRaisesRegex(ValueError,'AMBIGUOUS_AT_STATED_PRECISION'):select(from_text(text),[fact],text)
 def test_finer_reference_does_not_gain_an_invented_tolerance(self):
  text='Did pipeline Example run at 2026-10-20T01:02:03.1234567Z fail?';fact=self.fact();self.assertEqual(select(from_text(text),[fact],text)['value']['run_id'],'old');fact['value']['recent_runs'][1]['start']='2026-10-20T01:02:03.123456Z'
  with self.assertRaisesRegex(ValueError,'PRECISION_UNAVAILABLE'):select(from_text(text),[fact],text)
 def test_selector_cannot_change_quoted_time_or_choose_between_distinct_references(self):
  text='Did pipeline Example run at 2026-10-20T01:02:03Z fail?';selector=from_text(text);selector['at']='2026-10-21T01:02:03Z'
  with self.assertRaisesRegex(ValueError,'DIFFERS_FROM_QUOTE'):select(selector,[self.fact()],text)
  with self.assertRaisesRegex(ValueError,'REFERENCE_AMBIGUOUS'):from_text(text+' Compare 2026-10-21T01:02:03Z.')
 def test_no_selector_for_explicit_time_must_not_return_latest(self):
  text='Did pipeline Example run at 2026-10-20T01:02:03Z fail?'
  with self.assertRaisesRegex(ValueError,'NO_LATEST_SUBSTITUTION'):explicit_operational_fact({'kind':'FACT','subject':'job','question':'RUN_STATUS','source':{'start':0,'end':len(text),'quote':text}},[{'kind':'FACT','value':self.fact()}],'2026-10-23T01:00:00Z',text)
 def test_missing_zone_or_precision_and_duplicate_reference_provenance(self):
  with self.assertRaisesRegex(ValueError,'PRECISION_OR_ZONE'):from_text('Did the job on 2026-10-20 fail?')
  text='Did the job at 2026-10-20T01:02:03Z fail? Same run 2026-10-20T01:02:03Z.';selector=from_text(text);self.assertEqual(text[selector['source']['start']:selector['source']['end']],selector['source']['quote'])
 def test_native_producer_retains_seventh_digit_for_exact_run_identity(self):
  self.assertEqual(producer_time('2026-10-20T01:02:03.1234567',utc_declared=True),'2026-10-20T01:02:03.1234567Z')
  self.assertEqual(producer_time('2026-10-20T02:02:03.1234567+01:00'),'2026-10-20T01:02:03.1234567Z')
  with self.assertRaisesRegex(ValueError,'PRECISION_UNSUPPORTED'):producer_time('2026-10-20T01:02:03.1234567890Z')

if __name__=='__main__':unittest.main()
