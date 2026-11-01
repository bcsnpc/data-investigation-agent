from unittest.mock import Mock
import unittest
from investigator.investigation_cascade import Cascade


class InvestigationCascadeTests(unittest.TestCase):
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
