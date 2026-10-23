import copy,unittest
from fixture.apply import TemporalSourceScenario
from fixture.source_temporal import HISTORY,START,END
from test_fixture_failure_scenarios import SourceHistoryPlans
from investigator.live_gateway import validate_sql,_object
from investigator.live_gateway import GatewayDenied


class TemporalPlans(unittest.TestCase):
    def setUp(self):
        self.baseline=SourceHistoryPlans().baseline()
        names=['movement_id','warehouse_id','product_id','units','event_day','movement_type','source_modified_at_utc','source_row_version']
        self.inspection={'read_only':True,'exit_code':0,'body':{'status':'COMPLETED','sets':[
            [{'object_id':'123','temporal_type':'0','history_table_id':None,'proposed_history_id':None,'is_memory_optimized':'False','primary_keys':'1','triggers':'0'}],
            [{'is_primary_key':'True','column_name':'movement_id'}],
            [{'name':name,'generated_always_type':'0','is_hidden':'False'}for name in names],
            [{'row_count':'1','units':'16','newest_version':'28001'}]]}}

    def builder(self):return TemporalSourceScenario(self.baseline,self.inspection)

    def test_native_preexisting_feature_or_history_is_not_adopted(self):
        for field,value in [('temporal_type','2'),('history_table_id','444'),('proposed_history_id','444'),('triggers','1'),('primary_keys','0'),('is_memory_optimized','True')]:
            changed=copy.deepcopy(self.inspection);changed['body']['sets'][0][0][field]=value
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,'PREEXISTING'):TemporalSourceScenario(self.baseline,changed)
        changed=copy.deepcopy(self.inspection);changed['body']['sets'][3][0]['units']='17'
        with self.assertRaisesRegex(ValueError,'PREIMAGE_DIFFERS'):TemporalSourceScenario(self.baseline,changed)

    def test_probe_rolls_back_compatible_ddl_and_enable_commits_only_inside_guarded_transaction(self):
        probe=self.builder().enable(rollback_probe=True);enable=self.builder().enable()
        self.assertNotIn('COMMIT TRANSACTION',probe)
        self.assertIn('ROLLBACK TRANSACTION',probe)
        self.assertIn('COMMIT TRANSACTION',enable)
        self.assertLess(enable.index('Source preimage changed'),enable.index('ALTER TABLE'))
        self.assertIn('HISTORY_TABLE='+HISTORY,enable)
        self.assertIn('DATA_CONSISTENCY_CHECK=ON',enable)
        self.assertEqual(enable.count('HIDDEN NOT NULL'),2)
        self.assertNotIn('UPDATE ',enable);self.assertNotIn('GRANT ',enable)
        with self.assertRaisesRegex(ValueError,'PROBE_BOOLEAN'):self.builder().enable(rollback_probe='true')

    def test_history_read_is_native_parameterized_and_read_only_with_overflow(self):
        request=self.builder().observation([SourceHistoryPlans().added()])
        self.assertIn('FOR SYSTEM_TIME ALL',request['query'])
        self.assertIn(START,request['result_columns']);self.assertIn(END,request['result_columns'])
        self.assertNotIn('900101',request['query']);self.assertEqual(request['parameters'][0]['value'],900101)
        self.assertEqual(request['max_rows'],101)
        validate_sql(request['query'],{_object(v)for v in request['read_only_objects']})

    def test_temporal_modifier_cannot_bypass_objects_writes_or_other_version_forms(self):
        allowed={('app','stock_movements_round_two_20261003')}
        for query in (
            'SELECT * FROM app.other_table FOR SYSTEM_TIME ALL',
            'SELECT * FROM app.stock_movements_round_two_20261003 FOR SYSTEM_TIME AS OF @when',
            'SELECT * INTO app.copy FROM app.stock_movements_round_two_20261003 FOR SYSTEM_TIME ALL',
            'DELETE FROM app.stock_movements_round_two_20261003',
            'ALTER TABLE app.stock_movements_round_two_20261003 SET (SYSTEM_VERSIONING=OFF)',
            'SELECT * FROM other_database.app.stock_movements_round_two_20261003 FOR SYSTEM_TIME ALL'):
            with self.subTest(query=query),self.assertRaises(GatewayDenied):validate_sql(query,allowed)

    def test_cleanup_binds_owned_history_and_exact_native_digest_before_any_drop(self):
        sql=self.builder().disable(history_object_id=456,history_rows=3,history_sha256='a'*64)
        self.assertLess(sql.index('Native history changed since capture'),sql.index('SYSTEM_VERSIONING=OFF'))
        self.assertIn('history_table_id=456',sql)
        self.assertIn('DROP TABLE '+HISTORY,sql)
        self.assertNotIn('DROP TABLE [app].[stock_movements_round_two_20261003]',sql)
        for invalid in ('','a'*63,"';DROP TABLE x;--"):
            with self.assertRaisesRegex(ValueError,'DIGEST_REQUIRED'):self.builder().disable(history_object_id=456,history_rows=3,history_sha256=invalid)
        with self.assertRaises(ValueError):self.builder().disable(history_object_id=456,history_rows=10001,history_sha256='a'*64)


if __name__=='__main__':unittest.main()
