"""Retrieval cannot spend the planner turns allocated to tests."""
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import httpx
from openai import DefaultHttpxClient
import test_flexible_investigation as fixture
import test_session_replay as recorded_fixture
from investigator.adaptive_runtime import AdaptiveRuntime
from investigator.adaptive_planner import azure_plan
from investigator.action_budget import allocation
from investigator import planner_recording,dynamic_reasoning
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'acceptance/unknown_domain'))
from score_run import score
from run_ledger import row


class ActionBudgetTests(unittest.TestCase):
    def test_existing_total_is_partitioned_and_rejections_do_not_enlarge_it(self):
        state={'envelope':{'limits':{'planner_calls':6,'cloud_calls':4}},'planner_calls':4,'cloud_calls':0,
               'decisions':[{'decision':{'action':'LOOKUP'}} for _ in range(4)],'observations':[]}
        budget=allocation(state)
        self.assertEqual((budget['retrieval_limit'],budget['retrieval_remaining'],budget['test_turns_still_protected']),(4,0,2))
        state['decisions']=[]  # Four rejected paid proposals still cannot consume the reserve via retrieval.
        self.assertEqual(allocation(state)['retrieval_remaining'],0)
        state['envelope']['limits']['planner_calls']=1;state['planner_calls']=0
        self.assertEqual(allocation(state)['retrieval_remaining'],0)

    def test_exhausted_retrieval_is_absent_from_wire_and_rejected_locally(self):
        payload={'candidates':[],'observations':[],'hypotheses':[],
                 'action_budget':{'retrieval_remaining':0}}
        _,schema,_=dynamic_reasoning.wire_contract(payload)
        actions={v['properties']['kind']['enum'][0] for v in schema['properties']['next']['anyOf']}
        self.assertNotIn('LOOKUP',actions)
        self.assertTrue({'QUERY','ASK','STOP'}<=actions)
        proposal=fixture.DynamicTests().decision('LOOKUP',lookup={'operation':'search','value':'metadata'})[0]
        with self.assertRaisesRegex(ValueError,'RETRIEVAL_BUDGET_EXHAUSTED'):
            dynamic_reasoning.validate(proposal,payload)

    def test_out_of_budget_lookup_has_distinct_event_and_no_metadata_dispatch(self):
        helper=fixture.DynamicTests();helper.setUp();self.addCleanup(helper.doCleanups)
        helper.envelope['limits']['planner_calls']=2
        agent=AdaptiveRuntime(helper.runtime,lambda _:helper.decision('LOOKUP',lookup={'operation':'search','value':'context'}))
        with patch('investigator.dynamic_reasoning.lookup',side_effect=AssertionError('Retrieval must not dispatch')):
            result=agent.run(agent.create(helper.envelope,'exhausted-lookup')['id'])
        self.assertEqual(result['cloud_calls'],0)
        self.assertEqual(result['planner_calls'],2)  # Invalid provider proposals still cost calls.
        self.assertEqual(sum(e['kind']=='RETRIEVAL_BUDGET_REJECTED' for e in result['events']),2)
        self.assertEqual(result['action_budget']['retrieval_remaining'],0)

    def test_material_question_and_deadline_never_force_a_data_read(self):
        for expired in (False,True):
            helper=fixture.DynamicTests();helper.setUp()
            try:
                clock=[1000]
                agent=AdaptiveRuntime(helper.runtime,lambda _:helper.decision('ASK',question='Which exact reporting date window did you intend?'),clock=lambda:clock[0])
                identity=agent.create(helper.envelope,'material-hold')['id']
                if expired:clock[0]=10000
                result=agent.run(identity)
                self.assertEqual(result['cloud_calls'],0)
                self.assertEqual(result['stop_reason'],'DEADLINE' if expired else 'CLARIFICATION_REQUIRED')
                self.assertEqual(result['trajectory_metrics']['reads_per_run'],0)
            finally:helper.doCleanups()

    def test_recorded_retrieval_pressure_leaves_two_real_mock_reads_and_replays(self):
        helper=recorded_fixture.SessionReplayTests();helper.setUp();self.addCleanup(helper.doCleanups)
        calls=[]
        def provider(request):
            body=json.loads(request.content);payload=json.loads(body['input']);calls.append(payload)
            if payload['action_budget']['retrieval_remaining']:
                action={'kind':'LOOKUP','operation':'search','value':'context '+str(len(calls))}
            elif not any(o.get('tool')=='bounded_dax' for o in payload['observations']):
                action={'kind':'QUERY','tool':'bounded_dax','text':'EVALUATE ROW("value",[Total])','max_rows':20}
            else:
                action={'kind':'QUERY','tool':'bounded_sql','text':'SELECT COUNT(*) AS n FROM business.events','max_rows':20}
            return httpx.Response(200,json={'id':'offline','object':'response','model':'offline-fixture','status':'completed',
                'usage':None,'output':[{'type':'function_call','call_id':'offline','name':'dynamic_investigation_action',
                'arguments':json.dumps({'next':action,'hypotheses':{}})}]})
        policy=planner_recording.load_session(helper.original['id'],helper.recordings)[0]['context']['usage_policy']
        agent=AdaptiveRuntime(helper.helper.runtime,azure_plan,clock=lambda:1000,planner_profile={'adapter':'azure'},usage_policy=policy)
        with patch.object(planner_recording,'ROOT',helper.root),patch.dict(os.environ,{
                'INVESTIGATOR_RECORD_PLANNER':'1','AZURE_OPENAI_ENDPOINT':'https://offline.openai.azure.com',
                'AZURE_OPENAI_DEPLOYMENT':'offline-fixture','AZURE_OPENAI_API_KEY':'offline-placeholder-credential'}), \
                patch('openai.DefaultHttpxClient',side_effect=lambda **kw:DefaultHttpxClient(transport=httpx.MockTransport(provider),**kw)):
            helper.original=agent.run(agent.create(helper.helper.envelope,'retrieval-pressure')['id'])
        result=helper.replay('budget-pressure')
        self.assertEqual(result['status'],'MATCHED',result['differences'])
        self.assertEqual((result['network_calls'],result['unrecorded_tool_attempts']),(0,0))
        state=result['session'];metrics=state['trajectory_metrics']
        self.assertEqual((state['planner_calls'],metrics['retrieval_calls'],metrics['test_calls'],metrics['reads_per_run']),(6,4,2,2))
        self.assertEqual(state['action_budget']['retrieval_remaining'],0)
        self.assertEqual(metrics['retrieval_test_ratio'],2)
        self.assertEqual(score(result)['reads_per_run'],2)
        entry=row(result,planner_recording.load_session(helper.original['id'],helper.recordings))
        self.assertEqual(entry['reads_per_run'],2)
        self.assertEqual(entry['schema_prefetch_repairs'],1)
        self.assertEqual(entry['retrieval_test_ratio'],2)


if __name__=='__main__':unittest.main()
