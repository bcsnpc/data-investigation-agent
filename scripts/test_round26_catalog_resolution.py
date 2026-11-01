import unittest
from investigator.guided_intake import Catalog, prefill
from test_round23_intake_queries import graph


class CatalogResolutionTests(unittest.TestCase):
    def test_named_model_scopes_reused_measure_through_native_parents(self):
        catalog=self.catalog()
        catalog.nodes.update({'model':{'id':'model','kind':'MODEL','label':'Quarterly snapshot'},
            'table':{'id':'table','kind':'TABLE','label':'Activity'},
            'copy':{'id':'copy','kind':'MEASURE','label':'Net Revenue'}})
        catalog.edges.extend([{'source':'model','target':'table','kind':'CONTAINS'},
                              {'source':'table','target':'measure','kind':'CONTAINS'}])
        text='Quarterly snapshot Net Revenue looks wrong'
        result=prefill(text,{'measure':'measure','issue_type':'NUMBER_LOOKS_WRONG'},catalog)
        self.assertEqual(result['measure'],'measure')
        with self.assertRaisesRegex(ValueError,'DIRECT_TARGET_UNRESOLVED_OR_AMBIGUOUS'):
            prefill(text,{'measure':'copy','issue_type':'NUMBER_LOOKS_WRONG'},catalog)
        self.assertEqual([r['id']for r in catalog.measure_matches(text)],['measure'])
        # Removing the native parent is not repaired by a similar name.
        catalog.edges=[e for e in catalog.edges if not(e['source']=='table'and e['target']=='measure')]
        self.assertEqual(catalog.measure_matches(text),[])

    def test_named_model_does_not_resolve_two_native_measures_with_same_name(self):
        catalog=self.catalog()
        catalog.nodes.update({'model':{'id':'model','kind':'MODEL','label':'Quarterly snapshot'},
                              'copy':{'id':'copy','kind':'MEASURE','label':'Net Revenue'}})
        catalog.edges.extend([{'source':'model','target':m,'kind':'CONTAINS'}for m in ('measure','copy')])
        with self.assertRaisesRegex(ValueError,'DIRECT_TARGET_UNRESOLVED_OR_AMBIGUOUS'):
            prefill('Quarterly snapshot Net Revenue looks wrong',
                    {'measure':'measure','issue_type':'NUMBER_LOOKS_WRONG'},catalog)

    def test_measure_mention_is_retained_without_displacing_selected_report(self):
        catalog=self.catalog()
        result=prefill('Billing Overview Net Revenue',{'report':'report','measure':'measure',
            'issue_type':'NUMBER_LOOKS_WRONG'},catalog)
        self.assertEqual(result['status'],'READY')
        self.assertEqual(result['report'],'report')
        self.assertEqual(result['details']['measure'],'measure')
        self.assertNotIn('measure',result)

    def test_named_other_page_card_cannot_be_replaced_by_same_measure(self):
        catalog=self.catalog();catalog.nodes['card']['label']='North card'
        catalog.nodes.update({'global':{'id':'global','kind':'VISUAL','label':'Global card'},
                              'globalpage':{'id':'globalpage','kind':'PAGE','label':'Global page'}})
        catalog.edges.extend([{'source':'report','target':'globalpage','kind':'CONTAINS'},
            {'source':'globalpage','target':'global','kind':'CONTAINS'},
            {'source':'global','target':'measure','kind':'COMPUTED_FROM'}])
        with self.assertRaisesRegex(ValueError,'VISUAL_PROVENANCE'):
            prefill('Billing Overview Global card Net Revenue',{'report':'report','page':'page','visual':'card',
                'issue_type':'NUMBER_LOOKS_WRONG'},catalog,provenance={'visual':[5,6]})

    def test_measure_span_can_resolve_only_its_unique_visual_on_the_page(self):
        catalog=self.catalog();catalog.nodes['card']['label']='Net Revenue - unfiltered'
        text='Billing Overview Net Revenue card'
        result=prefill(text,{'report':'report','page':'page','visual':'card',
            'issue_type':'NUMBER_LOOKS_WRONG'},catalog,provenance={'visual':[3,4]})
        self.assertEqual(result['status'],'READY')
        self.assertEqual(result['visual'],'card')
        catalog.nodes['second']={'id':'second','kind':'VISUAL','label':'Net Revenue by region'}
        catalog.edges.extend([{'source':'page','target':'second','kind':'CONTAINS'},
                              {'source':'second','target':'measure','kind':'COMPUTED_FROM'}])
        with self.assertRaisesRegex(ValueError,'VISUAL_PROVENANCE'):
            prefill(text,{'report':'report','page':'page','visual':'card',
                'issue_type':'NUMBER_LOOKS_WRONG'},catalog,provenance={'visual':[3,4]})

    def test_lookup_accepts_unique_report_name_without_changing_target(self):
        from investigator.guided_text_resolver import Resolver
        catalog=self.catalog();resolver=Resolver(catalog=catalog,model=None,record=lambda e:None)
        result=resolver.lookup({'report':'Billing Overview','words':'Net Revenue'})
        self.assertEqual([r['id']for r in result['reports']],['report'])

    def test_named_model_uses_its_only_native_table_without_inventing_report(self):
        catalog = self.catalog()
        catalog.nodes.update({'model':{'id':'model','kind':'MODEL','label':'Quarterly snapshot'},
                              't':{'id':'t','kind':'TABLE','label':'Movements'}})
        catalog.edges.append({'source':'model','target':'t','kind':'CONTAINS'})
        result = prefill('Quarterly snapshot is stale', {'issue_type':'DATA_LOOKS_OLD'}, catalog)
        self.assertEqual(result['status'], 'READY')
        self.assertEqual(result['table'], 't')
        self.assertNotIn('report', result)
        catalog.nodes['t2'] = {'id':'t2','kind':'TABLE','label':'Rates'}
        catalog.edges.append({'source':'model','target':'t2','kind':'CONTAINS'})
        self.assertEqual(catalog.table_matches('Quarterly snapshot is stale'), [])

    def test_identifier_underscores_normalize_as_word_separators(self):
        catalog = self.catalog()
        catalog.nodes['t'] = {'id':'t','kind':'TABLE','label':'ledger_transactions'}
        self.assertEqual(catalog.table_matches('ledger transactions differs')[0]['id'], 't')

    def test_named_page_beats_unrelated_fuzzy_report_name(self):
        catalog = self.catalog()
        catalog.nodes['page']['label'] = 'Unfiltered control'
        catalog.nodes['other']['label'] = 'Net Reveneu'
        result = prefill('Net Revenue on Unfiltered control looks old',
                         {'issue_type': 'DATA_LOOKS_OLD'}, catalog)
        self.assertEqual(result['status'], 'READY')
        self.assertEqual(result['report'], 'report')

    def test_exact_table_beats_lower_ranked_fuzzy_table(self):
        catalog = self.catalog()
        catalog.nodes['a'] = {'id': 'a', 'kind': 'TABLE', 'label': 'ledger_transactions'}
        catalog.nodes['b'] = {'id': 'b', 'kind': 'TABLE', 'label': 'ledger_transaction'}
        # Use a lower fuzzy score outside the tie interval: an exact match
        # must not be rejected merely because another fuzzy result exists.
        from unittest.mock import patch
        original = catalog.ranked
        def ranked(text, kind, **kwargs):
            if kind == 'TABLE':return [{'id':'a','name':'ledger_transactions','score':1.0,'confidence':'NAMED'},
                                      {'id':'b','name':'ledger_transaction','score':.9,'confidence':'FUZZY'}]
            return original(text, kind, **kwargs)
        with patch.object(catalog, 'ranked', side_effect=ranked):
            result = prefill('ledger_transactions differs',
                {'issue_type':'NUMBER_LOOKS_WRONG','table':'a'}, catalog)
        self.assertEqual(result['status'], 'READY')
        self.assertEqual(result['table'], 'a')

    def test_named_page_disambiguates_reused_measure_across_reports(self):
        catalog = self.catalog()
        catalog.nodes['page']['label'] = 'Unfiltered control'
        catalog.edges.append({'source': 'othercard', 'target': 'measure', 'kind': 'COMPUTED_FROM'})
        result = prefill('Net Revenue on Unfiltered control looks old', {'issue_type': 'DATA_LOOKS_OLD'}, catalog)
        self.assertEqual(result['status'], 'READY')
        self.assertEqual(result['report'], 'report')
        self.assertEqual(result['page'], 'page')

    def test_named_physical_table_does_not_require_report(self):
        catalog = self.catalog()
        catalog.nodes['view'] = {'id': 'view', 'kind': 'VIEW', 'label': 'access_export'}
        result = prefill('Why does access_export differ for these accounts?',
                         {'issue_type': 'OTHERS_SEE_DIFFERENT_NUMBER'}, catalog)
        self.assertEqual(result['status'], 'READY')
        self.assertEqual(result['table'], 'view')
        self.assertNotIn('report', result)

    def catalog(self):
        g = graph()
        for node in g['nodes']:
            if node['id'] == 'measure':
                node['label'] = 'Net Revenue'
                node['enrichment'] = {'synonyms': ['receipts'], 'business_meaning': 'money collected'}
            if node['id'] == 'report':node['label'] = 'Billing Overview'
        return Catalog(g)

    def test_exact_normalized_synonym_and_typo_are_ranked_from_evidence(self):
        catalog = self.catalog()
        for text in ('Net Revenue is wrong', 'net-revenue is wrong', 'receipts is wrong', 'Net Reveneu is wrong'):
            matches = catalog.ranked(text, 'MEASURE')
            self.assertEqual(matches[0]['id'], 'measure')
            self.assertGreaterEqual(matches[0]['score'], .86)

    def test_measure_infers_only_unique_report_without_selecting_visual(self):
        result = prefill('Net Revenue looks old', {'issue_type': 'DATA_LOOKS_OLD'}, self.catalog())
        self.assertEqual(result['status'], 'READY')
        self.assertEqual(result['report'], 'report')
        self.assertNotIn('visual', result)
        self.assertEqual(result['resolution_assumptions'][0]['name'], 'Billing Overview')

    def test_same_measure_in_two_reports_asks_once_without_guessing(self):
        catalog = self.catalog()
        catalog.edges.append({'source': 'othercard', 'target': 'measure', 'kind': 'COMPUTED_FROM'})
        result = prefill('Net Revenue looks old', {'issue_type': 'DATA_LOOKS_OLD'}, catalog)
        self.assertEqual(result['status'], 'NEEDS_INPUT')
        self.assertEqual({c['id'] for c in result['question']['fields'][0]['choices']}, {'report', 'other'})

    def test_related_words_alone_do_not_silently_choose_report(self):
        result = prefill('money is odd', {'issue_type': 'NUMBER_LOOKS_WRONG'}, self.catalog())
        self.assertEqual(result['status'], 'NEEDS_INPUT')

    def test_missing_parent_does_not_create_named_report_binding(self):
        catalog = self.catalog(); catalog.edges = []
        self.assertEqual(catalog.report_matches('Net Revenue is wrong'), [])
