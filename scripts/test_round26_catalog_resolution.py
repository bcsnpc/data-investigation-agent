import unittest
from investigator.guided_intake import Catalog, prefill
from test_round23_intake_queries import graph


class CatalogResolutionTests(unittest.TestCase):
    def test_a_model_cannot_invent_a_report_when_the_ticket_names_a_native_container(self):
        catalog=self.catalog()
        catalog.nodes.update({'landing':{'id':'landing','kind':'SOURCE','label':'Quarterly landing'},
                              'native':{'id':'native','kind':'TABLE','label':'Rows'}})
        catalog.edges.append({'source':'landing','target':'native','kind':'CONTAINS'})
        with self.assertRaisesRegex(ValueError,'REPORT_REFERENCE'):
            prefill('Quarterly landing rows differ',{'report':'report','issue_type':'NUMBER_LOOKS_WRONG'},catalog)
        from unittest.mock import Mock
        from investigator.guided_text_resolver import Resolver
        from test_round23_reasoning import tool
        wrong={'proposal':{'version':'IntakeRequest/1','report':'report','issue_type':'NUMBER_LOOKS_WRONG',
                           'compared_with':{'kind':'NOTHING'}},'provenance':{},'figure_mentions':[]}
        corrected={'proposal':{'version':'IntakeRequest/1','issue_type':'NUMBER_LOOKS_WRONG',
                               'compared_with':{'kind':'NOTHING'}},'provenance':{},'figure_mentions':[]}
        model=Mock();model.complete.side_effect=[tool('resolve_intake',wrong),tool('resolve_intake',corrected)]
        result=Resolver(catalog=catalog,model=model,record=lambda _:None).resolve('Quarterly landing rows differ')
        self.assertEqual(result['status'],'READY');self.assertEqual(result['table'],'native')
    def test_model_inferred_page_cannot_make_a_loose_measure_card_unique(self):
        catalog=self.catalog();catalog.nodes['card']['label']='Net Revenue - filtered'
        catalog.nodes.update({'globalpage':{'id':'globalpage','kind':'PAGE','label':'Global page'},
                              'global':{'id':'global','kind':'VISUAL','label':'Net Revenue - unfiltered'}})
        catalog.edges.extend([{'source':'report','target':'globalpage','kind':'CONTAINS'},
            {'source':'globalpage','target':'global','kind':'CONTAINS'},
            {'source':'global','target':'measure','kind':'COMPUTED_FROM'}])
        with self.assertRaisesRegex(ValueError,'VISUAL_PROVENANCE'):
            prefill('Billing Overview Net Revenue card',{'report':'report','page':'page','visual':'card',
                'issue_type':'NUMBER_LOOKS_WRONG'},catalog,provenance={'visual':[3,4]})
        # A genuinely named page still supplies the user's scope.
        text='Billing Overview Global page Net Revenue card'
        result=prefill(text,{'report':'report','page':'globalpage','visual':'global',
            'issue_type':'NUMBER_LOOKS_WRONG'},catalog,provenance={'visual':[5,6]})
        self.assertEqual(result['status'],'READY')

    def test_visual_rejection_cannot_be_hidden_by_dropping_the_target_on_retry(self):
        from unittest.mock import Mock
        from investigator.guided_text_resolver import Resolver
        from test_round23_reasoning import tool
        catalog=self.catalog();catalog.nodes['card']['label']='Net Revenue - filtered'
        catalog.nodes.update({'p2':{'id':'p2','kind':'PAGE','label':'Global page'},
                              'v2':{'id':'v2','kind':'VISUAL','label':'Net Revenue - unfiltered'}})
        catalog.edges.extend([{'source':'report','target':'p2','kind':'CONTAINS'},
            {'source':'p2','target':'v2','kind':'CONTAINS'},{'source':'v2','target':'measure','kind':'COMPUTED_FROM'}])
        args={'proposal':{'version':'IntakeRequest/1','report':'report','page':'page','visual':'card',
                         'issue_type':'NUMBER_LOOKS_WRONG','compared_with':{'kind':'NOTHING'}},
              'provenance':{'visual':[3,4]},'figure_mentions':[]}
        from copy import deepcopy
        dropped=deepcopy(args);dropped['proposal'].pop('visual');dropped['provenance']={}
        model=Mock();model.complete.side_effect=[tool('resolve_intake',args),tool('resolve_intake',dropped)]
        result=Resolver(catalog=catalog,model=model,record=lambda _:None).resolve('Billing Overview Net Revenue card')
        self.assertEqual(result['status'],'NEEDS_INPUT');self.assertEqual(model.complete.call_count,2)
        self.assertEqual(result['question']['fields'][0]['field'],'visual')
        self.assertTrue(all(' on 'in x['name']for x in result['question']['fields'][0]['choices']))
    def test_named_container_beats_unrelated_generic_table_words(self):
        catalog=self.catalog()
        catalog.nodes.update({'landing':{'id':'landing','kind':'SOURCE','label':'quarterly_landing'},
            'native':{'id':'native','kind':'TABLE','label':'stock_rows_2026'},
            'unrelated':{'id':'unrelated','kind':'TABLE','label':'Movements'}})
        catalog.edges.append({'source':'landing','target':'native','kind':'CONTAINS'})
        result=prefill('Application stock movements are missing from quarterly_landing',
            {'issue_type':'RECORD_MISSING'},catalog)
        self.assertEqual(result['status'],'READY')
        self.assertEqual(result['table'],'native')
        self.assertNotIn('report',result)

    def test_named_container_scopes_duplicate_table_names_with_multiple_children(self):
        catalog=self.catalog()
        catalog.nodes.update({'landing':{'id':'landing','kind':'SOURCE','label':'Quarterly landing'},
            'native':{'id':'native','kind':'TABLE','label':'Movements'},
            'rates':{'id':'rates','kind':'TABLE','label':'Rates'},
            'unrelated':{'id':'unrelated','kind':'TABLE','label':'Movements'}})
        catalog.edges.extend({'source':'landing','target':i,'kind':'CONTAINS'}for i in ('native','rates'))
        self.assertEqual([r['id']for r in catalog.table_matches('Quarterly landing Movements differ')],['native'])
        # Without a named child a multi-table container remains unresolved.
        self.assertEqual(catalog.table_matches('Quarterly landing differs'),[])

    def test_two_named_containers_keep_their_actual_children_ambiguous(self):
        catalog=self.catalog()
        for parent,child,name in [('a','ta','East landing'),('b','tb','West landing')]:
            catalog.nodes[parent]={'id':parent,'kind':'SOURCE','label':name}
            catalog.nodes[child]={'id':child,'kind':'TABLE','label':'Movements'}
            catalog.edges.append({'source':parent,'target':child,'kind':'CONTAINS'})
        text='East landing and West landing Movements disagree'
        self.assertEqual({r['id']for r in catalog.table_matches(text)},{'ta','tb'})
        with self.assertRaisesRegex(ValueError,'DIRECT_TARGET_UNRESOLVED_OR_AMBIGUOUS'):
            prefill(text,{'table':'ta','issue_type':'RECORD_MISSING'},catalog)

    def test_missing_native_parent_never_falls_back_to_unrelated_name(self):
        catalog=self.catalog()
        catalog.nodes.update({'landing':{'id':'landing','kind':'SOURCE','label':'Quarterly landing'},
            'unrelated':{'id':'unrelated','kind':'TABLE','label':'Movements'}})
        self.assertEqual(catalog.table_matches('Quarterly landing Movements differ'),[])

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
