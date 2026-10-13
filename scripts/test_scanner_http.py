import json
import unittest
from unittest.mock import Mock,patch

from investigator.adapters import scanner_identity as auth
from investigator.adapters.scanner_http import ScannerHttp,channel
from investigator.adapters.graph_dependencies import query
from investigator.live_gateway import Gateway,GatewayDenied,configured
from test_scanner_guardrails import DECL,W,M,OTHER,FAB,PBI,permissions,ScannerGuardrailTests


class Response:
    def __init__(self,body,status=200,headers=None):
        self.content=json.dumps(body).encode();self.status=status;self.headers=headers or {}
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def read(self,n):return self.content[:n]


class ScannerTransportTests(ScannerGuardrailTests):
    def policy(self,grants):
        return {'version':1,'live_enabled':True,'identities':{channel(DECL):permissions(grants)}}
    def grant(self,url,method='GET',purpose='scanner_metadata'):
        return {'method':method,'url':url,'purpose':purpose}
    def transport(self,opener):
        tokens=auth.Tokens(DECL,managed=Mock());tokens.get_token=Mock(return_value='fake-bearer')
        meter=Mock(side_effect=lambda f:f())
        return ScannerHttp(tokens,meter=meter,opener=opener),tokens,meter

    def test_rejected_request_never_acquires_token_or_runs_meter(self):
        url=FAB+f'workspaces/{W}/items'
        with auth.job(DECL,[W],kind='SCAN'),configured(self.policy([self.grant(url)])):
            opener=Mock();http,tokens,meter=self.transport(opener)
            with self.assertRaises(GatewayDenied):http(f'workspaces/{W}/items/{M}/updateDefinition','post',body={})
            tokens.get_token.assert_not_called();meter.assert_not_called();opener.open.assert_not_called()

    def test_exact_native_definition_polls_are_bound_only_for_this_job(self):
        path=f'workspaces/{W}/reports/{M}/getDefinition';url=FAB+path
        policy=self.policy([self.grant(url,'POST')]);poll=FAB+'operations/'+OTHER
        with auth.job(DECL,[W],kind='CHANGE_DETECTION'),configured(policy):
            opener=Mock();opener.open.side_effect=[Response({},202,{'x-ms-operation-id':OTHER}),Response({'status':'Succeeded'}),Response({'definition':{}})]
            http,tokens,meter=self.transport(opener)
            http(path,'post');http('operations/'+OTHER);http('operations/'+OTHER+'/result')
            self.assertEqual(meter.call_count,3)
            self.assertEqual([v.args[0].full_url for v in opener.open.call_args_list],[url,poll,poll+'/result'])
            with self.assertRaises(GatewayDenied):http('operations/'+M)
            with self.assertRaises(GatewayDenied):http('operations/'+OTHER,'post')
        with auth.job(DECL,[W],kind='CHANGE_DETECTION'),configured(policy):
            with self.assertRaises(GatewayDenied):Gateway(policy).http(channel(DECL),'GET',poll)

    def test_continuation_cannot_change_host_workspace_path_or_add_operations(self):
        path=f'workspaces/{W}/items';url=FAB+path
        bad=[f'https://evil.invalid/v1/{path}?continuationToken=x',FAB+f'workspaces/{OTHER}/items?continuationToken=x',
             FAB+path+'/../items?continuationToken=x',url+'?continuationToken=x&refresh=true']
        for follow in bad:
            with self.subTest(follow=follow),auth.job(DECL,[W],kind='SCAN'),configured(self.policy([self.grant(url)])):
                opener=Mock();opener.open.return_value=Response({'continuationUri':follow})
                http,_,_=self.transport(opener)
                with self.assertRaises(ValueError):http(path)
                self.assertEqual(opener.open.call_count,1)
        with auth.job(DECL,[W],kind='SCAN'),configured(self.policy([self.grant(url)])):
            opener=Mock();opener.open.side_effect=[Response({'continuationToken':'a/b & c'}),Response({'value':[]})]
            http,_,_=self.transport(opener);http(path)
            http(path+'?continuationToken=a%2Fb%20%26%20c')
            self.assertEqual(opener.open.call_count,2)

    def test_operator_grant_alone_cannot_cross_workspace_via_opaque_poll(self):
        for url in (FAB+'operations/'+OTHER,PBI+'admin/workspaces/scanResult/'+OTHER):
            with self.subTest(url=url),auth.job(DECL,[W],kind='SCAN'):
                with self.assertRaisesRegex(GatewayDenied,'SCANNER_RESPONSE_BINDING_REQUIRED'):
                    Gateway(self.policy([self.grant(url)])).http(channel(DECL),'GET',url)

    def test_response_size_and_workspace_scope_fail_closed(self):
        url=FAB+f'workspaces/{W}/items';value=self.policy([self.grant(url)])
        value['identities'][channel(DECL)]['scanner']['workspaces'].append(OTHER)
        with auth.job(DECL,[OTHER],kind='SCAN'),configured(value):
            opener=Mock();http,tokens,meter=self.transport(opener)
            with self.assertRaises(GatewayDenied):http(f'workspaces/{W}/items')
            tokens.get_token.assert_not_called();meter.assert_not_called()
        with auth.job(DECL,[W],kind='SCAN'),configured(value):
            opener=Mock();opener.open.return_value=Response({'value':'a'*100})
            http,_,_=self.transport(opener);http.max_bytes=20
            with self.assertRaisesRegex(ValueError,'RESPONSE_BOUND'):http(f'workspaces/{W}/items')

    def test_modern_dax_route_closes_shape_scope_and_query(self):
        url=PBI+f'datasets/{M}/executeDaxQueries';policy=self.policy([self.grant(url,'POST','scanner_dax')]);g=Gateway(policy)
        body={'query':query('CALCULATIONS',10),'queryTimeout':120,'resultSetRowCountLimit':11}
        with auth.job(DECL,[W],kind='SCAN'):
            g.http(channel(DECL),'POST',url,body)
            changes=[{'queryTimeout':121},{'queryTimeout':True},{'resultSetRowCountLimit':1002},
                     {'effectiveUsername':'admin'},{'schemaOnly':True},{'memoryLimit':1},{'query':'EVALUATE Sales'}]
            for change in changes:
                with self.subTest(change=change),self.assertRaises(GatewayDenied):g.http(channel(DECL),'POST',url,{**body,**change})
            outside=PBI+f'datasets/{OTHER}/executeDaxQueries'
            with self.assertRaises(GatewayDenied):Gateway(self.policy([self.grant(outside,'POST','scanner_dax')])).http(channel(DECL),'POST',outside,body)

    def test_scheduled_wrapper_is_only_explicit_scanner_mode_and_resets_on_error(self):
        import scan_estate_graph as script
        config={'authentication':DECL,'workspace':W}
        def execute(_):
            auth.require_job(DECL,[W]);raise RuntimeError('test failure')
        with patch.object(script,'_execute_one_scoped',side_effect=execute):
            with self.assertRaisesRegex(RuntimeError,'test failure'):script._execute_one(config)
        with self.assertRaises(PermissionError):auth.require_job(DECL)
        with patch.object(script,'_execute_one_scoped',return_value='ordinary')as ordinary:
            self.assertEqual(script._execute_one({'authentication':{'mode':'federated_reader'}}),'ordinary')
            ordinary.assert_called_once()


if __name__=='__main__':unittest.main()
