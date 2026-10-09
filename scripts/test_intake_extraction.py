"""Current extraction protocol: no model-chosen catalog identity or comparator target."""
import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch
from investigator import intake_extraction as extraction
from investigator.question_intake import validate
from investigator.visual_target import TargetUnresolved

def fixture(ticket, **updates):
    raw={key:[] for key in extraction.SCHEMA['properties']}
    raw.update(kind='FIGURE_DIFFERENCE',primary=ticket,triage='MISMATCH_COMPLAINT:VERTICAL',
               measures=[{'quote':'Quantity','role':'PRIMARY'}],
               reports=[{'quote':'Report','role':'PRIMARY'}])
    raw.update(updates)
    model={'id':'model','name':'Model','dynamic_investigation':True,
        'measures':[{'id':'measure','name':'Quantity','aliases':['Handled Quantity']}],
        'columns':[{'column_id':'warehouse','name':'warehouse_name','aliases':['warehouse'],'data_type':'string'}],
        'reports':[{'id':'report','name':'Report'}],
        'visuals':[{'target_id':'card','report_id':'report','measure_ids':['measure'],'names':['Global card'],
                    'grouping_columns':[],'unsupported':None,'form':'CARD'},
                   {'target_id':'matrix','report_id':'report','measure_ids':['measure'],'names':['Warehouse matrix'],
                    'grouping_columns':['warehouse'],'unsupported':None,'form':'MATRIX'}]}
    return raw,{'text':ticket,'models':[model]}

