import importlib.util,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from investigator import physical_reads
from investigator.usage_governance import UsageHold
from investigator import physical_transport_retry as retry
class Throttle(Exception):http_status=429
class Denied(Exception):http_status=403
class PhysicalRetryTests(unittest.TestCase):
    def test_each_retry_is_admitted_and_first_failed_receipt_preserved(self):
        sends=[];reservations=[];receipts=[]
        def meter(tool,call):
            reservations.append(tool)
            try:
                with physical_reads.scope(meter):return call()
            finally:receipts.append(tool)
        def transport(body):
            sends.append(body.copy())
            if len(sends)<3:raise Throttle('capacity')
            return {'value':16}
        with physical_reads.scope(meter) as state,patch.object(retry,'backoff',lambda n:None):
            self.assertEqual(retry.execute({'query':'sealed'},transport,'bounded_dax'),{'value':16})
            self.assertEqual(state['first_report']['status'],'FAILED')
        self.assertEqual(len(sends),3);self.assertEqual(reservations,['bounded_dax']*2);self.assertEqual(receipts,reservations)
        self.assertEqual(sends,[{'query':'sealed'}]*3)
    def test_cap_refuses_before_retry_and_permission_does_not_retry(self):
        calls=[]
        def refused(tool,call):raise UsageHold('Read deadline or cap')
        def send(body):calls.append(body);raise Throttle('capacity')
        with physical_reads.scope(refused),patch.object(retry,'backoff',lambda n:None),self.assertRaises(UsageHold):retry.execute({},send,'bounded_dax')
        self.assertEqual(len(calls),1)
        calls=[]
        def denied(body):calls.append(body);raise Denied('permission')
        with physical_reads.scope(refused),self.assertRaises(Denied):retry.execute({},denied,'bounded_dax')
        self.assertEqual(len(calls),1)
    def test_archived_v6_provider_retry_pin_does_not_enable_physical_retry(self):
        calls=[]
        def send(body):calls.append(body);raise Throttle('capacity')
        old=SimpleNamespace(replaying=True,bootstrap={'state':{'provider_transport_retries':2,'tape_version':6}})
        with physical_reads.scope(lambda tool,call:call()),patch.object(retry.journal,'ACTIVE',SimpleNamespace(get=lambda:old)),self.assertRaises(Throttle):retry.execute({},send,'bounded_dax')
        self.assertEqual(len(calls),1)
        with self.assertRaises(Throttle):retry.execute({},send,'bounded_dax')
        self.assertEqual(len(calls),2)
    def test_metadata_429_results_retry_under_physical_only_meter_and_frozen_request(self):
        calls=[];charged=[]
        def transport(request):
            calls.append(request)
            return {'status':'UNAVAILABLE','http_status':429} if len(calls)<3 else {'id':'fixture endpoint'}
        def meter(kind,call):
            charged.append((kind,True))
            with physical_reads.scope(meter):return call()
        with physical_reads.scope(meter) as first,patch.object(retry,'backoff',lambda n:None):
            self.assertEqual(retry.execute({'workspace':'fixture'},transport,'fabric_endpoint_metadata'),{'id':'fixture endpoint'})
            self.assertEqual(first['first_report']['http_status'],429)
        self.assertEqual(charged,[('fabric_endpoint_metadata',True)]*2)
        self.assertEqual(calls,[{'workspace':'fixture'}]*3)
    def test_metadata_cap_permission_and_archived_result_do_not_resend(self):
        calls=[]
        def transport(request):calls.append(request);return {'status':'UNAVAILABLE','http_status':429}
        def refused(kind,call):raise UsageHold('Physical cap reached')
        with physical_reads.scope(refused),patch.object(retry,'backoff',lambda n:None),self.assertRaises(UsageHold):retry.execute({},transport,'fabric_endpoint_metadata')
        self.assertEqual(len(calls),1)
        with physical_reads.scope(refused):
            self.assertEqual(retry.execute({},lambda request:{'status':'UNAVAILABLE','http_status':403},'fabric_endpoint_metadata'),{'status':'UNAVAILABLE','http_status':403})
        old=SimpleNamespace(replaying=True,bootstrap={'state':{'provider_transport_retries':2}})
        with physical_reads.scope(refused),patch.object(retry.journal,'ACTIVE',SimpleNamespace(get=lambda:old)):
            self.assertEqual(retry.execute({},transport,'fabric_endpoint_metadata'),{'status':'UNAVAILABLE','http_status':429})
        self.assertEqual(len(calls),2)
if __name__=='__main__':unittest.main()

