import copy,json,unittest
from unittest.mock import patch
from investigator import process_outcomes
from investigator.process_debugging import Probe,vertical,VERSION
from investigator.adaptive_runtime import AdaptiveRuntime
import test_flexible_investigation as flexible_fixture


class OutcomeContractTests(unittest.TestCase):
    def valid(self,outcome):
        roles=set(process_outcomes.REQUIRED_ROLES[outcome])|{'baseline'}
        observations={role:{'id':role,'status':'COMPLETED','process_roles':[role]} for role in roles}
        if 'comparison' in observations:
            observations['comparison']['values_equal']=outcome in (
                'CONSISTENT_TO_BOUNDARY','INGESTION_GAP','BUSINESS_QUESTION')
            observations['comparison']['upper_layer']='layer-1'
        refs=list(observations)
        process={'procedure_step':1,'recommended_action':process_outcomes.ACTIONS[outcome],
          'visibility_boundary':{'deepest_layer':'layer-1','stopped_by':'REACHED','evidence_ids':refs[:1]},
          'baseline_above':{'status':'ESTABLISHED','layer':'layer-1','reason':None,'evidence_ids':['baseline']},
          'evidence_by_role':{r:([r] if r in process_outcomes.REQUIRED_ROLES[outcome] else [])
                              for r in process_outcomes.EVIDENCE_ROLES},
          'missing_capability':'A named adjacent binding or adapter capability is absent.'
                               if outcome in ('NO_KNOWN_PATTERN','NO_COMPARABLE_PATH') else None,
          'skipped_steps':[],'capabilities_declared':sorted({'evaluate_scoped_quantity','resolve_measure_path',
            'presentation_freshness','presentation_context','transformation_definition','job_history','ingestion'})}
        assessment={'classification':outcome,'evidence_ids':refs,'support':{'process':process}}
        return assessment,observations

    def test_every_outcome_accepts_only_its_evidence_contract(self):
        for outcome in process_outcomes.OUTCOMES:
            with self.subTest(outcome=outcome):
                assessment,observations=self.valid(outcome)
                process_outcomes.validate(assessment,observations)
                missing=process_outcomes.REQUIRED_ROLES[outcome][0]
                assessment['support']['process']['evidence_by_role'][missing]=[]
                with self.assertRaisesRegex(ValueError,'requires '+missing+' evidence'):
                    process_outcomes.validate(assessment,observations)

    def test_boundary_attribution_requires_baseline_or_specific_reason(self):
        assessment,observations=self.valid('TRANSFORMATION_LOGIC')
        assessment['support']['process']['baseline_above']={
            'status':'NOT_ESTABLISHED','layer':'layer-1','reason':'none','evidence_ids':[]}
        with self.assertRaisesRegex(ValueError,'specific establishment barrier'):
            process_outcomes.validate(assessment,observations)

    def test_boundary_attribution_baseline_must_be_immediately_above_divergence(self):
        assessment,observations=self.valid('TRANSFORMATION_LOGIC')
        observations['comparison']['upper_layer']='another-layer'
        with self.assertRaisesRegex(ValueError,'immediately above'):
            process_outcomes.validate(assessment,observations)

    def test_consistency_requires_a_successful_equal_boundary_comparison(self):
        assessment,observations=self.valid('CONSISTENT_TO_BOUNDARY')
        observations['comparison'].pop('values_equal')
        with self.assertRaisesRegex(ValueError,'successful equal boundary comparison'):
            process_outcomes.validate(assessment,observations)

    def test_every_verification_claim_requires_the_matching_comparison_result(self):
        equal=('CONSISTENT_TO_BOUNDARY','INGESTION_GAP','BUSINESS_QUESTION')
        divergent=('REFRESH_LATENCY','LOAD_LATENCY','PRESENTATION_LOGIC','TRANSFORMATION_LOGIC','DEFECT')
        for outcome in equal+divergent:
            with self.subTest(outcome=outcome):
                assessment,observations=self.valid(outcome)
                observations['comparison']['values_equal']=outcome in divergent
                with self.assertRaisesRegex(ValueError,'boundary comparison'):
                    process_outcomes.validate(assessment,observations)

    def test_no_comparable_path_requires_established_baseline_and_specific_gap(self):
        assessment,observations=self.valid('NO_COMPARABLE_PATH')
        process_outcomes.validate(assessment,observations)
        assessment['support']['process']['baseline_above']={
            'status':'NOT_ESTABLISHED','layer':'top','reason':'Reader unavailable','evidence_ids':[]}
        with self.assertRaisesRegex(ValueError,'established presentation baseline'):
            process_outcomes.validate(assessment,observations)

    def test_defect_rejects_any_skipped_competing_check(self):
        assessment,observations=self.valid('DEFECT')
        assessment['support']['process']['skipped_steps']=[{
          'step':5,'capability':'job_history','reason':'Adapter did not implement it.'}]
        with self.assertRaisesRegex(ValueError,'every competing'):
            process_outcomes.validate(assessment,observations)

    def test_capability_visibility_fields_are_bounded(self):
        assessment,observations=self.valid('NO_KNOWN_PATTERN')
        assessment['support']['process']['skipped_steps']=[{
            'step':1,'capability':'x','reason':'r'*301}]
        with self.assertRaisesRegex(ValueError,'Skipped procedure steps differ'):
            process_outcomes.validate(assessment,observations)
        assessment,observations=self.valid('NO_KNOWN_PATTERN')
        assessment['support']['process']['capabilities_declared']=['x'*81]
        with self.assertRaisesRegex(ValueError,'Declared capabilities'):
            process_outcomes.validate(assessment,observations)

    def test_historical_labels_map_without_rewriting(self):
        old={'classification':'EXPECTED_BEHAVIOR'};before=copy.deepcopy(old)
        self.assertEqual(process_outcomes.read_label(old['classification']),'TRANSFORMATION_LOGIC')
        self.assertEqual(old,before)


