import copy,unittest
from fixture.apply import TemporalSourceScenario
from fixture.source_temporal import HISTORY,START,END
import test_fixture_failure_scenarios as fixtures
from investigator.live_gateway import validate_sql,_object
from investigator.live_gateway import GatewayDenied


class TemporalPlans(unittest.TestCase):
    def setUp(self):
        self.baseline=fixtures.SourceHistoryPlans().baseline()
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
        request=self.builder().observation([fixtures.SourceHistoryPlans().added()])
        self.assertIn('FOR SYSTEM_TIME ALL',request['query'])
        self.assertIn(START,request['result_columns']);self.assertIn(END,request['result_columns'])
        # Native SQL text preserves datetime2(7); Python datetime transport
        # would otherwise discard the seventh fractional digit.
        self.assertIn('CONVERT(varchar(33),['+START+'],126)',request['query'])
        self.assertIn('CONVERT(varchar(33),['+END+'],126)',request['query'])
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
        self.assertIn("COALESCE(OBJECT_ID(N'app.stock_movements_round22_history'),-1)",sql)
        self.assertIn("OR COALESCE(CONVERT(varchar(64),HASHBYTES",sql)
        self.assertIn('DROP TABLE '+HISTORY,sql)
        self.assertNotIn('DROP TABLE [app].[stock_movements_round_two_20261003]',sql)
        for invalid in ('','a'*63,"';DROP TABLE x;--"):
            with self.assertRaisesRegex(ValueError,'DIGEST_REQUIRED'):self.builder().disable(history_object_id=456,history_rows=3,history_sha256=invalid)
        with self.assertRaises(ValueError):self.builder().disable(history_object_id=456,history_rows=10001,history_sha256='a'*64)

    def test_empty_native_history_still_has_a_cleanup_digest(self):
        digest=self.builder().history_digest()
        self.assertIn("COALESCE((SELECT ",digest)
        self.assertIn("),N'[]')",digest)
        import hashlib
        empty=hashlib.sha256('[]'.encode('utf-16le')).hexdigest()
        sql=self.builder().disable(history_object_id=456,history_rows=0,history_sha256=empty)
        self.assertIn("<>UPPER('"+empty+"')",sql)

    def test_native_time_comparison_retains_blank_separately_from_zero_and_exact_precision(self):
        request=self.builder().comparison([fixtures.SourceHistoryPlans().added()],before='2026-10-23T22:49:27.1219695Z',after='2026-10-23T22:49:27.1219696Z')
        validate_sql(request['query'],{_object(v)for v in request['read_only_objects']})
        self.assertIn('before_rows',request['result_columns']);self.assertIn('before_quantity',request['result_columns'])
        self.assertNotIn('ELSE 0',request['query']);self.assertNotIn('COALESCE',request['query'])
        self.assertEqual(request['parameters'][-2]['value'],'2026-10-23T22:49:27.1219695Z')
        self.assertNotIn('2026-10-23',request['query'])
        for before,after in [('2026-10-23T22:49:27Z','2026-10-23T22:49:26Z'),('2026-10-23T22:49:27Z','2026-10-23T22:49:27.0000000Z'),('2026-10-23T22:49:27+00:00','2026-10-23T22:49:28Z'),("2026-10-23T22:49:27Z';DROP TABLE x",'2026-10-23T22:49:28Z')]:
            with self.subTest(before=before),self.assertRaises(ValueError):self.builder().comparison([fixtures.SourceHistoryPlans().added()],before=before,after=after)

    def test_scored_history_admission_reads_native_versions_now_and_refuses_removed_history(self):
        import copy
        from investigator.investigator_harness import RunHarness,CaseLog
        import tempfile
        from pathlib import Path
        value=fixtures.SourceHistoryPlans().added();calls=[]
        native={'read_only_verified':True,'surface_report_binding':'VALUE_QUERY','rows':[
            {'movement_id':str(value['movement_id']),'history_coverage_from':'2026-10-23T22:43:47.9434148',
             'before_rows':'0','before_quantity':None,'after_rows':'1','after_quantity':'7'}]}
        state=copy.deepcopy(native)
        def read(request):calls.append('live read');return copy.deepcopy(state)
        def admit(ticket):
            return TemporalSourceScenario.admit(read,[value],before='2026-10-23T22:49:20Z',after='2026-10-23T22:49:28Z')
        class User:
            def submit(self,ticket):calls.append('submit');return {'run_id':'one'}
            def poll(self,run):return {'status':'Succeeded'}
            def outcome(self,run,status):return {'verdict':'not found'}
        with tempfile.TemporaryDirectory()as directory:
            available=CaseLog(Path(directory)/'available')
            RunHarness(User(),available,admit=admit).run({'id':'live'})
            self.assertEqual(calls,['live read','submit'])
            admission=next(x for x in available.events if x['event']=='ADMISSION')
            self.assertEqual(admission['value']['native_result'],native)
            self.assertEqual(admission['value']['native_result']['rows'][0]['before_quantity'],None)
            self.assertLess([x['event']for x in available.events].index('ADMISSION'),[x['event']for x in available.events].index('SUBMIT_ATTEMPT'))
            state['rows']=[]
            removed=CaseLog(Path(directory)/'removed')
            with self.assertRaisesRegex(ValueError,'LIVE_HISTORY_MISSING'):
                RunHarness(User(),removed,admit=admit).run({'id':'removed'})
            self.assertEqual(calls,['live read','submit','live read'])
            self.assertEqual(removed.events[-1]['value']['stage'],'ADMISSION')
            self.assertNotIn('SUBMIT_ATTEMPT',[x['event']for x in removed.events])
        for field,changed,error in [('history_coverage_from','2026-10-23T22:49:21','OUTSIDE_RETAINED'),
                                    ('before_quantity','0','EMPTY_RESULT_COLLAPSED'),
                                    ('after_quantity',None,'EMPTY_RESULT_COLLAPSED')]:
            state=copy.deepcopy(native);state['rows'][0][field]=changed
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,error):admit({})
        state=copy.deepcopy(native);state['surface_report_binding']='METADATA_ONLY'
        with self.assertRaisesRegex(ValueError,'NOT_ATTESTED'):admit({})


if __name__=='__main__':unittest.main()
