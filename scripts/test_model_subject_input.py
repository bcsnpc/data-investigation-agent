"""A user's model-measure subject survives extraction and cannot invent a visual."""
import copy,unittest
from investigator import ticket_inputs,intake_extraction
from investigator.question_intake import validate
from test_intake_extraction import fixture

class ModelSubjectTests(unittest.TestCase):
    def request(self,text):
        return {'text':text,'request_key':'synthetic-model-subject','structured':{'subject':'MODEL_MEASURE'}}

    def test_explicit_model_measure_subject_keeps_generic_global_hint_out_of_visual_resolution(self):
        text='Is the global Quantity in Model current?'
        raw,payload=fixture(text,kind='FRESHNESS',triage='MISMATCH_COMPLAINT:VERTICAL',
            reports=[{'quote':'Model','role':'PRIMARY'}],
            visuals=[{'quote':'global','role':'PRIMARY','form':'UNGROUPED'}])
        payload['_input_request']=self.request(text)
        result=intake_extraction.resolve(raw,payload)
        self.assertEqual(result['measure_id'],'measure')
        self.assertNotIn('target_visual',result)
        self.assertNotIn('report_binding',result)
        validate(result,payload)
        self.assertEqual(intake_extraction.wire(payload)['user_subject'],'MODEL_MEASURE')

    def test_model_subject_is_bound_to_original_closed_request(self):
        request=self.request('Quantity in Model')
        self.assertTrue(ticket_inputs.model_subject(request,request['text']))
        with self.assertRaisesRegex(ValueError,'different input'):
            ticket_inputs.model_subject(request,'Different Quantity in Model')
        request['structured']['report_link']='https://example.invalid/report'
        with self.assertRaises(ValueError):ticket_inputs.document(request)

    def test_visual_question_cannot_be_relabelled_as_model_subject(self):
        text='Which rows are hidden in Report Global card Quantity?'
        raw,payload=fixture(text,kind='FILTER_EFFECT',triage='BUSINESS_QUESTION:NONE',
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}])
        payload['_input_request']=self.request(text)
        with self.assertRaisesRegex(ValueError,'MODEL_SUBJECT_CONFLICT'):
            intake_extraction.resolve(raw,payload)

    def test_without_model_subject_missing_visual_still_refuses(self):
        raw,payload=fixture('Report Quantity differs.')
        from investigator.visual_target import TargetUnresolved
        with self.assertRaises(TargetUnresolved):intake_extraction.resolve(raw,payload)

    def test_identifier_description_requires_exact_token_repair_not_a_precision_question(self):
        from investigator.intake_rules import RuleViolation
        from investigator.numeral_roles import expected
        text='What does adjustment reason X73 mean?'
        phrase='adjustment reason X73';start=text.index(phrase)
        mention={'role':'IDENTIFIER','source':{'start':start,'end':start+len(phrase),'quote':phrase}}
        with self.assertRaisesRegex(RuleViolation,'IDENTIFIER_QUOTE_INVALID'):
            expected([mention],text,allow_opaque=True)
        start=text.index('X73');mention['source']={'start':start,'end':start+3,'quote':'X73'}
        self.assertEqual(expected([mention],text,allow_opaque=True)[0]['value'],'X73')

    def test_one_transposition_in_one_named_model_is_audited_without_visual_selection(self):
        text='Is global Qunatity in Model current?'
        raw,payload=fixture(text,kind='FRESHNESS',reports=[{'quote':'Model','role':'PRIMARY'}],
            measures=[{'quote':'Qunatity','role':'PRIMARY'}],visuals=[{'quote':'global','role':'PRIMARY','form':'UNGROUPED'}])
        payload['_input_request']=self.request(text)
        result=intake_extraction.resolve(raw,payload)
        self.assertNotIn('target_visual',result)
        self.assertIn('USER_MODEL_SUBJECT_CLOSED_MEASURE_TRANSPOSITION',
            [e.get('resolution') for e in result['extracted_ticket']['resolution_evidence']])
        validate(result,payload)

    def test_two_transposition_candidates_do_not_pick_a_measure(self):
        from investigator.form_description import transposed_measure
        candidates=[{'id':'a','name':'abcd'},{'id':'b','name':'adbc'}]
        self.assertIsNone(transposed_measure('abdc',candidates,None,[],model={'id':'model','measures':candidates}))

    def test_unresolved_model_subject_never_opens_a_report_visual_menu(self):
        from investigator.ticket_question_gate import scope_block
        text='Unknown measure in Model'
        raw,payload=fixture(text)
        payload['_input_request']=self.request(text)
        blocked=scope_block({'error':'INTAKE_EXTRACTION_INVALID','retained_extraction':raw,
            'refusal_reason':'Starting measure/model is unresolved'},payload)
        self.assertTrue(blocked.startswith('MODEL_MEASURE_UNRESOLVED'))

if __name__=='__main__':unittest.main()
