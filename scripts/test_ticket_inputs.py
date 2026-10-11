import unittest
from investigator import ticket_inputs, ticket_clarification
from investigator.onboarding import digest


class TicketInputTests(unittest.TestCase):
    def test_current_question_does_not_change_or_borrow_the_original_optional_fields(self):
        original={'text':'Old question','request_key':'one','structured':{'comparison':'APPLICATION'}}
        changed={'text':'New question','request_key':'two'}
        saved={'request':original,'ticket':{'current_input':changed}}
        self.assertEqual(ticket_inputs.active_request(saved),changed)
        self.assertEqual(saved['request'],original)
        self.assertIsNone(ticket_inputs.route(ticket_inputs.active_request(saved),changed['text'],None))

    def test_plain_text_keeps_its_original_bytes(self):
        request={'text':'Original question.','request_key':'one'}
        self.assertEqual(ticket_inputs.document(request)['text'],request['text'])

    def test_optional_user_strings_have_exact_intervals_in_a_labelled_document(self):
        request={'text':'Check this.','request_key':'one',
            'structured':{'number':'Global card shows about 3.4M.','report_page':'Inventory main page'}}
        document=ticket_inputs.document(request)
        for part in document['provenance']['parts']:
            original=request['text'] if part['pointer']=='/text' else request['structured'][part['pointer'].split('/')[-1]]
            self.assertEqual(document['text'][part['start']:part['end']],original)
            self.assertEqual(part['source_hash'],digest(original))
        self.assertEqual(document['provenance']['source_input_hash'],digest(request))

    def test_no_default_number_or_comparison_and_no_truncation(self):
        with self.assertRaises(ValueError):ticket_inputs.document({'text':'','request_key':'one'})
        with self.assertRaises(ValueError):ticket_inputs.document({'text':'a'*2000,'request_key':'one',
            'structured':{'number':'16'}})
        for structured in ({'number':16},{'comparison':'invented'},{'target_id':'invented'}):
            with self.assertRaises(Exception):ticket_inputs.document({'text':'Question','request_key':'one','structured':structured})

    def test_optional_link_has_an_exact_source_span_and_is_never_truncated(self):
        request={'text':'','request_key':'one','structured':{'report_link':'https://example.test/report'}}
        document=ticket_inputs.document(request)
        part=document['provenance']['parts'][-1]
        self.assertEqual(part['pointer'],'/structured/report_link')
        self.assertEqual(document['text'][part['start']:part['end']],request['structured']['report_link'])
        with self.assertRaises(ValueError):
            ticket_inputs.document({**request,'text':'x'*2000})

    def test_explicit_comparison_is_not_a_fabricated_choice_confirmation(self):
        request={'text':'Check Quantity.','request_key':'one','structured':{'comparison':'APPLICATION'}}
        config=ticket_clarification.settings()
        result=ticket_inputs.route(request,request['text'],config)
        self.assertEqual(result['version'],'ticket-comparison-input-v1')
        self.assertNotIn('confirmation',result)
        self.assertEqual(result['source_input_hash'],digest(request))
        self.assertIsNone(ticket_inputs.route(request,request['text'],{**config,'must_confirm':['COMPARISON']}))
        with self.assertRaises(ValueError):ticket_inputs.route(request,'Changed question.',config)
        config['comparison_choices']=[{'route':'STALE','label':'Freshness'}]
        with self.assertRaises(ValueError):ticket_inputs.route(request,request['text'],config)


if __name__=='__main__':unittest.main()
