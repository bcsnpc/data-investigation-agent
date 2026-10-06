import copy,unittest
from unittest.mock import patch
from jsonschema import Draft202012Validator,ValidationError
from investigator import synthesis_narrative as narrative,evidence_synthesis as synthesis
from investigator import process_outcomes,assessment_support
import test_process_debugging as contract_fixtures

class NarrativeContractTests(unittest.TestCase):
    def test_recorded_latency_role_failure_keeps_engine_rendered_mechanism(self):
        # Exact sealed Round Seven response; the final bare role stays invalid.
        recorded='The checked path preserves the counted rows from L1 (LANDING) to L0 (SEMANTIC), while the counted rows differ between L2 (APPLICATION) and L1 (LANDING). This places the recorded count change at the transfer into L1 (LANDING), and L0 (SEMANTIC) reflects the L1 (LANDING) result rather than a further change within the semantic layer.'
        state,payload=self.source('LOAD_LATENCY')
        history=next(o for o in state['observations'] if o['id']=='job_history')
        from test_source_delivery import DeliveryAdapter
        adapter=DeliveryAdapter(['report','delivery','application'],dict(report=12,delivery=12,application=13))
        adapter.modified='2026-10-04T02:02:00Z'
        delivery=adapter.source_delivery(None,None)
        marker=delivery['evidence'];history.update({k:v for k,v in marker.items() if k!='id'})
        for row in delivery['observations'][:-1]:
            row['status']='COMPLETED'
            state['observations'].append(row)
            payload['evidence'].append({'id':row['id'],'result':copy.deepcopy(row)})
        value=self.response(payload);value['technical_output']['text']=recorded
        before=copy.deepcopy(state)
        assessment,outputs=narrative.assemble(narrative.Response(value),payload,state)
        technical=outputs['technical_output']
        self.assertEqual(assessment,state['assessment']);self.assertEqual(state,before)
        self.assertEqual(technical['mechanism_rejection']['reason'],'INVALID_LAYER_REFERENCE')
        self.assertEqual(technical['model_mechanism']['text'],'')
        self.assertEqual(technical['engine_mechanism']['evidence_ids'],['job_history'])
        self.assertIn('last successful load preceded the observed source change',technical['explanation']['text'])
        self.assertNotIn('Mechanism paragraph omitted',technical['explanation']['text'])

    def test_delivery_rendering_never_upgrades_another_outcome_or_uncompleted_read(self):
        state,payload=self.source('LOAD_LATENCY')
        history=next(o for o in state['observations'] if o['id']=='job_history')
        history.update(check_kind='SOURCE_DELIVERY',delivery_result={'status':'LATENT'})
        self.assertIsNotNone(narrative.path_narrative.delivery_mechanism(state))
        for field,value in [('status','FAILED'),('delivery_result',{'status':'CURRENT'})]:
            changed=copy.deepcopy(state)
            next(o for o in changed['observations'] if o['id']=='job_history')[field]=value
            self.assertIsNone(narrative.path_narrative.delivery_mechanism(changed))
        state['assessment']['classification']='INGESTION_GAP'
        self.assertIsNone(narrative.path_narrative.delivery_mechanism(state))

    def test_model_mechanism_is_explicit_and_separate_from_rendered_spine(self):
        state,payload=self.source('CONSISTENT_TO_BOUNDARY')
        value=self.response(payload)
        value['technical_output']['text']='The measured quantity passes through unchanged.'
        _,outputs=narrative.assemble(narrative.Response(value),payload,state)
        mechanism=outputs['technical_output']['model_mechanism']
        self.assertEqual(mechanism['text'],value['technical_output']['text'])
        self.assertEqual(mechanism['provenance'],'PROVIDER_MECHANISM')
        self.assertNotIn('Measure:',mechanism['text'])
        self.assertIn('Measure:',outputs['technical_output']['explanation']['text'])

    def test_wrong_layer_role_omits_only_paragraph_and_keeps_the_finding(self):
        state,payload=self.source('TRANSFORMATION_LOGIC')
        for text in ('The application measure repeats matches.','L0 (APPLICATION) repeats matches.'):
            value=self.response(payload);value['technical_output']['text']=text
            before=copy.deepcopy(state)
            assessment,outputs=narrative.assemble(narrative.Response(value),payload,state)
            self.assertEqual(assessment,state['assessment']);self.assertEqual(state,before)
            technical=outputs['technical_output']
            self.assertEqual(technical['mechanism_rejection']['reason'],'INVALID_LAYER_REFERENCE')
            self.assertNotIn(text,technical['explanation']['text'])
            self.assertIn('Measure:',technical['explanation']['text'])

    def source(self,outcome):
        value,observations=contract_fixtures.OutcomeContractTests().valid(outcome)
        for role,o in observations.items():
            o.update(tool='process' if role=='comparison' else 'bounded_dax',completeness='COMPLETE_RESPONSE')
        observations['baseline']['test_purpose']='ESTABLISH_BASELINE'
        value.update(claim='An observed scoped result.',alternatives=['Other scopes remain untested.'],limits=['Only the stated scope was checked.'])
        value['support'].update(mechanism='Observed evidence.',mechanism_evidence_ids=list(observations),
            intent_dependency='NOT_REQUIRED',intent_basis='Implemented behavior only.',intent_evidence_ids=[],
            measure_connection='ESTABLISHED',measure_connection_basis='A baseline was read.',
            measure_connection_evidence_ids=['baseline'],remaining_test='Obtain intended rules.')
        return {'envelope':{'symptom':'Explain the observed difference.'},'assessment':value,'observations':list(observations.values())},{'evidence':[{'id':i,
            **({'result':copy.deepcopy(o)} if 'surface_difference' in o else {})} for i,o in observations.items()],
            'deterministic_process_finding':{'classification':outcome}}

    def response(self,payload):
        statement={'text':narrative.path_narrative.LIMITATION,
                   'evidence_ids':[payload['evidence'][0]['id']]}
        business=copy.deepcopy(statement)
        business['text']=narrative.business_text(payload['deterministic_process_finding']['classification'],payload)
        technical={**statement,'text':narrative.path_narrative.summary(payload)}
        boundaries=narrative.path_narrative.divergent_boundaries(payload)
        if boundaries:technical['boundary_evidence_id']=boundaries[0]
        return {'business_output':business,'technical_output':technical}

    def test_wrong_mechanism_boundary_is_omitted_while_original_finding_and_spine_survive(self):
        state,payload=self.source('TRANSFORMATION_LOGIC')
        value=self.response(payload);value['technical_output']['boundary_evidence_id']='equal-boundary'
        value['technical_output']['text']='A fabricated selection explains this change.'
        original=copy.deepcopy(state)
        assessment,outputs=narrative.assemble(narrative.Response(value),payload,state)
        self.assertEqual(assessment,state['assessment']);self.assertEqual(state,original)
        technical=outputs['technical_output']
        self.assertNotIn('fabricated selection',technical['explanation']['text'])
        self.assertIn('Mechanism paragraph omitted',technical['explanation']['text'])
        self.assertEqual(technical['mechanism_rejection']['reason'],'WRONG_DIVERGENT_BOUNDARY')
        from investigator.synthesis_wire import prepare
        _,wire,handles=prepare(payload)
        allowed=wire['properties']['technical_output']['properties']['boundary_evidence_id']['enum']
        self.assertEqual([handles[i] for i in allowed],narrative.path_narrative.divergent_boundaries(payload))

    def test_business_cannot_include_free_prose_assets_queries_or_extra_numbers(self):
        from investigator.output_contract import BUSINESS
        for outcome in process_outcomes.OUTCOMES:
            state,payload=self.source(outcome)
            for text in ['movement_values','SQL sum of units','aggregate level','Delta commit','406 output rows','other_asset_xyz']:
                value=self.response(payload);value['business_output']['text']+=' '+text
                with self.subTest(outcome=outcome,text=text),self.assertRaises(ValidationError):
                    narrative.assemble(narrative.Response(value),payload,state)
            self.assertFalse(any(c.isdigit() for c in BUSINESS[outcome]))

    def test_actions_are_derived_and_technical_attestation_cannot_be_omitted(self):
        for outcome in process_outcomes.OUTCOMES:
            state,payload=self.source(outcome)
            fields=[{'field':field,'layer':layer,'evidence_id':'baseline'} for layer,field in
                    [('report','connection'),('report','engine'),('report','object'),('data','connection'),('data','engine')]]
            state['assessment']['technical_output']={'unattested_surface_fields':fields}
            _,outputs=narrative.assemble(narrative.Response(self.response(payload)),payload,state)
            for key in ('business_output','technical_output'):
                self.assertEqual(outputs[key]['recommended_action']['code'],process_outcomes.ACTIONS[outcome])
                self.assertIn(outputs[key]['recommended_action']['text'],outputs[key]['explanation']['text'])
            text=outputs['technical_output']['explanation']['text']
            self.assertEqual(text.count('Unattested connection, engine, object on report (receipt baseline).'),1)
            self.assertEqual(text.count('Unattested connection, engine on data (receipt baseline).'),1)

    def test_every_outcome_preserves_complete_contract_and_allows_limitations(self):
        for outcome in process_outcomes.OUTCOMES:
            with self.subTest(outcome=outcome):
                state,payload=self.source(outcome);original=copy.deepcopy(state)
                assessment,outputs=narrative.assemble(narrative.Response(self.response(payload)),payload,state)
                self.assertEqual(assessment,state['assessment'])
                self.assertEqual(state,original)
                self.assertEqual(outputs['business_output']['additional_limitations'],[])
                expected=outcome in ('NO_KNOWN_PATTERN','NO_COMPARABLE_PATH')
                self.assertEqual(assessment['support']['process']['missing_capability'] is not None,expected)
                self.assertEqual(outputs['technical_output']['mandatory_limits'],state['assessment']['limits'])

    def test_all_dependent_control_fields_are_unrepresentable(self):
        state,payload=self.source('CONSISTENT_TO_BOUNDARY');validator=Draft202012Validator(narrative.schema(payload))
        fields=set(synthesis.schema()['properties'])|set(assessment_support.SCHEMA['properties'])|set(process_outcomes.schema()['properties'])
        fields.discard('evidence_ids')
        fields.update(('status','layer','reason','stopped_by','deepest_layer','intent_dependency','measure_connection'))
        for field in fields:
            for location in ('root','business_output','technical_output'):
                value=self.response(payload)
                target=value if location=='root' else value[location]
                target[field]='contradictory'
                with self.subTest(field=field,location=location),self.assertRaises(ValidationError):validator.validate(value)

    def test_unknown_receipts_and_missing_citations_are_unrepresentable(self):
        state,payload=self.source('CONSISTENT_TO_BOUNDARY');validator=Draft202012Validator(narrative.schema(payload))
        for refs in ([],['not-displayed']):
            value=self.response(payload);value['business_output']['evidence_ids']=refs
            with self.assertRaises(ValidationError):validator.validate(value)

    def test_model_has_no_limitations_channel(self):
        state,payload=self.source('CONSISTENT_TO_BOUNDARY')
        value=self.response(payload)
        value['limitations']=[{'text':'Intended semantics remain unconfirmed.','evidence_ids':['baseline']}]
        with self.assertRaises(ValidationError):
            narrative.assemble(narrative.Response(value),payload,state)

    def test_invalid_fixed_evidence_still_fails(self):
        state,payload=self.source('CONSISTENT_TO_BOUNDARY')
        state['assessment']['support']['process']['missing_capability']='A conclusion-preventing gap.'
        with self.assertRaisesRegex(ValueError,'Only capability-gap'):
            narrative.assemble(narrative.Response(self.response(payload)),payload,state)
        state['assessment']['support']['process']['missing_capability']=None
        next(o for o in state['observations'] if o['id']=='comparison')['values_equal']=False
        with self.assertRaisesRegex(ValueError,'successful equal boundary'):
            narrative.assemble(narrative.Response(self.response(payload)),payload,state)

    def test_production_provider_uses_only_narrative_wire_schema(self):
        state,payload=self.source('CONSISTENT_TO_BOUNDARY')
        from investigator.synthesis_wire import prepare
        _,wire,handles=prepare(payload)
        answer={'technical_output':{'text':'The declared calculation was checked.','evidence_ids':[next(iter(handles))]}}
        with patch('ticket_planner.azure_generate',return_value=(answer,{})) as provider:
            response,usage=synthesis.azure_synthesize(payload,{})
        self.assertIsInstance(response,narrative.Response)
        sent=provider.call_args.kwargs['schema']
        self.assertEqual(set(sent['properties']),{'technical_output'})
        self.assertFalse(sent['additionalProperties'])
        Draft202012Validator(sent).validate(answer)

if __name__=='__main__':unittest.main()
