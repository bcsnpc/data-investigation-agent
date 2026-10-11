import copy
import unittest
from investigator import input_reference, ticket_inputs, report_scope, intake_extraction
from investigator.adapters.report_link import bind, LinkRefused
from investigator.question_intake import validate
from investigator.onboarding import digest
from test_intake_extraction import fixture

WORKSPACE='11111111-1111-4111-8111-111111111111'
REPORT='22222222-2222-4222-8222-222222222222'
ASSET='fabric://'+WORKSPACE+'/'+REPORT
LINK='https://app.powerbi.com/groups/'+WORKSPACE+'/reports/'+REPORT+'/PageA'


def setup_reference(text='Global card Quantity shows 16. Can its saved context reproduce it?'):
    raw,payload=fixture(text,kind='VISUAL_CONTENT',triage='BUSINESS_QUESTION:NONE',reports=[],
        visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}],
        figures=[{'quote':'16','role':'PRIMARY','state':'NUMBER','precision_quote':None}])
    model=payload['models'][0];model['reports']=[{'id':ASSET,'name':'Report'}]
    for i,v in enumerate(model['visuals']):v.update(report_id=ASSET,page_id=ASSET+'/page/'+('PageA' if i==0 else 'PageB'))
    request={'text':text,'request_key':'one','structured':{'report_link':LINK}}
    payload['text']=ticket_inputs.document(request)['text']
    payload['_input_request']=request
    payload['_ticket_reference']=input_reference.from_input(request,payload['text'],payload['models'])
    return raw,payload,request


