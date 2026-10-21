import copy,json,tempfile,unittest
import subprocess
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from investigator.adapters.runner_schedule import bind_execution,plan,apply
from test_runner_prepare import PrepareTests
from investigator.runner_prepare import probe_plan

class ScheduleTests(unittest.TestCase):
    def config(self):
        job,gateway,probe,slim=PrepareTests().inputs()
        job['properties']['configuration']={'triggerType':'Schedule','replicaTimeout':1800,'replicaRetryLimit':0,'scheduleTriggerConfig':{'cronExpression':'0 */6 * * *','parallelism':1,'replicaCompletionCount':1}}
        config=probe_plan(job,gateway,probe,slim,image='registry/worker@sha256:'+'a'*64,run_id='daily-template',cli=['python','-m','azure.cli'],budget_environment='budget')
        config['per_execution']=True
        config['checks']['daily']={'kind':'smoke','options':{'config':{'run_id':'daily-template','demo_earned':False},'budget':{},'max_requests':10}}
        config['schedule']={'target':'daily','platform_monthly_usd':'14.82','smoke_monthly_usd':'0.857'}
        return config,job
    def test_each_execution_gets_distinct_health_and_exact_capture_binding(self):
        config,job=self.config();original=copy.deepcopy(config)
        one=bind_execution(config);two=bind_execution(config)
        self.assertNotEqual(one['run_id'],two['run_id'])
        self.assertEqual(config,original)
        for actual in (one,two):
            self.assertEqual(actual['checks']['daily']['options']['config']['run_id'],actual['run_id'])
            gateway=json.loads(actual['environment']['DIA_PLATFORM_GATEWAY_POLICY'])
            grant=gateway['identities']['worker:state']['runner_captures'][0]
            self.assertEqual(grant['run_id'],actual['run_id'])
            from investigator.live_gateway import Gateway,GatewayDenied
            g=Gateway(gateway);url=grant['account_url']+'/captures/'+grant['prefix']+'/'+grant['run_id']+'/00000001-header.json'
            with patch.dict('os.environ',{'DIA_LIVE_ACCESS_DISABLED':'0'}):
                g.http('worker:state','HEAD',url)
                with self.assertRaises(GatewayDenied):g.http('worker:state','HEAD',url.replace(grant['run_id'],'daily-template'))
    def test_daily_plan_costs_first_and_replaces_existing_schedule_only(self):
        config,job=self.config();before=copy.deepcopy(job)
        result=plan(config,job)
        self.assertEqual(job,before)
        self.assertEqual(result['prior_schedule']['cronExpression'],'0 */6 * * *')
        self.assertEqual(result['new_schedule']['cronExpression'],'0 6 * * *')
        self.assertEqual(result['new_resources'],[])
        self.assertEqual(result['cost']['monthly_platform_estimate_usd'],'15.677')
        config['schedule']['smoke_monthly_usd']='6'
        with self.assertRaisesRegex(ValueError,'EXCEEDS_PLATFORM'):plan(config,job)
    def test_apply_uses_existing_cli_and_readback_no_new_role_or_identity(self):
        config,job=self.config();calls=[]
        after=None
        def execute(argv,**kwargs):
            nonlocal after
            calls.append(argv)
            if 'show' in argv:return SimpleNamespace(stdout=json.dumps(after or job))
            body=json.loads(Path(argv[argv.index('--body')+1][1:]).read_bytes())
            self.assertEqual(set(body),{'properties'})
            after={'properties':body['properties']}
            return SimpleNamespace(stdout='')
        with patch.dict('sys.modules',{'investigator.build_phase':SimpleNamespace(admit_platform=lambda *a:None)}):
            result=apply(config,execute=execute)
        self.assertEqual(result['status'],'APPLIED')
        self.assertEqual(len(calls),3)
        self.assertEqual(calls[1][:5],['python','-m','azure.cli','rest','--method'])
        self.assertIn('show',calls[2]);self.assertEqual(result['readback_attempts'],1)

    def test_get_only_image_type_is_not_echoed_into_patch(self):
        config,job=self.config()
        job['properties']['template']['containers'][0]['imageType']='ContainerImage'
        job['properties']['configuration']['dapr']=None
        before=copy.deepcopy(job);result=plan(config,job)
        self.assertNotIn('imageType',result['body']['properties']['template']['containers'][0])
        self.assertNotIn('dapr',result['body']['properties']['configuration'])
        self.assertEqual(job,before)
        self.assertEqual(result['body']['properties']['template']['containers'][0]['image'],config['image'])

    def test_async_patch_polls_updating_twice_without_repeating_patch(self):
        config,job=self.config();calls=[];waits=[];after=None;readbacks=0
        def execute(argv,**kwargs):
            nonlocal after,readbacks
            calls.append(argv)
            if 'show' in argv:
                if after is None:return SimpleNamespace(stdout=json.dumps(job))
                readbacks+=1
                result=copy.deepcopy(after)
                result['properties']['provisioningState']='Updating' if readbacks<3 else 'Succeeded'
                return SimpleNamespace(stdout=json.dumps(result))
            body=json.loads(Path(argv[argv.index('--body')+1][1:]).read_bytes())
            after={'properties':body['properties']}
            return SimpleNamespace(stdout='')
        with patch.dict('sys.modules',{'investigator.build_phase':SimpleNamespace(admit_platform=lambda *a:None)}):
            result=apply(config,execute=execute,sleep=waits.append)
        self.assertEqual(waits,[30,45]);self.assertEqual(result['readback_attempts'],3)
        self.assertEqual(len(calls),5)
        self.assertEqual(sum('PATCH' in call for call in calls),1)

    def test_patch_failure_retains_exact_safe_stderr_after_successful_show(self):
        from investigator.adapters.control_failure import ControlCommandFailure
        config,job=self.config();calls=[]
        stderr='ERROR: (InvalidRequestContent) The request content was invalid.\r\nAdditional detail: expected properties.\r\n'
        def execute(argv,**kwargs):
            calls.append(argv)
            if len(calls)==1:return SimpleNamespace(stdout=json.dumps(job))
            raise subprocess.CalledProcessError(1,argv,output='{"error":{"code":"InvalidRequestContent"}}\n',stderr=stderr)
        with patch.dict('sys.modules',{'investigator.build_phase':SimpleNamespace(admit_platform=lambda *a:None)}),self.assertRaises(ControlCommandFailure) as caught:
            apply(config,execute=execute)
        self.assertEqual(len(calls),2)
        self.assertEqual(caught.exception.receipt['operation'],'schedule-patch')
        self.assertEqual(caught.exception.receipt['stderr'],stderr)
        self.assertFalse(caught.exception.receipt['stderr_redacted'])
        self.assertTrue(caught.exception.__suppress_context__)

if __name__=='__main__':unittest.main()
