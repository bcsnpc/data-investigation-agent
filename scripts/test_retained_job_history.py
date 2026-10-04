import copy,unittest
from unittest.mock import patch
from investigator.adapters.microsoft_process import MicrosoftProcessAdapter
from investigator.adapters.job_history import classify

class JobHistoryTests(unittest.TestCase):
    def rows(self,status='Completed',**extra):
        run={'id':'run','status':status,'startTimeUtc':'2026-09-18T18:12:02.4546073','endTimeUtc':'2026-09-18T18:13:23.9191421','failureReason':None};run.update(extra)
        return [{'asset_id':'job','capability':'run_history','status':'AVAILABLE','detail':[run]}]
    def test_failed_job_is_never_current_in_adapter(self):
        a=MicrosoftProcessAdapter.__new__(MicrosoftProcessAdapter);a.store=None;a.config={}
        with patch('investigator.context_search.latest',return_value={'version':'scan','observations':self.rows('Failed')}):
            result=a.job_history({'lower':{'transformation_asset_id':'job'}})
        self.assertEqual(result['status'],'UNAVAILABLE');self.assertEqual(result['run_state'],'FAILED')
        self.assertTrue(result['evidence']['runs'])
    def test_completion_progress_empty_and_unknown_are_distinct(self):
        for status,state in [('Completed','SUCCEEDED'),('Failed','FAILED'),('Cancelled','FAILED'),('InProgress','IN_PROGRESS'),('NotStarted','NOT_RUN'),('Other','UNKNOWN')]:
            with self.subTest(status=status):
                result=classify(self.rows(status));self.assertEqual(result['run_state'],state)
                self.assertEqual(result['status'],'CURRENT' if state=='SUCCEEDED' else 'UNAVAILABLE')
        self.assertEqual(classify([{'status':'AVAILABLE','detail':[]}])['run_state'],'NOT_RUN')
    def test_old_success_cannot_hide_new_failure(self):
        rows=self.rows();bad=copy.deepcopy(rows[0]['detail'][0]);bad.update(id='new',status='Failed',startTimeUtc='2026-09-19T00:00:00Z');rows[0]['detail'].append(bad)
        self.assertEqual(classify(rows)['run_state'],'FAILED')
    def test_error_payload_bad_timestamps_and_false_completion_are_unavailable(self):
        cases=[[{'status':'UNAVAILABLE','detail':{'error_type':'Denied'}}],self.rows(endTimeUtc=None),self.rows(endTimeUtc='2020-01-01T00:00:00Z'),self.rows(failureReason={'errorCode':'failed'}),self.rows(startTimeUtc='bad')]
        for rows in cases:
            with self.subTest(rows=rows):self.assertEqual(classify(rows)['status'],'UNAVAILABLE')
