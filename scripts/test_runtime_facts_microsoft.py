"""Real Microsoft endpoint/SQL compilation with deterministic recorded responses."""
import copy
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock,patch
from investigator.adapters.runtime_facts_microsoft import MicrosoftRuntimeFacts,sql_request,refresh_due
from investigator.adapters.metadata_error import MetadataUnavailable
from investigator.live_gateway import validate_sql
from investigator.shared_state import SharedState
from investigator.estate_graph_repository import GraphRepository
from cloud_facts_collector import collect,execute
from test_estate_graph import graph, T0, T1

WS='149f8d99-1c66-4a0a-9624-759be002bb60';ITEM='3484a2bc-98c5-4cef-be5c-a6215484075e'


def retained(raw):return {'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
def route(kind='JOB'):
    return {'kind':kind,'workspace':WS,'item':ITEM}

def audit():
    return {'reader':'r','connection':'example.datawarehouse.fabric.microsoft.com','database':'ops','schema':'dbo','table':'audit','principal':'reader-principal','producer_id':'pipeline1',
            'columns':{key:key for key in ('run_id','start','end','status','rows_read','rows_written','pipeline_name','accounting_state')}}

def answer(request,rows):
    return {'rows':rows,'read_only_verified':True,'surface_report_binding':'VALUE_QUERY',
            'surface_report':{'identity':'reader-principal','object':'ops','engine':'Microsoft Azure SQL Data Warehouse'}}


class MicrosoftFactsTests(unittest.TestCase):
    def adapter(self,subjects=None,http=None,sql=None):
        http=http or Mock(return_value={'status_code':200,'text':{'value':[{'id':'run1','status':'Failed','startTimeUtc':T0,'endTimeUtc':T1,'failureReason':{'errorCode':'ExampleFailure'}}]}})
        adapter=MicrosoftRuntimeFacts(subjects or {'visual':route()},http=http,sql=sql,retain=retained)
        return adapter,http

    def test_job_list_is_one_get_not_get_every_run_or_trigger(self):
        adapter,http=self.adapter();listing=adapter.list_changes(['visual']);values=adapter.fetch('visual',now=T1)
        self.assertEqual(http.call_count,1)
        self.assertEqual(http.call_args.args[0],'workspaces/'+WS+'/items/'+ITEM+'/jobs/instances')
        run=next(v for v in values if v['kind']=='JOB_RUN')
        self.assertEqual(run['value']['status'],'FAILED')
        self.assertEqual(run['value']['error'],{'errorCode':'ExampleFailure'})
        self.assertIsNone(run['value']['rows_read'])
        self.assertTrue(values[0]['provenance']['evidence_ids'][0].startswith('sha256:'))

    def test_403_becomes_retained_named_gap_never_empty_history(self):
        http=Mock(side_effect=MetadataUnavailable(403,{'error':{'code':'Forbidden'}}))
        adapter,_=self.adapter(http=http);adapter.list_changes(['visual']);values=adapter.fetch('visual',now=T1)
        self.assertEqual(values[0]['state'],'UNAVAILABLE');self.assertIn('403',values[0]['reason'])
        self.assertIsNone(values[0]['value'])

    def test_empty_history_is_successful_negative_not_failed_query(self):
        adapter,_=self.adapter(http=Mock(return_value={'status_code':200,'text':{'value':[]}}))
        adapter.list_changes(['visual']);values=adapter.fetch('visual',now=T1)
        self.assertEqual(values[0]['kind'],'RUN_HISTORY');self.assertEqual(values[0]['state'],'OBSERVED_NEGATIVE')
        self.assertEqual(values[0]['value']['runs'],[])
        self.assertIn('LOAD_ACCOUNTING_UNAVAILABLE',values[-1]['reason'])

    def test_partial_list_is_not_absence_or_overdue_proof(self):
        adapter,_=self.adapter(http=Mock(return_value={'status_code':200,'text':{'value':[],'continuationToken':'more'}}))
        adapter.list_changes(['visual']);values=adapter.fetch('visual',now=T1)
        self.assertEqual(values[-1]['state'],'UNAVAILABLE')
        self.assertIn('CONTINUATION',values[-1]['reason'])

    def test_refresh_history_and_schedule_real_routes_readonly(self):
        schedule={'enabled':True,'localTimeZoneId':'UTC','days':['Tuesday'],'times':['00:30','02:00']}
        def http(path,audience):
            self.assertEqual(audience,'powerbi')
            return {'status_code':200,'text':schedule if path.endswith('refreshSchedule') else {'value':[{'requestId':'refresh1','status':'Completed','startTime':T0,'endTime':T1}]}}
        adapter,_=self.adapter({'visual':route('MODEL')},http=http)
        adapter.list_changes(['visual']);values=adapter.fetch('visual',now='2026-10-13T01:30:00Z')
        by_kind={v['kind']:v for v in values}
        self.assertEqual(by_kind['REFRESH_STATE']['value']['state'],'SUCCEEDED')
        self.assertEqual(by_kind['SCHEDULE']['value']['next_due'],'2026-10-13T02:00:00Z')
        self.assertTrue(by_kind['OVERDUE']['value']['overdue'])

    def test_utc_schedule_and_unsupported_zone_explicit(self):
        self.assertEqual(refresh_due({'enabled':False},T1)['next_due'],None)
        with self.assertRaisesRegex(ValueError,'TIMEZONE_UNSUPPORTED'):
            refresh_due({'enabled':True,'days':['Tuesday'],'times':['12:00'],'localTimeZoneId':'unregistered'},T1)

    def test_audit_counts_attested_exact_same_run_and_first_source(self):
        r=route();r['audit']=audit()
        def sql(route,request):
            return answer(request,[{'run_id':'run1','start':T0,'end':T1,'status':'SUCCEEDED','rows_read':'360','rows_written':'359','pipeline_name':'pipeline1','accounting_state':'OBSERVED_COPY_OUTPUT'}])
        adapter,_=self.adapter({'visual':r},sql=sql)
        adapter.list_changes(['visual']);values=adapter.fetch('visual',now=T1)
        run=next(v for v in values if v['kind']=='JOB_RUN')
        self.assertEqual(run['value']['rows_read'],360);self.assertEqual(run['value']['rows_written'],359)
        self.assertEqual(run['value']['accounting'],'DECLARED_WAREHOUSE_AUDIT')
        self.assertEqual(len(run['provenance']['evidence_ids']),2)

    def test_audit_recount_or_other_producer_cannot_supply_activity_accounting(self):
        r=route();r['audit']=audit()
        request=sql_request(r['audit'],'audit')
        self.assertIn('WHERE [pipeline_name]=@producer',request['query'])
        self.assertEqual(request['parameters'],[{'name':'@producer','value':'pipeline1'}])
        for accounting_state,pipeline_name in [('RECOUNT','pipeline1'),('OBSERVED_COPY_OUTPUT','different')]:
            sql=Mock(side_effect=lambda route,request:answer(request,[{'run_id':'run1','start':T0,'end':T1,'status':'SUCCEEDED',
                'rows_read':'360','rows_written':'360','accounting_state':accounting_state,'pipeline_name':pipeline_name}]))
            adapter,_=self.adapter({'visual':r},sql=sql);adapter.list_changes(['visual']);values=adapter.fetch('visual',now=T1)
            self.assertIsNone(next(v for v in values if v['kind']=='JOB_RUN')['value']['rows_read'])
            self.assertIn('DECLARED_AUDIT_UNAVAILABLE',values[-1]['reason'])

    def test_unmatched_audit_run_does_not_supply_counts(self):
        r=route();r['audit']=audit()
        sql=Mock(side_effect=lambda route,request:answer(request,[{'run_id':'different','start':T0,'end':T1,'status':'SUCCEEDED','rows_read':'999','rows_written':'999','pipeline_name':'pipeline1','accounting_state':'OBSERVED_COPY_OUTPUT'}]))
        adapter,_=self.adapter({'visual':r},sql=sql);adapter.list_changes(['visual']);values=adapter.fetch('visual',now=T1)
        self.assertIsNone(next(v for v in values if v['kind']=='JOB_RUN')['value']['rows_read'])
        self.assertIn('NO_ROW_FOR_LISTED_RUN',values[-1]['reason'])

    def test_sql_attestation_failure_refuses_counts(self):
        r=route();r['audit']=audit()
        def sql(route,request):
            result=answer(request,[]);result['surface_report']['identity']='wrong';return result
        adapter,_=self.adapter({'visual':r},sql=sql);adapter.list_changes(['visual']);values=adapter.fetch('visual',now=T1)
        self.assertIn('DECLARED_AUDIT_UNAVAILABLE',values[-1]['reason'])

    def test_table_definition_modified_date_never_becomes_load(self):
        adapter,http=self.adapter({'visual':route('TABLE')});adapter.list_changes(['visual']);value=adapter.fetch('visual',now=T1)[0]
        http.assert_not_called();self.assertEqual(value['state'],'UNAVAILABLE')
        self.assertIn('NO_DECLARED_AUDIT_OR_DELTA',value['reason'])

    def test_profiles_actual_aggregates_compile_under_existing_sql_guard(self):
        profile={'reader':'r','connection':'example','database':'ops','schema':'dbo','table':'movements','principal':'reader-principal','key_columns':['id','units']}
        request=sql_request(profile,'profile')
        self.assertEqual(validate_sql(request['query'],{('dbo','movements')}),{('dbo','movements')})
        self.assertIn('COUNT_BIG(*)',request['query']);self.assertIn('HASHBYTES',request['query'])
        r=route('TABLE');r['profile']=profile
        adapter,_=self.adapter({'visual':r},sql=lambda route,request:answer(request,[{'row_count':'360','checksum_0':'123','checksum_1':'456'}]))
        value=adapter.profile('visual',load_marker='load1',now=T1)
        self.assertEqual(value['value']['row_count'],360)
        self.assertIn('NOT_EQUALITY_PROOF',value['value']['checksum_method'])
        self.assertEqual(value['provenance']['evidence_ids'][0][:7],'sha256:')

    def test_profile_query_identifier_injection_refused(self):
        with self.assertRaisesRegex(ValueError,'IDENTIFIER'):
            sql_request({'schema':'dbo','table':'t; DROP TABLE x','key_columns':['id']},'profile')

    def test_no_receipt_no_fact(self):
        adapter,_=self.adapter();adapter.retain=lambda raw:None
        with self.assertRaisesRegex(ValueError,'RETAINED_RECEIPT'):adapter.list_changes(['visual'])

    def test_live_entry_forces_shared_scan_category_even_inside_investigation_runner(self):
        from investigator.build_phase import operating_mode,purpose
        config={'estate':'estate','authentication':{},'storage':{},'receipt_uri_prefix':'blob://test','budget':{'environment':'test'},'subjects':{'visual':route()},'max_requests':2,'approval':'test'}
        with operating_mode(category='INVESTIGATION'):
            with patch('cloud_facts_collector.configured_state',return_value=Mock(backend='postgresql')):
                with patch('cloud_facts_collector.collect',side_effect=lambda *a,**k:purpose()):
                    self.assertEqual(execute(config),'SCAN')
            self.assertEqual(purpose(),'INVESTIGATION')

    def test_standalone_runner_existing_graph_scopes_and_shared_budget_reporting(self):
        with tempfile.TemporaryDirectory() as folder:
            state=SharedState.offline(Path(folder)/'state.sqlite');repo=GraphRepository(state);repo.migrate();repo.replace(graph())
            meter=Mock();meter.used=0;meter.owner='test-scan'
            http=Mock(return_value={'status_code':200,'text':{'value':[]}})
            config={'estate':'estate','authentication':{},'storage':{},'receipt_uri_prefix':'blob://test','budget':{'environment':'test'},'subjects':{'visual':route()},'max_requests':2,'approval':'test'}
            result=collect(config,state=state,http=http,sql=Mock(),retain=retained,meter=meter,clock=lambda:T1)
            self.assertEqual(result['purpose'],'SCAN');self.assertEqual(result['model_calls'],0)
            self.assertFalse(result['continuous_30_minute_freshness_claim'])
            self.assertEqual(result['selected_subjects'],['visual'])


if __name__=='__main__':unittest.main()
