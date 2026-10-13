import copy
import os
import unittest
from unittest.mock import Mock,patch
from investigator.adapters.binding_catalog import request_many
from investigator.live_gateway import configured, authorize_sql_payload, GatewayDenied
from test_vault_user_cache import D


OBJECTS=[{'connection':'server','database':'database','catalog':{'metadata':{
    'schema_name':'dbo','name':name}}} for name in ('movements','rates')]
POLICY={'version':1,'live_enabled':True,'identities':{'reader':{'sql':[{
    'server':'server','database':'database','read_only':True,'row_cap':251,
    'timeout_seconds':30,'objects':['dbo.movements','dbo.rates'],'controls':['CATALOG']}]}}}


class CatalogGatewayTests(unittest.TestCase):
    def setUp(self):
        env=patch.dict(os.environ,{'DIA_LIVE_ACCESS_DISABLED':'0','DIA_GATEWAY_SQL_IDENTITY':'reader'})
        env.start();self.addCleanup(env.stop)
        self.payload=request_many(OBJECTS)|{'server':'server','database':'database'}

    def test_exact_compiler_catalog_keeps_user_table_guards_and_no_sys_authority(self):
        with configured(POLICY):answer=authorize_sql_payload(self.payload)
        self.assertTrue(answer['require_read_only'])
        self.assertEqual(answer['read_only_objects'],['[dbo].[movements]','[dbo].[rates]'])
        self.assertEqual(answer['query'],self.payload['query'])

    def test_every_changed_query_parameter_shape_and_permission_refuses(self):
        changes=[lambda p:p.update(query=p['query']+'; SELECT 1'),
            lambda p:p.update(query=p['query'].replace('TOP 250','TOP 251')),
            lambda p:p.update(query='SELECT * FROM sys.tables'),
            lambda p:p['parameters'][0].update(value='secret_schema'),
            lambda p:p['parameters'].reverse(),lambda p:p.update(max_rows=252),
            lambda p:p['result_columns'].reverse(),lambda p:p['read_only_objects'].pop()]
        for change in changes:
            payload=copy.deepcopy(self.payload);change(payload)
            with configured(POLICY),self.assertRaises(GatewayDenied):authorize_sql_payload(payload)
        for change in (lambda p:p['identities']['reader']['sql'][0].update(controls=[]),
                       lambda p:p['identities']['reader']['sql'][0].update(objects=['dbo.movements']),
                       lambda p:p['identities']['reader']['sql'][0].update(row_cap=250),
                       lambda p:p['identities']['reader']['sql'][0].update(timeout_seconds=29),
                       lambda p:p.update(live_enabled=False)):
            policy=copy.deepcopy(POLICY);change(policy)
            with configured(policy),self.assertRaises(GatewayDenied):authorize_sql_payload(self.payload)

    def test_worker_establishes_permission_guards_on_each_real_table(self):
        import managed_sql_worker as worker
        from test_managed_identity_auth import IDENTITY
        from test_managed_sql_worker import Cursor
        class CatalogCursor(Cursor):
            def execute(self,query,*args):
                super().execute(query,*args)
                if query==worker.IDENTITY:self.rows=[('reader','database')]
                if query.startswith('SELECT TOP 250'):
                    self.description=[(key,str) for key in self_payload['result_columns']]
                    self.rows=[('dbo','movements','quantity','int',None)]
                return self
        self_payload=self.payload
        cursor=CatalogCursor();connection=Mock();connection.cursor.return_value=cursor
        with configured(POLICY):
            result=worker.execute(self.payload|{'authentication':IDENTITY},
                connect=Mock(return_value=connection),tokens=Mock(get_token=Mock(return_value='private-token')))
        self.assertTrue(result['read_only_verified'])
        guards=[args[0] for query,args in cursor.calls if query==worker.OBJECT_GUARD]
        self.assertEqual(guards,['[dbo].[movements]','[dbo].[rates]'])

    def test_cloud_reader_is_configured_without_claiming_authentication_or_calling_cli(self):
        from fabric_sql_surface import reader_availability
        from test_managed_identity_auth import IDENTITY
        for reader in (D|{'server':'server'},IDENTITY|{'server':'server','account':'reader'}):
            with patch('fabric_sql_auth.session_status',side_effect=AssertionError('No CLI')), \
                    patch('investigator.adapters.vault_user_cache.Tokens',side_effect=AssertionError('No auth call')):
                result=reader_availability({'fabric':{'sql_reader':reader,'auth':{'tenant_id':reader['tenant_id']}}})
            self.assertEqual(result['status'],'CONFIGURED')
            self.assertFalse(result['authentication_verified']);self.assertFalse(result['permission_verified'])

    def test_configured_transport_declares_probe_capability_not_an_observed_result(self):
        from test_independent_lower_read import Harness
        harness=Harness()
        harness.adapter.lower_surface={'status':'CONFIGURED','authentication_verified':False,'permission_verified':False}
        self.assertIn('independent_lower_surface',harness.adapter.capabilities())
        self.assertEqual(harness.lower_calls,[])
        harness.adapter.lower_surface={'status':'SIGN_IN_REQUIRED'}
        self.assertNotIn('independent_lower_surface',harness.adapter.capabilities())


if __name__=='__main__':unittest.main()
