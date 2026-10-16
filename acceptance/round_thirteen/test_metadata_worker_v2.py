import sys,tempfile,json,unittest,subprocess
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path.cwd()/'scripts'))
from investigator import process_tape as journal
from investigator.physical_reads import scope,run
from metadata_worker_v2 import owned_bounded,recorded_file_result,worker_command,sql_file_catalog
BOOT={'entry_point':'synthetic','context_identity':'retained-context','config':{},'profile':{},'usage_policy':{},'engine_hash':'synthetic-engine','state':{}}
WORKER='''import sys,json
sys.stdin.readline()
for i in range(3):
 print(json.dumps({'physical_read':'REQUEST','kind':'metadata_read'}),flush=True)
 if sys.stdin.readline().strip()!='ALLOW':raise RuntimeError('no admission')
 print(json.dumps({'physical_read':'DONE','kind':'metadata_read','status':'AVAILABLE'}),flush=True)
print(json.dumps({'worker':'complete'}),flush=True)
'''
class Tests(unittest.TestCase):
 def capture(self,root):
  program=root/'synthetic_worker.py';program.write_text(WORKER);path=root/'tape.json';t=journal.Tape(path,BOOT);counts=[]
  def meter(kind,call):counts.append(kind);journal.clock('extra_metadata');return call()
  def native():
   result=run([sys.executable,str(program)],input='{}',timeout=10)
   self.assertEqual(result.returncode,0);return {'catalog':['synthetic-only']}
  with journal.active(t),scope(meter):journal.bounded_call('catalog',{'schema':'dbo'},native)
  t.finish({'physical':1+len(counts)})
  return path,program
 def test_native_nested_worker_replayed_without_process_and_counts_are_physical(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);path,program=self.capture(root);original=path.read_bytes();t=journal.Tape(path);counts=[]
   def meter(kind,call):counts.append(kind);journal.clock('extra_metadata');return call()
   def producer():
    worker_command(t)
    result=run([sys.executable,str(program)],input='{}',timeout=10);self.assertEqual(result.returncode,0);return recorded_file_result()
   with patch.object(subprocess,'Popen',side_effect=AssertionError('real child forbidden')),journal.active(t),scope(meter):
    result=owned_bounded('catalog',{'schema':'dbo'},producer)
   self.assertEqual(result,{'catalog':['synthetic-only']});self.assertEqual(1+len(counts),3)
   t.finish({'physical':3});self.assertEqual(t.index,len(t.events));self.assertEqual(path.read_bytes(),original)
 def test_changed_compiled_worker_request_refuses(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);path,program=self.capture(root);original=path.read_bytes();t=journal.Tape(path)
   with journal.active(t),scope(lambda k,c:c()),self.assertRaises(journal.TapeError):owned_bounded('catalog',{'schema':'dbo'},lambda:run([sys.executable,str(program),'changed'],input='{}',timeout=10))
   self.assertEqual(path.read_bytes(),original)
 def test_missing_typed_guard_witness_not_skipped(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);path,program=self.capture(root);t=journal.Tape(path)
   with journal.active(t):
    t.event('BOUNDED_REQUEST',journal.bytes_of({'name':'catalog','request':{'schema':'dbo'}}))
    t.take('AUTH_STATE')
    with self.assertRaisesRegex(journal.TapeError,'GUARD_WITNESS_MISSING'):worker_command(t)
 def test_sql_compiler_uses_sealed_path_and_file_result_never_opens_credentials_or_original_output(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);program=root/'synthetic_worker.py';program.write_text(WORKER);path=root/'sql-tape.json';t=journal.Tape(path,BOOT)
   output=root/'original-missing-output.json';credential=root/'credential-never-created.xml'
   command=['powershell','-NoProfile','-File','Get-SqlMetadata.ps1','-Server','synthetic-server','-Database','synthetic-db','-VisibilitySchema','dbo','-CredentialPath',str(credential),'-OutputPath',str(output)]
   actual_popen=subprocess.Popen
   def fake(command,**kwargs):return actual_popen([sys.executable,str(program)],**kwargs)
   def meter(kind,call):journal.clock('extra_metadata');return call()
   def native():
    result=run(command,input='{}',timeout=240,capture_output=True,text=True,encoding='utf-8');self.assertEqual(result.returncode,0);return {'catalog':['synthetic-only']}
   with patch.object(subprocess,'Popen',side_effect=fake),journal.active(t),scope(meter):journal.bounded_call('catalog',{'server':'synthetic-server','database':'synthetic-db','schema':'dbo'},native)
   t.finish({'physical':3});original=path.read_bytes();t=journal.Tape(path)
   with patch.object(subprocess,'Popen',side_effect=AssertionError('native child forbidden')),journal.active(t),scope(meter):
    result=owned_bounded('catalog',{'server':'synthetic-server','database':'synthetic-db','schema':'dbo'},lambda:sql_file_catalog('synthetic-server','synthetic-db','dbo',script=Path.cwd()/'infra/scripts/Get-SqlMetadata.ps1',credential_file=str(credential)))
   t.finish({'physical':3});self.assertEqual(result,{'catalog':['synthetic-only']});self.assertEqual(path.read_bytes(),original);self.assertFalse(output.exists());self.assertFalse(credential.exists())
   t=journal.Tape(path)
   with patch.object(subprocess,'Popen',side_effect=AssertionError('native child forbidden')),journal.active(t),scope(meter),self.assertRaises(journal.TapeError):
    owned_bounded('catalog',{'server':'synthetic-server','database':'synthetic-db','schema':'dbo'},lambda:sql_file_catalog('changed-server','synthetic-db','dbo',script=Path.cwd()/'infra/scripts/Get-SqlMetadata.ps1',credential_file=str(credential)))
   self.assertEqual(path.read_bytes(),original)
 def test_script_or_semantic_change_refuses_without_consuming_worker(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);path,program=self.capture(root)
   # Typed synthetic witness used only to isolate compiler admission checks.
   start={'command':['powershell','-File','Different.ps1','-OutputPath','synthetic-output'],'mode':'STREAM'}
   with patch('metadata_worker_v2.worker_command',return_value=start),journal.active(journal.Tape(path)),self.assertRaisesRegex(journal.TapeError,'SCRIPT_DESCRIPTOR_DIFFERS'):
    sql_file_catalog('s','d','dbo',script=Path.cwd()/'infra/scripts/Get-SqlMetadata.ps1',credential_file='never-open')
   start['command'][2]='Get-SqlMetadata.ps1'
   with patch('metadata_worker_v2.worker_command',return_value=start),journal.active(journal.Tape(path)),self.assertRaisesRegex(journal.TapeError,'ARCHIVED_SCRIPT_MISSING'):
    sql_file_catalog('s','d','dbo',script=root/'Different.ps1',credential_file='never-open')
 def test_changed_server_is_compiled_not_copied_from_worker_witness(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);path,program=self.capture(root);t=journal.Tape(path)
   # Existing real sealed worker command will differ from the SQL compiler.
   with journal.active(t),scope(lambda k,c:c()),self.assertRaises(journal.TapeError):
    owned_bounded('catalog',{'schema':'dbo'},lambda:sql_file_catalog('changed-server','db','dbo',script=Path.cwd()/'infra/scripts/Get-SqlMetadata.ps1',credential_file='never-open'))
if __name__=='__main__':unittest.main()