class Adapter:
    def __init__(self,layers,values,*,not_comparable=(),explain=None,stopped='REACHED'):
        self.layers=[{'id':x} for x in layers];self.values=values
        self.not_comparable=set(not_comparable);self.explain=explain;self.stopped=stopped
        self.evaluated=[]
    def capabilities(self):return {'resolve_measure_path','evaluate_scoped_quantity','presentation_freshness',
      'presentation_context','transformation_definition','job_history','ingestion'}
    def resolve_path(self,measure):return {'layers':self.layers,'stopped_by':self.stopped,
      'evidence':{'id':'path','tool':'context'}}
    def presentation_freshness(self,path,scope):return {'status':'CURRENT'}
    def evaluate(self,layer,measure,scope):
        self.evaluated.append(layer['id']);identity=layer['id']
        if identity in self.not_comparable:return Probe('NOT_COMPARABLE',identity,reason='No faithful translation')
        return Probe('OBSERVED',identity,{'id':'read-'+identity,'tool':'probe'},self.values[identity],query='READ '+identity)
    def presentation_context(self,boundary,scope):return {'explains':False}
    def transformation_definition(self,boundary):
        return {'explains':bool(self.explain),'explanation':'A retrieved rule accounts for the difference.',
                'evidence':{'id':'definition','tool':'context'}} if self.explain else {'explains':False}
    def job_history(self,boundary):return {'status':'CURRENT'}
    def ingestion(self,path,scope):return {'status':'CURRENT'}


