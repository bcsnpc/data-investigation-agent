from copy import deepcopy
import unittest
from investigator.terminal_findings import attach
from cloud_guided_investigator import intake_question_outcome


class TerminalTests(unittest.TestCase):
    def query(self):
        return {'id':'query:one','layer':'one','purpose':'recreate','status':'SUCCEEDED','row_count':1,
                'text':'SELECT SUM(units) AS quantity FROM dbo.Rows','result':{'rows':[{'quantity':7}]}}
    def test_unresolved_keeps_partial_findings_calculation_limit_and_routing(self):
        before={'status':'UNRESOLVED','business':'No cause yet.','stop':'TOOL_OR_TIME_LIMIT'}
        result=attach(before,queries=[self.query()],context={'layers':{'one':{'label':'Serving'},'two':{'label':'Source'}}})
        self.assertEqual(before,{'status':'UNRESOLVED','business':'No cause yet.','stop':'TOOL_OR_TIME_LIMIT'})
        self.assertEqual(result['status'],'UNRESOLVED')
        for heading in ['Verdict: not established','Findings per layer:','Serving:','Source: not checked','Calculation:','Could not decide:','Routing: engineer']:
            self.assertIn(heading,result['business'])
        self.assertEqual(result['investigation_report']['findings_per_layer'][0]['observations'][0]['rows_sample'],[{'quantity':7}])
    def test_safety_stop_is_not_relabelled_as_an_answer(self):
        result=attach({'status':'BLOCKED','business':'Budget stopped.','stop':'MONTHLY_MODEL_EXHAUSTED'})
        self.assertEqual(result['status'],'BLOCKED');self.assertIn('No layer was admitted or read',result['business'])
    def test_answer_keeps_validated_verdict_and_technical_report(self):
        result=attach({'status':'ANSWERED','business':'observed value. 7','technical':{'verdict':'observed value'}},queries=[self.query()])
        self.assertIn('Verdict: observed value',result['business'])
        self.assertEqual(result['technical']['investigation_report'],result['investigation_report'])
    def test_question_keeps_choices_and_shows_candidate_observations(self):
        mapped={'question':{'text':'Which report?','fields':[{'field':'report','choices':[{'id':'r','name':'Revenue'}]}]},
                'candidate_checks':[{'candidate':'r','name':'Revenue','status':'SUCCEEDED','value':7,'query_id':'query:one'}]}
        saved=deepcopy(mapped)
        result=intake_question_outcome('It says7',mapped,resolution=None,step_costs=[],cost={})
        self.assertEqual(result['status'],'NEEDS_INPUT');self.assertEqual(mapped,saved)
        self.assertEqual(result['business']['fields'],mapped['question']['fields'])
        self.assertIn('Revenue',result['business']['text']);self.assertIn('Routing:',result['business']['text'])
    def test_retention_floor_is_explained_only_from_explicit_native_evidence(self):
        q=self.query();q.update(purpose='history',text='SELECT MIN(valid_from) AS earliest_available_time FROM dbo.Rows FOR SYSTEM_TIME ALL',
            result={'rows':[{'earliest_available_time':'2026-10-23T00:00:00Z'}]})
        result=attach({'status':'UNRESOLVED','business':'Earlier history not established.'},queries=[q])
        self.assertIn('Retention limit:',result['business']);self.assertIn('2026-10-23',result['business'])
        self.assertIn('empty history result is not proof of an earlier zero',result['business'])
        q.update(truncated=True,result={'rows':[{'version':4,'timestamp':'2026-10-23'}]})
        result=attach({'status':'UNRESOLVED'},queries=[q])
        self.assertEqual(result['investigation_report']['retention_limits'],[])
        q.update(text="SELECT '2026-10-23' AS earliest_available_time",result={'rows':[{'earliest_available_time':'2026-10-23'}]})
        self.assertEqual(attach({'status':'UNRESOLVED'},queries=[q])['investigation_report']['retention_limits'],[])
    def test_business_policy_routes_to_owner_without_judging_it(self):
        result=attach({'status':'NEEDS_INPUT','business':'Which intended rule?','question_reason':'BUSINESS_POLICY'})
        self.assertEqual(result['investigation_report']['routing']['to'],'BUSINESS_OWNER')
        finding=attach({'status':'ANSWERED','business':'Intended units not established.',
            'technical':{'verdict':'not found','routing':'BUSINESS_OWNER'}})
        self.assertEqual(finding['investigation_report']['routing']['to'],'BUSINESS_OWNER')
    def test_delta_retention_requires_complete_history_not_a_latest_n_sample(self):
        q=self.query();q.update(purpose='history',text='DESCRIBE HISTORY dbo.Rows LIMIT 251',
            metadata_scope={'history_limit':251},result={'rows':[{'version':5,'timestamp':'2026-10-25'},
                {'version':3,'timestamp':'2026-10-23'}]},row_count=2)
        result=attach({'status':'UNRESOLVED'},queries=[q]);limits=result['investigation_report']['retention_limits']
        self.assertEqual({r['field']:r['value']for r in limits},{'earliest_available_version':3,'earliest_available_timestamp':'2026-10-23'})
        q['metadata_scope']['history_limit']=2
        self.assertEqual(attach({'status':'UNRESOLVED'},queries=[q])['investigation_report']['retention_limits'],[])


if __name__=='__main__':unittest.main()
