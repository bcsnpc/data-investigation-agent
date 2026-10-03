"""Exact consumer-computed spans, with no model arithmetic or normalization."""
import copy
import unittest
from unittest.mock import patch
from investigator.question_intake import locate,QuoteRefused,azure_resolve,wire_contract

class QuoteProvenanceTests(unittest.TestCase):
    def test_exact_quote_computes_span(self):
        self.assertEqual(locate({'quote':'North'},'Pick North.'),{'start':5,'end':10,'quote':'North'})
    def test_one_character_change_and_case_change_refuse(self):
        for quote in ('NortX','north'):
            with self.assertRaisesRegex(QuoteRefused,'not found verbatim'):locate({'quote':quote},'North')
    def test_repeated_quote_refuses_with_count(self):
        with self.assertRaisesRegex(QuoteRefused,'occurs 2 times'):locate({'quote':'North'},'North versus North')
        with self.assertRaisesRegex(QuoteRefused,'occurs 2 times'):locate({'quote':'aa'},'aaa')
    def test_longer_unique_quote_on_next_extraction_resolves(self):
        ticket='North versus North'
        with self.assertRaises(QuoteRefused):locate({'quote':'North'},ticket)
        self.assertEqual(locate({'quote':'versus North'},ticket),{'start':6,'end':18,'quote':'versus North'})
    def test_offsets_from_model_are_rejected_not_discarded(self):
        for key in ('start','end'):
            with self.assertRaisesRegex(ValueError,'Unexpected fields'):locate({'quote':'North',key:0},'North')
    def payload(self):
        return {'text':'Revenue shows 9 for North.','models':[{'id':'model','measures':[{'id':'measure','name':'Revenue'}],'columns':[{'column_id':'column','name':'Region'}]}]}
    def response(self):
        return {'question_kind':{'kind':'VISUAL_CONTENT','source':{'quote':'Revenue'}},'action':'PROPOSE','model_id':'m0','measure_id':'m0v0','metric_quote':'Revenue','question':None,'filters':[],'dimension_ids':[],
            'report_quote':None,'target_request':{'value_source':{'quote':'North'},'column_source':None,'descriptor':{'state':'VALUE_ONLY','source':None}},'reported_candidates':[{'quote':'9'}],'triage':'MISMATCH_COMPLAINT:VERTICAL'}
    def test_quote_wire_computes_original_downstream_shape(self):
        with patch('ticket_planner.azure_generate',return_value=(self.response(),{})):
            value,_=azure_resolve(self.payload())
        self.assertEqual(value['reported_figure']['source'],{'start':14,'end':15,'quote':'9'})
        self.assertEqual(value['target_request']['value_source'],{'start':20,'end':25,'quote':'North'})
    def test_hostile_offset_on_figure_or_target_rejects(self):
        for kind in ('figure','target'):
            response=self.response()
            obj=response['reported_candidates'][0] if kind=='figure' else response['target_request']['value_source']
            obj['start']=0
            with patch('ticket_planner.azure_generate',return_value=(response,{})):
                with self.assertRaisesRegex(ValueError,'Unexpected fields'):azure_resolve(self.payload())
    def test_repeated_entities_record_every_occurrence_and_proceed(self):
        payload=self.payload();payload['text']+=' Revenue North Region Region'
        response=self.response();response['target_request']['column_source']={'quote':'Region'}
        response['filters']=[{'column_id':'m0c0','operator':'in','values':['North'],'quote':'North'}]
        with patch('ticket_planner.azure_generate',return_value=(response,{})):
            value,usage=azure_resolve(payload)
        for field in ('measure','column','selection'):
            records=[v for v in usage['quote_provenance'] if v['field']==field]
            self.assertTrue(records)
            self.assertTrue(all(len(v['occurrences'])==2 for v in records))
        self.assertEqual(value['target_request']['value_source']['start'],20)

    def test_field_not_text_controls_duplicate_rule(self):
        audit=[]
        for field in ('measure','column','selection'):
            locate({'quote':'9'},'9 versus 9',field=field,audit=audit)
        self.assertEqual([len(v['occurrences']) for v in audit],[2,2,2])
        with self.assertRaises(QuoteRefused):locate({'quote':'9'},'9 versus 9',field='reported_figure')

    def test_figure_quote_repair_only_changes_quote_and_is_longer_verbatim(self):
        from investigator.question_intake import FigureQuoteAmbiguous
        payload=self.payload();payload['text']+=' Earlier 9.'
        with patch('ticket_planner.azure_generate',return_value=(self.response(),{'usage':{'output_tokens':12}})):
            with self.assertRaises(FigureQuoteAmbiguous) as caught:azure_resolve(payload)
        repaired={**payload,'_figure_quote_repair':caught.exception.repair}
        for quote,error in [('shows 9',None),('Earlier 10',QuoteRefused),('fake shows 9',QuoteRefused),('9',QuoteRefused)]:
            with patch('ticket_planner.azure_generate',return_value=({'reported_candidates':[{'quote':quote}]},{})) as generate:
                if error:
                    with self.assertRaises(error):azure_resolve(repaired)
                else:
                    value,_=azure_resolve(repaired)
                    self.assertEqual(value['reported_figure']['source']['quote'],'shows 9')
                    self.assertEqual(value['reported_figure']['value'],'9')
                self.assertEqual(set(generate.call_args.kwargs['schema']['properties']),{'reported_candidates'})

    def test_longer_but_still_duplicated_quote_names_both_occurrences(self):
        from investigator.question_intake import FigureQuoteAmbiguous
        payload=self.payload();payload['text']+=' It shows 9 again.'
        with patch('ticket_planner.azure_generate',return_value=(self.response(),{})):
            with self.assertRaises(FigureQuoteAmbiguous) as caught:azure_resolve(payload)
        with patch('ticket_planner.azure_generate',return_value=({'reported_candidates':[{'quote':'shows 9'}]},{})):
            with self.assertRaisesRegex(FigureQuoteAmbiguous,'occurs 2 times at ticket spans'):
                azure_resolve({**payload,'_figure_quote_repair':caught.exception.repair})

    def test_model_schema_has_no_offset_fields_and_catalog_coverage_unchanged(self):
        payload=self.payload();wire,schema,_=wire_contract(payload)
        def check(value):
            if isinstance(value,dict):
                self.assertFalse({'start','end'} & set(value.get('properties',{})))
                for child in value.values():check(child)
            elif isinstance(value,list):
                for child in value:check(child)
        check(schema)
        self.assertEqual(len(wire['models']),1);self.assertEqual(len(wire['models'][0]['columns']),1)
        self.assertEqual(len(wire['models'][0]['measures']),1)

if __name__=='__main__':unittest.main()
