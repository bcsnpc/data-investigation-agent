"""Synthetic free-text role/provenance cases, independent of sealed tickets."""
from copy import deepcopy
from unittest.mock import Mock
import unittest
from investigator.guided_text_resolver import Resolver
from investigator.guided_intake import Catalog
from investigator.intake_span_references import tokens
from test_round23_intake_queries import graph,request
from test_round23_reasoning import tool


def reference(text,phrase,occurrence=1):
    start=-1
    for _ in range(occurrence):start=text.index(phrase,start+1)
    end=start+len(phrase)
    selected=[t for t in tokens(text) if start<=t['start'] and t['end']<=end]
    return [selected[0]['id'],selected[-1]['id']]


def proposal(text):
    return {'proposal':request(),'provenance':{'reported_figure':reference(text,'950'),
            'visual':reference(text,'Card')},'figure_mentions':[
                {'role':'PRIMARY','reference':reference(text,'950')}]}


class Tests(unittest.TestCase):
    def setUp(self):self.catalog=Catalog(graph());self.model=Mock();self.events=[]
    def resolver(self):return Resolver(catalog=self.catalog,model=self.model,record=self.events.append)
    def test_several_numerals_only_one_primary_is_not_ambiguous(self):
        text='On Report, Card shows 950 on 2026-10-26 for record 42.'
        args=proposal(text);args['figure_mentions'].extend([
            {'role':'DATE','reference':reference(text,'2026-10-26')},
            {'role':'IDENTIFIER','reference':reference(text,'42')}])
        self.model.complete.return_value=tool('resolve_intake',args)
        result=self.resolver().resolve(text)
        self.assertEqual(result['status'],'READY');self.assertEqual(result['reported_figure']['value'],'950')
        self.assertEqual(result['description'],text)
    def test_repeated_same_primary_more_than_eight_times_is_not_ambiguity(self):
        text='On Report, Card shows '+', '.join(['950']*10)+'.'
        args=proposal(text);args['figure_mentions']=[{'role':'PRIMARY','reference':reference(text,'950',i)} for i in range(1,11)]
        self.assertEqual(self.resolver().check(text,args)['status'],'READY')
    def test_two_genuinely_competing_primary_values_ask_named_value_choices(self):
        text='On Report, Card shows 950 or 900; I am unsure which.'
        args=proposal(text);args['figure_mentions'].append({'role':'PRIMARY','reference':reference(text,'900')})
        result=self.resolver().check(text,args)
        self.assertEqual(result['code'],'AMBIGUOUS_PRIMARY_FIGURE')
        self.assertEqual([c['name'] for c in result['question']['fields'][0]['choices']],['950','900'])
    def test_bad_span_once_then_exact_span_proceeds(self):
        text='On Report, Card shows 950.';bad=proposal(text);bad['provenance']['reported_figure']=[999,999]
        self.model.complete.side_effect=[tool('resolve_intake',bad),tool('resolve_intake',proposal(text))]
        self.assertEqual(self.resolver().resolve(text)['status'],'READY');self.assertEqual(self.model.complete.call_count,2)
    def test_two_bad_spans_refuse_without_reasking_the_named_report(self):
        text='On Report, Card shows 950.';bad=proposal(text);bad['provenance']['reported_figure']=[999,999]
        self.model.complete.return_value=tool('resolve_intake',bad)
        result=self.resolver().resolve(text)
        self.assertEqual(result['status'],'NEEDS_INPUT');self.assertEqual(self.model.complete.call_count,2)
        self.assertNotIn('report',[f['field'] for f in result['question']['fields']])
    def test_invalid_shape_is_retried_instead_of_crashing(self):
        text='On Report, Card shows 950.';bad=proposal(text);bad['proposal']['unrecognized']='field'
        self.model.complete.side_effect=[tool('resolve_intake',bad),tool('resolve_intake',proposal(text))]
        self.assertEqual(self.resolver().resolve(text)['status'],'READY')
    def test_model_cannot_rewrite_the_original_description(self):
        text='On Report, Card shows 950.';args=proposal(text);args['proposal']['description']='This number was confirmed.'
        self.assertEqual(self.resolver().check(text,args)['description'],text)
    def test_lookup_returns_actual_page_visual_measure_names(self):
        found=self.resolver().lookup({'words':'Report','report':'report'})
        self.assertEqual(found['reports'][0]['pages'][0]['visuals'][0]['name'],'Card')


if __name__=='__main__':unittest.main()
