import copy,unittest
from investigator import process_outcomes
from investigator.process_debugging import Probe,vertical,VERSION
from investigator.adaptive_runtime import AdaptiveRuntime
import test_flexible_investigation as flexible_fixture


class OutcomeContractTests(unittest.TestCase):
    def valid(self,outcome):
        roles=set(process_outcomes.REQUIRED_ROLES[outcome])|{'baseline'}
        observations={role:{'id':role,'status':'COMPLETED','process_roles':[role]} for role in roles}
        refs=list(observations)
        process={'procedure_step':1,'recommended_action':process_outcomes.ACTIONS[outcome],
          'visibility_boundary':{'deepest_layer':'layer-1','stopped_by':'REACHED','evidence_ids':refs[:1]},
          'baseline_above':{'status':'ESTABLISHED','layer':'layer-1','reason':None,'evidence_ids':['baseline']},
          'evidence_by_role':{r:([r] if r in process_outcomes.REQUIRED_ROLES[outcome] else [])
                              for r in process_outcomes.EVIDENCE_ROLES},
          'missing_capability':'A named adapter capability is absent.' if outcome=='NO_KNOWN_PATTERN' else None}
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

    def test_direct_lowest_layer_is_consistent_to_named_boundary(self):
        adapter=Adapter(['only'],{'only':10})
        result=vertical(adapter,'measure',{})
        self.assertEqual(result['classification'],'CONSISTENT_TO_BOUNDARY')
        self.assertEqual(result['technical_output']['visibility_boundary']['deepest_layer'],'only')
        self.assertEqual(adapter.evaluated,['only'])

    def test_business_question_verifies_flow_then_routes_to_domain_specialist(self):
        result=vertical(Adapter(['only'],{'only':10}),'measure',{'ticket_shape':'BUSINESS_QUESTION'})
        self.assertEqual(result['classification'],'BUSINESS_QUESTION')
        self.assertEqual(result['support']['process']['recommended_action'],'ASK_DOMAIN_SPECIALIST')

    def test_unreachable_source_names_stop_and_not_comparable_continues(self):
        adapter=Adapter(['top','middle','bottom','source'],{'top':10,'middle':10,'bottom':10,'source':10},
                        not_comparable={'middle'},stopped='NO_ACCESS')
        result=vertical(adapter,'measure',{})
        self.assertEqual(result['classification'],'CONSISTENT_TO_BOUNDARY')
        self.assertEqual(adapter.evaluated,['top','middle','bottom','source'])
        self.assertEqual(result['technical_output']['visibility_boundary']['stopped_by'],'NO_ACCESS')

    def test_known_runtime_adapter_runs_end_to_end_to_visible_boundary(self):
        fixture=flexible_fixture.DynamicTests();fixture.setUp();self.addCleanup(fixture.doCleanups)
        envelope=copy.deepcopy(fixture.envelope);envelope['strategy']=VERSION
        agent=AdaptiveRuntime(fixture.runtime,lambda _:self.fail('deterministic procedure must not call planner'))
        result=agent.run(agent.create(envelope,'vertical-known-domain')['id'])
        self.assertEqual(result['status'],'COMPLETED')
        self.assertEqual(result['outcome']['classification'],'CONSISTENT_TO_BOUNDARY')
        self.assertEqual(result['cloud_calls'],1)
        self.assertEqual(result['planner_calls'],0)
        self.assertEqual(len(fixture.native_calls),1)


if __name__=='__main__':unittest.main()
