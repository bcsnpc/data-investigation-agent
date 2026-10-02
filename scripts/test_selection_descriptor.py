import copy
import json
import unittest
from unittest.mock import patch
from jsonschema import Draft202012Validator,ValidationError
from investigator import selection_descriptor as descriptor,report_resolution
from investigator.question_intake import azure_resolve,wire_contract
import test_report_scoped_cells as scoped_fixture


class DescriptorTranslationTests(unittest.TestCase):
    def payload(self,text):
        return {'text':text,'models':[{'id':'model','measures':[{'id':'measure','name':'Revenue'}],
            'columns':[{'column_id':'column','name':'Region'}],
            'reports':[{'id':'report','name':'Example Report'}]}]}

    def response(self,value,hint):
        return {'report_quote':'Example Report','target_request':{
            'value_source':{'quote':value},'column_source':None,'descriptor':hint},
            'reported_candidates':[],'action':'PROPOSE','model_id':'m0','measure_id':'m0v0',
            'metric_quote':'Revenue','question':None,'triage':'MISMATCH_COMPLAINT:VERTICAL',
            'filters':[],'dimension_ids':[]}

    def translate(self,text,value,hint):
        with patch('ticket_planner.azure_generate',return_value=(self.response(value,hint),{})):
            return azure_resolve(self.payload(text))

    def test_warehouse_north_has_two_verbatim_nonoverlapping_fields(self):
        text='In Example Report, Revenue differs for warehouse North.'
        result,usage=self.translate(text,'North',{'state':'SEPARATED','source':{'quote':'warehouse'}})
        request=result['target_request']
        self.assertEqual(request['value_source']['quote'],'North')
        self.assertEqual(request['descriptor']['source']['quote'],'warehouse')
        self.assertIsNone(request['column_source'])
        descriptor.validate(request['descriptor'],request['value_source'],ticket=text)
        self.assertIn('descriptor',[x['field'] for x in usage['quote_provenance']])

    def test_bare_value_has_no_descriptor(self):
        result,_=self.translate('In Example Report, Revenue differs for North.','North',{'state':'VALUE_ONLY','source':None})
        self.assertEqual(result['target_request']['descriptor'],{'state':'VALUE_ONLY','source':None})

    def test_unseparated_phrase_is_explicit_and_not_silently_trimmed(self):
        result,_=self.translate('In Example Report, Revenue differs for warehouse North.','warehouse North',{'state':'UNSEPARATED','source':None})
        self.assertEqual(result['target_request']['value_source']['quote'],'warehouse North')
        self.assertIn('whole quoted phrase',descriptor.render(descriptor.note(result['target_request']['descriptor'])))

    def test_claimed_separation_with_overlap_is_refused(self):
        with self.assertRaisesRegex(ValueError,'overlap'):
            self.translate('In Example Report, Revenue differs for warehouse North.','warehouse North',{'state':'SEPARATED','source':{'quote':'warehouse'}})

    def test_wire_requires_descriptor_and_cannot_express_invalid_state_source_pairs(self):
        payload=self.payload('In Example Report, Revenue differs for warehouse North.')
        _,schema,_=wire_contract(payload)
        for state,source in (('SEPARATED',None),('VALUE_ONLY',{'quote':'warehouse'}),('UNSEPARATED',{'quote':'warehouse'})):
            with self.subTest(state=state),self.assertRaises(ValidationError):
                Draft202012Validator(schema).validate(self.response('North',{'state':state,'source':source}))
        missing=self.response('North',{'state':'VALUE_ONLY','source':None})
        del missing['target_request']['descriptor']
        with self.assertRaises(ValidationError):Draft202012Validator(schema).validate(missing)

    def test_hint_uses_exact_tokens_only_and_never_claims_binding_evidence(self):
        value={'state':'SEPARATED','source':{'start':0,'end':9,'quote':'warehouse'}}
        self.assertEqual(descriptor.note(value,'warehouse_name')['agreement'],'TEXT_AGREEMENT')
        self.assertEqual(descriptor.note(value,'warehousing')['agreement'],'TEXT_DISAGREEMENT')
        self.assertFalse(descriptor.note(value,'warehouse_name')['binding_evidence'])

    def test_current_producer_cannot_omit_descriptor_even_if_wire_enforcement_is_bypassed(self):
        response=self.response('North',{'state':'VALUE_ONLY','source':None})
        del response['target_request']['descriptor']
        with patch('ticket_planner.azure_generate',return_value=(response,{})):
            with self.assertRaisesRegex(ValueError,'descriptor'):
                azure_resolve(self.payload('In Example Report, Revenue differs for North.'))

    def test_hint_evidence_is_verbatim_but_never_leaks_identifier_form_or_json_into_business_prose(self):
        for quote in ('warehouse_name','app.Locations','{"field":"example"}'):
            value={'state':'SEPARATED','source':{'start':0,'end':len(quote),'quote':quote}}
            note=descriptor.note(value)
            self.assertEqual(note['descriptor']['source']['quote'],quote)
            text=descriptor.render(note,business=True)
            self.assertNotIn(quote,text)
            from investigator.business_vocabulary import validate_text
            validate_text(text,text)

    def test_intake_catalog_payload_is_byte_identical_and_schema_expansion_drops_no_entries(self):
        payload=self.payload('In Example Report, Revenue differs for warehouse North.');old=copy.deepcopy(payload)
        wire,schema,handles=wire_contract(payload)
        self.assertEqual(payload,old)
        self.assertEqual(len(wire['models'][0]['columns']),len(old['models'][0]['columns']))
        self.assertEqual(len(wire['models'][0]['reports']),len(old['models'][0]['reports']))
        before=copy.deepcopy(schema)
        target=before['properties']['target_request']['anyOf'][1]
        del target['properties']['descriptor'];target['required'].remove('descriptor')
        self.assertGreater(len(json.dumps(schema)),len(json.dumps(before)))


