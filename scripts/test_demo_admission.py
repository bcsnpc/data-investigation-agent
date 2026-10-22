"""Demo controls do not reintroduce network-blocking long writer leases."""
import copy,json,os,tempfile,time,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock,patch
from cloud_runner_context import demo_state_admission
from investigator.adapters.runner_deployment import launch
from investigator.shared_state import SharedState,TRANSACTION_ACTIVE
from investigator.shared_writer_lease import LEASE_ENV
from investigator.live_gateway import _network_unlocked,GatewayDenied


class DemoStateAdmissionTests(unittest.TestCase):
    def test_actual_short_transaction_commits_before_external_dispatch_and_deadline_restores(self):
        with tempfile.TemporaryDirectory() as folder:
            state=SharedState.offline(Path(folder)/'state.sqlite');state.migrate()
            now=time.time();ctx=SimpleNamespace(started_at=now-30,record=Mock())
            with patch.dict(os.environ,{'INVESTIGATOR_CLOUD_WORK_DEADLINE':str(now+2000)}):
                previous=os.environ['INVESTIGATOR_CLOUD_WORK_DEADLINE']
                with demo_state_admission({'run_id':'actual-run'},ctx) as admission:
                    state.put('synthetic','budget',{'settled':True})
                    self.assertFalse(TRANSACTION_ACTIVE.get());self.assertNotIn(LEASE_ENV,os.environ)
                    _network_unlocked() # Same check used by every live gateway/worker launch.
                    self.assertEqual(now+2000,admission['deadline'])
                    self.assertEqual(str(now+2000),os.environ['INVESTIGATOR_CLOUD_WORK_DEADLINE'])
                self.assertEqual(previous,os.environ['INVESTIGATOR_CLOUD_WORK_DEADLINE'])
            rows={c.args[0]:c.args[1]for c in ctx.record.call_args_list}
            self.assertFalse(rows['demo-state-admission']['transaction_active'])
            self.assertFalse(rows['demo-state-finalization']['legacy_lease_installed'])

    def test_failure_records_finalization_and_restores_deadline_without_replacing_primary(self):
        ctx=SimpleNamespace(started_at=time.time(),record=Mock())
        before=os.environ.get('INVESTIGATOR_CLOUD_WORK_DEADLINE')
        with self.assertRaisesRegex(RuntimeError,'worker failed'):
            with demo_state_admission({'run_id':'failing-run'},ctx):raise RuntimeError('worker failed')
        self.assertEqual(before,os.environ.get('INVESTIGATOR_CLOUD_WORK_DEADLINE'))
        self.assertEqual('FAILED',ctx.record.call_args_list[-1].args[1]['status'])

    def test_expired_absolute_deadline_or_existing_lock_refuses_before_work(self):
        ctx=SimpleNamespace(started_at=time.time()-3601,record=Mock())
        with self.assertRaisesRegex(ValueError,'DEADLINE_EXPIRED'):
            with demo_state_admission({'run_id':'late'},ctx):self.fail('No admission')
        ctx.record.assert_not_called()
        ctx.started_at=time.time()
        with patch.dict(os.environ,{LEASE_ENV:'legacy'}):
            with self.assertRaises(GatewayDenied):
                with demo_state_admission({'run_id':'locked'},ctx):self.fail('No admission')
        marker=TRANSACTION_ACTIVE.set(True)
        try:
            with self.assertRaises(GatewayDenied):
                with demo_state_admission({'run_id':'transaction'},ctx):self.fail('No admission')
        finally:TRANSACTION_ACTIVE.reset(marker)


class DemoLaunchAdmissionTests(unittest.TestCase):
    def config(self):
        return {'checks':{'demo':{'kind':'investigation','options':{'verification_proof':{}}}},'run_id':'demo-run',
            'deployment':{'resource_id':'/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/existing-rg/providers/Microsoft.App/jobs/job-dia-worker','cli':['az']},
            'image':'registry/image@sha256:'+'a'*64}
    def job(self,timeout=3600):
        return {'properties':{'configuration':{'replicaTimeout':timeout},'template':{'containers':[{'name':'worker','image':'old'}]}}}
    def test_live_readback_runtime_and_no_competing_job_are_checked_before_start(self):
        config=self.config();job=self.job();before=copy.deepcopy(job);calls=[]
        def execute(args,**kwargs):
            calls.append(args)
            if 'show'in args:return SimpleNamespace(stdout=json.dumps(job))
            if 'list'in args:
                self.assertEqual(60,kwargs['timeout'])
                return SimpleNamespace(stdout=json.dumps([{'name':'previous','properties':{'status':'Failed'}}]))
            return SimpleNamespace(stdout=json.dumps({'name':'new-demo-execution'}))
        with patch('investigator.build_phase.admit_platform'):
            result=launch(config,'demo',execute=execute)
        self.assertEqual('ADMITTED',result['demo_admission']['status']);self.assertEqual(4,len(calls))
        self.assertEqual(2,sum('list'in c for c in calls));self.assertEqual(job,before)
        self.assertIn('not excluded',result['demo_admission']['limitation'])

    def test_short_runtime_or_running_job_refuses_without_start_or_scope_change(self):
        for timeout,rows,reason in [(1800,[],'RUNTIME_BELOW'),(3600,[{'properties':{'status':'Running'}}],'COMPETING'),(3600,[{'name':'unknown'}],'STATUS_UNESTABLISHED')]:
            calls=[]
            def execute(args,**kwargs):
                calls.append(args)
                if 'show'in args:return SimpleNamespace(stdout=json.dumps(self.job(timeout)))
                if 'list'in args:return SimpleNamespace(stdout=json.dumps(rows))
                self.fail('Never start or change a resource after refused controls')
            with self.subTest(reason=reason),patch('investigator.build_phase.admit_platform'):
                with self.assertRaisesRegex(ValueError,reason):launch(self.config(),'demo',execute=execute)
            self.assertFalse(any('start'in c or 'update'in c for c in calls))


if __name__=='__main__':unittest.main()
