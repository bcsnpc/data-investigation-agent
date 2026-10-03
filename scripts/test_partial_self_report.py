import copy,json,unittest,sqlite3,tempfile
from pathlib import Path
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import patch
from investigator import flexible_tools,raw_surface_report
from investigator.process_debugging import Probe,attest,attest_surface
from investigator.surface_difference import grade,UNESTABLISHED


class PartialReportTests(unittest.TestCase):
    columns={'identity':'surface_identity','engine':'surface_engine','object':'surface_object'}
    request={'tool':'bounded_sql','max_rows':21,'limitation':'test','surface_report_columns':columns}
    declared={'identity':'reader','engine':'engine','object':'object','connection':'connection'}

    def extract(self,rows):
        return flexible_tools.extract({'rows':rows,'column_types':{}},self.request)

    def test_one_answer_two_nulls_retained_partial_and_binding_refused(self):
        row={'n':42,'[surface_identity]':'reader','[surface_engine]':None,'[surface_object]':None}
        result=self.extract([row]);raw=result['raw_surface_report']
        self.assertEqual(raw['rows'],[{k:v for k,v in row.items() if k!='n'}])
        self.assertEqual(result['surface_report'],{'identity':'reader','engine':None,'object':None})
        raw_surface_report.validate(self.request,result)
        p=attest(Probe('OBSERVED','layer',{'id':'receipt'},42,execution_surface=self.declared,
            surface_report=result['surface_report'],surface_reportable=('identity','engine','object')))
        a=p.evidence['surface_attestation']
        self.assertEqual(a['coverage'],'PARTIAL');self.assertEqual(p.status,'UNAVAILABLE')
        self.assertEqual(a['field_states']['engine'],'UNATTESTED')
        self.assertEqual(a['field_states']['identity'],'ATTESTED')
        self.assertEqual(a['missing_required_fields'],['engine','object'])

    def test_receipt_missing_raw_columns_fails_consumer_validation(self):
        result=self.extract([{'n':42,'surface_identity':'reader'}]);del result['raw_surface_report']
        with self.assertRaisesRegex(ValueError,'requires raw self-report'):raw_surface_report.validate(self.request,result)

    def test_wrong_extraction_cannot_erase_raw_or_invent_answer(self):
        result=self.extract([{'n':42,'surface_identity':'reader','surface_engine':None}])
        original=copy.deepcopy(result['raw_surface_report'])
        result['surface_report']['engine']='invented'
        with self.assertRaisesRegex(ValueError,'differs from original'):raw_surface_report.validate(self.request,result)
        self.assertEqual(result['raw_surface_report'],original)

    def test_raw_only_declared_columns_and_bounded_no_business_result(self):
        result=self.extract([{'business_secret':'never raw','surface_identity':'reader'}])
        self.assertNotIn('business_secret',json.dumps(result['raw_surface_report']))
        bad=copy.deepcopy(result);bad['raw_surface_report']['rows'][0]['n']=42
        with self.assertRaisesRegex(ValueError,'undeclared columns'):raw_surface_report.validate(self.request,bad)
        with self.assertRaisesRegex(ValueError,'text exceeds'):self.extract([{'surface_identity':'x'*301}])

    def test_missing_null_empty_inconsistent_are_distinguishable_raw(self):
        rows=[{'surface_identity':None},{'surface_identity':''},{}]
        result=self.extract(rows);self.assertEqual(result['raw_surface_report']['rows'],rows)
        self.assertIsNone(result['surface_report']);raw_surface_report.validate(self.request,result)

    def test_bounds_record_truncation_and_prevent_attestation_from_subset(self):
        rows=[{'surface_identity':'reader'}]*65
        result=self.extract(rows);raw=result['raw_surface_report']
        self.assertEqual(len(raw['rows']),64);self.assertTrue(raw['truncated']);self.assertIsNone(result['surface_report'])
        raw_surface_report.validate(self.request,result)

    def test_partial_cannot_grade_boundary_when_required_fields_missing(self):
        a=attest_surface(self.declared,{'identity':'reader','engine':None,'object':None},tuple(self.columns))
        o={'id':'x','surface_attestation':a,'surface_report_binding':'VALUE_QUERY','surface_report_receipt_id':'x'}
        self.assertEqual(grade(o,o)['grade'],UNESTABLISHED)

    def test_partial_sql_transport_report_keeps_null(self):
        self.assertEqual(flexible_tools._transport_report({'identity':'reader','object':None}),{'identity':'reader','object':None})

    def test_hostile_writer_cannot_complete_without_raw_and_failure_preserves_original(self):
        with tempfile.TemporaryDirectory() as directory:
            @contextmanager
            def connect():
                db=sqlite3.connect(Path(directory)/'receipts.sqlite')
                try:
                    with db:yield db
                finally:db.close()
            store=SimpleNamespace(connect=connect)
            response={'rows':[{'n':42,'surface_identity':'reader','surface_engine':None,'surface_object':None}],
                      'read_only_verified':True}
            bad={'rows':[],'surface_report':{'identity':'reader','engine':None,'object':None}}
            with patch.object(flexible_tools,'build',return_value=self.request),patch.object(flexible_tools,'extract',return_value=bad):
                written=flexible_tools.run(store,{'model_id':'model'},{},'bounded_sql',lambda _:response)
            self.assertEqual(written['status'],'FAILED')
            self.assertIn('raw_surface_report',written['result'])
            self.assertEqual(written['result']['raw_surface_report']['rows'],[{k:v for k,v in response['rows'][0].items() if k!='n'}])
            raw_surface_report.validate(self.request,written['result'])

    def test_other_all_fields_collapse_in_sql_session_is_removed(self):
        import fabric_sql_surface
        config={'fabric':{'auth':{'tenant_id':'tenant'},'sql_reader':{'account':'reader','profile':'.local/reader','server':'example.invalid'}}}
        answer=SimpleNamespace(returncode=0,stdout=json.dumps({'status':'REACHABLE','login_name':'reader','database_name':None}))
        result=fabric_sql_surface.self_report(config,'database',token=lambda *a:'unused',run=lambda *a,**k:answer)
        self.assertEqual(result['surface_report'],{'identity':'reader','object':None})


if __name__=='__main__':unittest.main()
