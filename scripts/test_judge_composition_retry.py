import copy
import unittest
from contextlib import contextmanager
from unittest.mock import patch
import test_flexible_investigation as fixture
from investigator.adaptive_runtime import AdaptiveRuntime
from investigator.process_debugging import VERSION
from investigator.evidence_prose import IncompleteProse

class JudgeRetryTests(unittest.TestCase):
    def run_case(self,responses,limit=6,daily_limit=6,expire=False):
        helper=fixture.DynamicTests();helper.setUp();self.addCleanup(helper.doCleanups)
        envelope=copy.deepcopy(helper.envelope);envelope['strategy']=VERSION
        envelope['limits']['planner_calls']=limit
        calls=[];recordings=[];now=[1000000.]
        def provider(payload,options):
            calls.append(copy.deepcopy(payload));result=responses[len(calls)-1]
            if expire:now[0]+=1000
            if isinstance(result,Exception):raise result
            return result,{'usage':{'output_tokens':10,'input_tokens':20}}
        @contextmanager
        def recording(context):
            recordings.append(context);yield
        policy={'environment':helper.store.environment,'daily_limits':{'planner_calls':daily_limit,'cloud_calls':60,'input_characters':1000000,'output_tokens':100000},'max_inflight_planners':1,'no_progress_limit':3}
        agent=AdaptiveRuntime(helper.runtime,lambda _:self.fail('no exploration'),process_judge=provider,usage_policy=policy,clock=lambda:now[0])
        identity=agent.create(envelope,'retry-test')['id']
        def vertical(adapter,*args):
            adapter.judge_definition({'definition':'bounded evidence'})
            # Stop after exercising real runtime admission, metering and recording.
            raise ValueError('test boundary after judgment')
        with patch('investigator.process_debugging.vertical',side_effect=vertical),patch('investigator.planner_recording.recording',recording):
            state=agent.run(identity)
        with helper.runtime.db() as db:
            self.assertEqual(db.execute("SELECT count(*) FROM adaptive_usage WHERE kind='planner'").fetchone()[0],len(calls))
            self.assertEqual(db.execute("SELECT count(*) FROM adaptive_usage WHERE status='RESERVED'").fetchone()[0],0)
        return state,calls,recordings

    def test_one_retry_is_distinct_and_both_attempts_count(self):
        state,calls,records=self.run_case([IncompleteProse('unfinished'),{'status':'COMPLETED'}])
        self.assertEqual(len(calls),2);self.assertEqual(calls[0],calls[1])
        self.assertEqual(state['planner_calls'],2)
        self.assertEqual([r['attempt'] for r in records],[1,2])
        kinds=[e['kind'] for e in state['events']]
        self.assertEqual(kinds.count('PROCESS_JUDGMENT_RETRY'),1)
        self.assertEqual(kinds.count('PROCESS_JUDGMENT_REJECTED'),1)
        self.assertEqual(kinds.count('PROCESS_JUDGMENT_COMPLETED'),1)

    def test_second_unfinished_response_holds_without_third_attempt(self):
        state,calls,_=self.run_case([IncompleteProse('unfinished'),IncompleteProse('unfinished')])
        self.assertEqual(len(calls),2);self.assertEqual(state['status'],'HELD')
        self.assertEqual(state['process_error']['error_type'],'IncompleteProse')
        self.assertEqual(state['stop_reason'],'PROCESS_FAILED')
        self.assertEqual(sum(e['kind']=='PROCESS_JUDGMENT_RETRY_EXHAUSTED' for e in state['events']),1)

    def test_retry_does_not_bypass_call_limit(self):
        state,calls,_=self.run_case([IncompleteProse('unfinished')],limit=1)
        self.assertEqual(len(calls),1);self.assertEqual(state['planner_calls'],1)
        self.assertEqual(state['status'],'HELD')
        self.assertIn('PROCESS_JUDGMENT_RETRY_EXHAUSTED',[e['kind'] for e in state['events']])

    def test_clean_and_other_errors_do_not_retry(self):
        for result in ({'status':'COMPLETED'},ValueError('too long'),TimeoutError()):
            with self.subTest(result=result):
                state,calls,_=self.run_case([result])
                self.assertEqual(len(calls),1)
                self.assertNotIn('PROCESS_JUDGMENT_RETRY',[e['kind'] for e in state['events']])

    def test_retry_respects_daily_budget_and_deadline(self):
        for options in ({'daily_limit':1},{'expire':True}):
            with self.subTest(options=options):
                state,calls,_=self.run_case([IncompleteProse('unfinished')],**options)
                self.assertEqual(len(calls),1);self.assertEqual(state['status'],'HELD')
                self.assertIn('PROCESS_JUDGMENT_RETRY_EXHAUSTED',[e['kind'] for e in state['events']])

    def test_received_invalid_prose_retains_provider_usage(self):
        from investigator.transformation_judgment import azure_judge
        metadata={'usage':{'input_tokens':20,'output_tokens':10}}
        with patch('ticket_planner._azure_generate',return_value=({'judgment':'EXPLAINS','explanation':'Unfinished','limitation':'Unknown.'},metadata)):
            with self.assertRaises(IncompleteProse) as caught:azure_judge({}, {})
        self.assertEqual(caught.exception.provider_metadata,metadata)
