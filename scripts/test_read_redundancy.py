"""Exact query reuse, without expression subsets or inferred result containment."""
import unittest
import sys
from pathlib import Path
import test_flexible_investigation as fixture
from investigator.adaptive_runtime import AdaptiveRuntime
from investigator.read_redundancy import normalized, key
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'acceptance/unknown_domain'))
from score_run import score
import test_session_replay as replay_fixture


class ReadRedundancyTests(unittest.TestCase):
    def test_normalization_preserves_labels_literals_and_lexical_types(self):
        sql=lambda text:normalized('bounded_sql',text)
        self.assertEqual(sql('SELECT 1 AS n'),sql('SELECT  1  AS n -- comment'))
        self.assertNotEqual(sql("SELECT N'abc'"),sql("SELECT N 'abc'"))
        self.assertNotEqual(sql("SELECT 'a b'"),sql("SELECT 'a  b'"))
        dax=lambda text:normalized('bounded_dax',text)
        self.assertNotEqual(dax('EVALUATE ROW("a",[X],"b",[Y])'),dax('EVALUATE ROW("b",[Y],"a",[X])'))
        self.assertNotEqual(dax('EVALUATE ROW("a",[X])'),dax('EVALUATE ROW("a",[X],"b",[Y])'))

    def test_scope_context_policy_and_limits_are_part_of_identity(self):
        plan={'model_id':'model','revision':1,'context_id':'context','query':'EVALUATE ROW("n",1)','max_rows':20}
        request={'context_hash':'hash','policy_hash':'policy'}
        original=key('bounded_dax',plan,request,'v1')
        for changed in (dict(plan,max_rows=30),dict(plan,model_id='other'),dict(plan,revision=2)):
            self.assertNotEqual(original,key('bounded_dax',changed,request,'v1'))
        self.assertNotEqual(original,key('bounded_dax',plan,request,'v2'))
        self.assertNotEqual(original,key('bounded_dax',plan,dict(request,policy_hash='other'),'v1'))
        self.assertNotEqual(original,key('bounded_dax',plan,dict(request,context_hash='other'),'v1'))
        self.assertNotEqual(key('bounded_dax',plan,request,'v1','scope1'),key('bounded_dax',plan,request,'v1','scope2'))

    def test_duplicate_keeps_read_budget_and_attaches_prior_receipt_then_source_runs(self):
        helper=fixture.DynamicTests();helper.setUp();self.addCleanup(helper.doCleanups)
        helper.envelope['limits']['cloud_calls']=2
        calls=[]
        def planner(payload):
            calls.append(payload)
            if len(calls)<=2:
                text='EVALUATE ROW("value",[Total])' if len(calls)==1 else 'EVALUATE  ROW ( "value", [Total] )'
                return helper.decision('QUERY',query={'tool':'bounded_dax','text':text,'max_rows':20})
            if len(calls)==3:
                reused=payload['observations'][-1];prior=payload['observations'][0]
                self.assertEqual(reused['duplicate_of'],prior['id'])
                self.assertEqual(reused['values'],prior['values'])
                return helper.decision('QUERY',query={'tool':'bounded_sql','text':'SELECT COUNT(*) AS n FROM business.events','max_rows':20})
            return helper.decision('ASK',question='Which intended business rule applies?')
        agent=AdaptiveRuntime(helper.runtime,planner)
        result=agent.run(agent.create(helper.envelope,'exact-duplicate')['id'])
        self.assertEqual(len(helper.native_calls),1)
        self.assertEqual(len(helper.sql_calls),1)
        self.assertEqual(result['cloud_calls'],2)
        self.assertEqual(score({'session':result})['redundant_reads_blocked'],1)
        self.assertEqual(result['planner_calls'],3)  # Existing read budget stops before another paid plan.

    def test_distinct_limit_is_not_refused(self):
        helper=fixture.DynamicTests();helper.setUp();self.addCleanup(helper.doCleanups)
        count=[0]
        def planner(payload):
            count[0]+=1
            if count[0]<=2:return helper.decision('QUERY',query={'tool':'bounded_dax',
                'text':'EVALUATE ROW("value",[Total])','max_rows':10*count[0]})
            return helper.decision('ASK',question='Which intended rule applies?')
        agent=AdaptiveRuntime(helper.runtime,planner)
        result=agent.run(agent.create(helper.envelope,'distinct-limit')['id'])
        self.assertEqual(result['cloud_calls'],2)
        self.assertEqual(score({'session':result})['redundant_reads_blocked'],0)

    def test_sql_duplicate_reuses_receipt_without_second_read(self):
        helper=fixture.DynamicTests();helper.setUp();self.addCleanup(helper.doCleanups)
        count=[0]
        def planner(payload):
            count[0]+=1
            if count[0]<=2:return helper.decision('QUERY',query={'tool':'bounded_sql',
                'text':'SELECT'+(' ' * count[0])+'COUNT(*) AS n FROM business.events','max_rows':20})
            return helper.decision('ASK',question='Which intended rule applies?')
        agent=AdaptiveRuntime(helper.runtime,planner)
        result=agent.run(agent.create(helper.envelope,'sql-duplicate')['id'])
        self.assertEqual(len(helper.sql_calls),1)
        self.assertEqual(result['cloud_calls'],1)
        self.assertEqual(score({'session':result})['redundant_reads_blocked'],1)

    def test_recorded_provider_probe_blocks_duplicate_without_new_read(self):
        helper=replay_fixture.SessionReplayTests();helper.setUp();self.addCleanup(helper.doCleanups)
        proposal={'next':{'kind':'QUERY','tool':'bounded_dax',
                         'text':'EVALUATE  ROW ( "value", [Total] )','max_rows':20},'hypotheses':{}}
        result=helper.replay('duplicate-probe',inject_at=5,injection=proposal)
        self.assertEqual(result['status'],'INJECTION_PROBE')
        self.assertEqual(result['session']['cloud_calls'],2)
        self.assertEqual(result['unrecorded_tool_attempts'],0)
        self.assertEqual(result['network_calls'],0)
        self.assertEqual(score(result)['redundant_reads_blocked'],1)


if __name__=='__main__':unittest.main()