class ExtractionTests(unittest.TestCase):
    def test_validated_retry_is_authority_without_overwriting_failed_response(self):
        bad={'measures':[{'quote':'invented'}]};good={'measures':[{'quote':'Quantity'}]}
        source={'retained_extraction':bad,'proposal':{'extracted_ticket':{'response':good}}}
        chosen=extraction.retained_response(source)
        self.assertEqual(chosen,good);chosen['measures'].clear()
        self.assertEqual(source['retained_extraction'],bad)
        self.assertEqual(source['proposal']['extracted_ticket']['response'],good)
        self.assertEqual(extraction.retained_response({'retained_extraction':bad,'proposal':None}),bad)

    def test_current_resolver_supplies_recordable_nonverbatim_retry_evidence(self):
        from investigator.question_intake import QuoteNotFound
        raw,payload=fixture('In Report, Quantity differs.',measures=[{'quote':'Invented metric','role':'PRIMARY'}])
        with patch('ticket_planner.azure_generate',return_value=(raw,{'response_id':'retained'})):
            with self.assertRaises(QuoteNotFound) as caught:extraction.azure_resolve(payload)
        self.assertEqual(caught.exception.repair,{'field':caught.exception.field,
            'quote':'Invented metric','response':raw})
        self.assertEqual(caught.exception.retained_extraction,raw)

    def test_independent_extraction_does_not_add_planner_context(self):
        raw,payload=fixture('In Report, Global card Quantity differs.',
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}])
        with patch('ticket_planner.azure_generate',return_value=(raw,{})) as provider:
            extraction.azure_extract(payload)
            before=provider.call_args
            extraction.azure_resolve(payload)
            after=provider.call_args
        self.assertEqual(before,after)
        self.assertEqual(provider.call_count,2)

    def test_extraction_survives_an_unresolved_target_without_another_model_call(self):
        raw,payload=fixture('In Report, Quantity differs.')
        with patch('ticket_planner.azure_generate',return_value=(raw,{'response_id':'retained'})) as provider:
            extracted,metadata=extraction.azure_extract(payload)
            with self.assertRaises(TargetUnresolved):extraction.resolve(extracted,payload)
            self.assertEqual(provider.call_count,1)
            self.assertEqual(metadata,{'response_id':'retained'})
            self.assertEqual(extracted,raw)

    def test_independent_extraction_still_rejects_nonverbatim_provenance(self):
        from investigator.question_intake import QuoteNotFound
        raw,payload=fixture('In Report, Quantity differs.',measures=[{'quote':'Invented metric','role':'PRIMARY'}])
        with patch('ticket_planner.azure_generate',return_value=(raw,{'response_id':'retained'})):
            with self.assertRaises(QuoteNotFound) as caught:extraction.azure_extract(payload)
        self.assertEqual(caught.exception.provider_metadata,{'response_id':'retained'})

    def test_sealed_two_figure_admission_responses_now_require_clarification(self):
        saved=json.loads((Path(__file__).resolve().parents[1]/'acceptance/model_steps/intake-competing-figures-regression.json').read_text())
        self.assertEqual(len(saved['responses']),2)
        for response in saved['responses']:
            with self.assertRaises(extraction.reported_figure.AmbiguousFigure):
                extraction.resolve(response,{'text':saved['ticket'],'models':[]})

    def test_competing_reported_figures_cannot_disappear_under_comparison_role(self):
        ticket='In Report, Quantity currently shows 8765 and 8766 for the identical card and scope. Both are reported values.'
        from itertools import product
        for first_role,role in product(extraction.ROLES,repeat=2):
            with self.subTest(first_role=first_role,role=role):
                raw,payload=fixture(ticket,comparisons=['8766'],
                    figures=[{'quote':'8765','role':first_role,'state':'NUMBER','precision_quote':None},
                             {'quote':'8766','role':role,'state':'NUMBER','precision_quote':None}])
                with self.assertRaises(extraction.reported_figure.AmbiguousFigure):
                    extraction.resolve(raw,payload)

    def test_equal_reported_candidates_do_not_manufacture_ambiguity(self):
        ticket='In Report, Global card Quantity shows 8765; another report also shows 8765.'
        raw,payload=fixture(ticket,comparisons=['another report also shows 8765'],
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}],
            figures=[{'quote':'Quantity shows 8765','role':'PRIMARY','state':'NUMBER','precision_quote':None},
                     {'quote':'also shows 8765','role':'COMPARISON','state':'NUMBER','precision_quote':None}])
        self.assertEqual(extraction.resolve(raw,payload)['reported_figure']['value'],'8765')

    def test_dev_guidance_keeps_setup_and_same_measure_comparator_roles_distinct(self):
        self.assertIn('same measure',extraction.INSTRUCTIONS)
        self.assertIn('Selections are only user-selected',extraction.INSTRUCTIONS)
        self.assertIn('contexts=[]',extraction.INSTRUCTIONS)
        ticket='In Report on Overview, Quantity shows 16. Can the saved declared context reproduce that figure?'
        raw,payload=fixture(ticket,kind='VISUAL_CONTENT',triage='BUSINESS_QUESTION:NONE',
            pages=[{'quote':'Overview','role':'PRIMARY'}],figures=[{'quote':'16','role':'PRIMARY','state':'NUMBER','precision_quote':None}])
        payload['models'][0]['visuals'][0].update(page_id='card-page',page_names=['Overview'])
        payload['models'][0]['visuals'][1].update(page_id='other-page',page_names=['Detail'])
        value=extraction.resolve(raw,payload)
        self.assertEqual(value['target_visual']['target_id'],'card')
        self.assertEqual(value['reported_figure']['value'],'16')
        validate(value,payload)

    def test_non_measure_title_span_cannot_hide_the_named_metric(self):
        ticket='In Report, Global card Quantity differs.'
        raw,payload=fixture(ticket,measures=[{'quote':'Global','role':'PRIMARY'},{'quote':'Quantity','role':'CONTEXT'}],visuals=[{'quote':'Global card','role':'PRIMARY','form':'CARD'}])
        value=extraction.resolve(raw,payload)
        self.assertEqual(value['metric_quote'],'Quantity')
        validate(value,payload)
        self.assertEqual(value['extracted_ticket']['resolution_evidence'][1]['resolution'],'UNRESOLVED')

    def test_mixed_technical_request_cannot_use_early_business_refusal(self):
        ticket='In Report, inspect Quantity on the Global card and decide the business rule.'
        raw,payload=fixture(ticket,kind='BUSINESS_MEANING',triage='BUSINESS_QUESTION:NONE')
        from investigator.intake_rules import RuleViolation
        with self.assertRaisesRegex(RuleViolation,'MIXED_TECHNICAL_SUBJECT_REQUIRED'):extraction.resolve(raw,payload)

    def test_named_card_form_preserves_title_and_does_not_choose_another_card(self):
        ticket='In Report, investigate Quantity on the Global card.'
        raw,payload=fixture(ticket,visuals=[{'quote':'Global card','role':'PRIMARY','form':'CARD'}])
        other=copy.deepcopy(payload['models'][0]['visuals'][0]);other.update(target_id='other',names=['Other'])
        payload['models'][0]['visuals'].append(other)
        payload['models'][0]['visuals'][0]['names']=['Global']
        value=extraction.resolve(raw,payload)
        self.assertEqual(value['target_visual']['target_id'],'card')
        self.assertIn('visual_name',value['target_visual']['match_basis']['matched'])
        validate(value,payload)

    def test_business_refusal_keeps_its_type_and_provider_receipt(self):
        ticket='Please decide the business rule.'
        raw,payload=fixture(ticket,kind='BUSINESS_MEANING',triage='BUSINESS_QUESTION:NONE',measures=[],reports=[])
        from investigator.question_kind import UnimplementedRoute
        with patch('ticket_planner.azure_generate',return_value=(raw,{'response_id':'recorded'})):
            with self.assertRaises(UnimplementedRoute) as caught:extraction.azure_resolve(payload)
        self.assertEqual(caught.exception.provider_metadata,{'response_id':'recorded'})

    def test_pure_business_intent_refuses_before_missing_measure_and_target(self):
        ticket='Should this rule be the business rule?'
        raw,payload=fixture(ticket,kind='BUSINESS_MEANING',triage='BUSINESS_QUESTION:NONE',measures=[],reports=[])
        from investigator.question_kind import UnimplementedRoute
        with self.assertRaisesRegex(UnimplementedRoute,'domain specialist'):extraction.resolve(raw,payload)

    def test_primary_setup_grouping_and_identifier_are_not_erased(self):
        ticket='In Report, Quantity by warehouse should include record 900099. Investigate the Warehouse matrix.'
        raw,payload=fixture(ticket,primary='Investigate the Warehouse matrix.',
            contexts=['Quantity by warehouse should include record 900099'],
            groupings=[{'quote':'by warehouse','column':'warehouse','role':'PRIMARY'}],
            identifiers=[{'quote':'900099','role':'PRIMARY'}],
            visuals=[{'quote':'Warehouse matrix','role':'PRIMARY','form':'TITLE'}])
        value=extraction.resolve(raw,payload)
        self.assertEqual(value['dimension_ids'],['warehouse'])
        self.assertEqual(value['expected_records'][0]['value'],'900099')
        self.assertEqual(value['filters'],[])
        self.assertEqual(value['reported_figure']['state'],'UNSPECIFIED')

    def test_primary_reported_figure_and_selection_survive_background_setup(self):
        ticket='In Report, I selected warehouse North; Quantity shows 16. Investigate the Global card.'
        raw,payload=fixture(ticket,primary='Investigate the Global card.',
            contexts=['In Report, I selected warehouse North; Quantity shows 16.'],
            figures=[{'quote':'shows 16','role':'PRIMARY','state':'NUMBER','precision_quote':None}],
            selections=[{'quote':'warehouse North','column':'warehouse','value':'North','role':'PRIMARY'}],
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}])
        result=extraction.resolve(raw,payload)
        self.assertEqual(result['reported_figure']['value'],'16')
        self.assertEqual(result['filters'],[{'column_id':'warehouse','operator':'in','values':['North']}])
        self.assertEqual(result['target_visual']['target_id'],'card')
        validate(result,payload)

    def test_background_visual_cannot_select_while_primary_facts_survive(self):
        ticket='In Report, the Global card Quantity shows 16. Investigate the discrepancy.'
        raw,payload=fixture(ticket,primary='Investigate the discrepancy.',
            contexts=['In Report, the Global card Quantity shows 16.'],
            figures=[{'quote':'shows 16','role':'PRIMARY','state':'NUMBER','precision_quote':None}],
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}])
        with self.assertRaises(TargetUnresolved) as caught:extraction.resolve(raw,payload)
        self.assertEqual(caught.exception.code,'TARGET_AMBIGUOUS')

    def test_comparator_figure_cannot_become_primary_even_when_mislabelled(self):
        ticket='In Report, Global card Quantity differs from another report that shows 16.'
        raw,payload=fixture(ticket,comparisons=['another report that shows 16'],
            figures=[{'quote':'shows 16','role':'PRIMARY','state':'NUMBER','precision_quote':None}],
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}])
        result=extraction.resolve(raw,payload)
        self.assertEqual(result['reported_figure']['state'],'UNSPECIFIED')

    def test_background_primary_date_scope_is_refused_not_discarded(self):
        ticket='In Report, Quantity for last week. Investigate the Global card.'
        raw,payload=fixture(ticket,primary='Investigate the Global card.',
            contexts=['Quantity for last week'],dates=[{'quote':'last week','role':'PRIMARY'}],
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}])
        with self.assertRaisesRegex(ValueError,'Stated date scope'):extraction.resolve(raw,payload)

    def test_comparison_global_card_cannot_select_even_if_mislabelled_primary(self):
        ticket='In Report, Quantity differs for warehouse North from the Global card.'
        raw,payload=fixture(ticket,comparisons=['Global card'],
            selections=[{'quote':'warehouse North','column':'warehouse','value':'North','role':'PRIMARY'}],
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}])
        with self.assertRaises(TargetUnresolved) as caught:extraction.resolve(raw,payload)
        self.assertEqual(caught.exception.code,'TARGET_AMBIGUOUS')
        self.assertEqual(len(caught.exception.candidates),2)

    def test_unique_unnamed_visual_and_ambiguous_and_none(self):
        raw,payload=fixture('In Report, Quantity differs.')
        with self.assertRaises(TargetUnresolved) as caught:extraction.resolve(raw,payload)
        self.assertEqual(caught.exception.code,'TARGET_AMBIGUOUS')
        payload['models'][0]['visuals']=payload['models'][0]['visuals'][:1]
        value=extraction.resolve(raw,payload)
        self.assertEqual(value['target_visual']['target_id'],'card')
        validate(value,payload)
        payload['models'][0]['visuals']=[]
        with self.assertRaises(TargetUnresolved) as caught:extraction.resolve(raw,payload)
        self.assertEqual(caught.exception.code,'TARGET_UNRESOLVED')

    def test_title_preserved_and_target_tampering_refused(self):
        raw,payload=fixture('In Report, Global card Quantity differs.',
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}])
        value=extraction.resolve(raw,payload);validate(value,payload)
        value['target_visual']['target_id']='matrix'
        with self.assertRaisesRegex(ValueError,'Resolved extraction differs'):validate(value,payload)

    def test_closed_schema_no_ids_or_offsets_and_code_computes_spans(self):
        raw,payload=fixture('In Report, Quantity differs.')
        payload['models'][0]['visuals']=payload['models'][0]['visuals'][:1]
        value=extraction.resolve(raw,payload)
        self.assertEqual(value['question_kind']['source']['start'],0)
        raw['visual_id']='card'
        with self.assertRaises(Exception):extraction.resolve(raw,payload)

    def test_mixed_technical_and_business_meaning_keeps_primary(self):
        ticket='In Report, Global card Quantity shows 16. Is that business rule correct?'
        raw,payload=fixture(ticket,kind='VISUAL_CONTENT',primary='In Report, Global card Quantity shows 16.',
            contexts=['Is that business rule correct?'],
            figures=[{'quote':'shows 16','role':'PRIMARY','state':'NUMBER','precision_quote':None}],
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}])
        value=extraction.resolve(raw,payload)
        self.assertEqual(value['question_kind']['kind'],'VISUAL_CONTENT')
        self.assertEqual(value['reported_figure']['state'],'NUMBER')
        validate(value,payload)

    def test_alias_then_normalized_matching_never_guesses(self):
        rows=[{'id':'a','name':'Sales Quantity','aliases':['Handled Quantity']}]
        self.assertEqual(extraction.match('Handled Quantity',rows,'id')['id'],'a')
        self.assertEqual(extraction.match('sales quantity',rows,'id')['id'],'a')
        with self.assertRaises(ValueError):extraction.match('Revenue',rows,'id')
        with self.assertRaises(ValueError):extraction.match('Sales Quantity',rows+[dict(rows[0],id='b')],'id')

    def test_ambiguous_measure_in_one_model_cannot_be_skipped_for_another_model(self):
        raw,payload=fixture('Quantity differs.')
        raw['reports']=[]
        model=payload['models'][0]
        model['measures'].append(dict(model['measures'][0],id='other-measure'))
        other=copy.deepcopy(model);other['id']='other-model';other['measures']=other['measures'][:1]
        payload['models'].append(other)
        with self.assertRaisesRegex(ValueError,'Ambiguous declared name'):extraction.resolve(raw,payload)

    def test_producer_collection_bounds_come_from_consumers(self):
        from investigator import numeral_roles, proposal_limits, reported_figure
        fields=extraction.SCHEMA['properties']
        self.assertEqual(fields['figures']['maxItems'],reported_figure.CANDIDATE_LIMIT)
        self.assertEqual(fields['selections']['maxItems'],proposal_limits.INTAKE_FILTERS)
        self.assertEqual(fields['groupings']['maxItems'],proposal_limits.INTAKE_DIMENSIONS)
        self.assertEqual(fields['identifiers']['maxItems']+fields['figures']['maxItems'],numeral_roles.LIMIT)

    def test_current_eval_reads_kind_from_new_taped_response(self):
        import base64,tempfile
        from run_current_intake_eval import nomination
        response={'output':[{'type':'function_call','name':'extract_ticket_spans','arguments':json.dumps({'kind':'FRESHNESS'})}]}
        outer={'body':base64.b64encode(json.dumps(response).encode()).decode()}
        tape={'events':[{'kind':'PROVIDER_RESPONSE','body':base64.b64encode(json.dumps(outer).encode()).decode()}]}
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'response.json';path.write_text(json.dumps(tape))
            self.assertEqual(nomination(path),'FRESHNESS')

    def test_wire_titles_without_values_or_identities_and_duplicate_catalog_growth_is_constant(self):
        raw,payload=fixture('In Report, Quantity differs.')
        before=extraction.request_size(payload);wire=extraction.wire(payload)
        self.assertEqual(set(wire),{'ticket','question_kinds','names','visual_titles'})
        self.assertEqual(wire['visual_titles'],['Global card','Warehouse matrix']);self.assertNotIn('target_id',json.dumps(wire));self.assertNotIn('model',json.dumps(wire))
        payload['models'][0]['visuals']*=10000
        self.assertEqual(extraction.request_size(payload),before)
        self.assertLessEqual(before,20000)

    def test_whole_request_over_cap_is_taped_before_provider(self):
        from ticket_planner import _azure_generate
        with patch('investigator.process_tape.event') as event,patch('openai.OpenAI') as client:
            with self.assertRaisesRegex(ValueError,'INTAKE_REQUEST_OVERSIZE'):
                _azure_generate({'text':'X'*20001},instructions='',schema={},name='extract',max_request_characters=20000)
        client.assert_not_called();self.assertEqual(event.call_args.args[1]['control'],'INTAKE_REQUEST_OVERSIZE')

    def test_sealed_wrong_cell_remains_a_regression_under_new_protocol(self):
        saved=json.loads((Path(__file__).parent/'fixtures/round_ten/wrong-cell-sealed-excerpt.json').read_text())
        # The immutable original proves equal values are not referent evidence.
        self.assertEqual(saved['wrong_answer_cell']['mode'],'TOTAL')
        raw,payload=fixture('In Report, Global card Quantity shows 16.',kind='VISUAL_CONTENT',
            figures=[{'quote':'shows 16','role':'PRIMARY','state':'NUMBER','precision_quote':None}],
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}])
        value=extraction.resolve(raw,payload)
        self.assertEqual(value['target_visual']['target_id'],'card')
        value['target_visual']['mode']='TOTAL'
        with self.assertRaises(ValueError):validate(value,payload)

    def test_current_producer_runs_real_intake_and_charges_its_bounded_request(self):
        from investigator.model_eval_intake import workspace
        from investigator.question_intake import Intake, snapshot
        from test_investigator_workspace import WorkspaceTests
        h=WorkspaceTests();h.setUp();self.addCleanup(h.doCleanups)
        raw,payload=fixture('In Model, Quantity differs.')
        raw['reports']=[{'quote':'Model','role':'PRIMARY'}]
        owner=workspace(h.agent,payload['models'],extraction.azure_resolve)
        request_payload={'text':payload['text'],'models':snapshot(owner)['models']}
        charge=extraction.request_size(request_payload)
        with patch('ticket_planner.azure_generate',return_value=(raw,{'usage':{'input_tokens':10,'output_tokens':10}})) as provider:
            result=Intake(owner,extraction.azure_resolve).resolve({'text':payload['text'],'request_key':'new-wire','parent_id':None})
        self.assertEqual(result['status'],'PROPOSED',result)
        self.assertEqual(result['proposal']['name_binding']['kind'],'MODEL')
        self.assertNotIn('models',provider.call_args.args[0])
        with h.store.connect() as db:
            row=db.execute("SELECT reserved FROM adaptive_usage WHERE session_id=?",('intake:'+result['id'],)).fetchone()
        self.assertEqual(json.loads(row[0])['input_characters'],charge)
        h.native.assert_not_called();h.source.assert_not_called()

if __name__=='__main__':unittest.main()
