import copy,json,unittest
from cloud_job_admission import admit,isolation
from cloud_stage_environment import build
from test_cloud_stage_environment import STAGE,POLICY,PLATFORM,SLIM

OBS={'observed_at':1000,'job':{'id':'/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/rg-test/providers/Microsoft.App/jobs/job-test',
    'properties':{'configuration':{'replicaTimeout':1800,'triggerType':'Manual'}}}}
LEASE={'owner':'verify-test','lease_id':'one-isolated-attempt','expires_at':2900}
ISOLATION={'observed_at':1000,'executions':[],'scheduled_job':OBS['job'],'advisory_lock_holders':0,
           'lease':dict(LEASE,status='ACTIVE')}
WINDOW={'run_admitted_at':1000,'overall_run_deadline':2800}

class AdmissionTests(unittest.TestCase):
    def test_1200_deadline_cannot_use_600_second_job(self):
        observed=copy.deepcopy(OBS);observed['job']['properties']['configuration']['replicaTimeout']=600
        before=copy.deepcopy(observed)
        with self.assertRaisesRegex(ValueError,'RUNTIME_MUST_MATCH'):
            admit({**WINDOW,'deadline':2200,'required_runtime_seconds':1800,'finalization_reserve_seconds':600},observed,now=1000)
        self.assertEqual(observed,before)
    def test_exact_bound_allowed_without_changing_settings(self):
        receipt=admit({**WINDOW,'deadline':2200,'required_runtime_seconds':1800,'finalization_reserve_seconds':600},OBS,now=1000)
        self.assertEqual(receipt['remaining_deadline_seconds'],1200)
        self.assertEqual(receipt['finalization_reserve_seconds'],600)
        self.assertFalse(receipt['platform_settings_changed'])
    def test_missing_stale_or_invalid_observation_refused(self):
        variants=[None,{},dict(OBS,observed_at=699),dict(OBS,observed_at=1001)]
        missing=copy.deepcopy(OBS);del missing['job']['properties']['configuration']['replicaTimeout'];variants.append(missing)
        for value in variants:
            with self.subTest(value=value),self.assertRaises(ValueError):admit({'deadline':1200,'required_runtime_seconds':1800},value,now=1000)
        for value in (float('nan'),float('inf'),True,1000):
            with self.subTest(deadline=value),self.assertRaises(ValueError):admit({'deadline':value,'required_runtime_seconds':1800},OBS,now=1000)
    def test_launch_builder_cannot_emit_verify_environment_without_admission(self):
        stage=dict(STAGE,**WINDOW,phase='verify',deadline=2900,required_runtime_seconds=1800,exclusive_writer=LEASE,finalization_reserve_seconds=600)
        kwargs=dict(worker_id='verify-test',ceiling_microdollars=20,margin_microdollars=10,admission_now=1000)
        with self.assertRaisesRegex(ValueError,'OBSERVATION_REQUIRED'):build(stage,POLICY,PLATFORM,SLIM,**kwargs)
        with self.assertRaisesRegex(ValueError,'DEADLINE_EXCEEDS_JOB_TIMEOUT'):
            build(stage,POLICY,PLATFORM,SLIM,job_observation=OBS,**kwargs)
        stage['deadline']=2200
        with self.assertRaisesRegex(ValueError,'ISOLATION_OBSERVATION_REQUIRED'):
            build(stage,POLICY,PLATFORM,SLIM,job_observation=OBS,**kwargs)
        result=build(stage,POLICY,PLATFORM,SLIM,job_observation=OBS,isolation_observation=ISOLATION,**kwargs)
        env={r['name']:r['value']for r in result['env']}
        self.assertEqual(json.loads(env['DIA_CLOUD_JOB_ADMISSION'])['replica_timeout_seconds'],1800)
        self.assertEqual(env['INVESTIGATOR_EXCLUSIVE_LEASE_ID'],LEASE['lease_id'])
        self.assertEqual(env['INVESTIGATOR_CLOUD_WORK_DEADLINE'],'2200')
    def test_inner_deadline_cannot_consume_reserved_finalization_time(self):
        for deadline,reserve in ((2800,600),(2200,0),(2201,600)):
            with self.subTest(deadline=deadline,reserve=reserve),self.assertRaisesRegex(ValueError,'FINALIZATION_RESERVE'):
                admit({**WINDOW,'deadline':deadline,'required_runtime_seconds':1800,'finalization_reserve_seconds':reserve},OBS,now=1000)
    def test_overall_deadline_duration_must_match_observed_runtime(self):
        for overall in (2200,2801):
            with self.assertRaisesRegex(ValueError,'OVERALL_DEADLINE_MUST_MATCH'):
                admit(dict(WINDOW,overall_run_deadline=overall,deadline=2200,required_runtime_seconds=1800,finalization_reserve_seconds=600),OBS,now=1000)
    def test_isolation_rejects_active_job_schedule_lock_or_short_lease(self):
        stage={'exclusive_writer':LEASE,'required_runtime_seconds':1800}
        bad=[]
        active=copy.deepcopy(ISOLATION);active['executions']=[{'properties':{'status':'Running'}}];bad.append(active)
        schedule=copy.deepcopy(ISOLATION);schedule['scheduled_job']['properties']['configuration']['triggerType']='Schedule';bad.append(schedule)
        locked=copy.deepcopy(ISOLATION);locked['advisory_lock_holders']=1;bad.append(locked)
        short=copy.deepcopy(ISOLATION);short['lease']['expires_at']=2700;bad.append(short)
        stale=copy.deepcopy(ISOLATION);stale['observed_at']=100;bad.append(stale)
        for value in bad:
            with self.subTest(value=value),self.assertRaises(ValueError):isolation(stage,value,now=1000)

if __name__=='__main__':unittest.main()
