import unittest
from unittest.mock import Mock
from threading import Barrier
from contextvars import ContextVar
from investigator.ai_investigation import Investigator
from investigator.investigative_queries import Queries
from test_round23_intake_queries import sql_objects
from test_round23_reasoning import MemoryCheckpoint
class ParallelTests(unittest.TestCase):
 def test_independent_requested_layers_overlap_and_keep_guard_context(self):
  barrier=Barrier(2);identity=ContextVar('synthetic_reader',default=None)
  def execute(layer,bound,**kwargs):
   self.assertEqual(identity.get(),'same-reader');barrier.wait(timeout=3);return {'rows':[{'n':7}]}
  layers={name:{'dialect':'T-SQL','objects':sql_objects()}for name in ('a','b')}
  queries=Queries(layers,execute=execute,reserve=Mock(),save=Mock())
  calls=[{'type':'tool_use','id':'read-'+name,'name':'run_sql','input':{'layer':name,'query':'SELECT SUM(quantity) AS n FROM dbo.Items','purpose':'compare'}}for name in layers]
  model=Mock();model.complete.side_effect=[{'content':calls},{'content':[{'type':'tool_use','id':'finish','name':'submit_finding','input':{'verdict':'observed value','cause':'Two native observations.','numbers':[7],'checked':['a','b'],'evidence_ids':['placeholder']}}]}]
  loop=Investigator(queries=queries,model=model,read_tools={},checkpoint=MemoryCheckpoint(),case_id='parallel',context={'intake':{'report':'r'},'path':{'nodes':[]}},triage={'facts':[]},validate_finding=lambda *a:{'business':'Two native observations.'})
  responses=model.complete.side_effect
  def complete(**kwargs):
   if not queries.records:return {'content':calls}
   return {'content':[{'type':'tool_use','id':'finish','name':'submit_finding','input':{'verdict':'observed value','cause':'Two native observations.','numbers':[7],'checked':['a','b'],'evidence_ids':list(loop.state['evidence'])[:1]}}]}
  model.complete.side_effect=complete
  token=identity.set('same-reader')
  try:result=loop.run()
  finally:identity.reset(token)
  self.assertEqual(len(queries.records),2);self.assertTrue(all(r['status']=='SUCCEEDED'for r in queries.records));self.assertEqual(model.complete.call_count,2);self.assertEqual(result['status'],'ANSWERED')
if __name__=='__main__':unittest.main()
