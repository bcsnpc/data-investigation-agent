import copy,unittest
from unittest.mock import Mock
from investigator.operational_intake import admit,response
from investigator.estate_graph_api import GraphAPI
import test_ledger_investigator as fixtures

class RawOperationalTests(unittest.TestCase):
 def catalog(self,*nodes):return {'estate':'fixture','as_of':None,'candidates':list(nodes)or[{'id':'job','kind':'PIPELINE','label':'Primary copy'}]}
 def test_raw_named_run_reaches_real_consumer_without_manually_supplied_target_or_latest_substitution(self):
  old={'run_id':'old','start':'2026-10-20T01:02:03.1234567Z','end':'2026-10-20T01:03:00Z','status':'FAILED'};new={'run_id':'new','start':'2026-10-21T01:02:03Z','end':'2026-10-21T01:03:00Z','status':'SUCCEEDED'}
  raw={'id':'raw','text':'Need the status of pipeline Primary copy, run started 2026-10-20 at 01:02:03 UTC. Did it fail?'};before=copy.deepcopy(raw);result=admit(raw,self.catalog());self.assertEqual(raw,before);self.assertEqual(result['status'],'READY')
  engine,_,reader,decision=fixtures.OperationalFactTests().status_engine([fixtures.fact('job','JOB_RUN',{**new,'recent_runs':[new,old]})]);answer=engine.run(result['ticket'])
  self.assertEqual(answer['verdict'],'failed job');self.assertEqual(answer['support']['operational_fact']['value']['run_id'],'old');reader.assert_not_called();decision.assert_not_called()
  for text in answer['outputs'].values():self.assertIn('whole-second precision',text);self.assertIn('not selected as the latest run',text)
 def test_ambiguous_names_ask_one_question_using_names_not_ids(self):
  c=self.catalog({'id':'internal-a','kind':'PIPELINE','label':'Copy north'},{'id':'internal-b','kind':'PIPELINE','label':'Copy south'})
  result=admit({'text':'Did Copy north or Copy south pipeline fail?'},c);out=response({'text':'original'},result)
  self.assertEqual(result['status'],'CLARIFYING');self.assertEqual(len(result['questions']),1)
  for name in('Copy north','Copy south'):self.assertIn(name,out['outputs']['business'])
  self.assertNotIn('internal-',out['outputs']['business'])
 def test_longer_exact_name_is_not_mistaken_for_its_contained_prefix(self):
  c=self.catalog({'id':'short','kind':'PIPELINE','label':'Copy work'},{'id':'long','kind':'PIPELINE','label':'Copy work continuation'})
  result=admit({'text':'Did pipeline Copy work continuation fail?'},c);self.assertEqual(result['ticket']['request']['subject'],'long')
 def test_supplied_visual_without_request_is_not_ignored_and_quantities_do_not_get_a_default_job(self):
  self.assertEqual(admit({'visual':'wrong','text':'Did pipeline Primary copy fail?'},self.catalog())['status'],'HELD')
  result=admit({'text':'Why is the report total higher?'},self.catalog());self.assertEqual(result['reason'],'RAW_CALCULATION_ADMISSION_NOT_INSTALLED');self.assertNotIn('ticket',result)
 def test_operational_guess_does_not_replace_a_calculation_filter_or_business_primary_ask(self):
  for text in('Why is the report total higher? Maybe pipeline Primary copy failed.', 'Which filter hides rows? Maybe pipeline Primary copy failed.'):
   result=admit({'text':text},self.catalog());self.assertEqual(result['status'],'HELD');self.assertNotIn('ticket',result)
  result=admit({'text':'Please decide the business rule for including failed runs of pipeline Primary copy.'},self.catalog());self.assertEqual(result['reason'],'BUSINESS_INTENT_REQUIRES_OWNER')
 def test_precise_missing_target_time_never_turns_into_latest(self):
  result=admit({'text':'Did pipeline Primary copy run on 2026-10-20 fail?'},self.catalog());self.assertEqual(result['status'],'CLARIFYING');self.assertIn('PRECISION',result['reason']);self.assertEqual(len(result['questions']),1)
 def test_candidate_projection_uses_only_explicit_graph_allowlist_and_refuses_truncation(self):
  repo=Mock();gateway=Mock();gateway.graph_objects.side_effect=lambda estate,ids,identity:list(ids)
  repo.records.return_value={'nodes':[{'id':'job','kind':'PIPELINE','label':'Primary copy'},{'id':'outside','kind':'PIPELINE','label':'Unadmitted'}],'edges':[],'truncated':False}
  graph=GraphAPI(repo,gateway,identity='reader',estate='fixture',allowed_objects=['job']);self.assertEqual([n['id']for n in graph.intake_candidates()['candidates']],['job']);repo.records.assert_called_once_with('fixture',at=None,identities={'job'},limit=1000)
  repo.records.return_value['truncated']=True
  with self.assertRaisesRegex(ValueError,'TRUNCATED'):graph.intake_candidates()

if __name__=='__main__':unittest.main()
