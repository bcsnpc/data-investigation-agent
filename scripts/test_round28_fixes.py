"""Synthetic generic regressions; no HealthNet oracle/ticket reads."""
import copy
import json
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock
from investigator.estate_graph_contract import digest
from investigator.ai_investigation import Investigator
from investigator.prompt_scope import project
from investigator.retained_definition_evidence import references,resolve
from investigator.form_candidate_admission import check
from investigator.guided_intake import Catalog,admit_or_question
from investigator.query_sql import compile_query
from investigator.discovery_completeness import check as completeness
from investigator.guided_investigator_installation import Factory


def catalog():
    nodes=[dict(id='r',kind='REPORT',label='Revenue'),dict(id='p',kind='PAGE',label='Overview'),
        dict(id='v',kind='VISUAL',label='Collections'),dict(id='other',kind='VISUAL',label='Collections'),
        dict(id='p2',kind='PAGE',label='Other'),dict(id='m',kind='MEASURE',label='Cash')]
    edges=[dict(source=a,target=b,kind=k)for a,b,k in [('r','p','CONTAINS'),('r','p2','CONTAINS'),('p','v','CONTAINS'),('p2','other','CONTAINS'),('v','m','COMPUTED_FROM')]]
    return Catalog(dict(nodes=nodes,edges=edges))

