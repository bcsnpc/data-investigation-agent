import unittest
from unittest.mock import Mock
from investigator.ai_investigation import Investigator,schema
from investigator.investigative_queries import Queries
from investigator.estate_graph_contract import digest
from test_round23_reasoning import MemoryCheckpoint,tool
from test_round23_intake_queries import sql_objects

class OperationalAnswer(unittest.TestCase):
 def test_native_job_answer_needs_no_value_queries_and_keeps_exact_run_details(self):
  at='2026-10-28T00:00:00Z';fact={'subject':'job','kind':'JOB_RUN','state':'OBSERVED','observed_at':at,'value':{'run_id':'native-run-1','status':'FAILED','start':at,'end':'2026-10-28T00:01:00Z','error':'Native controlled failure'}}
  read=Mock(return_value={'source':'native-history','status':'OBSERVED','observed_at':at,'facts':[fact]});execute=Mock();q=Queries({'x':{'dialect':'T-SQL','objects':sql_objects()}},execute=execute,reserve=Mock(),save=Mock())
  triage={'facts':[{'check':'JOB_RUNS','source':'facts-ledger','state':'OBSERVED','observed_at':at,'value':[fact]}]}
  context={'intake':{'report':'r','issue_type':'DATA_LOOKS_OLD','details':{'record':'Example producer'}},'path':{'nodes':[{'id':'job','kind':'PIPELINE','label':'Example producer'}]},'layers':{'x':{'label':'An admitted data layer'}}}
  model=Mock();engine=Investigator(queries=q,model=model,read_tools={'get_job_runs':{'description':'Read native runs','schema':schema({'node':{'enum':['job']}}),'run':lambda a:read(a['node'])}},checkpoint=MemoryCheckpoint(),case_id='case',context=context,triage=triage)
  def answer(**kwargs):
   evidence=engine.state['cache'][digest(['get_job_runs',{'node':'job'}])]['evidence_id']
   return tool('submit_finding',{'verdict':'failed job','cause':'The named producer run failed with its recorded native error. Numerical impact was not compared.','numbers':[],'checked':[],'evidence_ids':[evidence]})
  model.complete.side_effect=answer;result=engine.run();self.assertEqual(result['status'],'ANSWERED');self.assertEqual(result['model_calls'],1)
  for text in ('Example producer','native-run-1',at,'2026-10-28T00:01:00Z','Native controlled failure'):self.assertIn(text,result['business'])
  execute.assert_not_called();read.assert_called_once_with('job');self.assertEqual(result['case']['queries'],[])
if __name__=='__main__':unittest.main()