class DescriptorResolutionTests(unittest.TestCase):
    setUp=scoped_fixture.ScopedTests.setUp
    part=scoped_fixture.ScopedTests.part
    modify=scoped_fixture.ScopedTests.modify
    grouped=scoped_fixture.ScopedTests.grouped
    no_predicates=scoped_fixture.ScopedTests.no_predicates
    request=scoped_fixture.ScopedTests.request
    native=scoped_fixture.ScopedTests.native
    prepare=scoped_fixture.ScopedTests.prepare

    def run_hint(self,hint):
        self.no_predicates();self.grouped();self.request();self.native()
        self.scope['selection_request']['descriptor']={'state':'SEPARATED',
            'source':{'start':6,'end':6+len(hint),'quote':hint}}
        return self.prepare()

    def test_disagreeing_descriptor_does_not_change_lookup_or_resolution(self):
        scope,observations=self.run_hint('warehouse')
        self.assertEqual(scope['selection_resolution']['resolution_kind'],'OBSERVED')
        self.assertEqual(scope['selection_resolution']['column_id'],self.column['id'])
        self.assertEqual(scope['filters'][0]['values'],['North'])
        self.assertEqual(len(self.requests),1)
        self.assertNotIn('warehouse',self.requests[0]['query'])
        marker=observations[-1]
        self.assertEqual(marker['descriptor_hint']['agreement'],'TEXT_DISAGREEMENT')
        self.assertFalse(marker['descriptor_hint']['binding_evidence'])
        report_resolution.validate(marker,{o['id']:o for o in observations})

    def test_agreement_is_recorded_only_after_receipt_based_resolution(self):
        scope,observations=self.run_hint('Region')
        self.assertEqual(scope['selection_resolution']['resolution_kind'],'OBSERVED')
        self.assertEqual(len(self.requests),1)
        self.assertEqual(observations[-1]['descriptor_hint']['agreement'],'TEXT_AGREEMENT')
        self.assertIn('did not affect',descriptor.render(observations[-1]['descriptor_hint']))

    def test_descriptor_never_resolves_a_report_with_no_grouping_column(self):
        self.no_predicates();self.request();self.native()
        self.scope['selection_request']['descriptor']={'state':'SEPARATED',
            'source':{'start':6,'end':12,'quote':'Region'}}
        with self.assertRaisesRegex(report_resolution.ResolutionRefused,'no scoped grouping column'):
            self.prepare()
        self.assertEqual(self.requests,[])


if __name__=='__main__':unittest.main()
