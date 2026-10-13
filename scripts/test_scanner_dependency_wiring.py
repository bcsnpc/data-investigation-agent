import copy
import json
import unittest
from unittest.mock import Mock,patch

from scan_estate_graph import scanner_dependencies,validate
from investigator.adapters import scanner_identity as auth
from investigator.adapters.scanner_http import channel
from investigator.adapters.graph_dependencies import FUNCTIONS
from investigator.live_gateway import configured
from test_scanner_guardrails import DECL,W,M,OTHER,PBI,permissions
from test_graph_dax_http import ipc


class DependencyWiringTests(unittest.TestCase):
    def config(self):
        return {'estate':'synthetic','workspace':W,'owners':[M,OTHER], 'authentication':DECL,'storage':{},
            'definition_uri_prefix':'cas://definitions','budget':{},'max_requests':30,'approval':'owner',
            'dependency_models':[M]}
    def test_only_operator_selected_models_and_scanner_auth_accepted(self):
        for changes in ({'dependency_models':[M,M]},{'dependency_models':[W]},
                        {'authentication':{**DECL,'mode':'federated_reader'}},
                        {'sql':[{'identity':'ordinary','config':{},'objects':{}}]}):
            config={**self.config(),**changes}
            with self.subTest(changes=changes),self.assertRaises(ValueError):validate(config)
        with self.assertRaises(PermissionError):scanner_dependencies(self.config(),Mock(declaration=DECL),Mock(),Mock())

    def test_real_arrow_gateway_and_meter_for_four_fixed_queries(self):
        receipts=[];calls=[];token_calls=[]
        class Tokens(auth.Tokens):
            def get_token(self,scope):token_calls.append(scope);return 'FAKE_SECRET'
        class Response:
            status=200;headers={'Content-Type':'application/vnd.apache.arrow.stream'}
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self,n):return ipc([{'TABLE':'T','OBJECT':'M'}])
        class Opener:
            def open(self,request,timeout):calls.append(request);return Response()
        def sink(raw):
            import hashlib
            receipts.append(raw);return {'sha256':hashlib.sha256(raw).hexdigest()}
        identity=channel(DECL);url=PBI+f'datasets/{M}/executeDaxQueries'
        policy={'version':1,'live_enabled':True,'identities':{identity:permissions([{'method':'POST','url':url,'purpose':'scanner_dax'}])}}
        meter=Mock(side_effect=lambda call:call())
        with auth.job(DECL,[W],kind='CHANGE_DETECTION'),configured(policy),patch('investigator.adapters.graph_dax_http.build_opener',return_value=Opener()):
            callback=scanner_dependencies(self.config(),Tokens(DECL),meter,sink)
            self.assertEqual(callback({'workspace':W,'model':OTHER}),[])
            self.assertEqual(meter.call_count,0)
            with self.assertRaises(ValueError):callback({'workspace':OTHER,'model':M})
            results=callback({'workspace':W,'model':M})
        self.assertEqual([r['request']['kind']for r in results],list(FUNCTIONS))
        self.assertTrue(all(r['status']=='COLLECTED'for r in results))
        self.assertEqual(meter.call_count,4);self.assertEqual(len(calls),4);self.assertEqual(len(receipts),4)
        self.assertNotIn(b'FAKE_SECRET',b''.join(receipts))
        self.assertTrue(all(set(json.loads(request.data))=={'query','queryTimeout','resultSetRowCountLimit'}for request in calls))
        unchanged=self.config();unchanged.pop('dependency_models')
        self.assertIsNone(scanner_dependencies(unchanged,Mock(),Mock(),Mock()))


if __name__=='__main__':unittest.main()
