import copy
import unittest
from unittest.mock import patch
from jsonschema import Draft202012Validator
# Explicit historical wire-v2 decoder; current producer covered by test_intake_extraction.
from investigator.question_intake import azure_resolve_legacy as azure_resolve,validate,wire_contract
from investigator.definition_target import server_evidence,procedure_scope
from investigator.question_kind import reproduction
from investigator.numeral_roles import evidence
from investigator.name_kind import resolve


class NumeralKindTests(unittest.TestCase):
    def payload(self):
        return {'text':'In Application load fixture 20261003, Movement Units shows 7,661 units. I expected a movement numbered 900099 that is absent from the authored application fixture.',
            'models':[{'id':'model','name':'Application load fixture 20261003','dynamic_investigation':True,
                'measures':[{'id':'measure','name':'Movement Units'}],'columns':[],'reports':[]}]}

    def response(self,payload):
        return {'value_mentions':[],'question_kind':{'kind':'SOURCE_CORRECTNESS','source':{'quote':'I expected a movement numbered 900099'}},
            'action':'PROPOSE','model_id':'m0','measure_id':'m0v0','metric_quote':'Movement Units','question':None,
            'triage':'MISMATCH_COMPLAINT:VERTICAL','filters':[],'dimension_ids':[],
            'reported_candidates':[{'role':'FIGURE','quote':'shows 7,661 units'},
                {'role':'IDENTIFIER','quote':'a movement numbered 900099'},
                {'role':'OTHER','quote':'Application load fixture 20261003'}],
            'report_quote':'Application load fixture 20261003','target_request':None}

    def translate(self,payload,response=None):
        with patch('ticket_planner.azure_generate',return_value=(response or self.response(payload),{})):
            result,_=azure_resolve(payload)
        return validate(result,payload)

    def test_labelled_record_is_not_a_second_reported_figure(self):
        p=self.payload();r=self.translate(p)
        self.assertEqual(r['reported_figure']['value'],'7661')
        self.assertEqual([v['value'] for v in r['expected_records']],['900099'])
        self.assertEqual(r['numeral_mentions'][1]['role'],'IDENTIFIER')
        self.assertEqual(r['dimension_ids'],[])
        self.assertEqual(r['filters'],[])
        self.assertEqual(p['text'][r['expected_records'][0]['source']['start']:r['expected_records'][0]['source']['end']], 'a movement numbered 900099')
        for path in (server_evidence(r),procedure_scope({**r,'filters':[],'dimension_ids':[]})):
            self.assertEqual(path['expected_records'],r['expected_records'])

    def test_model_name_resolves_as_model_without_report_refusal(self):
        p=self.payload();r=self.translate(p)
        self.assertEqual(r['name_binding']['kind'],'MODEL')
        self.assertNotIn('report_binding',r);self.assertFalse(reproduction(r)['applicable'])

    def test_report_first_then_model_then_declared_layer_and_ambiguity_preserved(self):
        model={'id':'model','name':'Sales','reports':[{'id':'report','name':'Sales'}],
            'declared_layers':[{'id':'layer','name':'Sales'}]}
        source={'start':0,'end':5,'quote':'Sales'}
        self.assertEqual(resolve(source,model,'Sales')['kind'],'REPORT')
        model['reports']=[];self.assertEqual(resolve(source,model,'Sales')['kind'],'MODEL')
        model['name']='different';self.assertEqual(resolve(source,model,'Sales')['kind'],'LAYER')
        model['declared_layers'].append({'id':'second','name':'Sales'})
        with self.assertRaisesRegex(ValueError,'ambiguity'):resolve(source,model,'Sales')

    def test_unknown_role_or_missing_role_unrepresentable_and_two_figures_refused(self):
        p=self.payload();r=self.response(p);_,schema,_=wire_contract(p);validator=Draft202012Validator(schema)
        self.assertTrue(validator.is_valid(r))
        for edit in ('missing','unknown'):
            bad=copy.deepcopy(r)
            if edit=='missing':bad['reported_candidates'][0].pop('role')
            else:bad['reported_candidates'][0]['role']='probably a figure'
            self.assertFalse(validator.is_valid(bad))
        r['reported_candidates'][1]['role']='FIGURE'
        from investigator.reported_figure import AmbiguousFigure
        with patch('ticket_planner.azure_generate',return_value=(r,{})),self.assertRaises(AmbiguousFigure):azure_resolve(p)

    def test_hostile_invented_expected_record_or_reported_figure_refused(self):
        p=self.payload();r=self.translate(p)
        bad=copy.deepcopy(r);bad['expected_records'][0]['value']='900098'
        with self.assertRaises(ValueError):evidence(bad,p['text'])
        bad=copy.deepcopy(r);bad['reported_figure']['value']='900099'
        with self.assertRaises(ValueError):evidence(bad,p['text'])

    def test_numeric_model_suffix_never_becomes_an_expected_record(self):
        p=self.payload();r=self.response(p)
        r['reported_candidates'].append({'role':'IDENTIFIER','quote':'20261003'})
        from investigator.question_intake import QuoteRefused
        with patch('ticket_planner.azure_generate',return_value=(r,{})),self.assertRaisesRegex(QuoteRefused,'catalog name'):
            azure_resolve(p)

    def test_catalog_coverage_unchanged_by_wire_roles(self):
        p=self.payload();before=copy.deepcopy(p);wire,_,_=wire_contract(p)
        self.assertEqual(p,before)
        self.assertEqual(len(wire['models']),len(p['models']))
        self.assertEqual(len(wire['models'][0]['measures']),len(p['models'][0]['measures']))

    def test_identifier_cannot_supply_grouping_or_restriction_provenance(self):
        from investigator.numeral_roles import measure_scope
        p=self.payload();r=self.translate(p);source=r['expected_records'][0]['source']
        for quote in (source,{'start':source['start']+19,'end':source['end'],'quote':'900099'}):
            bad=copy.deepcopy(r);bad['dimension_ids']=['key'];bad['dimension_quotes']=[{'column_id':'key','source':quote}]
            with self.assertRaises(ValueError):measure_scope(bad,p['text'])
        bad=copy.deepcopy(r);bad['dimension_ids']=['key'];bad.pop('dimension_quotes')
        with self.assertRaisesRegex(ValueError,'membership only'):measure_scope(bad,p['text'])
        bad=copy.deepcopy(r);bad['scope_quotes']=[{'column_id':'key','quote':'900099'}]
        with self.assertRaisesRegex(ValueError,'restriction'):measure_scope(bad,p['text'])

    def test_independent_explicit_breakdown_is_not_silently_removed(self):
        from investigator.numeral_roles import measure_scope
        p=self.payload();r=self.translate(p);p['text']+=' Group by region.'
        a=p['text'].index('by region');r['dimension_ids']=['region'];r['dimension_quotes']=[{'column_id':'region',
            'source':{'start':a,'end':a+len('by region'),'quote':'by region'}}]
        measure_scope(r,p['text']);self.assertEqual(r['dimension_ids'],['region'])

    def test_unproven_grouping_is_not_wire_representable(self):
        p=self.payload();r=self.response(p);_,schema,_=wire_contract(p)
        r['dimension_ids']=['m0c0']
        self.assertFalse(Draft202012Validator(schema).is_valid(r))