class Fixes(TestCase):
    def test_definition_on_demand_is_exact_and_original_context_unchanged(self):
        item=dict(id='native',kind='DefinitionPart',name='model.bim',content_hash='a'*64,provenance={'source':'native'},metadata={'content':'native body '*10000})
        context=dict(retained_native_definitions=[item],path={'nodes':[]})
        original=copy.deepcopy(context);wire=project(context);reference=references(context)[0]
        self.assertNotIn('native body',json.dumps(wire));self.assertEqual(context,original)
        self.assertEqual(resolve(reference,context)['content'],item['metadata']['content'])
        self.assertEqual(wire['retained_native_definitions'][0]['evidence_id'],'case-evidence:'+digest(reference))
    def test_unknown_definition_without_fetch_proof_is_not_omitted(self):
        c={'retained_native_definitions':[dict(id='a',metadata={'content':'unproven native body'})]}
        self.assertEqual(project(c)['retained_native_definitions'],c['retained_native_definitions'])
    def test_shared_owner_does_not_expand_models(self):
        f=object.__new__(Factory);f.associated_nodes=None
        selected=dict(id='v',kind='VISUAL',owner='shared',properties={})
        f.graph=SimpleNamespace(intake_catalog=lambda:dict(nodes=[selected,dict(id='unrelated',kind='MODEL',owner='shared')],edges=[]),path_to_source=lambda _:dict(nodes=[selected],edges=[]))
        self.assertEqual([n['id']for n in f.target_path({'visual':'v'})['nodes']],['v'])
    def test_form_label_is_checked_inside_explicit_parent(self):
        request=dict(version='IntakeRequest/1',report='r',page='p',visual='Collections',issue_type='HOW_IS_THIS_CALCULATED',compared_with={'kind':'NOTHING'})
        result,checks,queries=check(request,catalog())
        self.assertEqual(result['visual'],'v');self.assertEqual(request['visual'],'Collections');self.assertTrue(checks)
        self.assertEqual(admit_or_question(result,catalog())['status'],'READY');self.assertFalse(queries)
    def test_explicit_valid_visual_is_never_substituted(self):
        request={'report':'r','page':'p','visual':'other'}
        result,checks,queries=check(request,catalog());self.assertEqual(result,request)
    def test_name_outside_selected_page_is_not_substituted(self):
        request={'report':'r','page':'p','visual':'not here'}
        result,checks,_=check(request,catalog());self.assertEqual(result,request);self.assertEqual(checks[0]['candidates'],[])
    def test_ties_use_bounded_value_checks_before_question(self):
        c=catalog();c.edges.append(dict(source='p',target='other',kind='CONTAINS'))
        request={'report':'r','page':'p','visual':'Collections','reported_figure':{'state':'NUMBER','value':'9','precision':'EXACT'}}
        probe=Mock(side_effect=lambda node,p,q:dict(status='SUCCEEDED',query_id='q'+node,value=9 if node=='v'else 8))
        result,checks,_=check(request,c,probe=probe);self.assertEqual(result['visual'],'v');self.assertEqual(probe.call_count,2)
    def test_unread_candidate_does_not_establish_unique_match(self):
        c=catalog();c.edges.append(dict(source='p',target='other',kind='CONTAINS'))
        request={'report':'r','page':'p','visual':'Collections','reported_figure':{'state':'NUMBER','value':'9','precision':'EXACT'}}
        probe=lambda n,p,q:dict(status='SUCCEEDED',query_id='q',value=9)if n=='v'else dict(status='UNAVAILABLE')
        self.assertEqual(check(request,c,probe=probe)[0]['visual'],'Collections')
    def test_readonly_string_functions_bind_and_writes_still_fail(self):
        objects=[dict(id='sql-table',metadata=dict(schema_name='dbo',name='Items',type_desc='USER_TABLE',columns=[dict(name='label',data_type='varchar')]))]
        for expression in ['RIGHT(label,3)','LEFT(label,2)','LEN(label)',"REPLACE(label,'x','y')",'REVERSE(label)']:
            with self.subTest(expression=expression):compile_query('SELECT '+expression+' AS part FROM dbo.Items',objects)
        for query in ["UPDATE dbo.Items SET label='x'",'SELECT dbo.run_code(label) AS p FROM dbo.Items',"SELECT * FROM OPENROWSET('x')"]:
            with self.assertRaises(Exception):compile_query(query,objects)
    def test_delivery_rejections_stop_at_same_evidence_frontier(self):
        v=object.__new__(Investigator);v.state={};v.queries=SimpleNamespace(records=[{'id':'q1'}])
        for _ in range(3):v.record_delivery_rejection('unsupported')
        self.assertEqual(v.state['outcome']['status'],'UNRESOLVED')
        self.assertIn('WITHOUT_NEW_READS',v.state['outcome']['stop'])
    def test_new_read_resets_rejection_frontier_but_not_repair_cap(self):
        v=object.__new__(Investigator);v.state={};v.queries=SimpleNamespace(records=[{'id':'q1'}])
        v.record_delivery_rejection('unsupported');v.queries.records.append({'id':'q2'});v.record_delivery_rejection('unsupported')
        self.assertEqual(v.state['delivery_rejections'],1)
        v.state['delivery_repair_attempts']=2
        with self.assertRaisesRegex(ValueError,'REPAIR_ATTEMPTS_EXHAUSTED'):v.repair_delivery({},'bad',kind='soft')
    def test_corrected_delivery_after_three_different_rejections_still_delivers(self):
        from test_round23_reasoning import LoopTests,tool
        fixture=LoopTests()
        validator=Mock(side_effect=[ValueError('TARGET_NOT_A_UNIQUE_OBSERVED_MATCH')]*3+
                       [{'business':'The checked total is 7.'}])
        loop=fixture.assemble([],validator=validator)
        def draft(number):
            return tool('submit_finding',{'verdict':'as designed','cause':'Revised supported draft '+str(number),
                'numbers':[7],'checked':['gold'],'evidence_ids':[loop.queries.records[0]['id']]},'draft-'+str(number))
        responses=[tool('run_sql',{'layer':'gold','query':'SELECT SUM(quantity) AS total FROM dbo.Items','purpose':'recreate'})]
        responses.extend(range(4))
        fixture.model.complete.side_effect=lambda **kw: draft(responses.pop(0)) if isinstance(responses[0],int) else responses.pop(0)
        result=loop.run()
        self.assertEqual(result['status'],'ANSWERED');self.assertEqual(result['model_calls'],5)
        fixture.execute.assert_called_once();self.assertEqual(validator.call_count,4)
    def test_different_drafts_cannot_retry_forever_at_one_evidence_frontier(self):
        v=object.__new__(Investigator);v.state={};v.queries=SimpleNamespace(records=[{'id':'q1'}])
        for n in range(6):v.record_delivery_rejection('unsupported',draft={'cause':str(n)})
        self.assertEqual(v.state['outcome']['stop'].split(':')[0],'DELIVERY_REVISION_LIMIT_WITHOUT_NEW_READS')
    def test_no_tool_turn_after_rejection_stops_with_checked_handoff(self):
        from test_round23_reasoning import LoopTests,tool
        fixture=LoopTests();v=fixture.assemble([tool('submit_finding',{'verdict':'not found','cause':'unchecked','numbers':[],'checked':[],'evidence_ids':['missing']}),{'content':[{'type':'text','text':'still thinking'}]}])
        result=v.run();self.assertEqual(result['status'],'UNRESOLVED');self.assertEqual(result['model_calls'],2)
        self.assertEqual(result['stop'],'DELIVERY_REJECTION_NO_NEW_READS_OR_TOOL_CALL');self.assertIn('investigation_report',result)
    def test_discovery_cannot_pass_empty_or_missing_columns(self):
        result=completeness({},{});self.assertFalse(result['complete'])
        result=completeness({'assets':[dict(id='t',kind='SqlObject',metadata={})]},{});self.assertTrue(any('columns missing'in x for x in result['gaps']))
    def test_model_requires_readability_and_rls_route_even_without_measures(self):
        b={'assets':[dict(id='model',kind='SemanticModel')]}
        result=completeness(b,{})
        self.assertTrue(any('readability'in x for x in result['gaps']));self.assertTrue(any('RLS'in x for x in result['gaps']))
    def test_discovery_rejects_relationship_to_unknown_column(self):
        b={'assets':[dict(id='rel',kind='SemanticRelationship',parent_id='model',metadata=dict(fromTable='A',fromColumn='missing',toTable='B',toColumn='missing'))]}
        self.assertFalse(completeness(b,{})['complete'])

    def test_unrelated_initial_intake_definitions_are_not_sent(self):
        from investigator.intake_prompt_scope import project as intake_project
        c=catalog();c.nodes['unrelated']=dict(id='unrelated',kind='MEASURE',label='Other metric',properties={'expression':'private irrelevant '*10000})
        v=intake_project(c,'Revenue Collections')
        self.assertNotIn('private irrelevant',json.dumps(v));self.assertNotIn('unrelated',{n['id']for n in v['candidate_names']})
        self.assertIn('unrelated',c.nodes)
    def test_report_setup_prepares_at_most_three_candidate_paths(self):
        c=catalog()
        for i in range(20):
            identity='v'+str(i);c.nodes[identity]=dict(id=identity,kind='VISUAL',label='Metric '+str(i));c.edges.append(dict(source='p',target=identity,kind='CONTAINS'))
        f=object.__new__(Factory);f.associated_nodes=None;f.routes={}
        path=Mock(side_effect=lambda root:dict(nodes=[c.nodes[root]],edges=[],stops=[]))
        f.graph=SimpleNamespace(intake_catalog=c.snapshot,path_to_source=path)
        result=f.target_path({'report':'r','page':'p','description':'check the number'})
        self.assertLessEqual(path.call_count,3);self.assertFalse(result['candidate_paths_exhaustive'])
    def test_discovery_complete_and_individual_gaps_are_loud(self):
        model=dict(id='model',kind='SemanticModel')
        table=dict(id='table',kind='SemanticTable',parent_id='model',name='Items',metadata={'columns':[{'name':'amount'}]})
        column=dict(id='column',kind='SemanticColumn',parent_id='table',name='amount')
        measure=dict(id='measure',kind='Measure',parent_id='table',metadata={'expression':'SUM(Items[amount])'})
        source=dict(id='source',kind='SqlObject',parent_id='sql://server/db',metadata={'columns':[{'name':'amount','data_type':'decimal'}]})
        binding=dict(table_asset='table',model_id='model',source_asset='source',server='server',sql_database='db',definition_sha256='a'*64)
        proof=dict(status='SUCCEEDED',read_only_verified=True,identity_reference='reader',observed_at='2026-11-26T00:00:00Z',capture_sha256='b'*64,rls_route=dict(status='VERIFIED',model_id='model',identity_reference='reader'))
        bundle=dict(assets=[model,table,column,measure,source],source_bindings=[binding],model_readability={'model':proof},graph=dict(nodes=[dict(id='m',properties={'asset_id':'measure'})],edges=[dict(source='m',target='column',kind='COMPUTED_FROM')]))
        config={'connections':{'source':dict(server='server',database='db')}}
        self.assertTrue(completeness(bundle,config)['complete'])
        for field in ('source_bindings','model_readability','graph'):
            bad=copy.deepcopy(bundle);bad.pop(field)
            self.assertFalse(completeness(bad,config)['complete'],field)
        bad=copy.deepcopy(bundle);bad['assets'].remove(bad['assets'][2]);self.assertFalse(completeness(bad,config)['complete'])