class VerticalProcedureTests(unittest.TestCase):
    def test_missing_required_adapter_capability_uses_named_fallback(self):
        adapter=Adapter(['top'],{'top':10})
        adapter.capabilities=lambda:{'resolve_measure_path'}
        result=vertical(adapter,'measure',{})
        self.assertEqual(result['classification'],'NO_KNOWN_PATTERN')
        self.assertIn('evaluate_scoped_quantity',result['support']['process']['missing_capability'])

    def test_minimal_adapter_never_turns_unimplemented_steps_into_findings(self):
        forbidden={'DEFECT','TRANSFORMATION_LOGIC','PRESENTATION_LOGIC','REFRESH_LATENCY','LOAD_LATENCY','INGESTION_GAP'}
        for values in ({'top':10,'lower':9},{'top':10,'lower':10}):
            with self.subTest(values=values):
                adapter=Adapter(['top','lower'],values)
                adapter.capabilities=lambda:{'resolve_measure_path','evaluate_scoped_quantity'}
                adapter.presentation_freshness=adapter.presentation_context=adapter.transformation_definition=adapter.job_history=adapter.ingestion=lambda *a:self.fail('undeclared capability was called')
                result=vertical(adapter,'measure',{})
                self.assertNotIn(result['classification'],forbidden)
                skipped=result['technical_output']['skipped_steps']
                self.assertIn('presentation_freshness',{x['capability'] for x in skipped})
                if values['top']!=values['lower']:
                    self.assertEqual(result['classification'],'NO_KNOWN_PATTERN')
                    self.assertEqual(result['technical_output']['visibility_boundary']['stopped_by'],'CAPABILITY_NOT_IMPLEMENTED')

    def test_three_layers_stop_at_first_explained_boundary(self):
        adapter=Adapter(['top','middle','bottom'],{'top':10,'middle':10,'bottom':8},explain=True)
        result=vertical(adapter,'measure',{})
        self.assertEqual(result['classification'],'TRANSFORMATION_LOGIC')
        self.assertEqual(result['terminating_step'],5)
        self.assertEqual(adapter.evaluated,['top','middle','bottom'])
        self.assertEqual(len(result['technical_output']['queries']),3)

    def test_definition_judgment_is_called_only_after_a_real_divergence(self):
        equal=Adapter(['top','lower'],{'top':10,'lower':10},explain=True)
        equal.transformation_definition=lambda boundary:self.fail('equal values must not request definition judgment')
        self.assertEqual(vertical(equal,'measure',{})['classification'],'CONSISTENT_TO_BOUNDARY')
        divergent=Adapter(['top','lower'],{'top':10,'lower':9},explain=True)
        calls=[];original=divergent.transformation_definition
        divergent.transformation_definition=lambda boundary:(calls.append(boundary) or original(boundary))
        result=vertical(divergent,'measure',{})
        self.assertEqual(result['classification'],'TRANSFORMATION_LOGIC');self.assertEqual(len(calls),1)
        self.assertEqual(calls[0]['upper_probe'].value,10);self.assertEqual(calls[0]['lower_probe'].value,9)

    def test_inconclusive_competing_check_blocks_defect(self):
        adapter=Adapter(['top','lower'],{'top':10,'lower':9})
        adapter.presentation_context=lambda *a:{'status':'INCONCLUSIVE','explains':None,'reason':'Runtime selections unavailable'}
        result=vertical(adapter,'measure',{})
        self.assertEqual(result['classification'],'NO_KNOWN_PATTERN')
        self.assertIn('presentation_context',{x['capability'] for x in result['technical_output']['skipped_steps']})
        self.assertEqual(result['business_output']['skipped_steps'],result['technical_output']['skipped_steps'])

    def test_single_reachable_layer_is_not_reported_as_consistent(self):
        adapter=Adapter(['only'],{'only':10})
        result=vertical(adapter,'measure',{})
        self.assertEqual(result['classification'],'NO_COMPARABLE_PATH')
        self.assertEqual(result['terminating_step'],3)
        self.assertEqual(result['technical_output']['boundary_summary']['comparisons_executed'],0)
        self.assertEqual(result['technical_output']['visibility_boundary']['deepest_layer'],'only')
        self.assertEqual(adapter.evaluated,['only'])

    def test_business_question_verifies_flow_then_routes_to_domain_specialist(self):
        result=vertical(Adapter(['top','lower'],{'top':10,'lower':10}),'measure',{'ticket_shape':'BUSINESS_QUESTION'})
        self.assertEqual(result['classification'],'BUSINESS_QUESTION')
        self.assertEqual(result['support']['process']['recommended_action'],'ASK_DOMAIN_SPECIALIST')

    def test_not_comparable_boundary_continues_to_later_divergence(self):
        adapter=Adapter(['top','middle','bottom','source'],{'top':10,'middle':10,'bottom':10,'source':8},
                        not_comparable={'middle'},stopped='NO_ACCESS',explain=True)
        result=vertical(adapter,'measure',{})
        self.assertEqual(result['classification'],'TRANSFORMATION_LOGIC')
        self.assertEqual(adapter.evaluated,['top','middle','bottom','source'])
        self.assertEqual(len(result['technical_output']['boundary_summary']['not_comparable']),2)

    def test_consistency_stops_before_later_not_comparable_boundary(self):
        adapter=Adapter(['top','middle','bottom'],{'top':10,'middle':10,'bottom':10},not_comparable={'bottom'})
        result=vertical(adapter,'measure',{})
        self.assertEqual(result['classification'],'CONSISTENT_TO_BOUNDARY')
        self.assertEqual(result['technical_output']['visibility_boundary']['deepest_layer'],'middle')
        self.assertEqual(result['technical_output']['visibility_boundary']['stopped_by'],'NOT_COMPARABLE')

    def test_known_runtime_adapter_runs_end_to_end_to_visible_boundary(self):
        fixture=flexible_fixture.DynamicTests();fixture.setUp();self.addCleanup(fixture.doCleanups)
        envelope=copy.deepcopy(fixture.envelope);envelope['strategy']=VERSION
        agent=AdaptiveRuntime(fixture.runtime,lambda _:self.fail('deterministic procedure must not call planner'))
        result=agent.run(agent.create(envelope,'vertical-known-domain')['id'])
        self.assertEqual(result['status'],'COMPLETED')
        self.assertEqual(result['outcome']['classification'],'NO_COMPARABLE_PATH')
        self.assertEqual(result['outcome']['assessment']['terminating_step'],3)
        process=result['outcome']['assessment']['support']['process']
        self.assertEqual(process['visibility_boundary']['stopped_by'],'CAPABILITY_UNAVAILABLE')
        self.assertTrue(process['missing_capability'])
        self.assertEqual(result['outcome']['assessment']['technical_output']['boundary_summary']['comparisons_executed'],0)
        self.assertEqual(result['cloud_calls'],1)
        self.assertEqual(result['planner_calls'],0)
        self.assertEqual(len(fixture.native_calls),1)

    def test_partition_label_gap_names_the_missing_stable_binding(self):
        from investigator.adapters.microsoft_process import MicrosoftProcessAdapter
        metadata={'measure':{'id':'measure','parent_id':'table'},'assets':[{'kind':'SemanticTable','name':'Activity',
          'metadata':{'partitions':[{'source':{'schemaName':'dbo','entityName':'movement_values'}}]}}],
          'gaps':[{'reason':'UNRESOLVED_PARTITION_IDENTITY','detail':'unbound'}]}
        adapter=MicrosoftProcessAdapter(None,None,None,None,None)
        with patch('investigator.adapters.microsoft_process.context_search.measure_path',return_value=metadata):
            result=adapter.resolve_path('measure')
        self.assertIn("'dbo.movement_values'",result['missing_comparable_quantity'])
        self.assertEqual(result['stopped_by'],'CAPABILITY_UNAVAILABLE')

    def test_declared_partition_resolves_only_through_declared_endpoint_scope(self):
        from investigator.adapters.microsoft_process import MicrosoftProcessAdapter
        ws='00000000-0000-0000-0000-000000000001';model_id='fabric://'+ws+'/model'
        endpoint='fabric://'+ws+'/00000000-0000-0000-0000-000000000002';lake='fabric://'+ws+'/lake'
        definition=json.dumps({'model':{'expressions':[{'name':'Source','expression':
          'Sql.Database("host", "00000000-0000-0000-0000-000000000002")'}]}})
        context={'version':'scan','assets':[
          {'id':endpoint,'parent_id':'fabric://'+ws,'kind':'SQLEndpoint','name':'Endpoint','availability':'CURRENT'},
          {'id':lake,'parent_id':'fabric://'+ws,'kind':'Lakehouse','name':'Lake','availability':'CURRENT'},
          {'id':lake+'/table','parent_id':lake,'kind':'LakehouseTable','name':'dbo.events','availability':'CURRENT'},
          {'id':'outside','parent_id':'other','kind':'LakehouseTable','name':'dbo.events','availability':'CURRENT'},
          {'id':'definition','parent_id':model_id,'kind':'DefinitionPart','name':'model.bim','availability':'CURRENT',
           'metadata':{'content':definition}}],
          'graph':{'edges':[{'source':endpoint,'target':lake,'relation':'NATIVE_CASCADEDELETE'}]}}
        model={'context':{'model_assets':[{'id':model_id,'kind':'SemanticModel'}]}}
        metadata={'assets':[{'kind':'SemanticTable','metadata':{'partitions':[{'source':{
          'schemaName':'dbo','entityName':'events','expressionSource':'Source'}}]}}]}
        adapter=MicrosoftProcessAdapter(object(),{'fabric':{'workspace_id':ws}},model,None,None)
        with patch('investigator.adapters.microsoft_process.context_search.latest',return_value=context):
            result=adapter._partition_binding(metadata)
        self.assertEqual(result['status'],'RESOLVED');self.assertEqual(result['asset']['id'],lake+'/table')
        self.assertEqual(result['provenance'],'DECLARED_BY_DEFINITION')
        self.assertEqual(result['relation_cross_check']['status'],'AGREES')

    def test_denied_definition_is_not_reported_as_no_declaration(self):
        from investigator.adapters.microsoft_process import MicrosoftProcessAdapter
        ws='00000000-0000-0000-0000-000000000001';model_id='fabric://'+ws+'/model'
        context={'version':'scan','assets':[],'graph':{'edges':[]},'coverage':{
            model_id+'/definition':{'status':'UNAVAILABLE','error_type':'PermissionError'}}}
        model={'context':{'model_assets':[{'id':model_id,'kind':'SemanticModel'}]}}
        metadata={'assets':[{'kind':'SemanticTable','metadata':{'partitions':[{'source':{
          'schemaName':'dbo','entityName':'events','expressionSource':'Source'}}]}}]}
        adapter=MicrosoftProcessAdapter(object(),{'fabric':{'workspace_id':ws}},model,None,None)
        with patch('investigator.adapters.microsoft_process.context_search.latest',return_value=context):
            result=adapter._partition_binding(metadata)
        self.assertEqual(result['status'],'ACCESS_DENIED')

    def test_malformed_and_unsupported_partition_definitions_are_not_absence(self):
        from investigator.adapters.microsoft_process import MicrosoftProcessAdapter
        ws='00000000-0000-0000-0000-000000000001';model_id='fabric://'+ws+'/model'
        definition={'id':'definition','parent_id':model_id,'kind':'DefinitionPart','name':'model.bim',
                    'availability':'CURRENT','metadata':{'content':'not-json'}}
        context={'version':'scan','assets':[definition],'graph':{'edges':[]},'coverage':{}}
        model={'context':{'model_assets':[{'id':model_id,'kind':'SemanticModel'}]}}
        metadata={'assets':[{'kind':'SemanticTable','metadata':{'partitions':[{'source':{
          'schemaName':'dbo','entityName':'events','expressionSource':'Source'}}]}}]}
        adapter=MicrosoftProcessAdapter(object(),{'fabric':{'workspace_id':ws}},model,None,None)
        with patch('investigator.adapters.microsoft_process.context_search.latest',return_value=context):
            self.assertEqual(adapter._partition_binding(metadata)['status'],'DEFINITION_UNAVAILABLE')
            definition['metadata']['content']=json.dumps({'model':{'expressions':[{
                'name':'Source','expression':'Web.Contents("https://example.invalid")'}]}})
            self.assertEqual(adapter._partition_binding(metadata)['status'],'UNSUPPORTED_DECLARATION')

    def test_external_source_absence_is_not_claimed_without_an_implemented_inspector(self):
        from investigator.adapters.microsoft_process import MicrosoftProcessAdapter
        adapter=MicrosoftProcessAdapter(object(),None,None,None,None)
        adapter._partition_binding=lambda metadata:{'status':'RESOLVED','asset':{'id':'gold','parent_id':'lake','name':'events'},
            'definition_asset_id':'definition','candidates':[]}
        metadata={'measure':{'id':'measure','parent_id':'table','metadata':{'expression':'SUM(Activity[units])'}},
          'assets':[{'kind':'SemanticTable','metadata':{'partitions':[]}},{'kind':'SemanticColumn','name':'units'}],
          'gaps':[]}
        with patch('investigator.adapters.microsoft_process.context_search.measure_path',return_value=metadata), \
             patch('investigator.adapters.microsoft_process.context_search.latest',return_value={'assets':[],'graph':{'edges':[]}}):
            result=adapter.resolve_path('measure')
        self.assertEqual(result['evidence']['declared_source_binding']['external_source_declaration']['status'],
                         'CAPABILITY_NOT_IMPLEMENTED')

    def test_presentation_context_reuses_bounded_slicer_parser(self):
        from investigator.adapters.microsoft_process import MicrosoftProcessAdapter
        part={'id':'page','name':'definition/pages/one/page.json','content_hash':'hash',
              'metadata':{'content':'{}'}}
        model={'context':{'scan_id':'00000000-0000-0000-0000-000000000001','model_assets':[],
            'reports':[{'report':{'id':'report'},'binding_status':'RESOLVED_EXPLICIT_ID',
                        'gaps':[],'report_definitions':[part]}]}}
        adapter=MicrosoftProcessAdapter(None,None,model,None,None)
        parsed={'status':'NO_SLICERS_CAPTURED','page_path':part['name']}
        with patch('report_slicer_context.assess',return_value=parsed) as assess:
            result=adapter.presentation_context({}, {})
        self.assertEqual(result['status'],'INCONCLUSIVE')
        self.assertEqual(result['evidence']['slicer_context'],[parsed])
        assess.assert_called_once()

    def test_transformation_definition_searches_relevant_names_then_judges_observed_values(self):
        from investigator.adapters.microsoft_process import MicrosoftProcessAdapter
        captured=[]
        judge=lambda payload:captured.append(payload) or {'status':'COMPLETED','explains':True,'explanation':'Defined logic explains it.'}
        adapter=MicrosoftProcessAdapter(object(),None,None,None,None,judge_definition=judge)
        boundary={'upper':{'measure':{'name':'Handled Quantity'}},
            'lower':{'definition_asset_id':'definition','semantic_table':'Activity','semantic_column':'units',
                     'binding':{'asset':{'name':'dbo.movement_values'}}},
            'upper_probe':Probe('OBSERVED','upper',value=10),'lower_probe':Probe('OBSERVED','lower',value=9)}
        found={'asset_id':'definition','context_version':'scan','content_hash':'hash','total_characters':100,
               'matches':[{'offset':5,'excerpt':'relevant'}],'truncated':False,'next_offset':None}
        with patch('investigator.adapters.microsoft_process.context_search.find_content',side_effect=lambda _,__,needle:{**found,'needle':needle}):
            result=adapter.transformation_definition(boundary)
        self.assertTrue(result['explains']);self.assertEqual(captured[0]['upper_value'],10)
        self.assertEqual(captured[0]['lower_value'],9)
        self.assertEqual([x['needle'] for x in result['evidence']['searches']],
                         ['Handled Quantity','Activity','units','dbo.movement_values'])

    def test_truncated_search_without_a_match_is_inconclusive_and_not_judged(self):
        from investigator.adapters.microsoft_process import MicrosoftProcessAdapter
        adapter=MicrosoftProcessAdapter(object(),None,None,None,None,
            judge_definition=lambda payload:self.fail('incomplete evidence must not be judged'))
        boundary={'upper':{'measure':{'name':'Handled Quantity'}},
          'lower':{'definition_asset_id':'definition','semantic_table':'Activity','semantic_column':'units',
                   'binding':{'asset':{'name':'dbo.movement_values'}}},
          'upper_probe':Probe('OBSERVED','upper',value=10),'lower_probe':Probe('OBSERVED','lower',value=9)}
        found={'asset_id':'definition','context_version':'scan','content_hash':'hash','total_characters':10000,
               'matches':[],'truncated':True,'next_offset':5000}
        with patch('investigator.adapters.microsoft_process.context_search.find_content',
                   side_effect=lambda _,__,needle:{**found,'needle':needle}):
            result=adapter.transformation_definition(boundary)
        self.assertEqual(result['status'],'UNAVAILABLE');self.assertIsNone(result['explains'])
        self.assertEqual(result['evidence']['completeness'],'PARTIAL')


if __name__=='__main__':unittest.main()
