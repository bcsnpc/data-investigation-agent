"""Exact query reuse, without expression subsets or inferred result containment."""
import unittest
import sys
from pathlib import Path
import test_flexible_investigation as fixture
from investigator.adaptive_runtime import AdaptiveRuntime
from investigator.read_redundancy import key
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'acceptance/unknown_domain'))
from score_run import score
import test_session_replay as replay_fixture


class ReadRedundancyTests(unittest.TestCase):
    def test_scope_context_policy_and_limits_are_part_of_identity(self):
        plan={'model_id':'model','revision':1,'context_id':'context','query':'EVALUATE ROW("n",1)','max_rows':20}
        request={'context_hash':'hash','policy_hash':'policy','compiled_read':'ROW(1)'}
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
                text='EVALUATE ROW("value",[Total])' if len(calls)==1 else 'EVALUATE  ROW ( "different label", [Total] )'
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
                'text':('SELECT COUNT(*) AS n FROM business.events a' if count[0]==1 else 'SELECT  COUNT(*) AS renamed FROM business.events other_alias'),'max_rows':20})
            return helper.decision('ASK',question='Which intended rule applies?')
        agent=AdaptiveRuntime(helper.runtime,planner)
        result=agent.run(agent.create(helper.envelope,'sql-duplicate')['id'])
        self.assertEqual(len(helper.sql_calls),1)
        self.assertEqual(result['cloud_calls'],1)
        self.assertEqual(score({'session':result})['redundant_reads_blocked'],1)

    def test_distinct_compiled_reads_are_never_refused_in_suite(self):
        # Every distinct fixture read is admitted, even though mock results agree.
        # This deliberately tests admission rather than just comparing hashes.
        queries=[
            ('bounded_dax','EVALUATE ROW("a",[Total])'),
            ('bounded_dax','EVALUATE ROW("a",[Total]+1)'),
            ('bounded_dax','EVALUATE ROW("a",[Total]*2)'),
            ('bounded_dax','EVALUATE ROW("a",[Total],"b",[Total]+1)'),
            ('bounded_sql','SELECT COUNT(*) AS n FROM business.events'),
            ('bounded_sql','SELECT COUNT(*)+1 AS n FROM business.events'),
            ('bounded_sql','SELECT COUNT(*) AS n FROM business.events WHERE 1=1'),
            ('bounded_sql','SELECT COUNT(*) AS n FROM business.events WHERE 1=2')]
        for tool,text in queries:
            with self.subTest(tool=tool,query=text):
                helper=fixture.DynamicTests();helper.setUp()
                try:
                    first=next(q for t,q in queries if t==tool and q!=text)
                    proposals=iter([first,text])
                    def planner(payload):
                        query=next(proposals,None)
                        return helper.decision('QUERY',query={'tool':tool,'text':query,'max_rows':20}) if query else helper.decision('ASK',question='What intent applies?')
                    agent=AdaptiveRuntime(helper.runtime,planner)
                    result=agent.run(agent.create(helper.envelope,'distinct-suite')['id'])
                    self.assertEqual(result['cloud_calls'],2)
                    scored=score({'session':result})
                    self.assertEqual(scored['redundant_reads_blocked'],0)
                    self.assertEqual(scored['result_equality_overlap_reads'],1)
                finally:helper.doCleanups()

    def test_compiler_resolves_dax_member_qualification_and_outer_row_labels(self):
        from investigator.query_dax import compile_query
        assets=[{'id':'t','kind':'SemanticTable','name':'Fact'},
                {'id':'m','kind':'Measure','name':'Total','parent_id':'t'},
                {'id':'n','kind':'Measure','name':'Other','parent_id':'t'}]
        first=compile_query('EVALUATE ROW("a",[Total],"b",[Other])',assets)
        second=compile_query("EVALUATE ROW(\"other\",'Fact'[Other],\"total\",'Fact'[Total])",assets)
        self.assertEqual(first['compiled_read'],second['compiled_read'])
        self.assertNotEqual(first['compiled_read'],compile_query('EVALUATE ROW("a",[Total])',assets)['compiled_read'])
        self.assertIsNone(compile_query('EVALUATE ROW("a",[Total]+NOW())',assets)['compiled_read'])

    def test_sql_compiled_aliases_in_nested_scopes_and_distinct_joins(self):
        from investigator.query_sql import compile_query
        objects=[{'id':'e','metadata':{'schema_name':'app','name':'events','type_desc':'USER_TABLE',
                 'columns':[{'name':'id','data_type':'int'},{'name':'amount','data_type':'int'}]}}]
        compile=lambda query:compile_query(query,objects)['compiled_read']
        pairs=[
            ('SELECT SUM(a.amount) AS total FROM app.events a','SELECT SUM(b.amount) AS renamed FROM app.events b'),
            ('WITH x AS (SELECT id AS k FROM app.events) SELECT COUNT(x.k) AS n FROM x',
             'WITH y AS (SELECT id AS other FROM app.events) SELECT COUNT(y.other) AS count_alias FROM y'),
            ('SELECT SUM(x.k) AS n FROM (SELECT amount AS k FROM app.events) x',
             'SELECT SUM(y.other) AS renamed FROM (SELECT amount AS other FROM app.events) y')]
        for first,second in pairs:self.assertEqual(compile(first),compile(second))
        distinct=[
            'SELECT SUM(a.amount) AS n FROM app.events a JOIN app.events b ON a.id=b.id',
            'SELECT SUM(b.amount) AS n FROM app.events a JOIN app.events b ON a.id=b.id',
            'SELECT SUM(a.amount) AS n FROM app.events a LEFT JOIN app.events b ON a.id=b.id',
            'SELECT COUNT(a.amount) AS n FROM app.events a JOIN app.events b ON a.id=b.id']
        self.assertEqual(len({compile(query) for query in distinct}),len(distinct))

    def test_order_by_output_alias_binding_is_preserved(self):
        from investigator.query_sql import compile_query
        objects=[{'id':'e','metadata':{'schema_name':'app','name':'events','type_desc':'USER_TABLE',
                 'columns':[{'name':'id','data_type':'int'},{'name':'amount','data_type':'int'}]}}]
        compile=lambda text:compile_query(text,objects)['compiled_read']
        first=compile('SELECT id AS a, amount AS b FROM app.events ORDER BY a')
        renamed=compile('SELECT id AS x, amount AS y FROM app.events ORDER BY x')
        distinct=compile('SELECT id AS b, amount AS a FROM app.events ORDER BY a')
        self.assertEqual(first,renamed)
        self.assertNotEqual(first,distinct)

    def test_posthoc_metrics_have_no_admission_effect(self):
        from trajectory_metrics import metrics
        state={'observations':[
            {'status':'COMPLETED','completeness':'COMPLETE_RESPONSE','read_fingerprint':'a','values':[{'n':1}]},
            {'status':'COMPLETED','completeness':'COMPLETE_RESPONSE','read_fingerprint':'b','values':[{'n':1}]},
            {'status':'REJECTED','metadata':{'proposed_tool':'bounded_sql'}}],
            'decisions':[{'decision':{'query':{'tool':'bounded_sql'}}},{'decision':{'query':{'tool':'bounded_sql'}}}],
            'events':[{'kind':'PROPOSAL_REPAIRED','detail':{'repair_kind':'schema_prefetch'}}]}
        import copy
        before=copy.deepcopy(state);report=metrics(state)
        self.assertEqual(state,before)
        self.assertEqual(report['result_equality_overlap_reads'],1)
        self.assertEqual(report['schema_prefetch_repairs'],1)
        self.assertEqual(report['sql_rejection_rate'],0.5)

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
