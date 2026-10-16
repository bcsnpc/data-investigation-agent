import json,tempfile,unittest
from pathlib import Path
from cloud_verification_capture import Capture,replay
from read_budget import Catalog
from investigator.usage_governance import UsageGovernor
from investigator.runtime import fingerprint

PROGRAM='''from read_budget import Catalog
from investigator.usage_governance import UsageGovernor
def perform(b,work,catalog,live):
 runtime=Catalog(catalog,b['state']['environment'])
 g=UsageGovernor(runtime,b['usage_policy'],lambda:172799.0)
 def read():
  if b['state']['inputs']['fail']:raise ValueError('RETAINED_SYNTHETIC_READ_FAILURE')
  return {'count':7}
 return g.metered_read(b['state']['inputs']['session_id'],'one',read)
'''
class CaptureAccountingTests(unittest.TestCase):
 def test_success_and_failure_have_nonzero_owned_accounting_and_exact_replay(self):
  for fail in (False,True):
   with self.subTest(fail=fail),tempfile.TemporaryDirectory() as folder:
    root=Path(folder);source=root/'catalog.sqlite';runtime=Catalog(source,'estate')
    policy={'environment':'estate','daily_limits':{'planner_calls':20,'cloud_calls':2,'input_characters':100000,'output_tokens':30000},'max_inflight_planners':1,'no_progress_limit':2}
    UsageGovernor(runtime,policy,lambda:172799.0)
    program=root/'program.py';program.write_text(PROGRAM)
    c=Capture(root/'capture',inputs={'session_id':'same','fail':fail,'verification_cap':40},config={},policy=policy,
      engine_hash=fingerprint(),program=program,files={},databases={'catalog.sqlite':source},environment='estate',context_identity='fixture')
    final=c.execute();self.assertEqual(final['accounting']['physical_requests'],1)
    self.assertEqual(final['accounting']['pending_reservations'],0)
    self.assertEqual(final['status'],'FAILED' if fail else 'COMPLETED')
    result=replay(root/'capture',root/'replay');self.assertTrue(result['matched'])
    self.assertEqual(result['accounting']['physical_requests'],1)
    self.assertFalse((c.work/'model-catalog.sqlite').exists())
if __name__=='__main__':unittest.main()
