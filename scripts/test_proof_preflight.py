import base64
import copy
from io import BytesIO
import json
import unittest
from unittest.mock import MagicMock, patch
from io import StringIO

from investigator import proof_preflight as preflight
from investigator.admin_api import create_app
from investigator.onboarding import Conflict
import test_source_diagnostics as fixture


def definition(mode='directLake',extra=None):
    body={'model':{'tables':[{'partitions':[{'mode':mode}]}],'roles':[{'name':'secret-role','members':['secret-user']}],
                   'dataSources':[{'connectionString':'secret-password'}]}}
    if extra:body['model'].update(extra)
    return {'definition':{'parts':[{'path':'model.bim','payloadType':'InlineBase64',
                                    'payload':base64.b64encode(json.dumps(body).encode()).decode()}]}}


class PreflightTests(unittest.TestCase):
    def setUp(self):
        h=fixture.SourceTests();h.setUp();self.addCleanup(h.doCleanups)
        self.store=h.store;self.model=h.model
        self.model['workspace']='11111111-1111-1111-1111-111111111111'
        self.model['native_id']='22222222-2222-2222-2222-222222222222'
        self.calls=[];self.responses={
            'item':{'id':self.model['native_id'],'type':'SemanticModel'},
            'dataset':{'id':self.model['native_id'],'isRefreshable':True},
            'access':{'value':[{'role':'Admin','principal':{'displayName':'secret-user'}}]},
            'refresh':{'value':[{'status':'Completed','serviceExceptionJson':'secret-error'}]},
            'definition':definition()}
        self.transport=MagicMock(side_effect=self.dispatch)

    def dispatch(self,endpoint,method,audience):
        self.calls.append((endpoint,method,audience))
        key='definition' if 'getDefinition' in endpoint else 'access' if 'roleAssignments' in endpoint else 'refresh' if 'refreshes' in endpoint else 'dataset' if audience=='powerbi' else 'item'
        return {'status_code':200,'text':copy.deepcopy(self.responses[key])}

    def run_check(self):return preflight.run(self.store,'model',self.transport,sleep=lambda seconds:None)

    def test_matching_definitions_and_refresh_never_certify_exclusivity(self):
        r=self.run_check();self.assertEqual(r['status'],'COMPLETED');self.assertEqual(r['http_calls'],6)
        self.assertTrue(r['assessment']['definition_hashes_equal_at_probes'])
        self.assertFalse(r['assessment']['live_acceptance_ready']);self.assertEqual(r['assessment']['gate_status'],'BLOCKED')
        self.assertIn('EXCLUSIVE_PUBLICATION_CONTROL_NOT_IMPLEMENTED',r['assessment']['blockers'])
        self.assertIn('WORKSPACE_WRITE_ROLES_OBSERVED',r['assessment']['blockers'])

    def test_sensitive_definition_members_and_errors_not_retained(self):
        r=self.run_check();self.assertNotIn('secret',json.dumps(r))
        definition_probe=r['observations'][-1]['summary']
        self.assertEqual(definition_probe['partition_modes'],['directLake']);self.assertEqual(definition_probe['role_count'],1)

    def test_before_after_definition_change_is_explicit(self):
        count=0
        def dispatch(*args):
            nonlocal count
            if 'getDefinition' in args[0]:
                count+=1
                if count==2:self.responses['definition']=definition('import')
            return self.dispatch(*args)
        self.transport.side_effect=dispatch;r=self.run_check()
        self.assertFalse(r['assessment']['definition_hashes_equal_at_probes'])
        self.assertIn('DEFINITION_CHANGED_BETWEEN_PROBES',r['assessment']['blockers'])

    def test_import_mode_is_not_a_generation_guarantee(self):
        self.responses['definition']=definition('import');r=self.run_check()
        self.assertFalse(r['assessment']['live_acceptance_ready'])
        self.assertIn('INPUT_PUBLICATION_GENERATION_UNBOUND',r['assessment']['blockers'])

    def test_partial_access_page_is_not_full_permission_inventory(self):
        self.responses['access']['continuationToken']='secret-token';r=self.run_check()
        self.assertIn('WORKSPACE_ACCESS_PAGE_INCOMPLETE',r['assessment']['blockers'])
        self.assertNotIn('secret-token',json.dumps(r));self.assertEqual(r['http_calls'],6)

    def test_viewer_only_snapshot_does_not_prove_current_principal_readonly(self):
        self.responses['access']={'value':[{'role':'Viewer'}]};r=self.run_check()
        self.assertFalse(r['observations'][2]['summary']['effective_principal_permissions_verified'])
        self.assertFalse(r['assessment']['exclusive_write_boundary_verified'])

    def test_denied_probe_preserves_http_status_and_continues(self):
        def dispatch(*args):return {'status_code':403,'text':{'message':'secret'}} if 'roleAssignments' in args[0] else self.dispatch(*args)
        self.transport.side_effect=dispatch;r=self.run_check()
        self.assertEqual(r['observations'][2]['http_status'],403)
        self.assertEqual(r['observations'][-1]['status'],'OBSERVED');self.assertNotIn('secret',json.dumps(r))

    def test_failed_transport_never_persists_exception_message(self):
        self.transport.side_effect=RuntimeError('secret token and user info');r=self.run_check()
        self.assertEqual(r['http_calls'],6);self.assertNotIn('secret',json.dumps(r))
        self.assertTrue(all(o['status']=='UNAVAILABLE' for o in r['observations']))

    def test_wrong_remote_identity_is_not_accepted(self):
        self.responses['item']['id']='wrong';r=self.run_check()
        self.assertEqual(r['observations'][0]['status'],'UNAVAILABLE')

    def test_lro_result_is_bounded_and_operation_id_validated(self):
        operation='33333333-3333-3333-3333-333333333333'
        def dispatch(endpoint,method,audience):
            if 'getDefinition' in endpoint:return {'status_code':202,'headers':{'x-ms-operation-id':operation,'Retry-After':'0'}}
            if endpoint.endswith('/result'):return {'status_code':200,'text':definition()}
            if endpoint.startswith('operations/'):return {'status_code':200,'text':{'status':'Succeeded'}}
            return self.dispatch(endpoint,method,audience)
        self.transport.side_effect=dispatch;r=self.run_check()
        self.assertEqual(r['http_calls'],10);self.assertTrue(r['assessment']['definition_hashes_equal_at_probes'])

    def test_external_operation_location_is_never_followed(self):
        def dispatch(endpoint,*args):
            if 'getDefinition' in endpoint:return {'status_code':202,'headers':{'x-ms-operation-id':'https://evil.test/token','Location':'https://evil.test/token'}}
            return self.dispatch(endpoint,*args)
        self.transport.side_effect=dispatch;r=self.run_check()
        self.assertEqual(r['http_calls'],6);self.assertEqual(r['observations'][-1]['status'],'UNAVAILABLE')

    def test_lro_still_running_exits_without_unbounded_polling(self):
        def dispatch(endpoint,*args):
            if 'getDefinition' in endpoint:return {'status_code':202,'headers':{'x-ms-operation-id':'33333333-3333-3333-3333-333333333333','Retry-After':'0'}}
            if endpoint.startswith('operations/'):return {'status_code':200,'text':{'status':'Running'}}
            return self.dispatch(endpoint,*args)
        self.transport.side_effect=dispatch;r=self.run_check()
        self.assertEqual(r['http_calls'],10);self.assertEqual(r['observations'][-1]['error_type'],'TimeoutError')

    def test_deadline_stops_new_calls_and_preserves_partial_evidence(self):
        tick=[0]
        def dispatch(*args):
            result=self.dispatch(*args);tick[0]=241;return result
        self.transport.side_effect=dispatch
        r=preflight.run(self.store,'model',self.transport,clock=lambda:tick[0],sleep=lambda s:None)
        self.assertEqual(r['http_calls'],1);self.assertEqual(r['observations'][0]['status'],'OBSERVED')

    def test_changed_local_context_stops_additional_probes(self):
        def dispatch(*args):
            result=self.dispatch(*args);self.model['revision']+=1;return result
        self.transport.side_effect=dispatch;r=self.run_check()
        self.assertEqual(r['http_calls'],1);self.assertIn('LOCAL_MODEL_CHANGED_DURING_PREFLIGHT',r['assessment']['blockers'])

    def test_probe_reserved_before_dispatch_and_history_reads_do_not_call(self):
        def dispatch(*args):
            with self.store.connect() as db:
                body=json.loads(db.execute('SELECT body FROM proof_preflights').fetchone()[0])
            self.assertGreater(body['http_calls'],0);self.assertEqual(body['observations'][-1]['status'],'DISPATCHED')
            return self.dispatch(*args)
        self.transport.side_effect=dispatch;r=self.run_check();calls=self.transport.call_count
        self.assertEqual(preflight.read(self.store,'model',r['id'])['status'],'COMPLETED')
        self.assertEqual(len(preflight.listing(self.store,'model')),1);self.assertEqual(self.transport.call_count,calls)

    def test_tampered_history_is_rejected(self):
        r=self.run_check()
        with self.store.connect() as db:db.execute("UPDATE proof_preflights SET body='{}' WHERE id=?",(r['id'],))
        with self.assertRaises(Conflict):preflight.read(self.store,'model',r['id'])

    def test_historical_context_is_marked_stale(self):
        r=self.run_check();self.model['revision']+=1
        self.assertFalse(preflight.read(self.store,'model',r['id'])['local_context_current'])

    def test_disabled_or_invalid_model_cannot_probe(self):
        self.model['enabled']=False
        with self.assertRaises(Conflict):self.run_check()
        self.transport.assert_not_called()

    def test_cross_model_history_is_rejected(self):
        r=self.run_check()
        with self.assertRaises(KeyError):preflight.read(self.store,'other',r['id'])

    def test_definition_duplicate_parts_and_oversized_payload_rejected(self):
        body=definition();body['definition']['parts']*=2
        with self.assertRaises(ValueError):preflight.definition_summary(body)
        body=definition();body['definition']['parts'][0]['payload']='a'*8_000_001
        with self.assertRaises(ValueError):preflight.definition_summary(body)

    def test_malformed_base64_and_missing_model_are_not_guessed(self):
        body=definition();body['definition']['parts'][0]['payload']='!'
        with self.assertRaises(ValueError):preflight.definition_summary(body)
        body=definition();body['definition']['parts'][0]['path']='other.json'
        self.assertFalse(preflight.definition_summary(body)['tmsl_model_observed'])

    def test_admin_history_api_has_no_execution_endpoint(self):
        r=self.run_check();app=create_app(self.store,'a'*32,'r'*32)
        for token,status in [('a'*32,'200 OK'),('r'*32,'403 Forbidden')]:
            statuses=[]
            output=b''.join(app({'PATH_INFO':'/api/v2/admin/models/model/proof-preflights/'+r['id'],'REQUEST_METHOD':'GET',
                                'HTTP_AUTHORIZATION':'Bearer '+token},lambda s,h:statuses.append(s)))
            self.assertEqual(statuses,[status])
            if status=='200 OK':self.assertEqual(json.loads(output)['assessment']['gate_status'],'BLOCKED')

    def test_interrupted_collection_remains_visible_without_automatic_replay(self):
        self.transport.side_effect=KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt):self.run_check()
        saved=preflight.listing(self.store,'model')[0]
        self.assertEqual(saved['status'],'RUNNING');self.assertEqual(saved['http_calls'],1)
        self.assertEqual(saved['observations'][0]['status'],'DISPATCHED');self.transport.assert_called_once()

    def test_invalid_retry_interval_does_not_sleep(self):
        def dispatch(endpoint,*args):
            if 'getDefinition' in endpoint:return {'status_code':202,'headers':{'x-ms-operation-id':'33333333-3333-3333-3333-333333333333','Retry-After':'3600'}}
            return self.dispatch(endpoint,*args)
        self.transport.side_effect=dispatch;sleep=MagicMock()
        result=preflight.run(self.store,'model',self.transport,sleep=sleep)
        sleep.assert_not_called();self.assertEqual(result['http_calls'],6)

    def test_worker_sanitizes_http_error_without_exposing_message(self):
        from run_proof_preflight import worker
        request={'tenant':'fixture','endpoint':'workspaces/test','method':'get','audience':'fabric'}
        for error,expected in [('Metadata HTTP status 403',403),('secret token details',None)]:
            output=StringIO()
            with patch('sys.stdin',StringIO(json.dumps(request))),patch('sys.stdout',output),patch('metadata_auth.FabricCliTokens'),patch('metadata_auth.MetadataHttp') as http:
                http.return_value.side_effect=RuntimeError(error);worker()
            result=json.loads(output.getvalue());self.assertEqual(result['status_code'],expected)
            self.assertNotIn('secret',output.getvalue())

    def test_parent_transport_uses_timeout_and_rejects_worker_failure(self):
        from run_proof_preflight import transport
        config={'fabric':{'auth':{'python':'python','tenant_id':'tenant'}}}
        with patch('run_proof_preflight.subprocess.run',return_value=MagicMock(returncode=1,stdout='secret')) as execute:
            with self.assertRaises(RuntimeError):transport(config)('workspaces/test','get','fabric')
            self.assertEqual(execute.call_args.kwargs['timeout'],105)


if __name__=='__main__':unittest.main()
