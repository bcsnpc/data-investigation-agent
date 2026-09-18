"""Adversarial parser admission and evidence-driven dynamic runtime tests."""
import copy
import unittest
from unittest.mock import patch
from uuid import uuid4
import test_enterprise_discovery as discovery_fixture
from investigator import query_sql,query_dax,dynamic_reasoning
from investigator.enterprise_discovery import Discovery
from investigator.runtime import Runtime
from investigator.adaptive_runtime import AdaptiveRuntime
from investigator.native_identity import make,KEY
from investigator.model_context import assets
from investigator.onboarding import Conflict


class QueryParserTests(unittest.TestCase):
    def test_lookup_handles_roundtrip_without_mutating_payload(self):
        payload={'candidates':[],'hypotheses':[],'observations':[],
                 'context':[{'id':'fabric://model/measure/Encoded%20Name','parent_id':'fabric://model/table'}]}
        original=copy.deepcopy(payload)
        wire,schema,handles=dynamic_reasoning.wire_contract(payload)
        self.assertEqual(payload,original)
        self.assertEqual(wire['context'][0]['id'],'a0')
        result=dynamic_reasoning.from_wire({'next':{'kind':'LOOKUP','operation':'asset','value':'a0'},'hypotheses':[]},handles)
        self.assertEqual(result['lookup']['value'],original['context'][0]['id'])
        with self.assertRaises(ValueError):
            dynamic_reasoning.from_wire({'next':{'kind':'LOOKUP','operation':'asset','value':'invented'},'hypotheses':[]},handles)

    def test_hypothesis_wire_schema_separates_new_and_evidenced_updates(self):
        schema=dynamic_reasoning.wire_schema([], [{'id':'h1'}], [{'id':'receipt'}])
        variants=schema['properties']['hypotheses']['items']['anyOf']
        new,update=variants
        self.assertNotIn('h1',new['properties']['id']['enum'])
        self.assertEqual(new['properties']['status']['enum'],['OPEN'])
        self.assertEqual(update['properties']['id']['enum'],['h1'])
        self.assertNotIn('OPEN',update['properties']['status']['enum'])
        self.assertEqual(update['properties']['evidence_ids']['items']['enum'],['receipt'])
        self.assertEqual(update['properties']['evidence_ids']['minItems'],1)

    def test_generated_sql_requires_retrieved_schema_but_metadata_lookup_is_available_first(self):
        def tools(observations):
            choices=dynamic_reasoning.wire_schema([],observations=observations)['properties']['next']['anyOf']
            return next(c for c in choices if c['properties']['kind']['enum']==['QUERY'])['properties']['tool']['enum']
        self.assertEqual(tools([]),['bounded_dax'])
        observation={'id':'receipt','tool':'context','status':'COMPLETED','metadata':{'asset':{'id':'source','kind':'SqlObject',
          'availability':'CURRENT','metadata':{'columns':[{'name':'id'}]}}}}
        self.assertIn('bounded_sql',tools([observation]))
        observation['status']='REJECTED'
        self.assertEqual(tools([observation]),['bounded_dax'])

    def test_scalar_comparison_preserves_expression_and_filter_semantics(self):
        keys=dynamic_reasoning.scalar_read_keys
        self.assertEqual(keys('EVALUATE ROW("first",[Ratio])'),keys('evaluate row("renamed", [Ratio])'))
        self.assertNotEqual(keys('EVALUATE ROW("v",[Ratio])'),keys('EVALUATE ROW("v",[Ratio]+1)'))
        self.assertNotEqual(keys('EVALUATE ROW("v",CALCULATE([Ratio],Events[Region]="West"))'),keys('EVALUATE ROW("v",CALCULATE([Ratio],Events[Region]="East"))'))
        self.assertFalse(keys('EVALUATE CALCULATETABLE(ROW("v",[Ratio]))'))
        self.assertFalse(keys('EVALUATE ROW("v",NOW())'))

    def test_large_context_excerpt_exposes_both_ends_and_marks_omission(self):
        value={'context_version':'revision','content':'START'+('x'*15000)+'END'}
        with patch('investigator.context_search.get_asset',return_value=value):
            observed=dynamic_reasoning.lookup(None,{'operation':'asset','value':'asset'})
        self.assertEqual(observed['completeness'],'PARTIAL')
        self.assertIn('START',observed['metadata']['excerpt_head'])
        self.assertIn('END',observed['metadata']['excerpt_tail'])
        self.assertGreater(observed['metadata']['omitted_characters'],0)

    def setUp(self):
        self.objects=[{'id':'events','metadata':{'schema_name':'approved','name':'events','type_desc':'USER_TABLE',
          'columns':[{'name':'id','data_type':'int'},{'name':'amount','data_type':'decimal'}, {'name':'state','data_type':'varchar'}]}}]
        self.assets=[{'id':'t','kind':'SemanticTable','name':'Events'},
                     {'id':'c','kind':'SemanticColumn','name':'Region','parent_id':'t'},
                     {'id':'m','kind':'Measure','name':'Ratio','parent_id':'t'}]

    def test_sql_cte_joins_aggregates_and_parameters(self):
        value=query_sql.compile_query("WITH a AS (SELECT id, SUM(amount) AS total FROM approved.events WHERE state='ok' GROUP BY id) SELECT a.id,a.total FROM a JOIN approved.events AS e ON e.id=a.id WHERE a.total>1",self.objects)
        self.assertEqual(value['asset_ids'],['events']);self.assertEqual(value['result_columns'],['id','total'])
        self.assertNotIn("'ok'",value['query']);self.assertIn('@p0',value['query']);self.assertIn('TOP 251',value['query'])

    def test_sql_write_escape_ambiguous_unknown_and_unsupported_rejected(self):
        bad=["DELETE FROM approved.events","SELECT * INTO approved.new FROM approved.events",
             "SELECT * FROM approved.events; DROP TABLE approved.events", "EXEC proc", "SELECT dbo.secret() FROM approved.events",
             "SELECT * FROM remote.db.approved.events", "SELECT * FROM hidden.events", "SELECT * FROM OPENROWSET('a','b','c')",
             "SELECT missing FROM approved.events", "SELECT @@VERSION FROM approved.events", "SELECT * FROM approved.events WITH (NOLOCK)",
             "SELECT * FROM approved.events OPTION(MAXDOP 8)", "SELECT * FROM approved.events FOR XML AUTO",
             "SELECT id FROM approved.events a JOIN approved.events b ON a.id=b.id", "SELECT TOP 50 PERCENT * FROM approved.events",
             "SELECT COUNT(*) FROM approved.events WHERE id=@x"]
        for query in bad:
            with self.subTest(query=query),self.assertRaises(Exception):query_sql.compile_query(query,self.objects)

    def test_dax_nested_measure_ratio_and_filters(self):
        value=query_dax.compile_query('EVALUATE CALCULATETABLE(ROW("value", DIVIDE([Ratio],2)), TREATAS({"West"}, Events[Region]))',self.assets)
        self.assertEqual(value['asset_ids'],['c','m']);self.assertIn('TOPN(251',value['query'])
        value=query_dax.compile_query('EVALUATE VAR x = [Ratio] RETURN ROW("v",x)',self.assets)
        self.assertIn('VAR x',value['query'])

    def test_dax_no_unknown_reference_function_second_query_or_command(self):
        for query in ['EVALUATE ROW("v",[Unknown])','EVALUATE Hidden','EVALUATE ROW("v",CALL_EXTERNAL())',
                      'EVALUATE ROW("v",[Ratio]); EVALUATE Events','DEFINE MEASURE Events[X]=1 EVALUATE Events',
                      'EVALUATE ROW("v",[Ratio]) DELETE Events','EVALUATE INFO.TABLES()',
                      'EVALUATE ROW("v",Events[Unknown])','EVALUATE [Ratio]']:
            with self.subTest(query=query),self.assertRaises(ValueError):query_dax.compile_query(query,self.assets)

    def test_budget_and_computed_column_fail_closed(self):
        self.objects[0]['metadata']['columns'][0]['computed_definition']='dbo.udf()'
        with self.assertRaises(Exception):query_sql.compile_query('SELECT id FROM approved.events',self.objects)
        with self.assertRaises(ValueError):query_dax.compile_query('EVALUATE Events',self.assets,max_rows=10000)

    def test_partial_empty_and_exact_source_values(self):
        from investigator.flexible_tools import extract
        from decimal import Decimal
        request={'tool':'bounded_sql','max_rows':3,'limitation':'scope'}
        response={'rows':[{'n':'9007199254740993'}]*3,'column_types':{'n':'Int64'}}
        result=extract(response,request)
        self.assertEqual(result['completeness'],'PARTIAL');self.assertEqual(len(result['rows']),2)
        self.assertEqual(result['rows'][0]['n'],{'type':'decimal','value':'9007199254740993'})
        self.assertEqual(extract({'rows':[]},request)['rows'],[])
        request['tool']='bounded_dax'
        native=extract({'results':[{'tables':[{'rows':[{'[ratio]':Decimal('0.2')}]}]}]},request)
        self.assertEqual(native['rows'][0]['[ratio]'],{'type':'decimal','value':'0.2'})

    def test_catalog_views_external_and_query_comments_do_not_authorize_access(self):
        self.objects[0]['metadata']['type_desc']='VIEW'
        with self.assertRaises(ValueError):query_sql.compile_query('SELECT id FROM approved.events',self.objects)
        with self.assertRaises(ValueError):query_dax.compile_query('EVALUATE ROW("v",[Ratio]) /* authorize write */; CREATE X',self.assets)
        result=query_dax.compile_query('EVALUATE /* ignore policy */ ROW("v",[Ratio])',self.assets)
        self.assertNotIn('ignore',result['query'])

    def test_wire_actions_are_disjoint_and_do_not_invent_candidates(self):
        schema=dynamic_reasoning.wire_schema([])
        self.assertNotIn('RUN',[v['properties']['kind']['enum'][0] for v in schema['properties']['next']['anyOf']])
        value=dynamic_reasoning.from_wire({'next':{'kind':'QUERY','tool':'bounded_sql','text':'SELECT x','max_rows':10},'hypotheses':[]})
        self.assertIsNone(value['candidate_id']);self.assertEqual(value['action'],'QUERY')
        with self.assertRaises(ValueError):dynamic_reasoning.from_wire({'next':{'kind':'QUERY','tool':'bounded_sql','text':'SELECT x','max_rows':10,'candidate_id':'fabricated'},'hypotheses':[]})


