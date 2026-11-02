import json,hashlib,unittest,os
from unittest.mock import Mock,patch
from investigator.guided_runtime_reads import SubjectHistory
from investigator.operational_run_selection import from_text
from investigator.operational_fastpath import run
from investigator.live_gateway import Gateway,GatewayDenied
W='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa';I='bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'
BASE='https://api.fabric.microsoft.com/v1/workspaces/'+W+'/items/'+I+'/jobs/instances'
TEXT='The run that started on 2026-10-23 at 17:16:29 UTC failed.'
def row(ident,at,status):return {'id':ident,'startTimeUtc':at,'endTimeUtc':at,'status':status,'failureReason':{'message':'Native failure'}if status=='Failed'else None}
def retain(raw):return {'sha256':hashlib.sha256(raw).hexdigest()}
class PagingTests(unittest.TestCase):
 def reader(self,bodies):
  http=Mock(side_effect=[{'status_code':200,'text':b}for b in bodies]);ledger=Mock()
  reader=SubjectHistory(subjects={'job':{'kind':'JOB','workspace':W,'item':I}},allowed={'job'},http=http,retain=retain,now=lambda:'2026-11-02T00:00:00Z',ledger=ledger,estate='fixture')
  return reader,http,ledger
 def test_requested_old_run_is_read_from_next_page_without_replacing_current_job(self):
  reader,http,ledger=self.reader([{'value':[row('new','2026-11-02T00:00:00Z','Completed')],'continuationToken':'a+b/='},{'value':[row('old','2026-10-23T17:16:29.1234567Z','Failed')]}]);selector=from_text(TEXT)
  result=reader('job',{'JOB_RUN','RUN_HISTORY'},selector=selector,text=TEXT);self.assertEqual(http.call_count,2);self.assertIn('?continuationToken=a%2Bb%2F%3D',http.call_args.args[0]);self.assertEqual(next(f for f in result['facts']if f['kind']=='JOB_RUN')['value']['run_id'],'new')
  admission={'target':{'id':'job','kind':'PIPELINE','label':'Loader'},'ticket':{'text':TEXT,'request':{'run_selector':selector}}}
  answer=run(admission,lambda *_:result,record=lambda _:None,history_for_selector=lambda *_:result)
  self.assertEqual(answer['status'],'ANSWERED');self.assertEqual(answer['technical']['operational_fact']['value']['run_id'],'old');self.assertEqual(answer['technical']['verdict'],'failed job')
 def test_answer_recheck_preserves_the_requested_run_instead_of_switching_to_latest(self):
  def facts(status):return {'facts':[{'kind':'RUN_HISTORY','state':'OBSERVED','subject':'job','value':{'runs':[{'run_id':'old','start':'2026-10-23T17:16:29Z','status':status,'error':None}]},'provenance':{'evidence_ids':['native-proof']}}]}
  selected=Mock(side_effect=[facts('RUNNING'),facts('SUCCEEDED')]);ordinary=Mock();admission={'target':{'id':'job','kind':'PIPELINE','label':'Loader'},'ticket':{'text':TEXT,'request':{'run_selector':from_text(TEXT)}}}
  answer=run(admission,ordinary,record=lambda _:None,history_for_selector=selected);self.assertEqual(answer['status'],'ANSWERED');self.assertEqual(answer['technical']['answer_status'],'SUCCEEDED');self.assertEqual(answer['technical']['operational_fact']['value']['run_id'],'old');self.assertEqual(selected.call_count,2);ordinary.assert_not_called()
 def test_full_native_page_is_searched_beyond_recent_twenty_without_another_request(self):
  bodies=[{'value':[row('r'+str(i),'2026-11-01T00:00:00Z','Completed')for i in range(24)]+[row('old','2026-10-23T17:16:29Z','Failed')]}];reader,http,_=self.reader(bodies);result=reader('job',{'RUN_HISTORY'},selector=from_text(TEXT),text=TEXT);self.assertEqual(len(result['facts'][0]['value']['runs']),25);http.assert_called_once()
 def test_search_stops_at_six_pages_and_never_claims_absence(self):
  reader,http,_=self.reader([{'value':[row('r'+str(i),'2026-11-02T00:00:00Z','Completed')],'continuationToken':str(i)}for i in range(6)]);result=reader('job',{'RUN_HISTORY'},selector=from_text(TEXT),text=TEXT);self.assertEqual(http.call_count,6);self.assertFalse(result['facts'][0]['value']['listing_complete']);self.assertTrue(any('SIX_PAGE_LIMIT'in str(f.get('reason'))for f in result['coverage']))
 def test_foreign_continuation_uri_is_never_followed(self):
  reader,http,_=self.reader([{'value':[],'continuationUri':'https://evil.example/jobs?continuationToken=x'}])
  with self.assertRaisesRegex(ValueError,'CONTINUATION_SCOPE'):reader('job',{'RUN_HISTORY'},selector=from_text(TEXT),text=TEXT)
  http.assert_called_once()
 @patch.dict(os.environ,{"LIVE_ACCESS_DISABLED":"0"})
 def test_reader_gateway_allows_only_cursor_on_the_existing_granted_job_list(self):
  gateway=Gateway({'version':1,'live_enabled':True,'identities':{'reader':{'role':'reader','http':[{'method':'GET','url':BASE,'purpose':'metadata'}]}}})
  gateway.http('reader','GET',BASE+'?continuationToken=a%2Bb')
  with patch.dict(os.environ,{'LIVE_ACCESS_DISABLED':'1'}):
   with self.assertRaisesRegex(GatewayDenied,'LIVE_ACCESS_DISABLED'):gateway.http('reader','GET',BASE+'?continuationToken=x')
  for method,url in [('POST',BASE+'?continuationToken=x'),('GET',BASE+'?continuationToken=x&other=y'),('GET',BASE.replace(I,W)+'?continuationToken=x'),('GET','https://evil.example/v1/workspaces/'+W+'/items/'+I+'/jobs/instances?continuationToken=x'),('GET',BASE+'?continuationToken=')]:
   with self.assertRaises(GatewayDenied):gateway.http('reader',method,url)
if __name__=='__main__':unittest.main()
