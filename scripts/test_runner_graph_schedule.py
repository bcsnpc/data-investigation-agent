import copy
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from investigator.adapters.runner_graph_schedule import plan,apply,validate_pair,costs,GRAPH_CRON,DAILY_CRON
from investigator.adapters.runner_schedule import plan as daily_plan,bind_execution
from test_runner_schedule import ScheduleTests


class IndependentSchedules(unittest.TestCase):
    def inputs(self):
        config,job=ScheduleTests().config()
        job['location']='South Central US'
        job['identity']={'type':'UserAssigned','userAssignedIdentities':{'/existing/worker-mi':{'clientId':'already-existing'}}}
        job['properties']['environmentId']='/existing/container-environment'
        job['properties']['provisioningState']='Succeeded'
        container=job['properties']['template']['containers'][0]
        container['resources']={'cpu':0.5,'memory':'1Gi'}
        container['name']='worker'
        graph={'estate':'fixture','workspace':'fixture','owners':{},'authentication':{},'storage':{},
               'definition_uri_prefix':'retained','budget':{},'max_requests':50,'approval':'Existing owner-approved scope'}
        gateway=json.loads(config['environment']['DIA_PLATFORM_GATEWAY_POLICY'])
        container['env'].extend([{'name':'DIA_GRAPH_SCAN_CONFIG','value':json.dumps(graph)},
                                 {'name':'DIA_GRAPH_SCAN_GATEWAY','value':json.dumps(gateway)}])
        return config,job

    def readbacks(self,prepared,job,config):
        daily=copy.deepcopy(job)
        daily['properties'].update(daily_plan(config,job)['body']['properties'])
        daily['properties']['provisioningState']='Succeeded'
        graph={'id':prepared['resource_id'],**copy.deepcopy(prepared['body'])}
        graph['properties']['provisioningState']='Succeeded'
        return daily,graph

    def test_new_job_preserves_retained_scope_without_changing_daily(self):
        config,job=self.inputs();before=copy.deepcopy((config,job));prepared=plan(job,config)
        self.assertEqual((config,job),before)
        self.assertEqual(prepared['method'],'PUT');self.assertTrue(prepared['resource_id'].endswith('/job-dia-graph-scan'))
        self.assertEqual(prepared['new_roles'],[])
        body=prepared['body'];container=body['properties']['template']['containers'][0]
        self.assertEqual(body['identity'],{'type':'UserAssigned','userAssignedIdentities':{'/existing/worker-mi':{}}})
        self.assertEqual(body['properties']['environmentId'],job['properties']['environmentId'])
        self.assertEqual(container['resources'],{'cpu':0.5,'memory':'1Gi'})
        self.assertEqual(body['properties']['configuration']['replicaTimeout'],1800)
        self.assertEqual(body['properties']['configuration']['scheduleTriggerConfig']['cronExpression'],GRAPH_CRON)
        self.assertEqual(container['command'],['python','/app/scripts/dia.py','run','graph','--estate','/work/runner-estate.json','--runtime','worker'])
        env={v['name']:v['value'] for v in container['env']}
        self.assertNotIn('DIA_GRAPH_SCAN_CONFIG',env);self.assertNotIn('DIA_GRAPH_SCAN_GATEWAY',env)
        runner=json.loads(env['DIA_RUNNER_ESTATE_JSON'])
        old_env={v['name']:v['value']for v in job['properties']['template']['containers'][0]['env']}
        self.assertEqual(runner['checks'],{'graph':{'kind':'scan','options':{'config':json.loads(old_env['DIA_GRAPH_SCAN_CONFIG'])}}})
        old_gateway=json.loads(old_env['DIA_GRAPH_SCAN_GATEWAY'])
        actual_gateway=json.loads(runner['environment']['DIA_PLATFORM_GATEWAY_POLICY'])
        old_gateway['identities']['worker:state']['runner_captures']=actual_gateway['identities']['worker:state']['runner_captures']
        self.assertEqual(actual_gateway,old_gateway)
        one,two=bind_execution(runner),bind_execution(runner)
        self.assertNotEqual(one['run_id'],two['run_id'])

    def test_empty_resource_enrichment_is_not_an_extra_allocation(self):
        config,job=self.inputs();prepared=plan(job,config);daily,graph=self.readbacks(prepared,job,config)
        graph['properties']['template']['containers'][0]['resources']['ephemeralStorage']=''
        self.assertEqual(validate_pair(daily,graph,image=config['image'])['status'],'PASS')
        graph['properties']['template']['containers'][0]['resources']['gpu']=1
        with self.assertRaisesRegex(ValueError,'RESOURCES_DIFFER'):validate_pair(daily,graph,image=config['image'])

    def test_combined_cost_is_bounded_without_free_grants(self):
        cost=costs();self.assertEqual(cost['combined_monthly_usd'],'19.077133')
        self.assertEqual(cost['graph_vCPU_seconds'],31*4*1800*.5)
        self.assertEqual(cost['graph_GiB_seconds'],31*4*1800)
        self.assertFalse(cost['free_grants_assumed'])
        with self.assertRaisesRegex(ValueError,'EXCEED_PLATFORM'):costs(platform='16')
        with self.assertRaisesRegex(ValueError,'INVALID'):costs(graph='NaN')

    def test_preflight_requires_both_independent_schedules(self):
        config,job=self.inputs();prepared=plan(job,config);daily,graph=self.readbacks(prepared,job,config)
        self.assertEqual(validate_pair(daily,graph,image=config['image'])['status'],'PASS')
        for left,right in ((None,graph),(daily,None)):
            with self.assertRaisesRegex(ValueError,'SCHEDULES_REQUIRED'):validate_pair(left,right)
        for which in ('daily','graph'):
            wrong=copy.deepcopy(daily if which=='daily'else graph)
            wrong['properties']['configuration']['triggerType']='Manual'
            with self.assertRaisesRegex(ValueError,'MISSING_OR_DIFFERS'):
                validate_pair(wrong,graph) if which=='daily'else validate_pair(daily,wrong)
        with self.assertRaisesRegex(ValueError,'DISTINCT'):validate_pair(daily,daily)
        graph['properties']['provisioningState']='Failed'
        with self.assertRaisesRegex(ValueError,'NOT_SUCCEEDED'):validate_pair(daily,graph)

    def test_retired_wrapper_cannot_satisfy_schedule_preflight(self):
        config,job=self.inputs();prepared=plan(job,config);daily,graph=self.readbacks(prepared,job,config)
        graph['properties']['template']['containers'][0]['command']=['python','scripts/graph_scan_bootstrap.py']
        with self.assertRaisesRegex(ValueError,'TYPED_RUNNER_REQUIRED'):validate_pair(daily,graph)

    def test_identity_environment_image_and_size_are_checked(self):
        config,job=self.inputs();prepared=plan(job,config);daily,graph=self.readbacks(prepared,job,config)
        for mutation,reason in ((lambda x:x['identity'].update(userAssignedIdentities={'other':{}}),'IDENTITY'),
                                (lambda x:x['properties'].update(environmentId='other'),'ENVIRONMENT'),
                                (lambda x:x['properties']['template']['containers'][0].update(image='other'),'IMAGE'),
                                (lambda x:x['properties']['template']['containers'][0].update(resources={'cpu':1,'memory':'2Gi'}),'RESOURCES')):
            wrong=copy.deepcopy(graph);mutation(wrong)
            with self.assertRaisesRegex(ValueError,reason):validate_pair(daily,wrong,image=config['image'])

    def test_apply_uses_one_approved_put_then_reads_both_without_other_writes(self):
        config,job=self.inputs();prepared=plan(job,config);daily,graph=self.readbacks(prepared,job,config)
        calls=[]
        def execute(argv,**kwargs):
            calls.append(argv)
            if 'PUT' in argv:
                self.assertEqual(json.loads(Path(argv[argv.index('--body')+1][1:]).read_bytes()),prepared['body'])
                return SimpleNamespace(stdout='')
            return SimpleNamespace(stdout=json.dumps(graph if argv[argv.index('--ids')+1]==graph['id']else daily))
        with patch('investigator.build_phase.admit_platform'):
            result=apply(prepared,execute=execute)
        self.assertEqual(result['status'],'APPLIED');self.assertEqual(len(calls),3)
        self.assertEqual(sum('PUT'in call for call in calls),1)
        self.assertEqual(result['validation']['daily']['cron'],DAILY_CRON)
        self.assertTrue(all('role'not in call and 'identity'not in call for call in calls))

    def test_pending_creation_polls_without_repeating_put_and_missing_daily_fails(self):
        config,job=self.inputs();prepared=plan(job,config);daily,graph=self.readbacks(prepared,job,config)
        calls=[];waits=[];graph_reads=0
        def execute(argv,**kwargs):
            nonlocal graph_reads
            calls.append(argv)
            if 'PUT'in argv:return SimpleNamespace(stdout='')
            if argv[argv.index('--ids')+1]==graph['id']:
                graph_reads+=1;value=copy.deepcopy(graph)
                value['properties']['provisioningState']='Updating'if graph_reads==1 else'Succeeded'
            else:value=daily
            return SimpleNamespace(stdout=json.dumps(value))
        with patch('investigator.build_phase.admit_platform'):
            self.assertEqual(apply(prepared,execute=execute,sleep=waits.append)['readback_attempts'],2)
        self.assertEqual(waits,[30]);self.assertEqual(sum('PUT'in c for c in calls),1)
        daily['properties']['configuration']['triggerType']='Manual'
        with patch('investigator.build_phase.admit_platform'),self.assertRaisesRegex(ValueError,'MISSING_OR_DIFFERS'):
            apply(prepared,execute=execute)


if __name__=='__main__':unittest.main()
