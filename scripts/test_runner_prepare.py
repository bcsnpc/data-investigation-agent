import copy,json,unittest
from investigator.runner_prepare import probe_plan
from test_managed_sql_worker import AUTH

class PrepareTests(unittest.TestCase):
    def inputs(self):
        mi=copy.deepcopy(AUTH)
        auth={'mode':'federated_reader','client_id':AUTH['client_id'],'principal_id':AUTH['principal_id'],'tenant_id':AUTH['tenant_id'],'managed_identity':mi}
        job={'id':'/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/rg/providers/Microsoft.App/jobs/existing',
             'properties':{'template':{'containers':[{'env':[{'name':k,'value':v} for k,v in {'INVESTIGATOR_PG_HOST':'pg.test','INVESTIGATOR_PG_DATABASE':'state','INVESTIGATOR_PG_USER':'worker'}.items()]}]}}}
        sql={'server':'endpoint.test','database':'bronze','objects':['[dbo].[movements]','[dbo].[rates]'],'read_only':True,'row_cap':251,'timeout_seconds':30,'controls':['PREWARM']}
        gateway={'version':1,'live_enabled':True,'identities':{'investigation':{'sql':[sql]},'worker:state':{'role':'platform','platform_databases':[{'host':'pg.test','database':'state'}]},'snapshots':{'role':'platform'},'tapes':{'role':'platform'},'federated:'+AUTH['tenant_id']+':'+AUTH['client_id']+':sql':{'http':[]}}}
        slim={'version':'slim-recording-v1','account_url':'https://synthetic.blob.core.windows.net','identity':mi,'snapshot_channel':'snapshots','tape_channel':'tapes','tape_class':'EXACT'}
        probe={'server':'endpoint.test','database':'bronze','authentication':auth,'request':{'query':'SELECT units FROM dbo.movements','read_only_objects':['[dbo].[movements]'],'max_rows':2,'result_columns':['units']},'provenance':{'tape_sha256':'b'*64}}
        return job,gateway,probe,slim
    def test_preparation_narrows_existing_scope_and_hydrates_public_environment(self):
        inputs=self.inputs();before=copy.deepcopy(inputs)
        plan=probe_plan(*inputs,image='registry/worker@sha256:'+'a'*64,run_id='test-run',cli=['python','-m','azure.cli'],budget_environment='existing-budget')
        self.assertEqual(inputs,before)
        gateway=json.loads(plan['environment']['DIA_PLATFORM_GATEWAY_POLICY'])
        self.assertEqual(gateway['identities']['investigation']['sql'][0]['objects'],['[dbo].[movements]'])
        self.assertEqual(gateway['identities']['investigation']['sql'][0]['controls'],[])
        self.assertEqual(gateway['identities']['worker:state']['runner_captures'][0]['run_id'],'test-run')
        self.assertEqual(plan['checks']['bronze']['options']['budget'],{'environment':'existing-budget'})
        self.assertNotIn('model',gateway['identities'])
        self.assertNotIn('bootstrap',plan)
    def test_preparation_cannot_add_an_object_permission(self):
        inputs=self.inputs();inputs[2]['request']['read_only_objects']=['[dbo].[different]']
        with self.assertRaisesRegex(ValueError,'OBJECT_SCOPE_EXPANSION'):
            probe_plan(*inputs,image='registry/worker@sha256:'+'a'*64,run_id='test-run',cli=['python','-m','azure.cli'],budget_environment='existing-budget')

if __name__=='__main__':unittest.main()
