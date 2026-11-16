from unittest.mock import Mock
import unittest
from investigator.investigation_cascade import Cascade


class InvestigationCascadeTests(unittest.TestCase):
    def test_escalation_gets_bounded_literal_query_preview_without_mutating_evidence(self):
        from copy import deepcopy
        from investigator.investigation_cascade import query_handoff
        query={'id':'e1','layer':'gold','text':'SELECT quantity FROM dbo.Items',
               'status':'SUCCEEDED','row_count':3,'truncated':False,
               'result':{'rows':[{'quantity':7},{'quantity':8},{'quantity':9}]}}
        original=deepcopy(query)
        view=query_handoff(query)
        self.assertEqual(view['result_preview']['rows_sample'],[{'quantity':7},{'quantity':8}])
        self.assertTrue(view['result_preview']['sample_only'])
        self.assertEqual(view['result_preview']['full_result_evidence_id'],'e1')
        self.assertEqual(query,original)
        query['result']['rows']=[{'large':'x'*2000}]
        self.assertNotIn('result_preview',query_handoff(query))

    def test_generic_cached_layer_schema_never_bypasses_local_admission(self):
        from investigator.ai_investigation import Investigator
        from investigator.investigative_queries import Queries
        from test_round23_reasoning import MemoryCheckpoint
        from test_round23_intake_queries import sql_objects
        from jsonschema import ValidationError
        execute=Mock()
        queries=Queries({'gold':{'dialect':'T-SQL','objects':sql_objects()}},
            execute=execute,reserve=Mock(),save=Mock())
        engine=Investigator(queries=queries,model=Mock(),read_tools={},checkpoint=MemoryCheckpoint(),
            case_id='local-admission',context={'intake':{},'path':['gold']},triage=[],
            validate_finding=Mock())
        with self.assertRaises(ValidationError):
            engine.dispatch('run_sql',{'layer':'unknown','query':'SELECT 1','purpose':'compare'})
        execute.assert_not_called()

    def test_real_checkpoint_continuation_reuses_native_query_across_models(self):
        from investigator.ai_investigation import Investigator,schema
        from investigator.investigative_queries import Queries
        from test_round23_reasoning import MemoryCheckpoint,tool
        from test_round23_intake_queries import sql_objects
        execute=Mock(return_value={'rows':[[7]]})
        queries=Queries({'gold':{'dialect':'T-SQL','objects':sql_objects()}},
            execute=execute,reserve=Mock(),save=Mock())
        query={'layer':'gold','query':'SELECT SUM(quantity) AS total FROM dbo.Items','purpose':'recreate'}
        sol=Mock();sol.model='sol'
        sol.complete.side_effect=[tool('run_sql',query)]+[
            tool('get_definition',{'node':str(i)},identity='definition-'+str(i))for i in range(6)]
        reads={'get_definition':{'description':'Read retained logic',
            'schema':schema({'node':{'enum':[str(i)for i in range(6)]}}),'run':Mock(return_value={'definition':'retained'})}}
        engine=Investigator(queries=queries,model=sol,read_tools=reads,checkpoint=MemoryCheckpoint(),
            case_id='same-case',context={'intake':{'report':'report'},'path':['gold']},triage=[],
            validate_finding=Mock(return_value={'business':'Checked total is 7.'}))
        astra=Mock();astra.model='astra'
        def answer(**kwargs):
            return tool('submit_finding',{'verdict':'as designed','cause':'Checked total is 7.',
                'numbers':[7],'checked':['gold'],'evidence_ids':[queries.records[0]['id']]})
        responses=[tool('run_sql',query),answer]
        def complete(**kwargs):
            response=responses.pop(0)
            return response(**kwargs)if callable(response)else response
        astra.complete.side_effect=complete
        result=Cascade(engine,lambda:astra).run()
        self.assertEqual(result['status'],'ANSWERED')
        self.assertEqual(result['investigation_cascade']['resolved_by_model'],'astra')
        execute.assert_called_once()
        self.assertEqual(sol.complete.call_count,7)
        self.assertEqual(astra.complete.call_count,2)
        self.assertEqual(result['model_calls'],9)
        self.assertEqual(len(queries.records),1)

    def engine(self,first_status):
        engine=Mock();engine.tool_limit=15;engine.deadline_seconds=900;engine.model.model='sol'
        engine.state={'evidence':{'old':{'kind':'QUERY'}},'cache':{'same-call':{'evidence_id':'old'}},'pending':None}
        engine.queries.records=[{'id':'old','layer':'source','text':'SELECT 1','status':'SUCCEEDED'}]
        engine.run.side_effect=[{'status':first_status,'model_calls':3,'tools_used':7,'stop':'TOOL_OR_TIME_LIMIT'},
                                {'status':'ANSWERED','model_calls':5,'tools_used':9}]
        return engine

    def test_only_unresolved_escalates_with_same_queries_cache_and_total_limits(self):
        engine=self.engine('UNRESOLVED');fallback=Mock();fallback.return_value.model='astra'
        original_cache=engine.state['cache'];result=Cascade(engine,fallback).run()
        self.assertEqual(result['investigation_cascade']['resolved_by_model'],'astra')
        self.assertIs(engine.state['cache'],original_cache)
        self.assertEqual(len(engine.queries.records),1)
        self.assertEqual(engine.tool_limit,15);self.assertEqual(engine.deadline_seconds,900)
        self.assertEqual(result['investigation_cascade']['stages'][1]['model_calls'],2)

    def test_answer_and_safety_boundary_never_escalate(self):
        for status in ('ANSWERED','BLOCKED','UNESTABLISHED'):
            engine=self.engine(status);fallback=Mock();result=Cascade(engine,fallback).run()
            fallback.assert_not_called();self.assertFalse(result['investigation_cascade']['escalated'])

    def test_uncertain_pending_request_does_not_escalate(self):
        engine=self.engine('UNRESOLVED');engine.state['pending']={'kind':'MODEL'};fallback=Mock()
        Cascade(engine,fallback).run();fallback.assert_not_called()
