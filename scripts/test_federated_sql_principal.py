"""Federated reader display labels must not replace SQL's observed principal."""
import copy
import unittest
from investigator.adapters.sql_principal import expected
from investigator.adapters.binding_catalog import read, read_many
from fabric_sql_surface import declared


class FederatedSqlPrincipalTests(unittest.TestCase):
    def setUp(self):
        self.reader={'mode':'federated_reader','account':'reader-display-label','server':'endpoint',
            'client_id':'11111111-1111-4111-8111-111111111111',
            'tenant_id':'22222222-2222-4222-8222-222222222222',
            'principal_id':'33333333-3333-4333-8333-333333333333',
            'managed_identity':{'mode':'managed_identity',
                'client_id':'44444444-4444-4444-8444-444444444444',
                'tenant_id':'55555555-5555-4555-8555-555555555555',
                'principal_id':'66666666-6666-4666-8666-666666666666'}}
        self.principal=self.reader['client_id']+'@'+self.reader['tenant_id']
        self.config={'fabric':{'sql_reader':self.reader}}
        self.obj={'connection':'endpoint','database':'warehouse','asset_id':'table',
            'catalog':{'metadata':{'schema_name':'dbo','name':'items'}}}
        self.answer={'surface_report':{'identity':self.principal,'object':'warehouse',
                'engine':'Microsoft Azure SQL Data Warehouse'},'read_only_verified':True,
            'rows':[{'schema_name':'dbo','table_name':'items','column_name':'quantity',
                'data_type':'bigint','collation_name':None}]}

    def test_guarded_federated_catalog_preserves_exact_observed_evidence(self):
        original=copy.deepcopy(self.answer)
        result=read_many(self.config,[self.obj],execute=lambda *a:self.answer)
        self.assertEqual(result['table'][1]['surface_report'],original['surface_report'])
        self.assertEqual(self.answer,original)
        single=copy.deepcopy(self.answer)
        single['rows']=[{k:v for k,v in self.answer['rows'][0].items() if k not in ('schema_name','table_name')}]
        self.assertEqual(read(self.config,self.obj,execute=lambda *a:single)[1]['surface_report'],original['surface_report'])
        self.assertEqual(declared(self.reader,'warehouse')['identity'],self.principal)

    def test_display_label_wrong_app_wrong_tenant_and_oid_are_not_aliases(self):
        for identity in (self.reader['account'],self.reader['principal_id'],
                self.reader['principal_id']+'@'+self.reader['tenant_id'],
                self.reader['client_id']+'@'+self.reader['managed_identity']['tenant_id']):
            with self.subTest(identity=identity):
                answer=copy.deepcopy(self.answer);answer['surface_report']['identity']=identity
                with self.assertRaisesRegex(ValueError,'guarded surface evidence'):
                    read_many(self.config,[self.obj],execute=lambda *a:answer)

    def test_correct_principal_never_bypasses_permission_database_or_engine(self):
        for field,value in (('identity','other'),('object','other'),('engine','other')):
            answer=copy.deepcopy(self.answer);answer['surface_report'][field]=value
            with self.assertRaises(ValueError):read_many(self.config,[self.obj],execute=lambda *a:answer)
        answer=copy.deepcopy(self.answer);answer['read_only_verified']=False
        with self.assertRaises(ValueError):read_many(self.config,[self.obj],execute=lambda *a:answer)

    def test_invalid_federation_declaration_refuses_before_expected_identity(self):
        for field in ('client_id','tenant_id','principal_id'):
            reader=copy.deepcopy(self.reader);reader[field]='not-a-uuid'
            with self.assertRaises(ValueError):expected(reader)

    def test_absent_principal_is_never_matching_absence(self):
        for reader in ({}, {'account': None}, {'account': ''}):
            with self.assertRaisesRegex(ValueError, 'PRINCIPAL_REQUIRED'):expected(reader)

    def test_existing_user_and_legacy_identities_unchanged(self):
        for mode in (None,'key_vault_user_cache','managed_identity'):
            reader={'account':'reader@example.test','mode':mode}
            self.assertEqual(expected(reader),'reader@example.test')

if __name__=='__main__':unittest.main()
