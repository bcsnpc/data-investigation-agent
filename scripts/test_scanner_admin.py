import hashlib
import json
import unittest
from unittest.mock import Mock

from investigator.adapters import scanner_identity as auth
from investigator.adapters.scanner_admin import collect,ENDPOINT
from investigator.adapters.scanner_http import ScannerHttp,channel
from investigator.adapters.metadata_error import MetadataUnavailable
from investigator.live_gateway import configured,GatewayDenied
from test_scanner_guardrails import DECL,W,M,OTHER,PBI,permissions
from test_scanner_http import Response
from test_scanner_dependency_wiring import DependencyWiringTests


class AdminScannerTests(unittest.TestCase):
    def setUp(self):
        self.raw=[]
        self.sink=lambda raw:(self.raw.append(json.loads(raw)),{'sha256':hashlib.sha256(raw).hexdigest()})[1]
        self.config={'authentication':DECL,'workspace':W,'admin_metadata':True}
    def test_actual_transport_only_response_bound_poll_and_result_are_sent(self):
        url=PBI+ENDPOINT;policy={'version':1,'live_enabled':True,'identities':{channel(DECL):permissions([{'method':'POST','url':url,'purpose':'scanner_metadata'}])}}
        opener=Mock();opener.open.side_effect=[Response({'id':M,'status':'NotStarted'},202),
            Response({'id':M,'status':'Running'}),Response({'id':M,'status':'Succeeded'}),Response({'workspaces':[{'id':W,'datasets':[]}]})]
        meter=Mock(side_effect=lambda call:call());sleep=Mock()
        with auth.job(DECL,[W],kind='SCAN'),configured(policy):
            tokens=auth.Tokens(DECL);tokens.get_token=Mock(return_value='FAKE_SECRET')
            http=ScannerHttp(tokens,meter=meter,opener=opener)
            result=collect(self.config,http,self.sink,sleep=sleep)
        self.assertEqual(result['status'],'COLLECTED');self.assertEqual(result['requests'],4)
        self.assertEqual(meter.call_count,4);sleep.assert_called_once_with(2)
        self.assertEqual(len(result['receipts']),4);self.assertFalse(result['graph_evidence_admitted'])
        self.assertNotIn('FAKE_SECRET',json.dumps(self.raw));self.assertEqual(result['wait_seconds'],2)
        self.assertEqual(self.raw[0]['request']['body'],{'workspaces':[W]})

    def test_empty_and_foreign_results_do_not_establish_coverage(self):
        for workspaces in ([],[{'id':OTHER}],[{'id':W},{'id':OTHER}]):
            http=Mock(side_effect=[{'status_code':202,'text':{'id':M}},
                {'status_code':200,'text':{'id':M,'status':'Succeeded'}},{'status_code':200,'text':{'workspaces':workspaces}}])
            with auth.job(DECL,[W],kind='SCAN'):result=collect(self.config,http,self.sink,sleep=Mock())
            self.assertEqual(result['status'],'UNKNOWN');self.assertFalse(result['graph_evidence_admitted'])

    def test_permission_refusal_retained_and_poll_bound_not_retried(self):
        http=Mock(side_effect=MetadataUnavailable(403,{'error':{'code':'Forbidden'}}))
        with auth.job(DECL,[W],kind='SCAN'):result=collect(self.config,http,self.sink,sleep=Mock())
        self.assertEqual(result['failure']['http_status'],403);self.assertEqual(len(result['receipts']),1)
        self.assertEqual(result['status'],'UNKNOWN');http.assert_called_once()
        http=Mock(side_effect=[{'status_code':202,'text':{'id':M}}]+[{'status_code':200,'text':{'id':M,'status':'Running'}}]*8)
        sleep=Mock()
        with auth.job(DECL,[W],kind='SCAN'):result=collect(self.config,http,self.sink,sleep=sleep)
        self.assertEqual(result['status'],'UNKNOWN');self.assertEqual(http.call_count,9);self.assertEqual(sleep.call_count,7)

    def test_optin_scanner_job_required_and_guard_failures_escape(self):
        from scan_estate_graph import validate
        config=DependencyWiringTests().config();config['admin_metadata']='yes'
        with self.assertRaises(ValueError):validate(config)
        config['admin_metadata']=True;config['authentication']={**DECL,'mode':'federated_reader'}
        with self.assertRaises(ValueError):validate(config)
        with self.assertRaises(PermissionError):collect(self.config,Mock(),self.sink)
        self.assertEqual(collect({},Mock(),self.sink)['status'],'NOT_REQUESTED')
        for error in (GatewayDenied('blocked'),ValueError('GRAPH_PHYSICAL_REQUEST_CAP')):
            with auth.job(DECL,[W],kind='SCAN'),self.assertRaises(type(error)):
                collect(self.config,Mock(side_effect=error),self.sink,sleep=Mock())


if __name__=='__main__':unittest.main()
