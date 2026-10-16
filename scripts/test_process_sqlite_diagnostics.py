import importlib.util,json,sqlite3,sys,tempfile,unittest
from contextlib import closing,contextmanager
from pathlib import Path
sys.path.insert(0,'scripts')
from investigator.process_tape import Tape,active,bytes_of,validate_event
from investigator import process_failure as failure,local_accounting as accounting
@contextmanager
def connection(filename,timeout=5):
 with closing(sqlite3.connect(filename,timeout=timeout)) as db:
  with db:yield db

class Tests(unittest.TestCase):
 def test_real_busy_code_phase_retained_and_replayed_without_retry(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);dbfile=root/'fixture.sqlite';first=sqlite3.connect(dbfile);second=sqlite3.connect(dbfile,timeout=0)
   try:
    first.execute('CREATE TABLE fixture(x INT)');first.commit();first.execute('BEGIN IMMEDIATE')
    tape=Tape(root/'tape.json',{'entry_point':'diagnostic_test','context_identity':'synthetic','config':{},'profile':{},'usage_policy':None,'engine_hash':'synthetic','state':{'local_accounting':accounting.PIN}})
    with active(tape):
     with self.assertRaises(sqlite3.OperationalError) as caught:accounting.boundary('PROCESS_STAGE_ADMISSION',lambda:second.execute('BEGIN IMMEDIATE'))
     observed=failure.capture(caught.exception)
     self.assertEqual(observed['sqlite'],{'code':sqlite3.SQLITE_BUSY,'name':'SQLITE_BUSY','phase':'PROCESS_STAGE_ADMISSION'})
     self.assertTrue(observed['message_redacted'])
     tape.finish(observed)
    replay=Tape(root/'tape.json')
    with active(replay):
     with self.assertRaises(sqlite3.OperationalError) as repeated:accounting.boundary('PROCESS_STAGE_ADMISSION',lambda:self.fail('must not retry/read'))
     self.assertEqual(failure.capture(repeated.exception)['sqlite'],observed['sqlite'])
   finally:second.close();first.rollback();first.close()
 def test_arbitrary_sqlite_text_and_invalid_attrs_never_enter_result(self):
  error=sqlite3.OperationalError('BUSINESS_RAW_SECRET_VALUE');error.sqlite_errorname='SQLITE_BUSY private';error.sqlite_errorcode=True;error.sqlite_phase='arbitrary-source-value'
  recorded=failure.capture(error);self.assertNotIn('BUSINESS_RAW_SECRET_VALUE',json.dumps(recorded));self.assertEqual(recorded['sqlite'],{'code':None,'name':None,'phase':'UNSPECIFIED'})
 def test_legacy_failure_shape_remains_valid_without_new_fields(self):
  old={'error_type':'OperationalError','message':'withheld','message_redacted':True,'module':'adaptive_runtime.py','line':710,'errno':None}
  self.assertEqual(failure.validate(old),old)
 def test_successful_worker_guard_remains_sealed_before_receipt_failure(self):
  with tempfile.TemporaryDirectory() as folder:
   tape=Tape(Path(folder)/'tape.json',{'entry_point':'diagnostic_test','context_identity':'synthetic','config':{},'profile':{},'usage_policy':None,'engine_hash':'synthetic','state':{'local_accounting':accounting.PIN}})
   with active(tape):
    tape.event('WORKER_START',bytes_of({'command':['synthetic']}))
    tape.event('WORKER_READ',b'{"physical_read":"DONE","status":"AVAILABLE","guard_passed":true,"kind":"sql_object_permissions"}\n')
    def failed():raise sqlite3.OperationalError('database is locked')
    with self.assertRaises(sqlite3.OperationalError) as caught:accounting.boundary('PROCESS_READ_RECEIPT_PERSISTENCE',failed)
    observed=failure.capture(caught.exception);tape.event('WORKER_END',bytes_of({'returncode':1}));tape.finish(observed)
   replay=Tape(tape.path);guard=validate_event(replay.events[2],3);self.assertIn(b'"guard_passed":true',guard)
   error=json.loads(validate_event(replay.events[3],4));self.assertEqual(error['stage'],'PROCESS_READ_RECEIPT_PERSISTENCE');self.assertEqual(error['status'],'FAILED')

 def test_real_runtime_stage_and_receipt_boundaries_retain_busy_phase(self):
  from types import SimpleNamespace
  from investigator.adaptive_runtime import AdaptiveRuntime
  with tempfile.TemporaryDirectory() as folder:
   filename=Path(folder)/'catalog.sqlite';lock=sqlite3.connect(filename);lock.execute('CREATE TABLE fixture(x)');lock.commit();lock.execute('BEGIN IMMEDIATE')
   calls=[]
   def db():calls.append('connect');return closing(sqlite3.connect(filename,timeout=0))
   agent=AdaptiveRuntime.__new__(AdaptiveRuntime);agent.runtime=SimpleNamespace(db=db);agent.governor=None
   agent.load=lambda *args:self.fail('locked admission must not load');agent.save=lambda *args:self.fail('locked admission must not save')
   try:
    for operation,phase in [(lambda:agent._persist_process_stage('session','PROCESS_STAGE_STARTED',{}),'PROCESS_STAGE_ADMISSION'),(lambda:agent._persist_process_read('session','read',{'id':'receipt'},False),'PROCESS_READ_RECEIPT_PERSISTENCE')]:
     tape=Tape(Path(folder)/(phase+'.json'),{'entry_point':'diagnostic_test','context_identity':'synthetic','config':{},'profile':{},'usage_policy':None,'engine_hash':'synthetic','state':{'local_accounting':accounting.PIN}})
     with active(tape),self.assertRaises(sqlite3.OperationalError) as caught:operation()
     self.assertEqual(failure.capture(caught.exception)['sqlite'],{'code':sqlite3.SQLITE_BUSY,'name':'SQLITE_BUSY','phase':phase})
    self.assertEqual(len(calls),2)
   finally:lock.rollback();lock.close()
 def test_flexible_successful_transport_then_locked_receipt_is_typed_failure(self):
  from types import SimpleNamespace
  from unittest.mock import patch
  from investigator import flexible_tools
  with tempfile.TemporaryDirectory() as folder:
   filename=Path(folder)/'catalog.sqlite';lock=sqlite3.connect(filename);lock.execute('CREATE TABLE fixture(x)');lock.commit()
   store=SimpleNamespace(connect=lambda:connection(filename,timeout=0));calls=[]
   def execute(request):
    calls.append(request);lock.execute('BEGIN IMMEDIATE');return {'read_only_verified':True}
   request={'tool':'bounded_sql','query':'synthetic','max_rows':2};result={'rows':[{'v':1}],'cause_verified':False}
   try:
    with patch.object(flexible_tools,'build',return_value=request),patch.object(flexible_tools,'extract',return_value=result),patch('investigator.raw_surface_report.validate'),patch('investigator.physical_transport_retry.execute',side_effect=lambda request,fn,tool:fn(request)):
     tape=Tape(Path(folder)/'receipt.json',{'entry_point':'diagnostic_test','context_identity':'synthetic','config':{},'profile':{},'usage_policy':None,'engine_hash':'synthetic','state':{'local_accounting':accounting.PIN}})
     with active(tape),self.assertRaises(sqlite3.OperationalError) as caught:flexible_tools.run(store,{'model_id':'synthetic'},{},'bounded_sql',execute,receipt_id='synthetic')
    self.assertEqual(len(calls),1);self.assertEqual(failure.capture(caught.exception)['sqlite']['phase'],'FLEXIBLE_READ_RECEIPT_PERSISTENCE')
    self.assertEqual(failure.capture(caught.exception)['sqlite']['code'],sqlite3.SQLITE_BUSY)
   finally:lock.rollback();lock.close()
 def test_flexible_caught_local_error_retains_diagnostic_in_failed_receipt(self):
  from types import SimpleNamespace
  from unittest.mock import patch
  from investigator import flexible_tools
  with tempfile.TemporaryDirectory() as folder:
   filename=Path(folder)/'catalog.sqlite';store=SimpleNamespace(connect=lambda:connection(filename));error=sqlite3.OperationalError('PRIVATE_RAW_VALUE');error.sqlite_errorcode=sqlite3.SQLITE_BUSY;error.sqlite_errorname='SQLITE_BUSY';error.sqlite_phase='PROCESS_READ_RECEIPT_PERSISTENCE'
   def execute(request):raise error
   with patch.object(flexible_tools,'build',return_value={'tool':'bounded_sql'}),patch('investigator.receipt_integrity.seal'),patch('investigator.physical_transport_retry.execute',side_effect=lambda request,fn,tool:fn(request)):
    result=flexible_tools.run(store,{'model_id':'synthetic'},{},'bounded_sql',execute,receipt_id='synthetic')
   self.assertEqual(result['status'],'FAILED');self.assertEqual(result['result']['local_failure']['sqlite']['code'],sqlite3.SQLITE_BUSY)
   self.assertNotIn('PRIVATE_RAW_VALUE',json.dumps(result))

if __name__=='__main__':unittest.main()
