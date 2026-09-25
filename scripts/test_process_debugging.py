import copy,unittest
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
                               if outcome in ('NO_KNOWN_PATTERN','NO_COMPARABLE_PATH') else None}
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

    def test_historical_labels_map_without_rewriting(self):
        old={'classification':'EXPECTED_BEHAVIOR'};before=copy.deepcopy(old)
        self.assertEqual(process_outcomes.read_label(old['classification']),'TRANSFORMATION_LOGIC')
        self.assertEqual(old,before)


class Adapter:
    def __init__(self,layers,values,*,not_comparable=(),explain=None,stopped='REACHED'):
        self.layers=[{'id':x} for x in layers];self.values=values
        self.not_comparable=set(not_comparable);self.explain=explain;self.stopped=stopped
        self.evaluated=[]
    def capabilities(self):return {'resolve_measure_path','evaluate_scoped_quantity'}
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

    def test_three_layers_stop_at_first_explained_boundary(self):
        adapter=Adapter(['top','middle','bottom'],{'top':10,'middle':10,'bottom':8},explain=True)
        result=vertical(adapter,'measure',{})
        self.assertEqual(result['classification'],'TRANSFORMATION_LOGIC')
        self.assertEqual(result['terminating_step'],5)
        self.assertEqual(adapter.evaluated,['top','middle','bottom'])
        self.assertEqual(len(result['technical_output']['queries']),3)

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


if __name__=='__main__':unittest.main()
