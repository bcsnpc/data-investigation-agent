import copy,unittest
from fixture.source_access import AccessSourceScenario,ACTORS,DATA,EXPORT
from investigator.live_gateway import validate_sql,_object


class AccessPlans(unittest.TestCase):
    def inspection(self):
        return {'status':'METADATA_AVAILABLE','attempts':[{'body':{'sets':[
            [{'database_name':'billingapp','app_schema_id':'5'}],
            [{'name':actor,'role_name':'db_datareader'}for actor in ACTORS],
            [{'rows_id':None,'readers_id':None,'export_id':None}]]}}]}

    def test_existing_database_readers_required_and_objects_never_adopted(self):
        AccessSourceScenario(self.inspection())
        for path,value in [('database','ordersops'),('role','db_owner'),('object',123)]:
            changed=self.inspection();sets=changed['attempts'][-1]['body']['sets']
            if path=='database':sets[0][0]['database_name']=value
            elif path=='role':sets[1][0]['role_name']=value
            else:sets[2][0]['export_id']=value
            with self.subTest(path=path),self.assertRaises(ValueError):AccessSourceScenario(changed)

    def test_visibility_is_data_not_permissions_impersonation_or_real_rls(self):
        sql=AccessSourceScenario.create()
        self.assertLess(sql.index('Isolated access fixture already exists'),sql.index('CREATE TABLE'))
        self.assertIn('CURRENT_USER',sql);self.assertIn('BEGIN TRANSACTION',sql)
        for denied in ('GRANT ','CREATE USER','ALTER ROLE','EXECUTE AS','SECURITY POLICY','CREATE SCHEMA'):
            self.assertNotIn(denied,sql)
        self.assertEqual({case:sum(units for c,group,units in DATA if c==case and group==0)for case in (1,2,3)},{1:10,2:20,3:30})
        self.assertEqual({case:sum(units for c,group,units in DATA if c==case)for case in (1,2,3)},{1:25,2:45,3:65})

    def test_both_readers_use_the_identical_read_only_group_query(self):
        one=AccessSourceScenario.read();two=AccessSourceScenario.read()
        self.assertEqual(one,two);self.assertEqual(one['max_rows'],4)
        self.assertEqual(one['read_only_objects'],[EXPORT])
        validate_sql(one['query'],{_object(EXPORT)})
        self.assertNotIn('orderops_investigator',one['query']);self.assertNotIn('dia-investigator-round19',one['query'])

    def test_cleanup_is_hash_and_object_bound_before_any_drop(self):
        receipt={'rows_id':1,'readers_id':2,'export_id':3,'row_count':6,'reader_mapping_count':3,'fixture_sha256':'a'*64}
        sql=AccessSourceScenario.cleanup(receipt)
        self.assertLess(sql.index('Access fixture changed since capture'),sql.index('DROP VIEW'))
        self.assertIn('COALESCE(OBJECT_ID',sql)
        for changed in ({**receipt,'row_count':7},{**receipt,'fixture_sha256':None},{**receipt,'export_id':True}):
            with self.assertRaises(ValueError):AccessSourceScenario.cleanup(changed)


if __name__=='__main__':unittest.main()
