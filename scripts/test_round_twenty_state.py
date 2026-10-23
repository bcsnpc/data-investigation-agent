import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import Mock, patch

from investigator.postgres_connection import connect
from investigator.shared_state import SharedState, TRANSACTION_ACTIVE
from investigator.live_gateway import Gateway, GatewayDenied
from investigator.shared_writer_lease import isolated, LEASE_ENV, OWNER_ENV
from investigator.daily_smoke import run_smoke, schedule_plan, _blob_roundtrip


class ConnectionTests(unittest.TestCase):
    def test_connect_timeout_retries_with_bounded_startup_settings(self):
        result = object()
        factory = Mock(side_effect=[TimeoutError('connection'), result])
        sleep = Mock()
        self.assertIs(connect(connector=factory, sleep=sleep, host='platform', options='-c search_path=dia_state'), result)
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [30])
        self.assertEqual(factory.call_count, 2)
        for call in factory.call_args_list:
            self.assertEqual(call.kwargs['connect_timeout'], 15)
            self.assertEqual({k:call.kwargs[k]for k in ('keepalives','keepalives_idle','keepalives_interval','keepalives_count')},
                             {'keepalives':1,'keepalives_idle':30,'keepalives_interval':10,'keepalives_count':3})
            self.assertIn('statement_timeout=30000', call.kwargs['options'])
            self.assertIn('idle_in_transaction_session_timeout=30000', call.kwargs['options'])
    def test_authorisation_is_never_retried_and_second_timeout_propagates(self):
        for error, expected in [(PermissionError('authentication'), 1), (TimeoutError('connection'), 2)]:
            factory, sleep = Mock(side_effect=error), Mock()
            with self.assertRaises(type(error)): connect(connector=factory, sleep=sleep)
            self.assertEqual(factory.call_count, expected)
    def test_statement_execution_is_not_replayed(self):
        db = Mock(); factory = Mock(return_value=db)
        db.execute.side_effect=TimeoutError('statement timeout')
        opened=connect(connector=factory, sleep=Mock())
        with self.assertRaises(TimeoutError): opened.execute('SELECT 1')
        self.assertEqual(factory.call_count, 1)
    def test_drop_records_idle_interval_without_sql_arguments_or_replaying(self):
        from investigator.postgres_connection import ObservedConnection
        factory=Mock();factory.execute.side_effect=[object(),ConnectionError('dropped')]
        clock=Mock(side_effect=[0,1,2,42,43,43]);db=ObservedConnection(factory,clock=clock)
        db.execute('SELECT 1')
        with self.assertRaises(ConnectionError)as failure:db.execute('SELECT private_data',('do-not-log',))
        timing=failure.exception.postgres_connection_timing
        self.assertEqual(timing['idle_before_request_seconds'],40)
        self.assertEqual(timing['failed_request_seconds'],1)
        self.assertNotIn('do-not-log',str(failure.exception.__notes__))
        self.assertNotIn('private_data',str(failure.exception.__notes__))
        self.assertEqual(factory.execute.call_count,2)
    def test_shared_transactions_close_before_external_work_and_open_fresh(self):
        first,second=Mock(),Mock();factory=Mock(side_effect=[first,second])
        state=SharedState(factory,backend='postgresql',mode='live')
        with patch('investigator.shared_writer_lease.check'):
            with state.transaction()as db:db.execute('SELECT 1')
            first.close.assert_called_once()
            self.assertFalse(TRANSACTION_ACTIVE.get())
            # A long Fabric call belongs here, with no PG connection held.
            with state.transaction()as db:db.execute('SELECT 2')
        self.assertEqual(factory.call_count,2);second.close.assert_called_once()
    def test_commit_drop_also_has_idle_diagnostics_without_replay(self):
        from investigator.postgres_connection import ObservedConnection
        raw=Mock();raw.commit.side_effect=ConnectionError('ack lost')
        db=ObservedConnection(raw,clock=Mock(side_effect=[0,10,11,11]))
        with self.assertRaises(ConnectionError)as failure:db.commit()
        self.assertEqual(failure.exception.postgres_connection_timing['operation'],'commit')
        self.assertEqual(failure.exception.postgres_connection_timing['idle_before_request_seconds'],10)
        raw.commit.assert_called_once()
    def test_safe_read_reconnects_once_but_put_never_replays(self):
        from contextlib import nullcontext
        state=SharedState(Mock(),backend='postgresql',mode='live')
        failure=ConnectionError('lost response');failure.postgres_connection_timing={'idle_before_request_seconds':41}
        with patch.object(state,'transaction',side_effect=lambda:nullcontext(Mock()))as transaction,patch.object(state,'_get',side_effect=[failure,{'revision':1,'body':{}}]),patch('time.sleep')as sleep:
            self.assertEqual(state.get('namespace','id')['revision'],1)
            self.assertEqual(transaction.call_count,2);sleep.assert_called_once_with(30)
        self.assertEqual(state.connection_failures[0]['connection_timing']['idle_before_request_seconds'],41)
        with patch.object(state,'transaction',side_effect=lambda:nullcontext(Mock()))as transaction,patch.object(state,'_get',side_effect=ConnectionError('drop')),patch('time.sleep')as sleep:
            with self.assertRaises(ConnectionError):state.put('namespace','id',{})
            self.assertEqual(transaction.call_count,1);sleep.assert_not_called()


class LockTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'state.sqlite';self.state=SharedState.offline(self.path);self.state.migrate()
        self.env=patch.dict(os.environ);self.env.start();self.addCleanup(self.env.stop)
        os.environ.pop(LEASE_ENV,None)
        self.gateway=Gateway({'version':1,'live_enabled':True,'identities':{}})
    def test_estate_and_model_authorisation_is_denied_while_budget_transaction_open(self):
        for invoke in [lambda:self.gateway.http('model','POST','https://model.example'),
                       lambda:self.gateway.sql('reader','sql','db','SELECT 1'),
                       lambda:self.gateway.native_control('reader','XMLA_EVALUATE',{}),
                       lambda:self.gateway.sql_control('reader','sql','db','SELF_REPORT')]:
            with self.state.transaction():
                with self.assertRaisesRegex(GatewayDenied,'NETWORK_DURING_SHARED_STATE_TRANSACTION'): invoke()
        self.assertFalse(TRANSACTION_ACTIVE.get())
        with self.assertRaisesRegex(GatewayDenied,'IDENTITY_NOT_ALLOWED'):
            self.gateway.sql('reader','sql','db','SELECT 1')
    def test_parent_refuses_worker_before_spawn_inside_transaction(self):
        from investigator.physical_reads import run
        fallback=Mock()
        with self.state.transaction():
            with self.assertRaisesRegex(GatewayDenied,'NETWORK_DURING_SHARED_STATE_TRANSACTION'):
                run(['worker'],input='{}',timeout=30,fallback=fallback)
        fallback.assert_not_called()
    def test_legacy_writer_lease_cannot_cover_a_network_call_and_exception_releases_it(self):
        with self.assertRaisesRegex(GatewayDenied,'NETWORK_DURING_EXCLUSIVE_WRITER_LEASE'):
            with isolated(self.state,owner='run',lease_id='lease',expires_at=time.time()+30,approval='test'):
                self.gateway.http('reader','GET','https://fabric.example')
        self.assertEqual(self.state.get('application_writer_lease','exclusive')['body']['status'],'RELEASED')
    def test_process_crash_cannot_leave_a_permanent_lease(self):
        command = ('from investigator.shared_state import SharedState;'
          'from investigator.shared_writer_lease import acquire;import os,time,sys;'
          's=SharedState.offline(sys.argv[1]);'
          'acquire(s,owner="crash",lease_id="dead",expires_at=time.time()+0.2,approval="test");'
          'os._exit(9)')
        child=subprocess.run([sys.executable,'-c',command,str(self.path)],
            env=dict(os.environ,PYTHONPATH=str(Path(__file__).parent)),timeout=10)
        self.assertEqual(child.returncode,9)
        time.sleep(0.3)
        # Crash bypasses finally; persisted expiry is authoritative, no manual unlock.
        self.state.put('after_crash','probe',{'ok':True})
        self.assertEqual(self.state.get('after_crash','probe')['body'],{'ok':True})


class SmokeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.state=SharedState.offline(Path(self.tmp.name)/'state.sqlite');self.state.migrate()
        auth={'principal_id':'reader'}
        self.config={'version':1,'run_id':'smoke-20261021','reader_authentication':auth,
                     'gold_payload':{'authentication':auth,'require_read_only':True,'query':'SELECT SUM(units) AS value FROM dbo.movements','read_only_objects':['[dbo].[movements]'],'result_columns':['value'],'max_rows':2},'platform_blob':{},'demo_earned':False}
        self.context=Mock();self.context.step.side_effect=lambda name,fn:fn()
    def test_smoke_roundtrips_own_database_and_blob_without_holding_transaction(self):
        def external(*args):
            self.assertFalse(TRANSACTION_ACTIVE.get());return {'status':'PASS'}
        result=run_smoke(self.config,self.context,state=self.state,sign_in=external,gold_read=external,blob_roundtrip=external)
        self.assertEqual(result['status'],'INCOMPLETE');self.assertFalse(result['demo_included'])
        self.assertEqual(result['checks']['check_access']['result']['rows'][0]['reason'],'ACCESS_CHECK_NOT_CONFIGURED')
        self.assertEqual(result['budget_line'],'collectors')
        self.assertEqual([call.args[0] for call in self.context.step.call_args_list],
                         ['check-access','sign_in','gold_read','postgres_write_read','blob_write_read'])
        # A transient retry with the same run identity remains safe and exercises a write.
        self.assertEqual(run_smoke(self.config,self.context,state=self.state,sign_in=external,gold_read=external,blob_roundtrip=external)['status'],'INCOMPLETE')
    def test_earned_demo_is_explicit_and_failure_has_no_sensitive_error_message(self):
        kwargs=dict(state=self.state,sign_in=lambda:{},gold_read=lambda _: {},blob_roundtrip=lambda *_:{})
        self.config['demo_earned']=True
        with self.assertRaisesRegex(ValueError,'EARNED_SMOKE_DEMO'):run_smoke(self.config,self.context,**kwargs)
        result=run_smoke(self.config,self.context,demo=lambda:(_ for _ in ()).throw(RuntimeError('secret password')),**kwargs)
        self.assertEqual(result['status'],'FAIL');self.assertNotIn('secret password',json.dumps(result))
        self.assertEqual(result['checks']['family_a_demo']['error_type'],'RuntimeError')
    def test_actual_blob_adapter_checks_manifest_and_chunk_readback(self):
        from investigator.artifact_store import LocalObjects
        objects=LocalObjects(Path(self.tmp.name)/'blobs')
        with patch('investigator.adapters.blob_artifacts.BlobObjects',return_value=objects), \
             patch('investigator.adapters.blob_artifacts.bound_credential'), patch('investigator.live_gateway.current'):
            result=_blob_roundtrip({'account_url':'https://platform.blob.core.windows.net','identity':{},'channel':'state'},b'health')
        self.assertEqual(result['status'],'PASS')
    def test_schedule_uses_existing_job_and_refuses_cost_above_twenty(self):
        kwargs=dict(resource_id='/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/g/providers/Microsoft.App/jobs/worker',image='registry/image@sha256:abc',platform_monthly_usd='14.83',smoke_monthly_usd='0.05')
        plan=schedule_plan(**kwargs)
        self.assertEqual(plan['cron_expression'],'0 6 * * *');self.assertEqual(plan['new_resources'],[])
        self.assertEqual(plan['monthly_platform_estimate_usd'],'14.88')
        with self.assertRaisesRegex(ValueError,'BUDGET'):schedule_plan(**dict(kwargs,smoke_monthly_usd='6'))
