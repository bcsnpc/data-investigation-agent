"""Physical-read identity belongs to reservation, including nested SQL guards."""
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import Mock,patch
from scan_estate_graph import Meter,READ_OBSERVER

class NestedMeterTests(unittest.TestCase):
    def test_outer_request_keeps_its_ordinal_while_inner_requests_complete(self):
        state=Mock();state.get.return_value={'body':{'policy':{},'round_policy':{}}}
        observations=[]
        # Authority is injected; the actual Meter must allocate and retain its
        # ordinal before invoking a read that admits nested physical requests.
        mode=SimpleNamespace(active=lambda:True,purpose=lambda default:'INVESTIGATION')
        with patch.dict(sys.modules,{'investigator.build_phase':mode}),patch('investigator.shared_usage.SharedUsage') as authority:
            meter=Meter(state,{'environment':'existing-budget'},100)
            token=READ_OBSERVER.set(lambda name,body:observations.append((name,body)))
            try:
                result=meter(lambda:[meter(lambda:{'guard':2}),meter(lambda:{'guard':3}),meter(lambda:{'quantity':4})])
            finally:READ_OBSERVER.reset(token);meter.close()
            self.assertEqual(authority.return_value.reserve.call_count,4)
            self.assertEqual(authority.return_value.settle.call_count,4)
        self.assertEqual([body['ordinal'] for _,body in observations],[2,3,4,1])
        self.assertEqual([name for name,_ in observations],['physical_read:2','physical_read:3','physical_read:4','physical_read:1'])
        self.assertEqual(observations[-1][1]['result'],result)
        self.assertEqual(len({body['ordinal']for _,body in observations}),4)

if __name__=='__main__':unittest.main()
