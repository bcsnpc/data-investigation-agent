import base64,copy,json,runpy,sqlite3,sys,tempfile,unittest
from pathlib import Path
from contextlib import closing
from types import SimpleNamespace
sys.path.insert(0,str(Path.cwd()/'scripts'))
H=runpy.run_path(str(Path(__file__).with_name('code_verifier_capture.py')))
class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.work=Path(self.tmp.name)
  with closing(sqlite3.connect(self.work/'catalog.sqlite')) as db,db:
   db.execute('CREATE TABLE adaptive_usage(environment,session_id,kind,reserved,status)')
   db.executemany('INSERT INTO adaptive_usage VALUES(?,?,?,?,?)',[('fixture','own','cloud',json.dumps({'cloud_calls':2}),'SETTLED'),('fixture','own:prewarm-controls','cloud',json.dumps({'cloud_calls':1}),'SETTLED'),('fixture','other','cloud',json.dumps({'cloud_calls':500}),'SETTLED')])
  self.b={'usage_policy':{'daily_limits':{'cloud_calls':10}},'state':{'environment':'fixture','profile_member':None,'native_path_identities':{},'inputs':{'session_id':'own','verification_cap':3}}}
 def event(self,count,cap=3):
  return {'kind':'BOUNDED_REQUEST','body':base64.b64encode(json.dumps({'name':'binding_verification_admission','request':{'count':count,'cap':cap,'decision':'ADMITTED'}}).encode()).decode()}
 def test_owned_counts_and_controls_separate_from_unrelated_usage(self):
  tape=SimpleNamespace(events=[self.event(2)],replaying=False)
  f=H['finalize'](self.b,self.work,{},None,'COMPLETED',tape)
  self.assertEqual(f['accounting']['physical_requests'],3);self.assertEqual(f['accounting']['control_requests'],1);self.assertEqual(f['accounting']['verification_physical_requests'],2);self.assertEqual(f['accounting']['verification_reads'],2);self.assertEqual(f['accounting']['diagnostic_reads'],0)
 def test_probe_and_physical_allowance_excess_refused(self):
  with self.assertRaisesRegex(ValueError,'PROBE_CAP_DIFFERS'):H['finalize'](self.b,self.work,{},None,'COMPLETED',SimpleNamespace(events=[self.event(4)],replaying=False))
  self.b['usage_policy']['daily_limits']['cloud_calls']=2
  with self.assertRaisesRegex(ValueError,'PHYSICAL_ALLOWANCE_EXCEEDED'):H['finalize'](self.b,self.work,{},None,'COMPLETED',SimpleNamespace(events=[],replaying=False))
 def test_owned_model_usage_never_hidden_under_zero_model_claim(self):
  with closing(sqlite3.connect(self.work/'catalog.sqlite')) as db,db:db.execute("INSERT INTO adaptive_usage VALUES('fixture','own','planner','{}','SETTLED')")
  with self.assertRaisesRegex(ValueError,'OWNED_NONREAD_USAGE'):H['accounting'](self.b,self.work)
if __name__=='__main__':unittest.main()
