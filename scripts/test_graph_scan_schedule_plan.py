import copy
import unittest
from graph_scan_schedule_plan import build


class PlanTests(unittest.TestCase):
    def setUp(self):
        env={name:'retained-public-value' for name in ('INVESTIGATOR_STATE_BACKEND','INVESTIGATOR_PG_HOST','INVESTIGATOR_PG_DATABASE','INVESTIGATOR_PG_USER','AZURE_CLIENT_ID','DIA_GATEWAY_STATE_IDENTITY','DIA_GATEWAY_HTTP_IDENTITY')}
        self.job={'id':'/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/rg-test/providers/Microsoft.App/jobs/existing-job',
            'properties':{'configuration':{'triggerType':'Manual','manualTriggerConfig':{'parallelism':1,'replicaCompletionCount':1},'replicaTimeout':1200},
                'template':{'containers':[{'name':'worker','image':'old','resources':{'cpu':2,'memory':'4Gi'},'env':[{'name':k,'value':v}for k,v in env.items()]}]}}}
        self.config={key:{} for key in ('estate','workspace','owners','authentication','storage','definition_uri_prefix','budget','max_requests')}
        self.config['approval']='Owner approval 2026-10-13';self.gateway={'version':1,'live_enabled':False,'identities':{}}
        self.image='ghcr.io/example/worker@sha256:'+'a'*64
    def test_plan_preserves_scope_and_environment_and_bounds_compute(self):
        before=copy.deepcopy(self.job);result=build(self.job,self.config,self.gateway,self.image)
        self.assertEqual(self.job,before);self.assertEqual(result['method'],'PATCH')
        self.assertNotIn('identity',result['body'])
        template=result['body']['properties']['template']['containers'][0]
        self.assertEqual(template['resources'],{'cpu':2,'memory':'4Gi'})
        self.assertEqual(template['env'][:7],before['properties']['template']['containers'][0]['env'])
        self.assertEqual(result['compute_upper_bound_30_days']['vCPU_seconds'],144000)
        self.assertEqual(result['body']['properties']['configuration']['replicaRetryLimit'],0)
        self.assertEqual(template['command'],['python','scripts/graph_scan_bootstrap.py'])
    def test_mutable_image_and_new_resource_shape_refused(self):
        with self.assertRaisesRegex(ValueError,'PINNED'):build(self.job,self.config,self.gateway,'ghcr.io/example/worker:latest')
        self.job['id']='/subscriptions/other/resources/new'
        with self.assertRaisesRegex(ValueError,'EXISTING'):build(self.job,self.config,self.gateway,self.image)
    def test_platform_environment_cannot_be_invented(self):
        self.job['properties']['template']['containers'][0]['env']=[]
        with self.assertRaisesRegex(ValueError,'ENVIRONMENT_MISSING'):build(self.job,self.config,self.gateway,self.image)


if __name__=='__main__':unittest.main()