class InputReferenceTests(unittest.TestCase):
    def test_supplied_link_is_a_reference_not_a_name_quote_or_clicked_choice(self):
        raw,payload,request=setup_reference()
        value=intake_extraction.resolve(raw,payload);validate(value,payload)
        binding=value['report_binding'];reference=binding['reference']
        self.assertEqual(binding['resolution_kind'],'DECLARED_REFERENCE')
        self.assertIsNone(binding['source']);self.assertNotIn('confirmation',binding)
        self.assertEqual(reference['source']['quote'],LINK)
        self.assertEqual(reference['source_input_hash'],digest(request))
        self.assertEqual(value['target_visual']['target_id'],'card')
        self.assertEqual(value['reported_figure']['value'],'16')
        report_scope.report_binding(binding,reports=payload['models'][0]['reports'],ticket=payload['text'])

    def test_model_cannot_supply_its_own_reference_authority(self):
        raw,payload,_=setup_reference();value=intake_extraction.resolve(raw,payload)
        for missing in ('_input_request','_ticket_reference'):
            hostile=copy.deepcopy(payload);hostile.pop(missing)
            with self.assertRaisesRegex(ValueError,'supplied reference authority'):validate(value,hostile)

    def test_changed_request_and_catalog_refuse(self):
        _,payload,request=setup_reference();proof=payload['_ticket_reference']
        with self.assertRaisesRegex(ValueError,'another request'):
            input_reference.validate(proof,reports=payload['models'][0]['reports'],ticket='Changed')
        reports=[{'id':ASSET,'name':'Changed name'}]
        with self.assertRaisesRegex(ValueError,'catalog changed'):input_reference.validate(proof,reports=reports)
        request['structured']['report_link']=LINK+'?autoAuth=true'
        with self.assertRaisesRegex(ValueError,'document changed'):
            input_reference.from_input(request,payload['text'],payload['models'])

    def test_binding_identity_must_match_reference(self):
        _,payload,_=setup_reference();value=input_reference.binding(payload['_ticket_reference'])
        value['report_id']='other'
        with self.assertRaisesRegex(ValueError,'differs from its binding'):
            report_scope.report_binding(value,reports=payload['models'][0]['reports'],ticket=payload['text'])

    def test_native_binding_never_uses_display_name_similarity(self):
        _,payload,_=setup_reference();models=payload['models']
        models[0]['reports'][0]['id']='another-asset'
        with self.assertRaisesRegex(LinkRefused,'report is absent'):bind(LINK,models)

    def test_foreign_workspace_and_unknown_page_refuse(self):
        _,payload,_=setup_reference()
        for link in (LINK.replace(WORKSPACE,'33333333-3333-4333-8333-333333333333'),LINK.replace('PageA','Unknown')):
            with self.assertRaises(LinkRefused):bind(link,payload['models'])

    def test_duplicate_native_binding_refuses_even_if_names_differ(self):
        _,payload,_=setup_reference();models=payload['models'];other=copy.deepcopy(models[0]);other['id']='other-model'
        other['reports'][0]['name']='Other label';models.append(other)
        with self.assertRaisesRegex(LinkRefused,'multiply bound'):bind(LINK,models)

    def test_embedding_reference_requires_unique_retained_binding(self):
        _,payload,_=setup_reference()
        result=bind('https://app.powerbi.com/reportEmbed?reportId='+REPORT+'&pageName=PageA',payload['models'])
        self.assertEqual(result['report_id'],ASSET)

    def test_predicates_and_bookmarks_never_disappear_into_a_broader_scope(self):
        _,payload,request=setup_reference()
        for suffix in ("?filter=Sales/Region%20eq%20'North'",'?bookmarkGuid=SavedState'):
            request['structured']['report_link']=LINK+suffix
            with self.assertRaisesRegex(LinkRefused,'CONTEXT_UNSUPPORTED'):input_reference.preflight(request)
            with self.assertRaisesRegex(LinkRefused,'CONTEXT_UNSUPPORTED'):bind(LINK+suffix,payload['models'])

    def test_named_report_conflict_refuses_instead_of_overriding_user_text(self):
        text='In Other report, Global card Quantity shows 16. Can its saved context reproduce it?'
        raw,payload,_=setup_reference(text)
        raw['reports']=[{'quote':'Other report','role':'PRIMARY'}]
        payload['models'][0]['reports'].append({'id':'other','name':'Other report'})
        payload['_ticket_reference']=input_reference.from_input(payload['_input_request'],payload['text'],payload['models'])
        with self.assertRaisesRegex(ValueError,'conflicts with the supplied report'):intake_extraction.resolve(raw,payload)

    def test_link_page_cannot_supply_a_target_when_two_visuals_match(self):
        raw,payload,_=setup_reference();raw['visuals']=[]
        visual=copy.deepcopy(payload['models'][0]['visuals'][0]);visual['target_id']='second-card'
        payload['models'][0]['visuals'].append(visual)
        with self.assertRaisesRegex(ValueError,'uniquely select a visual'):intake_extraction.resolve(raw,payload)

    def test_confirmed_target_cannot_escape_the_link_page(self):
        from test_intake_confirmation import confirm
        raw,payload,_=setup_reference()
        confirmed,_,_=confirm(payload,raw,target='matrix',mode='TOTAL')
        with self.assertRaisesRegex(ValueError,'Confirmed target differs'):
            intake_extraction.resolve(raw,confirmed)

    def test_binding_keeps_catalog_coverage_and_leaves_provider_catalog_unchanged(self):
        from investigator.intake_extraction import wire
        raw,payload,_=setup_reference()
        before=copy.deepcopy(payload['models'])
        rendered_before=wire(payload)
        intake_extraction.resolve(raw,payload)
        self.assertEqual(payload['models'],before)
        self.assertEqual(wire(payload),rendered_before)
        self.assertEqual(len(before[0]['visuals']),2)

    def test_declared_reference_can_carry_an_inventory_without_an_external_contract(self):
        _,payload,_=setup_reference();binding=input_reference.binding(payload['_ticket_reference'])
        report_scope.validate_inventory({'report_id':ASSET,'discovered':[],'entries':[]},[],
            binding=binding,reports=payload['models'][0]['reports'],ticket=payload['text'])


if __name__=='__main__':unittest.main()
