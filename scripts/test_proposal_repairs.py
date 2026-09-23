"""Repairs save planner calls without inventing semantics or broadening authority."""
import copy
import json
import os
import unittest
from unittest.mock import patch
import test_flexible_investigation as fixture
from investigator.proposal_repairs import repair
from investigator.adaptive_runtime import AdaptiveRuntime
from investigator.dynamic_reasoning import validate
import httpx
from openai import DefaultHttpxClient
from investigator import planner_recording
from investigator.adaptive_planner import azure_plan
import test_session_replay as replay_fixture


class LocalRepairTests(unittest.TestCase):
    def test_identical_duplicates_and_text_bounds_preserve_input(self):
        h={'id':'h1','claim':'c'*401,'status':'OPEN','evidence_ids':[]}
        proposal={'action':'ASK','candidate_id':None,'question':'q'*501,'stop_reason':None,
                  'hypotheses':[h,copy.deepcopy(h)],'lookup':None,'query':None,'assessment':None}
        original=copy.deepcopy(proposal)
        fixed,events=repair(proposal)
        validate(fixed,{'candidates':[],'observations':[],'hypotheses':[]})
        self.assertEqual(proposal,original)
        self.assertEqual(len(fixed['hypotheses']),1)
        self.assertEqual({e['repair_kind'] for e in events},{'hypothesis_id','text_bound'})
        self.assertEqual(len(fixed['question']),500)
        self.assertEqual(len(fixed['hypotheses'][0]['claim']),400)

    def test_conflicting_duplicates_remain_rejected_and_query_never_changes(self):
        h={'id':'h1','claim':'First claim','status':'OPEN','evidence_ids':[]}
        proposal={'action':'QUERY','candidate_id':None,'question':None,'stop_reason':None,
                  'hypotheses':[h,dict(h,claim='Conflicting claim')], 'lookup':None,
                  'query':{'tool':'bounded_sql','text':'x'*16001,'max_rows':1},'assessment':None}
        fixed,events=repair(proposal)
        self.assertEqual(fixed,proposal)
        self.assertFalse(events)
        with self.assertRaises(ValueError):validate(fixed,{'candidates':[],'observations':[],'hypotheses':[]})

    def test_three_consecutive_duplicate_shapes_progress_without_extra_planning(self):
        helper=fixture.DynamicTests();helper.setUp();self.addCleanup(helper.doCleanups)
        calls=[]
        def planner(payload):
            calls.append(payload)
            if len(calls)<=3:
                h={'id':'h'+str(len(calls)),'claim':'A structural hypothesis.','status':'OPEN','evidence_ids':[]}
                return helper.decision('QUERY',query={'tool':'bounded_sql',
                    'text':f'SELECT COUNT(*) AS n{len(calls)} FROM business.events','max_rows':20},hypotheses=[h,dict(h)])
            return helper.decision('ASK',question='Which intended business rule applies?')
        agent=AdaptiveRuntime(helper.runtime,planner)
        result=agent.run(agent.create(helper.envelope,'duplicate-shape')['id'])
        self.assertEqual(result['planner_calls'],4)
        self.assertEqual(len(helper.sql_calls),3)
        self.assertNotEqual(result['stop_reason'],'NO_PROGRESS')
        self.assertFalse(any(e['kind']=='PROPOSAL_REJECTED' for e in result['events']))
        kinds=[e['detail']['repair_kind'] for e in result['events'] if e['kind']=='PROPOSAL_REPAIRED']
        self.assertEqual(kinds.count('hypothesis_id'),3)
        self.assertEqual(kinds.count('schema_prefetch'),1)

    def test_unauthorized_object_is_not_prefetched_or_executed(self):
        helper=fixture.DynamicTests();helper.setUp();self.addCleanup(helper.doCleanups)
        agent=AdaptiveRuntime(helper.runtime,lambda _:helper.decision('QUERY',query={
            'tool':'bounded_sql','text':'SELECT COUNT(*) AS n FROM forbidden.secrets','max_rows':20}))
        with patch('investigator.dynamic_reasoning.lookup',side_effect=AssertionError('Unauthorized prefetch')):
            result=agent.step(agent.create(helper.envelope,'unauthorized')['id'])
        self.assertEqual(result['cloud_calls'],0)
        self.assertFalse(helper.sql_calls)
        self.assertEqual(result['events'][-1]['kind'],'PROPOSAL_REJECTED')

    def test_repair_is_recorded_even_when_dispatch_deadline_has_elapsed(self):
        helper=fixture.DynamicTests();helper.setUp();self.addCleanup(helper.doCleanups)
        clock=[1000]
        def planner(payload):
            clock[0]=2000
            return helper.decision('ASK',question='q'*501)
        agent=AdaptiveRuntime(helper.runtime,planner,clock=lambda:clock[0])
        result=agent.run(agent.create(helper.envelope,'repair-deadline')['id'])
        self.assertEqual(result['stop_reason'],'DEADLINE')
        self.assertEqual(result['cloud_calls'],0)
        self.assertTrue(any(e['kind']=='PROPOSAL_REPAIRED' for e in result['events']))

    def test_recorded_three_rejection_shapes_are_repaired_in_full_offline_replay(self):
        helper=replay_fixture.SessionReplayTests();helper.setUp();self.addCleanup(helper.doCleanups)
        calls=[]
        def provider(request):
            calls.append(request)
            if len(calls)<=3:
                h={'id':'h'+str(len(calls)),'claim':'c'*401,'status':'OPEN','evidence_ids':[]}
                action={'kind':'QUERY','tool':'bounded_sql',
                        'text':f'SELECT COUNT(*) AS n{len(calls)} FROM business.events','max_rows':20}
                hypotheses=[h,dict(h)]
            else:
                action={'kind':'ASK','question':'q'*501};hypotheses=[]
            return httpx.Response(200,json={'id':'offline','object':'response','model':'offline-fixture',
                'status':'completed','usage':None,'output':[{'type':'function_call','call_id':'offline',
                'name':'dynamic_investigation_action','arguments':json.dumps({'next':action,'hypotheses':hypotheses})}]})
        policy=planner_recording.load_session(helper.original['id'],helper.recordings)[0]['context']['usage_policy']
        agent=AdaptiveRuntime(helper.helper.runtime,azure_plan,clock=lambda:1000,planner_profile={'adapter':'azure'},usage_policy=policy)
        with patch.object(planner_recording,'ROOT',helper.root),patch.dict(os.environ,{
                'INVESTIGATOR_RECORD_PLANNER':'1','AZURE_OPENAI_ENDPOINT':'https://offline.openai.azure.com',
                'AZURE_OPENAI_DEPLOYMENT':'offline-fixture','AZURE_OPENAI_API_KEY':'offline-placeholder-credential'}), \
                patch('openai.DefaultHttpxClient',side_effect=lambda **kw:DefaultHttpxClient(transport=httpx.MockTransport(provider),**kw)):
            helper.original=agent.run(agent.create(helper.helper.envelope,'recorded-repairs')['id'])
        result=helper.replay('repairs')
        self.assertEqual(result['status'],'MATCHED',result['differences'])
        self.assertEqual(result['session']['planner_calls'],4)
        self.assertEqual(result['session']['cloud_calls'],3)
        kinds=[e['detail']['repair_kind'] for e in result['session']['events'] if e['kind']=='PROPOSAL_REPAIRED']
        self.assertEqual(kinds.count('hypothesis_id'),3)
        self.assertEqual(kinds.count('text_bound'),4)
        self.assertEqual(kinds.count('schema_prefetch'),1)


if __name__=='__main__':unittest.main()
