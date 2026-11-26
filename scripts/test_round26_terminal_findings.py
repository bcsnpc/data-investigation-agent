from copy import deepcopy
import unittest
from investigator.terminal_findings import attach
from cloud_guided_investigator import intake_question_outcome


class TerminalTests(unittest.TestCase):
    def test_interruption_renders_retained_handoff_reads_without_upgrading_status(self):
        from investigator.regression_features import configured
        before={'status':'INTERRUPTED','business':'Provider timed out.','stop':'NVIDIA_TRANSPORT_UNAVAILABLE',
                'handoff':{'queries':[self.query()],'query_history_status':'RETAINED_ENGINE_QUERY_RECORDS',
                           'context':{'layers':{'one':{'label':'Serving'}}},'lineage_status':'RETAINED_ENGINE_CONTEXT'}}
        saved=deepcopy(before);result=attach(before,queries=[],context={})
        self.assertEqual(before,saved);self.assertEqual(result['status'],'INTERRUPTED')
        self.assertIn('Serving:',result['business']);self.assertNotIn('No layer was admitted or read',result['business'])
        self.assertEqual(result['investigation_report']['findings_per_layer'][0]['observations'][0]['rows_sample'],[{'quantity':7}])
    def test_unestablished_or_unlabelled_handoff_is_not_native_support(self):
        for label in (None,'NOT_ESTABLISHED_BEFORE_ENGINE_INITIALIZATION'):
            result=attach({'status':'INTERRUPTED','handoff':{'queries':[self.query()],'query_history_status':label}})
            self.assertEqual(result['investigation_report']['findings_per_layer'],[])
    def test_explicit_case_inputs_win_over_partial_handoff_fallback(self):
        before={'status':'INTERRUPTED','handoff':{'queries':[self.query()],'query_history_status':'RETAINED_ENGINE_QUERY_RECORDS',
                'context':{'layers':{'one':{'label':'Old'}}},'lineage_status':'RETAINED_ENGINE_CONTEXT'}}
        query={**self.query(),'id':'query:current','layer':'two'}
        result=attach(before,queries=[query],context={'layers':{'two':{'label':'Current'}}})
        findings=result['investigation_report']['findings_per_layer'];self.assertEqual([f['name']for f in findings],['Current'])
        self.assertEqual(findings[0]['observations'][0]['evidence_id'],'query:current')
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
    def test_unfinished_calculation_does_not_invent_a_discrepancy(self):
        result=attach({'status':'UNRESOLVED','stop':'TOOL_OR_TIME_LIMIT'},
            queries=[self.query()],context={'conclusion_contract':'question-first-v1'})
        self.assertEqual(result['status'],'UNRESOLVED')
        self.assertIn('stated question',result['conclusion']['direct_answer'])
        self.assertNotIn('discrepancy',result['conclusion']['direct_answer'])

    def test_exact_successful_retry_is_not_missing_but_error_stays_in_history(self):
        failed={**self.query(),'id':'query:failed','signature':'bound-query-one',
                'status':'ERROR','error':'endpoint timed out'}
        success={**self.query(),'id':'query:success','signature':'bound-query-one'}
        context={'conclusion_contract':'question-first-v1'}
        outcome={'status':'UNRESOLVED','stop':'TOOL_OR_TIME_LIMIT'}
        result=attach(outcome,queries=[failed,success],context=context)
        self.assertNotIn('one: endpoint timed out',result['conclusion']['undecided'])
        observations=result['investigation_report']['findings_per_layer'][0]['observations']
        self.assertEqual([o['status']for o in observations],['READ_FAILED','OBSERVED'])
        self.assertEqual(result['status'],'UNRESOLVED')
        from investigator.regression_features import configured
        for queries in ([success,failed],[failed,{**success,'signature':'different-query'}],
                        [{k:v for k,v in failed.items()if k!='signature'},success]):
            with self.subTest(queries=queries):
                self.assertIn('one: endpoint timed out',attach(outcome,queries=queries,
                    context=context)['conclusion']['undecided'])

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

    def test_answered_summary_preserves_validated_explanation_as_prose(self):
        from investigator.regression_features import configured
        conclusion = {'direct_answer': 'Different caller mappings explain the totals.',
                      'verdict_class': 'AS DESIGNED', 'calculation_explanation': 'The retained view sums the caller-matched rows.',
                      'undecided': [], 'routing': 'BUSINESS_OWNER',
                      'context_gap': {'type': 'business rule', 'note': 'Which visibility groups are intended.'}}
        outcome = {'status': 'ANSWERED', 'business': 'Caller mapping explains the result.',
                   'conclusion': conclusion, 'technical': {'verdict': 'access difference'}}
        result = attach(outcome)
        calculation = result['investigation_report']['calculation'][0]
        self.assertEqual(calculation['expression'], conclusion['calculation_explanation'])
        self.assertEqual(calculation['source'], 'DELIVERED_CONCLUSION')
        self.assertNotIn('calculation definition was not established', result['business'])

    def test_summary_does_not_upgrade_an_unresolved_or_malformed_explanation(self):
        result = attach({'status': 'UNRESOLVED', 'conclusion': {'calculation_explanation': 'Not verified.'}})
        self.assertEqual(result['status'], 'UNRESOLVED')
        self.assertEqual(result['investigation_report']['calculation'], [])
        result = attach({'status': 'ANSWERED', 'conclusion': {'calculation_explanation': 'Missing validated structure.'}})
        self.assertEqual(result['investigation_report']['calculation'], [])


if __name__=='__main__':unittest.main()
