"""Saved evidence must get a delivery opportunity within the existing15 actions."""
import unittest
from test_round23_reasoning import LoopTests, tool

class ClosingActionTests(unittest.TestCase):
 def make(self,bad=False):
  helper=LoopTests();loop=helper.assemble([])
  query={'layer':'gold','query':'SELECT SUM(quantity) AS total FROM dbo.Items','purpose':'recreate'}
  def response(**kw):
   call=helper.model.complete.call_count
   if call==1:return tool('run_sql',query)
   q=loop.queries.records[0]['id']
   if call<=14:return tool('get_evidence',{'id':q},str(call))
   if call==15 and not bad:return tool('run_sql',{**query,'query':'SELECT COUNT(*) AS rows FROM dbo.Items'},'no-new-read')
   return tool('submit_finding',{'verdict':'observed value','cause':'The checked value is7.','numbers':[7],'checked':['gold'],'evidence_ids':['unknown']if bad else[q]},'delivery')
  helper.model.complete.side_effect=response
  return helper,loop
 def test_last_slot_delivers_and_never_dispatches_a_fifteenth_investigation_read(self):
  h,loop=self.make();out=loop.run()
  self.assertEqual(out['status'],'ANSWERED');self.assertEqual(out['tools_used'],15);self.assertEqual(out['model_calls'],16)
  h.execute.assert_called_once();self.assertEqual(len(loop.queries.records),1)
  self.assertIn('FINAL_ACTION_RESERVED_FOR_VALIDATED_DELIVERY',str(h.checkpoint.value['messages']))
  self.assertEqual(len({c.kwargs['system']for c in h.model.complete.call_args_list}),1)
 def test_final_action_still_requires_the_normal_evidence_validator(self):
  h,loop=self.make(bad=True);out=loop.run()
  self.assertEqual(out['status'],'UNRESOLVED');self.assertEqual(out['tools_used'],15);h.validator.assert_not_called()
  self.assertIn('UNKNOWN_EVIDENCE_REFERENCE',str(h.checkpoint.value['messages']))
 def test_no_synthetic_conclusion_or_extra_action_when_no_successful_read(self):
  h=LoopTests();loop=h.assemble([tool('run_sql',{'layer':'gold','query':'DELETE FROM dbo.Items','purpose':'recreate'})]);loop.tool_limit=1
  self.assertEqual(loop.run()['status'],'UNRESOLVED');h.execute.assert_not_called();h.validator.assert_not_called()

class PhysicalReadClosureTests(unittest.TestCase):
 def test_ticket_physical_cap_closes_reads_but_preserves_validated_delivery(self):
  from investigator.usage_governance import UsageHold
  h=LoopTests();loop=h.assemble([]);query={'layer':'gold','query':'SELECT SUM(quantity) AS total FROM dbo.Items','purpose':'recreate'}
  h.execute.side_effect=[{'columns':['total'],'rows':[[7]]},UsageHold('GUIDED_PHYSICAL_CAP_REACHED')]
  def response(**kw):
   n=h.model.complete.call_count
   if n==1:return tool('run_sql',query)
   if n==2:return tool('run_sql',{**query,'query':'SELECT COUNT(*) AS n FROM dbo.Items'},'cap')
   if n==3:return tool('run_sql',{**query,'query':'SELECT MAX(quantity) AS n FROM dbo.Items'},'must-not-dispatch')
   return tool('submit_finding',{'verdict':'observed value','cause':'The checked value is7.','numbers':[7],'checked':['gold'],'evidence_ids':[loop.queries.records[0]['id']]},'delivery')
  h.model.complete.side_effect=response;out=loop.run()
  self.assertEqual(out['status'],'ANSWERED');self.assertEqual(h.execute.call_count,2)
  self.assertTrue(h.checkpoint.value['physical_reads_closed'])
  self.assertIn('PHYSICAL_READS_CLOSED_USE_SAVED_EVIDENCE',str(h.checkpoint.value['messages']))
 def test_other_budget_or_safety_stops_still_block(self):
  from investigator.usage_governance import UsageHold
  from investigator.live_gateway import GatewayDenied
  for error in (UsageHold('MONTHLY_PHYSICAL_INVESTIGATION_EXHAUSTED'),GatewayDenied('READ_ONLY_REQUIRED')):
   h=LoopTests();loop=h.assemble([tool('run_sql',{'layer':'gold','query':'SELECT SUM(quantity) AS total FROM dbo.Items','purpose':'recreate'})]);h.execute.side_effect=error
   self.assertEqual(loop.run()['status'],'BLOCKED');self.assertEqual(h.model.complete.call_count,1)

if __name__=='__main__':unittest.main()
