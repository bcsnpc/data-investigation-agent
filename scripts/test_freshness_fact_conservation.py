import copy,unittest
from investigator import question_account as account
class FreshnessFactConservationTests(unittest.TestCase):
 def test_identical_attempt_facts_render_once_with_all_receipts_preserved(self):
  checks={'job_history':{'status':'CURRENT','accounting_observed':False},'source_delivery':{'status':'UNAVAILABLE','reason':'No declared mapping reaches this source.'}}
  state={'envelope':{'symptom':'Inspect freshness.','question_kind':{'kind':'FRESHNESS'}},'assessment':{'classification':'TRANSFORMATION_LOGIC','technical_output':{}},'observations':[{'id':i,'status':'COMPLETED','check_kind':'FRESHNESS_ATTEMPT','freshness_attempt':{'checks':copy.deepcopy(checks)}} for i in ('one','two')]}
  before=copy.deepcopy(state);result=account.build(state);text=account.render(result)
  self.assertEqual(text.count('Processing history was read'),1);self.assertEqual(text.count('No declared mapping reaches this source.'),1)
  self.assertEqual(result['subjects'][0]['evidence_ids'],['one','two']);self.assertEqual(state,before)
 def test_distinct_refusals_are_not_collapsed(self):
  state={'envelope':{'symptom':'Inspect freshness.','question_kind':{'kind':'FRESHNESS'}},'assessment':{'classification':'TRANSFORMATION_LOGIC','technical_output':{}},'observations':[{'id':i,'status':'COMPLETED','check_kind':'FRESHNESS_ATTEMPT','freshness_attempt':{'checks':{'job_history':{'status':'UNAVAILABLE','reason':reason},'source_delivery':{'status':'UNAVAILABLE','reason':'No mapping.'}}}} for i,reason in [('one','First load absent.'),('two','Second load absent.')]]}
  text=account.render(account.build(state));self.assertIn('First load absent.',text);self.assertIn('Second load absent.',text)
if __name__=='__main__':unittest.main()
