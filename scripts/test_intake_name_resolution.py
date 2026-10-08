import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch
from investigator import intake_name_resolution as names, intake_extraction as extraction
from investigator.question_intake import validate
from test_intake_extraction import fixture


class NameResolutionTests(unittest.TestCase):
    def test_runner_up_below_threshold_still_blocks_an_insufficient_lead(self):
        rows=[{'id':'a','name':'other beta gamma delta'},
              {'id':'b','name':'extra other beta gamma delta'}]
        with self.assertRaisesRegex(ValueError,'Ambiguous') as caught:
            names.resolve('alpha beta gamma delta',rows,'id')
        evidence=caught.exception.resolution_evidence
        self.assertLess(evidence['runner_up']['score'],evidence['threshold'])
        self.assertEqual({r['id'] for r in caught.exception.candidates},{'a','b'})

    def test_reordered_alias_words_do_not_receive_exact_alias_priority(self):
        rows=[{'id':'a','name':'Operations','aliases':['Sales Revenue']},
              {'id':'b','name':'Revenue Sales'}]
        ranked=names.rank('Revenue Sales',rows,'id')
        self.assertEqual(next(r['basis'] for r in ranked if r['id']=='a'),'token_overlap')
        with self.assertRaisesRegex(ValueError,'Ambiguous'):names.resolve('Revenue Sales',rows,'id')

    def test_policy_rejects_invalid_types_and_inconsistent_weights(self):
        original=names.policy()
        for changes in ({'threshold':True},{'alias_score':0.5},{'exact_score':float('nan')},
                        {'closed_value_edit_distance':2},{'closed_value_maximum':False},{'reason':' '},
                        {'ignored':1}):
            with self.subTest(changes=changes),patch.object(Path,'read_text',return_value=json.dumps({**original,**changes})):
                with self.assertRaisesRegex(ValueError,'Invalid intake'):names.policy()

    def test_page_constraint_does_not_attempt_to_select_a_visual_by_itself(self):
        ticket='In Report on Overview, Global card Quantity differs.'
        raw,payload=fixture(ticket,pages=[{'quote':'Overview','role':'PRIMARY'}],
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}])
        for v in payload['models'][0]['visuals']:
            v.update(page_id='page',page_names=['Overview Operations'])
        value=extraction.resolve(raw,payload)
        self.assertEqual(value['target_visual']['target_id'],'card')
        self.assertIn('page_name',value['target_visual']['match_basis']['matched'])
        validate(value,payload)

    def test_columnless_selection_reaches_existing_request_contract_without_inventing_filter(self):
        ticket='In Report, Warehouse matrix Quantity differs; I selected North.'
        raw,payload=fixture(ticket,
            selections=[{'quote':'I selected North','column':None,'value':'North','role':'PRIMARY'}],
            visuals=[{'quote':'Warehouse matrix','role':'PRIMARY','form':'TITLE'}])
        value=extraction.resolve(raw,payload)
        self.assertEqual(value['filters'],[])
        self.assertEqual(value['selection_request']['value_source']['quote'],'North')
        self.assertEqual(value['selection_request']['descriptor'],{'state':'VALUE_ONLY','source':None})
        validate(value,payload)

    def test_ambiguous_column_hint_is_nonbinding_and_is_not_dropped(self):
        ticket='In Report, Warehouse matrix Quantity differs; I selected warehouse North.'
        raw,payload=fixture(ticket,
            selections=[{'quote':'I selected warehouse North','column':'warehouse','value':'North','role':'PRIMARY'}],
            visuals=[{'quote':'Warehouse matrix','role':'PRIMARY','form':'TITLE'}])
        payload['models'][0]['columns'].append(dict(payload['models'][0]['columns'][0],column_id='other-warehouse'))
        value=extraction.resolve(raw,payload)
        self.assertEqual(value['filters'],[])
        self.assertIsNone(value['selection_request']['column_source'])
        self.assertEqual(value['selection_request']['descriptor']['state'],'SEPARATED')
        self.assertTrue(any(r['quote']=='warehouse' and r['resolution']=='AMBIGUOUS'
                            for r in value['extracted_ticket']['resolution_evidence']))
        validate(value,payload)

    def test_named_target_can_precede_the_question_without_becoming_background(self):
        ticket='In Report, Global card Quantity looks high. Explain its value.'
        raw,payload=fixture(ticket,primary='Explain its value.',
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}])
        value=extraction.resolve(raw,payload)
        self.assertEqual(value['target_visual']['target_id'],'card')
        validate(value,payload)

    def test_repeated_selection_word_is_bound_inside_its_stated_relationship(self):
        ticket='North is background. In Report, Warehouse matrix Quantity differs; I selected warehouse North.'
        raw,payload=fixture(ticket,contexts=['North is background.'],
            visuals=[{'quote':'Warehouse matrix','role':'PRIMARY','form':'TITLE'}],
            selections=[{'quote':'I selected warehouse North','column':'warehouse','value':'North','role':'PRIMARY'}])
        value=extraction.resolve(raw,payload)
        self.assertEqual(value['filters'][0]['values'],['North'])
        source=value['value_mentions'][0]['source']
        self.assertEqual(source['start'],ticket.rindex('North'))
        validate(value,payload)

    def test_triage_uses_consumer_pairs_and_state_is_not_duplicated(self):
        from investigator.intake_triage import PAIRS
        from jsonschema import Draft202012Validator
        self.assertEqual(extraction.SCHEMA['properties']['triage']['enum'],list(PAIRS))
        self.assertNotIn('reported_state',extraction.SCHEMA['properties'])
        raw,payload=fixture('In Report, Global card Quantity shows 16.',
            figures=[{'quote':'shows 16','role':'PRIMARY','state':'NUMBER','precision_quote':None}],
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}])
        self.assertEqual(extraction.resolve(raw,payload)['reported_figure']['state'],'NUMBER')
        raw['triage']='MISMATCH_COMPLAINT:NONE'
        self.assertTrue(list(Draft202012Validator(extraction.SCHEMA).iter_errors(raw)))

    def test_normalization_and_partial_report(self):
        for quote in ('sales dashboard', 'Sales_Dashboard', 'salesDashboard'):
            rows=[{'id':'a','name':'Sales Dashboard - Ops'}]
            self.assertEqual(names.resolve(quote,rows,'id')['id'],'a')
        self.assertEqual(names.tokens('Customers'),names.tokens('customer'))
        self.assertEqual(names.tokens('[SalesQuantity]'),names.tokens('sales_quantity'))

    def test_close_measures_remain_ambiguous_and_evidence_names_both(self):
        with self.assertRaisesRegex(ValueError,'Ambiguous') as caught:
            names.resolve('Revenue',[{'id':'a','name':'Revenue'},{'id':'b','name':'Net Revenue'}],'id')
        self.assertEqual({r['id'] for r in caught.exception.candidates},{'a','b'})
        self.assertEqual(caught.exception.resolution_evidence['runner_up']['score'],0.9)

    def test_alias_precedence_and_audit(self):
        audit=[]
        found=names.resolve('Handled Quantity',[{'id':'a','name':'Units','aliases':['Handled Quantity']},
            {'id':'b','name':'Handled Quantity'}],'id',audit)
        self.assertEqual(found['id'],'a')
        self.assertEqual(audit[0]['best']['basis'],'declared_alias')

    def test_closed_values_only_unique_one_edit(self):
        self.assertEqual(names.closed_value('Noth',['North','South']),'North')
        with self.assertRaises(ValueError):names.closed_value('Noth',['North','Notch'])
        with self.assertRaises(ValueError):names.closed_value('Noth',list(range(33)))

    def test_measure_in_setup_is_not_discarded_when_question_says_its(self):
        ticket='In Report, Quantity looks high. Explain its global value.'
        raw,payload=fixture(ticket,primary='Explain its global value.',
            contexts=['In Report, Quantity looks high.'],
            measures=[{'quote':'Quantity','role':'CONTEXT'}],
            reports=[{'quote':'Report','role':'CONTEXT'}],
            visuals=[{'quote':'global value','role':'PRIMARY','form':'UNGROUPED'}])
        value=extraction.resolve(raw,payload)
        self.assertEqual(value['measure_id'],'measure')
        self.assertEqual(value['target_visual']['target_id'],'card')
        validate(value,payload)

    def test_partial_report_resolution_is_revalidated_by_consumer(self):
        ticket='In Report, Global card Quantity differs.'
        raw,payload=fixture(ticket,visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}])
        payload['models'][0]['reports'][0]['name']='Report Operations'
        value=extraction.resolve(raw,payload)
        validate(value,payload)
        value['extracted_ticket']['resolution_evidence'][0]['best']['score']=0
        with self.assertRaises(ValueError):validate(value,payload)

    def test_full_report_suffix_at_extracted_location_resolves_models(self):
        ticket='In Report abcdef, Global card Quantity differs.'
        raw,payload=fixture(ticket,visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}])
        first=payload['models'][0]
        first['reports'][0]['name']='Report abcdef'
        second=copy.deepcopy(first);second['id']='second'
        second['reports'][0]={'id':'other-report','name':'Report ghijkl'}
        payload['models'].append(second)
        value=extraction.resolve(raw,payload)
        self.assertEqual(value['model_id'],'model')
        self.assertEqual(value['report_binding']['source']['quote'],'Report abcdef')
        validate(value,payload)

    def test_setup_visual_and_comparator_cannot_select_target(self):
        from investigator.visual_target import TargetUnresolved
        ticket='In Report, Global card Quantity is background. Explain Quantity against global value.'
        raw,payload=fixture(ticket,primary='Explain Quantity against global value.',
            contexts=['In Report, Global card Quantity is background.'],comparisons=['global value'],
            visuals=[{'quote':'Global card','role':'CONTEXT','form':'TITLE'},
                     {'quote':'global value','role':'PRIMARY','form':'UNGROUPED'}])
        with self.assertRaises(TargetUnresolved):extraction.resolve(raw,payload)


if __name__=='__main__':unittest.main()
