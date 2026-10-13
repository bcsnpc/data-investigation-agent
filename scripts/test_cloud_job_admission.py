import copy,json,unittest
from cloud_job_admission import admit
from cloud_stage_environment import build
from test_cloud_stage_environment import STAGE,POLICY,PLATFORM,SLIM

OBS={'observed_at':1000,'job':{'id':'/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/rg-test/providers/Microsoft.App/jobs/job-test',
    'properties':{'configuration':{'replicaTimeout':600}}}}

class AdmissionTests(unittest.TestCase):
    def test_1200_deadline_cannot_use_600_second_job(self):
        before=copy.deepcopy(OBS)
        with self.assertRaisesRegex(ValueError,'DEADLINE_EXCEEDS_JOB_TIMEOUT'):
            admit({'deadline':2200},OBS,now=1000)
        self.assertEqual(OBS,before)
    def test_exact_bound_allowed_without_changing_settings(self):
        receipt=admit({'deadline':1600},OBS,now=1000)
        self.assertEqual(receipt['remaining_deadline_seconds'],600)
        self.assertFalse(receipt['platform_settings_changed'])
    def test_missing_stale_or_invalid_observation_refused(self):
        variants=[None,{},dict(OBS,observed_at=699),dict(OBS,observed_at=1001)]
        missing=copy.deepcopy(OBS);del missing['job']['properties']['configuration']['replicaTimeout'];variants.append(missing)
        for value in variants:
            with self.subTest(value=value),self.assertRaises(ValueError):admit({'deadline':1200},value,now=1000)
        for value in (float('nan'),float('inf'),True,1000):
            with self.subTest(deadline=value),self.assertRaises(ValueError):admit({'deadline':value},OBS,now=1000)
    def test_launch_builder_cannot_emit_verify_environment_without_admission(self):
        stage=dict(STAGE,phase='verify',deadline=2200)
        kwargs=dict(worker_id='verify-test',ceiling_microdollars=20,margin_microdollars=10,admission_now=1000)
        with self.assertRaisesRegex(ValueError,'OBSERVATION_REQUIRED'):build(stage,POLICY,PLATFORM,SLIM,**kwargs)
        with self.assertRaisesRegex(ValueError,'DEADLINE_EXCEEDS_JOB_TIMEOUT'):
            build(stage,POLICY,PLATFORM,SLIM,job_observation=OBS,**kwargs)
        stage['deadline']=1500
        result=build(stage,POLICY,PLATFORM,SLIM,job_observation=OBS,**kwargs)
        env={r['name']:r['value']for r in result['env']}
        self.assertEqual(json.loads(env['DIA_CLOUD_JOB_ADMISSION'])['replica_timeout_seconds'],600)

if __name__=='__main__':unittest.main()
