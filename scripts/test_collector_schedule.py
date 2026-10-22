import copy
import json
import unittest
from cloud_facts_dispatcher import execute, select
from investigator.adapters.collector_schedule import plan, preflight, estimate


def configs():
    return [{'estate':estate,'authentication':{},'storage':{},'receipt_uri_prefix':'offline',
        'budget':{},'subjects':{'node':{'kind':'MODEL','workspace':'0'*8+'-'+'0'*4+'-'+'0'*4+'-'+'0'*4+'-'+'0'*12,'item':'1'*8+'-'+'1'*4+'-'+'1'*4+'-'+'1'*4+'-'+'1'*12}},
        'max_requests':8,'approval':'owner-approved test','list_interval_seconds':21600,
        'max_subjects_per_wake':2} for estate in ['fixture','billing','sample']]


class State:
    backend='postgresql'
    def __init__(self):self.rows={}
    def get(self,n,k):return self.rows[n,k]
    def put(self,n,k,b,revision=None):self.rows[n,k]={'body':b,'revision':1 if revision is None else revision+1}


def source():
    return {'id':'/subscriptions/'+'a'*8+'-'+'a'*4+'-'+'a'*4+'-'+'a'*4+'-'+'a'*12+'/resourceGroups/rg/providers/Microsoft.App/jobs/job-dia-worker',
        'location':'southcentralus','identity':{'type':'UserAssigned','userAssignedIdentities':{'existing-mi':{'principalId':'existing'}}},
        'properties':{'environmentId':'existing-env','configuration':{'replicaTimeout':1800,'triggerType':'Schedule',
            'scheduleTriggerConfig':{'cronExpression':'0 6 * * *'}},
            'template':{'containers':[{'name':'worker','image':'old','resources':{'cpu':0.5,'memory':'1Gi'},'env':[]}]}}}


class CollectorScheduleTests(unittest.TestCase):
    def runner(self):return {'image':'registry/worker@sha256:'+'a'*64,'per_execution':True,'environment':{},
        'checks':{'collect':{'kind':'facts-dispatcher','options':{'configs':configs()}}}}

    def test_round_robin_one_estate_per_wake_and_shared_scan_label(self):
        state=State();calls=[]
        results=[execute(configs(),state=state,collector=lambda c:calls.append(c['estate']) or {'physical_requests':2}) for _ in range(4)]
        self.assertEqual(calls,['billing','fixture','sample','billing'])
        self.assertTrue(all(len(r['other_estates_not_read'])==2 and r['purpose']=='SCAN' for r in results))

    def test_no_cursor_advance_after_failed_collection(self):
        state=State()
        def fail(c):raise ValueError('retained failure')
        with self.assertRaisesRegex(ValueError,'retained failure'):execute(configs(),state=state,collector=fail)
        self.assertEqual(state.rows,{})

    def test_request_listing_and_subject_bounds_cannot_be_widened(self):
        for key,value in [('max_requests',9),('list_interval_seconds',1800),('max_subjects_per_wake',3)]:
            with self.subTest(key=key):
                c=configs();c[0][key]=value
                with self.assertRaisesRegex(ValueError,'ALLOWANCE'):select(c,State())

    def test_duplicate_estate_refuses(self):
        with self.assertRaisesRegex(ValueError,'DUPLICATE'):select([configs()[0],configs()[0]],State())

    def test_plan_preserves_source_and_existing_schedules(self):
        original=source();before=copy.deepcopy(original);p=plan(original,self.runner())
        self.assertEqual(original,before);self.assertEqual(p['new_roles'],[])
        self.assertEqual(p['existing_schedules_unchanged'],['job-dia-worker','job-dia-graph-scan'])
        self.assertEqual(p['cost']['combined_monthly_usd'],'19.76673300')
        self.assertEqual(p['body']['identity']['userAssignedIdentities'],{'existing-mi':{}})
        readback={'id':p['resource_id'],**p['body']}
        self.assertEqual(preflight(readback,original)['status'],'PASS')

    def test_preflight_rejects_missing_schedule_resource_or_environment(self):
        original=source();p=plan(original,self.runner());readback={'id':p['resource_id'],**p['body']}
        for mutation in [lambda j:j['properties']['configuration']['scheduleTriggerConfig'].clear(),
            lambda j:j['properties']['template']['containers'][0]['resources'].update(cpu=0.5),
            lambda j:j['properties'].update(environmentId='another'),
            lambda j:j['properties'].update(provisioningState='Failed')]:
            altered=copy.deepcopy(readback);mutation(altered)
            with self.assertRaises(ValueError):preflight(altered,original)

    def test_unpinned_or_nonunique_capture_refuses(self):
        for key,value in [('image','worker:latest'),('per_execution',False)]:
            r=self.runner();r[key]=value
            with self.assertRaises(ValueError):plan(source(),r)

    def test_preflight_rejects_wrong_executable_or_unpinned_image(self):
        original=source();p=plan(original,self.runner());readback={'id':p['resource_id'],**p['body']}
        for field,value in [('command',['python','arbitrary.py']),('image','worker:latest')]:
            altered=copy.deepcopy(readback);altered['properties']['template']['containers'][0][field]=value
            with self.assertRaisesRegex(ValueError,'TYPED_PINNED'):preflight(altered,original)

    def test_combined_estimate_must_fit_monthly_cap(self):
        with self.assertRaisesRegex(ValueError,'EXCEEDS_20'):estimate(base='19.5')


if __name__=='__main__':unittest.main()
