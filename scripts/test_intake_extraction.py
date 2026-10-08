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
    raw.update(kind='FIGURE_DIFFERENCE',primary=ticket,reported_state='UNSPECIFIED',
               measures=[{'quote':'Quantity','role':'PRIMARY'}],
               reports=[{'quote':'Report','role':'PRIMARY'}])
    raw.update(updates)
    if updates.get('figures'):raw['reported_state']=updates['figures'][0]['state']
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

    def test_wire_no_visuals_values_identifiers_and_catalog_growth_does_not_expand_request(self):
        raw,payload=fixture('In Report, Quantity differs.')
        before=extraction.request_size(payload);wire=extraction.wire(payload)
        self.assertEqual(set(wire),{'ticket','question_kinds','names'})
        self.assertNotIn('Global card',json.dumps(wire));self.assertNotIn('target_id',json.dumps(wire))
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