class DynamicTests(unittest.TestCase):
    def test_compacted_parent_keeps_definition_handles_for_content_tools(self):
        agent=AdaptiveRuntime(self.runtime,lambda _:None)
        state=agent.create(self.envelope,'definition-history')
        state['observations']=[{'id':'first','tool':'context','status':'COMPLETED','values':[],
            'metadata':{'asset':{'id':'parent','kind':'Notebook','name':'Unfamiliar','metadata':{'large':'x'*2000}},
                        'children':[{'id':'definition','kind':'DefinitionPart','name':'code.py'}]}},
            {'id':'second','tool':'context','status':'COMPLETED','values':[], 'metadata':{}}]
        payload=agent.payload(state,[])
        self.assertEqual(payload['observations'][0]['metadata']['children'][0]['id'],'definition')
        wire,schema,handles=dynamic_reasoning.wire_contract(payload)
        content=next(c for c in schema['properties']['next']['anyOf'] if c['properties'].get('operation',{}).get('enum')==['content'])
        allowed=content['properties']['value']['enum']
        self.assertEqual([handles[h] for h in allowed],['definition'])

    def test_repeated_context_stops_without_pretending_new_evidence(self):
        agent=AdaptiveRuntime(self.runtime,lambda _:self.decision('LOOKUP',lookup={'operation':'search','value':'events'}))
        result=agent.run(agent.create(self.envelope,'repeated-context')['id'])
        self.assertEqual(result['stop_reason'],'NO_PROGRESS')
        self.assertEqual(result['planner_calls'],3)
        self.assertEqual(result['cloud_calls'],0)
        self.assertEqual(result['observations'][-1]['duplicate_of'],result['observations'][0]['id'])

    def test_rejected_queries_stop_without_spending_cloud_budget(self):
        agent=AdaptiveRuntime(self.runtime,lambda _:self.decision('QUERY',query={
            'tool':'bounded_sql','text':'SELECT missing_column FROM business.events','max_rows':20}))
        result=agent.run(agent.create(self.envelope,'invalid-columns')['id'])
        self.assertEqual(result['cloud_calls'],0)
        self.assertEqual(result['planner_calls'],2)
        self.assertEqual(result['stop_reason'],'NO_PROGRESS')
        self.assertIn('column binding failed',result['observations'][0]['metadata']['reason'])
        self.assertFalse(self.sql_calls)

    def test_rejected_lookups_stop_without_cloud_calls(self):
        agent=AdaptiveRuntime(self.runtime,lambda _:self.decision('LOOKUP',lookup={'operation':'asset','value':'unknown'}))
        result=agent.run(agent.create(self.envelope,'invalid-lookups')['id'])
        self.assertEqual(result['planner_calls'],2)
        self.assertEqual(result['stop_reason'],'NO_PROGRESS')
        self.assertEqual(result['cloud_calls'],0)

    def test_duplicate_detection_rejects_tampered_prior_receipt(self):
        query={'tool':'bounded_dax','text':'EVALUATE ROW("v",[Total])','max_rows':20}
        agent=AdaptiveRuntime(self.runtime,lambda _:self.decision('QUERY',query=query))
        identity=agent.create(self.envelope,'tampered-dedup')['id']
        agent.step(identity)
        state=agent.get(identity)
        receipt=next(o['id'] for o in state['observations'] if o['tool']=='bounded_dax')
        with self.store.connect() as db:
            db.execute('UPDATE flexible_diagnostics SET result=? WHERE id=?',('{}',receipt))
        with self.assertRaises(Conflict):dynamic_reasoning.candidate(self.store,self.config,state,query)

    def test_dynamic_budget_admission_keeps_cloud_and_legacy_bounds(self):
        from investigator.adaptive_candidates import catalog
        envelope=copy.deepcopy(self.envelope)
        envelope['limits'].update(planner_calls=12,input_characters=200000)
        catalog(self.store,self.config,envelope)
        envelope['limits']['planner_calls']=13
        with self.assertRaises(ValueError):catalog(self.store,self.config,envelope)
        envelope['limits']['planner_calls']=12
        envelope.pop('strategy')
        with self.assertRaises(ValueError):catalog(self.store,self.config,envelope)

    def test_relabelled_completed_scalar_is_rejected_without_second_query(self):
        calls=[]
        def planner(payload):
            calls.append(payload)
            if len(calls)<=2:
                return self.decision('QUERY',query={'tool':'bounded_dax','text':'EVALUATE ROW("label'+str(len(calls))+'",[Total])','max_rows':20})
            self.assertIn('already observed',payload['observations'][-1]['metadata']['reason'])
            return self.decision('ASK',question='What business rule defines the expected amount?')
        agent=AdaptiveRuntime(self.runtime,planner)
        result=agent.run(agent.create(self.envelope,'dedup')['id'])
        self.assertEqual(result['cloud_calls'],1)
        self.assertEqual(len(self.native_calls),1)

    def setUp(self):
        self.fixture=discovery_fixture.DiscoveryTests();self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
        f=self.fixture
        f.config['fabric']['native_reader']={'mode':'isolated_reader','tenant_id':str(uuid4()),'principal_id':str(uuid4()),
           'account':'reader@example.com','workspace_ids':[f.ws]}
        f.discovery=Discovery(f.store,f.config);f.scan();self.store=f.store;self.config=f.config
        self.model=self.store.list(True)[0];self.native_calls=[];self.sql_calls=[]
        def native(request):
            self.native_calls.append(request)
            response={'results':[{'tables':[{'rows':[{'[value]':12}]}]}]}
            return dict(response,**{KEY:make(response,request,self.config['fabric']['native_reader'])})
        def source(request):
            self.sql_calls.append(request)
            return {'rows':[{'n':'12'}],'read_only_verified':True}
        self.runtime=Runtime(self.store,self.config,native,source)
        m=self.model
        self.envelope={'model_id':m['id'],'revision':m['revision'],'context_id':m['context_id'],
          'measure_id':m['context']['measures'][0]['id'],'filters':[],'dimension_ids':[],'source_tests':[],
          'symptom':'Is this data empty?','strategy':dynamic_reasoning.VERSION,
          'limits':{'cloud_calls':4,'planner_calls':6,'wall_seconds':900,'input_characters':80000,'max_depth':3}}

    def decision(self,action,**kwargs):
        return dict(action=action,candidate_id=None,question=None,stop_reason=None,hypotheses=[],
                    lookup=None,query=None,assessment=None)|kwargs,{}

    def test_lookup_rejected_query_two_real_tools_hypothesis_revision_and_replay(self):
        calls=[]
        def planner(payload):
            calls.append(payload)
            if len(calls)==1:return self.decision('LOOKUP',lookup={'operation':'asset','value':next(a['id'] for a in dynamic_reasoning.context_search.latest(self.store)['assets'] if a['kind']=='SqlObject')},
                hypotheses=[{'id':'empty','claim':'Source may be empty','status':'OPEN','evidence_ids':[]}])
            if len(calls)==2:return self.decision('QUERY',query={'tool':'bounded_sql','text':'DROP TABLE business.events','max_rows':20})
            if len(calls)==3:
                self.assertEqual(payload['observations'][-1]['status'],'REJECTED')
                return self.decision('QUERY',query={'tool':'bounded_sql','text':'SELECT COUNT(*) AS n FROM business.events','max_rows':20})
            if len(calls)==4:
                receipt=payload['observations'][-1]['id']
                return self.decision('QUERY',query={'tool':'bounded_dax','text':'EVALUATE ROW("value", [Total])','max_rows':20},
                    hypotheses=[{'id':'empty','claim':'Observed source count is nonzero','status':'REJECTED','evidence_ids':[receipt]}])
            return self.decision('STOP',stop_reason='ENOUGH_DIAGNOSTICS',assessment={
                'classification':'INSUFFICIENT_EVIDENCE','claim':'Both scoped reads returned values; equivalence is not established.',
                'evidence_ids':[o['id'] for o in payload['observations'] if o['tool']!='context'],
                'alternatives':['Measures may have different meanings'],'limits':['No intended business contract supplied']})
        agent=AdaptiveRuntime(self.runtime,planner)
        result=agent.run(agent.create(self.envelope,'dynamic')['id'])
        self.assertEqual(result['status'],'COMPLETED');self.assertEqual(result['cloud_calls'],2)
        self.assertEqual(result['hypotheses'][0]['status'],'REJECTED')
        self.assertEqual(len(self.native_calls),1);self.assertEqual(len(self.sql_calls),1)
        self.assertEqual(result['outcome']['assessment']['provenance'],'LLM_INFERRED')
        self.assertFalse(result['outcome']['cause_verified'])
        self.assertEqual(agent.run(result['id'])['id'],result['id']);self.assertEqual(len(calls),5)

    def test_changed_context_holds_before_planning(self):
        agent=AdaptiveRuntime(self.runtime,lambda _:self.fail('stale planning'))
        state=agent.create(self.envelope,'stale');self.fixture.scan()
        self.assertEqual(agent.run(state['id'])['status'],'HELD');self.assertFalse(self.native_calls)

    def test_principal_and_parser_checked_before_native_dispatch(self):
        from investigator.flexible_tools import build
        plan={k:self.envelope[k] for k in ('model_id','revision','context_id')}
        plan.update(query='EVALUATE ROW("v", [Total])',max_rows=20)
        denied=copy.deepcopy(self.config);denied['fabric'].pop('native_reader')
        with self.assertRaises(Conflict):build(self.store,plan,denied,'bounded_dax')
        plan['query']='EVALUATE ROW("v", [Secret])'
        with self.assertRaises(ValueError):build(self.store,plan,self.config,'bounded_dax')

    def test_missing_source_permission_receipt_fails_and_replay_does_not_call(self):
        from investigator.flexible_tools import run
        calls=[]
        plan={k:self.envelope[k] for k in ('model_id','revision','context_id')}
        plan.update(query='SELECT COUNT(*) AS n FROM business.events',max_rows=20)
        result=run(self.store,plan,self.config,'bounded_sql',lambda q:calls.append(q) or {'rows':[{'n':'1'}]})
        self.assertEqual(result['status'],'FAILED');self.assertEqual(len(calls),1)

    def test_dynamic_cancel_before_next_turn_has_no_query(self):
        agent=AdaptiveRuntime(self.runtime,lambda _:self.fail('cancelled planning'))
        state=agent.create(self.envelope,'cancel');agent.cancel(state['id'])
        self.assertEqual(agent.run(state['id'])['status'],'CANCELLED');self.assertFalse(self.native_calls)

    def test_assessment_cannot_claim_verified_cause_or_cite_unknown_evidence(self):
        proposal=self.decision('STOP',stop_reason='ENOUGH_DIAGNOSTICS',assessment={
            'classification':'VERIFIED_TECHNICAL_DEFECT','claim':'verified','evidence_ids':[],
            'alternatives':['unknown'],'limits':['unknown']})[0]
        payload={'hypotheses':[],'observations':[],'candidates':[]}
        with self.assertRaises(ValueError):dynamic_reasoning.validate(proposal,payload)
        proposal['assessment']['classification']='LIKELY_TECHNICAL_DEFECT'
        with self.assertRaises(ValueError):dynamic_reasoning.validate(proposal,payload)

    def test_invalid_planner_contract_is_feedback_without_remote_dispatch(self):
        calls=[]
        def planner(payload):
            calls.append(payload)
            if len(calls)==1:return self.decision('RUN',candidate_id='invented')
            self.assertEqual(payload['observations'][0]['status'],'REJECTED')
            return self.decision('ASK',question='What business rule defines the expected value?')
        agent=AdaptiveRuntime(self.runtime,planner);r=agent.run(agent.create(self.envelope,'bad-contract')['id'])
        self.assertEqual(r['status'],'NEEDS_INPUT');self.assertEqual(r['cloud_calls'],0)


if __name__=='__main__':unittest.main()
