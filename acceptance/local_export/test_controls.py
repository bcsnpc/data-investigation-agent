import unittest,sys,pathlib,json,types
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path.cwd()/'scripts'))
from sql_compile import select,decode
from guarded_controls import full_export_transport,ControlReader,capped_governor_type
class Controls(unittest.TestCase):
 def test_lossless_binary_and_date_compile(self):
  cols=[{'name':'rv','logical_type':'BINARY'},{'name':'d','logical_type':'DATETIME'},{'name':'n','logical_type':'DECIMAL'}];r=select('dbo','table',cols,fabric=True)
  self.assertIn('CONVERT(varchar(max),[rv],2)',r['query']);self.assertIn('CONVERT(varchar(40),[d],127)',r['query']);self.assertNotIn('__surface_identity',r['query']);self.assertEqual(decode('00AF','BINARY'),b'\x00\xaf');self.assertEqual(str(decode('12.3400','DECIMAL')),'12.3400')
 def test_money_float_exact_serialization(self):
  r=select('dbo','t',[{'name':'m','logical_type':'DECIMAL','native_type':'money'},{'name':'f','logical_type':'REAL','native_type':'float'}],fabric=False)
  self.assertIn('CONVERT(varchar(100),[m],2)',r['query']);self.assertIn('CONVERT(varchar(100),[f],3)',r['query'])
 def test_guarded_worker_request(self):
  cfg={'sql':{'server':'fake','database':'fake','auth':{'credential_file':'name-only'}}};request=select('app','a',[{'name':'id','logical_type':'INTEGER'}],fabric=False)
  calls=[]
  def run(cmd,**kw):calls.append((cmd,json.loads(kw['input'])));return types.SimpleNamespace(returncode=0,stdout=json.dumps({'rows':[],'read_only_verified':True}))
  with patch('investigator.physical_reads.run',run):v=full_export_transport(cfg,{'surface':'AZURE_SQL'},request)
  self.assertTrue(v['read_only_verified']);self.assertTrue(calls[0][1]['require_read_only']);self.assertEqual(calls[0][1]['max_rows'],10000);self.assertTrue(calls[0][0][-1].endswith('Read-ExportSource.ps1'))
 def test_original_investigation_bound_untouched(self):
  v=json.loads((pathlib.Path.cwd()/'infra/scripts/WorkerResponseBounds.json').read_text());self.assertEqual(v['SOURCE_SQL']['maximum_rows'],251);self.assertEqual(v['FABRIC_SQL']['maximum_rows'],251)
  for n in ['Read-ExportSource.ps1','Read-ExportFabric.ps1']:
   s=(pathlib.Path(__file__).parent/n).read_text();self.assertIn('maximum_rows = 10000',s);self.assertIn('16777216',s);self.assertIn('sql_database_permissions',s);self.assertIn('sql_object_permissions',s)
 def test_projected_transport_refused_before_send(self):
  class G:
   def metered_read(self,*a):raise AssertionError('no admission')
  c=ControlReader(G(),{'_estate':{'recording':{'tape_class':'PRIVACY_PROJECTED'}}},'fake',physical_cap=32)
  with self.assertRaisesRegex(ValueError,'NOT_WIRED'):c.read_sql({'surface':'AZURE_SQL','query':'SELECT 1'})
 def test_owner_stop_prevents_new_logical_or_physical_admission(self):
  class G:
   def metered_read(self,*a):raise AssertionError('no admission')
  c=ControlReader(G(),{},'fake',physical_cap=32,should_stop=lambda:True)
  with self.assertRaisesRegex(RuntimeError,'EXPORT_OWNER_STOP'):c.read_sql({'surface':'AZURE_SQL','query':'SELECT 1'})
  self.assertEqual(c.logical,0);self.assertEqual(c.requests,[])
 def test_owner_stop_prevents_next_physical_child_admission(self):
  cls=capped_governor_type();gov=cls.__new__(cls);gov.export_should_stop=lambda:True;gov.export_admissions=4;gov.export_cap=400
  with self.assertRaisesRegex(RuntimeError,'EXPORT_OWNER_STOP'):gov.reserve(None,'owner','request','cloud')
  self.assertEqual(gov.export_admissions,4)
if __name__=='__main__':unittest.main()
