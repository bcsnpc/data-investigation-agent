import unittest,tempfile,pathlib,sys,sqlite3,decimal,json
sys.path.insert(0,str(pathlib.Path.cwd()/'scripts'))
from investigator.privacy_projection import Projection
from exporter import export,VERSION
class ExportTests(unittest.TestCase):
 def plan(self,kind='TEXT',cls='EXACT'):
  return {'version':VERSION,'estate_id':'synthetic','tape_class':cls,'estate_manifest_hash':'0'*64,'enterprise_context':{'id':'synthetic-enterprise','hash':'0'*64},'contexts':[{'model_id':'synthetic-model','context_id':'synthetic-context','context_hash':'0'*64,'revision':1}],'assets':[{'asset_id':'fixture://table/a','role':'APPLICATION','query':'SELECT [name] FROM [app].[a]','columns':[{'name':'name','native_type':kind,'logical_type':kind,'identity':'fixture://table/a/column/name'}],'max_rows':2,'max_bytes':1024}]}
 def result(self,rows,**kw):return {'status':'AVAILABLE','truncated':False,'rows':rows,'receipt':{'identity':'fake-reader','surface':'fake-sql','query':'SELECT [name] FROM [app].[a]','status':'AVAILABLE','physical_requests':1},**kw}
 def test_exact_types_null_decimal(self):
  with tempfile.TemporaryDirectory() as t:
   m=export(self.plan('DECIMAL'),lambda a:self.result([[decimal.Decimal('12.3400')],[None]]),pathlib.Path(t)/'out')
   self.assertEqual(m['status'],'COMPLETE')
   con=sqlite3.connect(pathlib.Path(t)/'out/data.sqlite')
   try:self.assertEqual(con.execute('select * from t0000').fetchall(),[('12.3400',),(None,)])
   finally:con.close()
 def test_datetime_100ns_preserved(self):
  with tempfile.TemporaryDirectory() as t:
   out=pathlib.Path(t)/'out';stamp='2026-10-11T03:00:00.1234567'
   export(self.plan('DATETIME'),lambda a:self.result([[stamp]]),out)
   con=sqlite3.connect(out/'data.sqlite')
   try:self.assertEqual(con.execute('select name from t0000').fetchone()[0],stamp)
   finally:con.close()
 def test_projected_raw_nowhere(self):
  secret='sensitive_synthetic_AccountName';policy={'tape_class':'PRIVACY_PROJECTED','version':'estate-privacy-projection-v1','estate_id':'synthetic','key_reference':'fake-key','columns':['fixture://table/a/column/name']};p=Projection(policy,lambda _:b'x'*32)
  with tempfile.TemporaryDirectory() as t:
   out=pathlib.Path(t)/'out';m=export(self.plan(cls='PRIVACY_PROJECTED'),lambda a:self.result([[secret]]),out,projection=p)
   self.assertEqual(m['status'],'COMPLETE')
   for f in out.iterdir():self.assertNotIn(secret.encode(),f.read_bytes())
 def test_truncation_and_caps_refuse(self):
  for result in [self.result([['a']],truncated=True),self.result([['a'],['b'],['c']]),self.result([['x'*1025]])]:
   with tempfile.TemporaryDirectory() as t:
    with self.assertRaises(ValueError):export(self.plan(),lambda a:result,pathlib.Path(t)/'out')
    self.assertEqual(json.loads((pathlib.Path(t)/'out/manifest.json').read_text())['status'],'BLOCKED')
 def test_no_secret_receipt_field(self):
  r=self.result([['a']]);r['receipt']['password']='secret'
  with tempfile.TemporaryDirectory() as t:
   out=pathlib.Path(t)/'out'
   with self.assertRaisesRegex(ValueError,'UNSAFE'):export(self.plan(),lambda a:r,out)
   self.assertNotIn(b'secret',(out/'manifest.json').read_bytes())
 def test_no_type_approximation(self):
  with tempfile.TemporaryDirectory() as t:
   with self.assertRaisesRegex(ValueError,'TYPE_MISMATCH'):export(self.plan('INTEGER'),lambda a:self.result([['2']]),pathlib.Path(t)/'out')
 def test_existing_output_refused(self):
  with tempfile.TemporaryDirectory() as t:
   with self.assertRaisesRegex(ValueError,'EXCLUSIVE'):export(self.plan(),lambda a:None,t)
 def test_later_refusal_preserves_committed_partial_asset(self):
  import copy
  plan=self.plan();second=copy.deepcopy(plan['assets'][0]);second['asset_id']='fixture://table/b';plan['assets'].append(second)
  def read(asset):
   if asset['asset_id'].endswith('/b'):raise RuntimeError('CONTROL_REFUSED')
   return self.result([['already validated']])
  with tempfile.TemporaryDirectory() as t:
   out=pathlib.Path(t)/'out'
   with self.assertRaisesRegex(RuntimeError,'REFUSED'):export(plan,read,out)
   manifest=json.loads((out/'manifest.json').read_text());self.assertEqual(manifest['status'],'BLOCKED');self.assertEqual(len(manifest['assets']),1)
   con=sqlite3.connect(out/'data.sqlite')
   try:self.assertEqual(con.execute('select * from t0000').fetchall(),[('already validated',)])
   finally:con.close()
if __name__=='__main__':unittest.main()
