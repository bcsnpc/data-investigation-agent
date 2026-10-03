import copy,unittest
from unittest.mock import patch
from jsonschema import Draft202012Validator,ValidationError
from investigator import synthesis_wire as wire,evidence_synthesis as synthesis
from investigator.adapters.structured_output_contract import validate as provider_validate

class WirePreflightTests(unittest.TestCase):
    def payload(self):
        return {'outcome':'NO_COMPARABLE_PATH','rendered_business':'The visual "Example" was checked.',
            'evidence':[{'id':'actual-receipt'},{'id':'definition'},{'id':'comparison'}],
            'candidates':[{'receipt_id':'comparison','definition_receipt_id':'definition',
                'read_receipt_ids':['actual-receipt','actual-receipt']}],
            'boundaries':[{'comparison_id':'comparison'}]}

    def test_business_quote_cannot_enter_provider_enum_and_handles_decode_exactly(self):
        payload=self.payload();before=copy.deepcopy(payload);view,schema,handles=wire.prepare(payload)
        self.assertNotIn('rendered_business',view);self.assertNotIn('business_output',schema['properties'])
        provider_validate(schema);self.assertEqual(payload,before)
        value={'technical_output':{'text':'The declared calculation was checked.','evidence_ids':['r0']}}
        result=wire.decode(value,payload,schema,handles)
        self.assertEqual(result['technical_output']['evidence_ids'],['actual-receipt'])
        self.assertEqual(result['business_output']['text'],payload['rendered_business'])
        value['technical_output']['evidence_ids']=['invented-receipt']
        with self.assertRaises(ValidationError):wire.decode(value,payload,schema,handles)

    def test_every_spine_reference_resolves_before_provider(self):
        for field in ('receipt_id','definition_receipt_id','read_receipt_ids'):
            payload=self.payload();payload['candidates'][0][field]=['missing'] if field=='read_receipt_ids' else 'missing'
            with self.subTest(field=field),patch('ticket_planner.azure_generate') as call:
                with self.assertRaisesRegex(ValueError,'Dangling synthesis spine receipt missing'):synthesis.azure_synthesize(payload,{})
                call.assert_not_called()
        payload=self.payload();payload['boundaries'][0]['comparison_id']='missing'
        with self.assertRaisesRegex(ValueError,'missing'):wire.validate_references(payload)

    def test_original_store_must_establish_every_visible_receipt(self):
        payload=self.payload();originals=[{'id':e['id'],'status':'COMPLETED'} for e in payload['evidence']]
        wire.validate_references(payload,originals);originals[0]['status']='FAILED'
        with self.assertRaisesRegex(ValueError,'actual-receipt'):wire.validate_references(payload,originals)
        with self.assertRaisesRegex(ValueError,'actual-receipt'):wire.validate_references(payload,originals[1:])

    def test_provider_refuses_quoted_enum_and_unsupported_schema(self):
        _,schema,_=wire.prepare(self.payload())
        for change,error in (({'enum':['a"b']},'quote'),({'maxLength':500},'unsupported keywords'),({'pattern':'.*'},'unsupported keywords')):
            wrong=copy.deepcopy(schema);wrong['properties']['technical_output']['properties']['text'].update(change)
            with self.subTest(change=change),self.assertRaisesRegex(ValueError,error):provider_validate(wrong)
        for field in ('additionalProperties','required'):
            wrong=copy.deepcopy(schema);wrong.pop(field)
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,'require every field'):provider_validate(wrong)

    def test_consumer_bound_is_supplied_and_validated_without_truncation(self):
        from investigator import proposal_limits as limits,synthesis_narrative
        _,schema,handles=wire.prepare(self.payload())
        self.assertIn(str(limits.ASSESSMENT_CLAIM),schema['properties']['technical_output']['properties']['text']['description'])
        value={'technical_output':{'text':'x'*(limits.ASSESSMENT_CLAIM+1)+'.','evidence_ids':['r0']}}
        local=wire.decode(value,self.payload(),schema,handles)
        with self.assertRaises(ValidationError):Draft202012Validator(synthesis_narrative.schema(self.payload())).validate(local)

    def test_handle_view_preserves_coverage(self):
        from investigator.onboarding import encoded
        payload=self.payload();view,_,_=wire.prepare(payload)
        for key in ('evidence','candidates','boundaries'):self.assertEqual(len(view[key]),len(payload[key]))
        self.assertLess(len(encoded(view)),len(encoded(payload)))

    def test_invalid_provider_citation_preserves_numeric_usage(self):
        from investigator.generation_policy import ProviderResponseError,failure_usage
        answer={'technical_output':{'text':'The calculation was checked.','evidence_ids':['invented']}}
        with patch('ticket_planner.azure_generate',return_value=(answer,{'usage':{'input_tokens':20,'output_tokens':30}})):
            with self.assertRaises(ProviderResponseError) as caught:synthesis.azure_synthesize(self.payload(),{})
        self.assertEqual(failure_usage(caught.exception),{'input_tokens':20,'output_tokens':30})

    def test_runtime_names_dangling_id_without_reservation_or_provider_call(self):
        from test_evidence_synthesis import SynthesisTests
        from investigator import synthesis_digest
        helper=SynthesisTests();helper.setUp();self.addCleanup(helper.doCleanups)
        agent,state=helper.stopped()
        with agent.runtime.db() as db:
            state=agent.load(db,state['id']);payload=synthesis_digest.build(state,db)
            state['assessment']=helper.answer(payload);agent.save(db,state,'TEST_ASSESSMENT',{})
        bad={**payload,'candidates':[{'receipt_id':'missing-spine-receipt'}]}
        with patch('investigator.synthesis_spine.build',return_value=bad),patch('ticket_planner.azure_generate') as provider:
            result=agent.synthesize(state['id'],synthesis.azure_synthesize)
        provider.assert_not_called()
        record=result['synthesis']
        self.assertEqual(record['status'],'BLOCKED');self.assertEqual(record['calls'],0)
        self.assertIn('missing-spine-receipt',record['reason'])

if __name__=='__main__':unittest.main()
