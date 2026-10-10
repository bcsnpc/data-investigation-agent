import base64
import copy
import json
import unittest
from unittest.mock import Mock
from report_list_worker import read

W='11111111-1111-4111-8111-111111111111'
T='22222222-2222-4222-8222-222222222222'
P='33333333-3333-4333-8333-333333333333'


class ReaderMetadataTests(unittest.TestCase):
    def setUp(self):
        self.reader={'mode':'isolated_reader','tenant_id':T,'principal_id':P,
            'account':'reader@example.com','workspace_ids':[W]}
        self.claims={'oid':P,'tid':T,'aud':'https://analysis.windows.net/powerbi/api',
            'upn':'reader@example.com'}
        self.request={'endpoint':'groups/'+W+'/reports','workspace_ids':[W],'reader':self.reader}
        self.http_calls=[];self.application=Mock(return_value='isolated-cache')
        self.token=Mock(side_effect=lambda *args:'header.'+base64.urlsafe_b64encode(json.dumps(self.claims).encode()).decode().rstrip('=')+'.signature')
        def factory(tokens,*,meter):
            def send(endpoint,*,audience):
                tokens.get_token('https://analysis.windows.net/powerbi/api/.default')
                self.http_calls.append((endpoint,audience))
                return {'status_code':200,'text':{'value':[]}}
            return send
        self.factory=factory

    def run_read(self,request=None):return read(request or self.request,application=self.application,
        token=self.token,http_factory=self.factory,meter=Mock())

    def test_reader_identity_and_powerbi_audience_are_explicit(self):
        result=self.run_read()
        self.token.assert_called_once_with('isolated-cache','reader@example.com',T,
                                           'https://analysis.windows.net/powerbi/api/.default')
        self.assertEqual(result['reader']['principal_id'],P)
        self.assertNotIn('access_token',json.dumps(result))
        self.assertEqual(self.http_calls,[(self.request['endpoint'],'powerbi')])

    def test_wrong_principal_tenant_audience_or_account_refuses(self):
        for key,value in [('oid',T),('tid',P),('aud','https://database.windows.net/'),('upn','admin@example.com')]:
            with self.subTest(key=key):
                original=copy.deepcopy(self.claims);self.claims[key]=value
                with self.assertRaises(ValueError):self.run_read()
                self.claims=original
        self.assertEqual(self.http_calls,[])

    def test_no_arbitrary_host_or_mutation_endpoint(self):
        for endpoint in ['https://api.powerbi.com/anything','groups/'+W+'/datasets',
                         'groups/'+W+'/reports?other=1','groups/'+T+'/reports']:
            with self.subTest(endpoint=endpoint):
                with self.assertRaises(ValueError):self.run_read({**self.request,'endpoint':endpoint})
        self.token.assert_not_called()

    def test_reader_scope_cannot_be_broadened_in_request(self):
        request={**self.request,'workspace_ids':[W,T]}
        with self.assertRaisesRegex(ValueError,'allowlist'):self.run_read(request)
        self.token.assert_not_called()

    def test_extra_profile_or_publisher_fallback_not_accepted(self):
        with self.assertRaises(ValueError):self.run_read({**self.request,'publisher':True})
        self.token.assert_not_called()


if __name__=='__main__':unittest.main()
