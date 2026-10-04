import copy,unittest
from investigator.load_accounting import classify
from test_source_delivery import audit_row

class AuditRowTests(unittest.TestCase):
    def test_malformed_history_named_excluded_and_valid_row_used(self):
        malformed=dict(audit_row(),run_id='old-broken',start_time_utc=None,rows_read=None)
        result=classify([malformed,audit_row()],'producer')
        self.assertEqual(result['status'],'CURRENT')
        self.assertEqual(result['run_id'],'load')
        self.assertEqual(result['excluded_rows'][0]['run_id'],'old-broken')
        self.assertIn('timestamp',result['excluded_rows'][0]['reason'].lower())
        self.assertIn('not proof',result['reason'])

    def test_exclusions_survive_engine_rendering_without_business_identifiers(self):
        from investigator.source_delivery import render_account
        job=classify([dict(audit_row(),run_id='broken-run',start_time_utc=None),audit_row()],'producer')
        observation={'metadata':{'load_accounting':job}}
        self.assertIn('broken-run',render_account(observation))
        self.assertIn('Missing UTC timestamp',render_account(observation))
        business=render_account(observation,True)
        self.assertNotIn('broken-run',business)
        self.assertIn('not proof',business)

    def test_no_valid_covering_row_refuses_and_names_each_exclusion(self):
        result=classify([{'run_id':'bad'},dict(audit_row(),pipeline_name='other')],'producer')
        self.assertEqual(result['status'],'UNAVAILABLE')
        self.assertEqual([r['run_id'] for r in result['excluded_rows']],['bad','load'])

    def test_newer_failed_or_running_run_never_hidden_by_older_success(self):
        for state in ('Failed','InProgress','Cancelled','NotStarted'):
            newer=dict(audit_row(),run_id='newer',status=state,start_time_utc='2026-10-04T03:00:00Z',end_time_utc=None,rows_read=None,rows_written=None)
            result=classify([audit_row(),newer],'producer')
            self.assertEqual(result['status'],'UNAVAILABLE')
            self.assertIn(state,result['reason'])
            self.assertNotIn('excluded_rows',result)

    def test_tied_distinct_latest_runs_are_still_ambiguous(self):
        result=classify([audit_row(),dict(audit_row(),run_id='another')],'producer')
        self.assertEqual(result['status'],'UNAVAILABLE')
        self.assertIn('ambiguous',result['reason'])

    def test_every_malformed_counter_timestamp_and_status_is_excluded(self):
        for changes in ({'rows_read':None},{'rows_written':True},{'rows_read':-1},
                        {'end_time_utc':'bad'},{'accounting_state':'estimated'},
                        {'status':'unknown'},{'run_id':''}):
            result=classify([dict(audit_row(),**changes)],'producer')
            self.assertEqual(result['status'],'UNAVAILABLE')
            self.assertEqual(len(result['excluded_rows']),1)

    def test_original_receipt_revalidation_recomputes_exclusions(self):
        from investigator.source_delivery import validate
        from test_source_delivery import DeliveryAdapter
        from investigator.process_debugging import vertical
        a=DeliveryAdapter(['report','delivery','application'],dict(report=12,delivery=12,application=13));a.modified='2026-10-04T01:59:59Z'
        result=vertical(a,'m',{});observations={o['id']:o for o in result['_observations']}
        marker=observations['delivery'];validate(marker,observations)
        bad=dict(audit_row(),run_id='old-broken',start_time_utc=None)
        from test_source_delivery import typed
        observations['audit']['values']+=typed([bad])
        with self.assertRaisesRegex(ValueError,'audit differs'):validate(marker,observations)

if __name__=='__main__':unittest.main()
