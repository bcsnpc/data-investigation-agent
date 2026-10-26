import copy
import unittest
from unittest.mock import Mock,patch
from investigator import calculation_intake as intake
from investigator.intake_span_references import tokens
from investigator.reported_figure import AmbiguousFigure,UnavailablePrecision

def ref(text,quote):
    start=text.index(quote);end=start+len(quote);ts=tokens(text)
    return [next(t['id']for t in ts if t['start']==start),next(t['id']for t in ts if t['end']==end)]

def raw(text,target='Net receipts',kind='CALCULATION',figure=None):
    return {'kind':kind,'primary':[1,len(tokens(text))],
      'targets':[{'words':ref(text,target),'kind':'VISUAL','role':'PRIMARY'}],
      'figures':[]if figure is None else[{'words':ref(text,figure),'role':'PRIMARY'}],
      'filters':[],'periods':[],'comparison':{'kind':'NONE','words':None}}

def catalog():
    return {'candidates':[{'id':'r','kind':'REPORT','label':'Cash report'},
      {'id':'p','kind':'PAGE','label':'Daily overview'},
      {'id':'v','kind':'VISUAL','label':'Net receipts','enrichment':{
        'synonyms':['money received'],'business_meaning':'Net receipts after returned payments'}},
      {'id':'m','kind':'MEASURE','label':'Net amount'}],
      'edges':[{'source':'r','target':'p','kind':'CONTAINS'},
        {'source':'p','target':'v','kind':'CONTAINS'},{'source':'v','target':'m','kind':'COMPUTED_FROM'}]}

class CalculationAdmission(unittest.TestCase):
    def test_non_numeric_figure_reference_gets_one_correction_without_inventing_a_number(self):
        text='When was Net amount last refreshed?'
        bad=raw(text,target='Net amount',kind='FRESHNESS',figure='Net amount')
        bad['targets'][0]['kind']='MEASURE'
        corrected=copy.deepcopy(bad);corrected['figures']=[]
        decide=Mock(side_effect=[bad,corrected])
        result=intake.extract(text,decide,catalog(),retain=lambda _:None)
        self.assertEqual(result['reported_figure'],{'state':'UNSPECIFIED'})
        self.assertEqual(decide.call_count,2)
        self.assertIn('PRIMARY_FIGURE_SPAN_IS_TARGET_NAME',decide.call_args_list[1].args[0]['previous_rejection'])
        with self.assertRaises(intake.ExtractionNeedsInput):
            intake.extract(text,Mock(return_value=bad),catalog(),retain=lambda _:None)

    def test_broad_figure_span_retries_without_choosing_among_genuine_rivals(self):
        text='Net receipts shows 950 for invoice_id 321.'
        bad=raw(text,figure='950 for invoice_id 321');correct=raw(text,figure='950')
        decide=Mock(side_effect=[bad,correct])
        result=intake.extract(text,decide,catalog(),retain=lambda _:None)
        self.assertEqual(result['reported_figure']['value'],'950')
        self.assertEqual(decide.call_count,2)
        self.assertIn('FIGURE_SPAN_NOT_ONE_STATED_NUMBER',decide.call_args_list[1].args[0]['previous_rejection'])

    def test_refresh_question_uses_only_the_declared_measure_owner(self):
        text='When was Net amount last refreshed?';value=raw(text,target='Net amount',kind='FRESHNESS')
        value['targets'][0]['kind']='MEASURE';c=catalog()
        c['candidates'].append({'id':'model','kind':'MODEL','label':'Cash model'})
        c['edges'].append({'source':'model','target':'m','kind':'CONTAINS'})
        result=intake.resolve({'text':text},c,self.extract(text,value))
        self.assertEqual(result['ticket']['request']['kind'],'FACT')
        self.assertEqual(result['ticket']['request']['subject'],'model')
        self.assertEqual(result['ticket']['request']['question'],'REFRESH_STATUS')
        self.assertIn('Checking refresh status for Cash model',result['ticket']['assumptions'][0])
        c['candidates'].append({'id':'other-model','kind':'MODEL','label':'Other model'})
        c['edges'].append({'source':'other-model','target':'m','kind':'CONTAINS'})
        held=intake.resolve({'text':text},c,self.extract(text,value))
        self.assertEqual(held['status'],'CLARIFYING')
        self.assertEqual(held['reason'],'REFRESH_OWNER_UNRESOLVED')

    def test_explicit_model_locates_duplicate_measure_without_using_its_value(self):
        text='Net amount in the Cash model shows 950.'
        value=raw(text,target='Net amount',figure='950');value['targets'][0]['kind']='MEASURE'
        value['targets'].append({'words':ref(text,'Cash model'),'kind':'MODEL','role':'CONTEXT'})
        c=catalog();c['candidates'] += [{'id':'model','kind':'MODEL','label':'Cash model'},
            {'id':'other-model','kind':'MODEL','label':'Other model'},
            {'id':'other-measure','kind':'MEASURE','label':'Net amount'}]
        c['edges'] += [{'source':'model','target':'m','kind':'CONTAINS'},
            {'source':'other-model','target':'other-measure','kind':'CONTAINS'}]
        result=intake.resolve({'text':text},c,self.extract(text,value))
        self.assertEqual(result['status'],'READY')
        self.assertEqual(result['ticket']['request']['subject'],'m')
        value['targets'][-1]['role']='COMPARISON'
        self.assertEqual(intake.resolve({'text':text},c,self.extract(text,value))['reason'],'CALCULATION_TARGET_TIED')

    def test_named_model_scopes_visual_only_through_declared_measure_edge(self):
        text='Net receipts in the Cash model shows 950.';value=raw(text,figure='950')
        value['targets'].append({'words':ref(text,'Cash model'),'kind':'MODEL','role':'CONTEXT'})
        c=catalog();c['candidates'].append({'id':'model','kind':'MODEL','label':'Cash model'})
        c['edges'].append({'source':'model','target':'m','kind':'CONTAINS'})
        result=intake.resolve({'text':text},c,self.extract(text,value))
        self.assertEqual(result['ticket']['request']['subject'],'v')
        c['edges']=[e for e in c['edges']if e['kind']!='COMPUTED_FROM']
        self.assertEqual(intake.resolve({'text':text},c,self.extract(text,value))['reason'],'CALCULATION_TARGET_UNRESOLVED')

    def test_exact_named_location_survives_omitted_producer_location(self):
        text='Net receipts on the Daily overview page in the Cash report shows 950.'
        value=raw(text,figure='950');c=catalog()
        c['candidates'].append({'id':'elsewhere','kind':'VISUAL','label':'Net receipts'})
        result=intake.resolve({'text':text},c,self.extract(text,value))
        self.assertEqual(result['ticket']['request']['subject'],'v')
        self.assertEqual(result['ticket']['reported_figure']['value'],'950')

    def test_raw_location_cannot_be_borrowed_from_comparison_or_negation(self):
        for text,comparison in (
                ('Net receipts shows 950 compared with a value in the Cash report.',True),
                ('Net receipts shows 950, not in the Cash report.',False)):
            with self.subTest(text=text):
                value=raw(text,figure='950');c=catalog()
                c['candidates'].append({'id':'elsewhere','kind':'VISUAL','label':'Net receipts'})
                if comparison:value['comparison']={'kind':'report','words':ref(text,'a value in the Cash report')}
                self.assertEqual(intake.resolve({'text':text},c,self.extract(text,value))['reason'],'CALCULATION_TARGET_TIED')

    def extract(self,text,value):
        return intake.extract(text,Mock(return_value=value),catalog(),retain=lambda _:None)

    def test_malformed_producer_shape_retries_with_field_feedback_instead_of_crashing(self):
        text='Net receipts shows 950.';correct=raw(text,figure='950');invalid=copy.deepcopy(correct)
        invalid['targets']='not an array'
        decide=Mock(side_effect=[invalid,correct])
        result=intake.extract(text,decide,catalog(),retain=lambda _:None)
        self.assertEqual(result['reported_figure']['value'],'950')
        feedback=decide.call_args_list[1].args[0]['previous_rejection']
        self.assertIn('$.targets',feedback);self.assertNotIn('additionalProperties',feedback)
        self.assertEqual(decide.call_count,2)
        with self.assertRaises(intake.ExtractionNeedsInput):
            intake.extract(text,Mock(return_value=invalid),catalog(),retain=lambda _:None)

    def test_filter_span_retry_names_the_wrong_field_and_preserves_selection(self):
        text='Net receipts shows 950 for invoice_id 321.'
        value=raw(text,figure='950')
        value['filters']=[{'words':ref(text,'321'),'column':ref(text,'invoice_id'),
                           'value':ref(text,'321'),'role':'PRIMARY'}]
        corrected=copy.deepcopy(value);corrected['filters'][0]['words']=ref(text,'invoice_id 321')
        decide=Mock(side_effect=[value,corrected]);events=[]
        result=intake.extract(text,decide,catalog(),retain=events.append)
        feedback=decide.call_args_list[1].args[0]['previous_rejection']
        self.assertIn('filters[0] words=',feedback)
        self.assertIn('column=',feedback);self.assertIn('value=',feedback)
        self.assertIn('do not invent a relationship',feedback)
        self.assertEqual(result['filters'][0]['words']['quote'],'invoice_id 321')
        self.assertEqual(result['reported_figure']['value'],'950')
        self.assertEqual(decide.call_count,2)

    def test_graph_name_alias_and_meaning_are_ranked_search_evidence(self):
        self.assertEqual(intake.rank('Net receipts',catalog())[0]['basis'],'NAME')
        match=intake.rank('money received',catalog())[0]
        self.assertEqual((match['id'],match['confidence'],match['basis']),('v',.94,'ENRICHMENT_SYNONYM'))
        self.assertGreater(intake.rank('returned payments',catalog())[0]['confidence'],0)
        self.assertTrue(match['search_aid_only'])

    def test_name_search_treats_separators_as_words_without_erasing_suffixes(self):
        c=catalog();c['candidates'][2]['label']='Net_receipts'
        self.assertEqual(intake.rank('Net receipts',c)[0]['confidence'],1)
        self.assertEqual(intake.rank('Net-receipts',c)[0]['confidence'],1)
        self.assertEqual(intake.words('Net_receipts'),{'net','receipts'})
        text='Net receipts shows 950.'
        value=self.extract(text,raw(text,figure='950'))
        self.assertEqual(intake.resolve({'text':text},c,value)['ticket']['visual'],'v')
        c['candidates'].append({'id':'second','kind':'VISUAL','label':'Net-receipts'})
        self.assertEqual(intake.resolve({'text':text},c,value)['reason'],'CALCULATION_TARGET_TIED')
        c['candidates']=[{'id':'suffixed','kind':'VISUAL','label':'Net_receipts_archived'}]
        self.assertLess(intake.rank('Net receipts',c)[0]['confidence'],.9)

    def test_high_confidence_admits_assumption_exact_number_and_pending_comparison(self):
        text='Net receipts shows 950.';ticket={'id':'raw','text':text};before=copy.deepcopy(ticket)
        result=intake.resolve(ticket,catalog(),self.extract(text,raw(text,figure='950')))
        self.assertEqual(ticket,before);self.assertEqual(result['status'],'READY')
        admitted=result['ticket'];self.assertEqual(admitted['visual'],'v')
        self.assertEqual(admitted['reported_figure']['value'],'950')
        self.assertEqual(admitted['reported_figure']['precision'],{'state':'EXACT'})
        self.assertTrue(admitted['request']['comparison_pending'])
        self.assertIn('Net receipts',admitted['assumptions'][0])

    def test_tied_targets_ask_one_grounded_question_and_never_display_ids(self):
        text='Net receipts shows 950.';c=catalog()
        c['candidates'].append({'id':'private-other','kind':'VISUAL','label':'Net receipts'})
        result=intake.resolve({'text':text},c,self.extract(text,raw(text,figure='950')))
        self.assertEqual(result['reason'],'CALCULATION_TARGET_TIED');self.assertEqual(len(result['questions']),1)
        self.assertNotIn('private-other',result['questions'][0]['text'])
        self.assertEqual({v['label']for v in result['questions'][0]['choices']},{'Net receipts'})

    def test_explicit_page_selects_its_visual_without_asking_for_report_again(self):
        text='Cash report Daily overview Net receipts shows 950.';value=raw(text,figure='950')
        value['targets']+=[{'words':ref(text,'Cash report'),'kind':'REPORT','role':'PRIMARY'},
                           {'words':ref(text,'Daily overview'),'kind':'PAGE','role':'PRIMARY'}]
        c=catalog();c['candidates'].append({'id':'outside','kind':'VISUAL','label':'Net receipts'})
        result=intake.resolve({'text':text},c,self.extract(text,value))
        self.assertEqual(result['status'],'READY');self.assertEqual(result['ticket']['visual'],'v')

    def test_comparison_span_never_selects_the_primary_visual(self):
        text='Net receipts is 950 versus Gross receipts 1200 in my spreadsheet.';value=raw(text,figure='950')
        value['targets'].append({'words':ref(text,'Gross receipts'),'kind':'VISUAL','role':'COMPARISON'})
        value['figures'].append({'words':ref(text,'1200'),'role':'COMPARISON'})
        value['comparison']={'kind':'spreadsheet','words':ref(text,'my spreadsheet')}
        c=catalog();c['candidates'].append({'id':'gross','kind':'VISUAL','label':'Gross receipts'})
        result=intake.resolve({'text':text},c,self.extract(text,value))
        self.assertEqual(result['ticket']['visual'],'v');self.assertEqual(result['ticket']['comparison']['value'],'1200')

    def test_named_spreadsheet_without_its_value_does_not_block_recreation_and_freshness(self):
        text='Net receipts is 950 versus my spreadsheet.';value=raw(text,figure='950')
        value['comparison']={'kind':'spreadsheet','words':ref(text,'my spreadsheet')}
        admitted=intake.resolve({'text':text},catalog(),self.extract(text,value))['ticket']
        self.assertTrue(admitted['request']['comparison_pending']);self.assertNotIn('comparison',admitted)
        from test_ledger_investigator import ToolLoopTests
        tools,engine,reader,_=ToolLoopTests().build()
        request=copy.deepcopy(admitted['request']);request['subject']='visual'
        answer=engine.run({'visual':'visual','text':text,'request':request})
        self.assertTrue(reader.called);self.assertTrue(tools.graph.node_facts.called)
        self.assertGreater(reader.call_count,1)
        self.assertNotIn('question',answer)
        self.assertFalse(any(r['kind']=='GIVEN_COMPARISON'for r in answer['evidence'].values()))

    def test_compare_subject_cannot_point_at_a_different_visual_than_the_reader(self):
        from test_ledger_investigator import ToolLoopTests
        tools,engine,reader,_=ToolLoopTests().build()
        with self.assertRaisesRegex(ValueError,'SUBJECT_ADMISSION_DIFFERS'):
            engine.run({'visual':'visual','text':'Check this card.','request':{'kind':'COMPARE','subject':'another-card'}})
        reader.assert_not_called();tools.graph.node_facts.assert_not_called()

    def test_real_rival_primary_values_do_not_get_retried_until_one_disappears(self):
        text='Net receipts is 950 or 960.';value=raw(text,figure='950')
        value['figures'].append({'words':ref(text,'960'),'role':'PRIMARY'});decide=Mock(return_value=value)
        with self.assertRaises(AmbiguousFigure):intake.extract(text,decide,catalog(),retain=lambda _:None)
        self.assertEqual(decide.call_count,1)

    def test_bad_token_reference_retries_once_then_refuses(self):
        text='Net receipts shows 950.';value=raw(text,figure='950');bad=copy.deepcopy(value)
        bad['figures'][0]['words']=[900,901];decide=Mock(side_effect=[bad,value]);events=[]
        result=intake.extract(text,decide,catalog(),retain=events.append)
        self.assertEqual(result['reported_figure']['value'],'950');self.assertEqual(decide.call_count,2)
        with self.assertRaisesRegex(ValueError,'NEEDS_INPUT'):
            intake.extract(text,Mock(return_value=bad),catalog(),retain=lambda _:None)

    def test_enumerated_span_keeps_exact_referent_without_asking_the_user(self):
        text='Please check Net receipts today.';value=raw(text)
        first,last=value['primary'];value['primary']=list(range(first,last+1))
        parsed=self.extract(text,value)
        self.assertEqual(parsed['primary']['quote'],text)
        self.assertEqual(intake.reference([2,3,4],text),intake.reference([2,4],text))
        self.assertEqual(intake.reference([2],text),intake.reference([2,2],text))
        one='Net receipts shows 950.';value=raw(one,figure='950')
        value['figures'][0]['words']=[ref(one,'950')[0]]
        self.assertEqual(self.extract(one,value)['reported_figure']['value'],'950')
        for invalid in ([1,3,4],[4,3,2],[1,10**12,10**13]):
            with self.assertRaisesRegex(ValueError,'CONTIGUOUS'):intake.reference(invalid,text)

    def test_context_page_locates_measure_without_becoming_a_filter_or_comparator(self):
        text='Net amount on Daily overview shows 950.';value=raw(text,target='Net amount',figure='950')
        value['targets'][0]['kind']='MEASURE'
        value['targets'].append({'words':ref(text,'Daily overview'),'kind':'PAGE','role':'CONTEXT'})
        c=catalog();c['candidates'].append({'id':'other-measure','kind':'MEASURE','label':'Net amount'})
        admitted=intake.resolve({'text':text},c,self.extract(text,value))
        self.assertEqual(admitted['status'],'READY');self.assertEqual(admitted['ticket']['request']['subject'],'v')
        self.assertEqual(admitted['ticket']['intake_scope']['filters'],[])
        value['targets'][-1]['role']='COMPARISON'
        tied=intake.resolve({'text':text},c,self.extract(text,value))
        self.assertEqual(tied['reason'],'CALCULATION_TARGET_TIED')

    def test_same_measure_in_multiple_visuals_never_uses_reported_value_to_pick_a_cell(self):
        text='Net amount on Daily overview shows 950.';value=raw(text,target='Net amount',figure='950')
        value['targets'][0]['kind']='MEASURE'
        value['targets'].append({'words':ref(text,'Daily overview'),'kind':'PAGE','role':'CONTEXT'})
        c=catalog();c['candidates'].append({'id':'north','kind':'VISUAL','label':'North card'})
        c['edges'] += [{'source':'p','target':'north','kind':'CONTAINS'},
                       {'source':'north','target':'m','kind':'COMPUTED_FROM'}]
        result=intake.resolve({'text':text},c,self.extract(text,value))
        self.assertEqual(result['reason'],'CALCULATION_VISUAL_SCOPE_UNRESOLVED')
        self.assertEqual({n['label']for n in result['questions'][0]['choices']},{'Net receipts','North card'})
        self.assertNotIn('ticket',result)

    def test_negated_page_mention_does_not_supply_a_target_location(self):
        text='Net amount, not on Daily overview, shows 950.';value=raw(text,target='Net amount',figure='950')
        value['targets'][0]['kind']='MEASURE';value['targets'].append({'words':ref(text,'Daily overview'),'kind':'PAGE','role':'CONTEXT'})
        c=catalog();c['candidates'].append({'id':'other','kind':'MEASURE','label':'Net amount'})
        result=intake.resolve({'text':text},c,self.extract(text,value))
        self.assertEqual(result['reason'],'CALCULATION_TARGET_TIED')

    def test_provider_schema_rejection_retries_but_real_provider_errors_do_not(self):
        from jsonschema import ValidationError
        text='Net receipts shows 950.';value=raw(text,figure='950')
        decide=Mock(side_effect=[ValidationError('wrong producer shape'),value])
        self.assertEqual(intake.extract(text,decide,catalog(),retain=lambda _:None)['reported_figure']['value'],'950')
        self.assertEqual(decide.call_count,2)

    def test_primary_reference_cannot_be_taken_from_the_comparison_span(self):
        text='Net receipts is 950 versus Gross receipts 1200.';value=raw(text,figure='950')
        value['comparison']={'kind':'report','words':ref(text,'Gross receipts 1200')}
        value['targets'][0]['words']=ref(text,'Gross receipts')
        with self.assertRaisesRegex(ValueError,'PRIMARY_REFERENT_INSIDE_COMPARISON_SPAN'):
            intake.extract(text,Mock(return_value=value),catalog(),retain=lambda _:None)

    def test_filters_and_periods_remain_exact_scoped_provenance_not_mentions(self):
        text='Net receipts with warehouse North on 2026-09-14 is 950.';value=raw(text,figure='950')
        value['filters']=[{'words':ref(text,'warehouse North'),'column':ref(text,'warehouse'),
                           'value':ref(text,'North'),'role':'PRIMARY'}]
        value['periods']=[ref(text,'2026-09-14')]
        parsed=self.extract(text,value);result=intake.resolve({'text':text},catalog(),parsed)
        scope=result['ticket']['intake_scope']
        self.assertEqual(scope['filters'][0]['value']['quote'],'North')
        self.assertEqual(scope['periods'][0]['quote'],'2026-09-14')
        bad=copy.deepcopy(value);bad['filters'][0]['value']=ref(text,'950')
        with self.assertRaisesRegex(ValueError,'NEEDS_INPUT'):
            intake.extract(text,Mock(return_value=bad),catalog(),retain=lambda _:None)

    def test_precision_is_recorded_not_widened_and_business_intent_refuses(self):
        text='Net receipts is about 3.4M.';parsed=self.extract(text,raw(text,figure='about 3.4M'))
        self.assertEqual(parsed['reported_figure']['precision'],{'state':'STATED_PLACE','place':5})
        value=raw(text,kind='BUSINESS_MEANING',figure='about 3.4M')
        result=intake.resolve({'text':text},catalog(),self.extract(text,value))
        self.assertEqual(result['reason'],'BUSINESS_INTENT_REQUIRES_OWNER')

    def test_longer_name_is_not_tied_with_its_contained_prefix(self):
        c={'candidates':[{'id':'short','kind':'VISUAL','label':'Receipts'},
                         {'id':'long','kind':'VISUAL','label':'Receipts adjusted'}]}
        ranked=intake.rank('Receipts adjusted',c)
        self.assertEqual(ranked[0]['id'],'long');self.assertGreater(ranked[0]['confidence']-ranked[1]['confidence'],.1)

    def test_named_application_entity_can_be_a_primary_subject_without_inventing_a_report(self):
        text='Why does Payment movements have a different quantity?'
        value=raw(text,target='Payment movements');value['targets'][0]['kind']='SOURCE'
        c={'candidates':[{'id':'application-source','kind':'SOURCE','label':'Payment movements'}],'edges':[]}
        parsed=intake.extract(text,Mock(return_value=value),c,retain=lambda _:None)
        result=intake.resolve({'text':text},c,parsed)
        self.assertEqual(result['ticket']['request']['subject'],'application-source')
        self.assertNotIn('visual',result['ticket']);self.assertTrue(result['ticket']['request']['comparison_pending'])

    def test_stated_scope_compiles_through_declared_column_or_stays_explicitly_unavailable(self):
        text='Net receipts selected warehouse 7 is 950.';value=raw(text,figure='950')
        value['filters']=[{'words':ref(text,'selected warehouse 7'),'column':ref(text,'warehouse'),
                           'value':ref(text,'7'),'role':'PRIMARY'}]
        admitted=intake.resolve({'text':text},catalog(),self.extract(text,value))['ticket']
        compiled=intake.compile_scope(admitted,{'columns':[{'column_id':'declared-warehouse','name':'warehouse','data_type':'int64'}]})
        self.assertEqual(compiled['filters'],{'filters':[{'column_id':'declared-warehouse','operator':'in','values':[7]}],'dimension_ids':[]})
        unresolved=intake.compile_scope(admitted)
        self.assertIn('scope_gap',unresolved);self.assertNotIn('filters',unresolved)
        self.assertEqual(unresolved['intake_scope'],admitted['intake_scope'])

    def test_unresolved_scope_never_calls_a_value_reader_but_keeps_quick_checks(self):
        from test_ledger_investigator import ToolLoopTests
        tools,engine,reader,events=ToolLoopTests().build();tools.scope_gap='Period has no declared binding.'
        answer=engine.run({'visual':'visual','text':'Check my selected period.',
            'intake_scope':{'filters':[],'periods':[{'quote':'selected period'}]}})
        reader.assert_not_called()
        self.assertTrue(tools.graph.node_facts.called)
        self.assertEqual(answer['verdict'],'not found');self.assertEqual(answer['question']['code'],'SCOPE_REQUIRED')
        self.assertIn('Period has no declared binding.',answer['outputs']['business'])

    def test_missing_comparison_recreates_and_checks_freshness_before_any_question(self):
        from test_ledger_investigator import ToolLoopTests
        tools,engine,reader,events=ToolLoopTests().build()
        answer=engine.run({'visual':'visual','text':'Check my number.','request':{
            'kind':'COMPARE','subject':'visual','comparison_pending':True}})
        self.assertTrue(reader.called);self.assertTrue(tools.graph.node_facts.called)
        self.assertGreater(reader.call_count,1)
        self.assertNotEqual(answer['stop_reason'],'COMPARISON_REQUIRED_AFTER_QUICK_CHECKS')
        self.assertNotIn('question',answer)
        self.assertTrue(any(r['kind']=='READ'for r in answer['evidence'].values()))

    def test_filter_effect_recreates_but_never_turns_into_a_pipeline_finding(self):
        from test_ledger_investigator import ToolLoopTests
        tools,engine,reader,events=ToolLoopTests().build()
        answer=engine.run({'visual':'visual','text':'Which filter hides rows?','request':{
            'kind':'COMPARE','subject':'visual','question_kind':'FILTER_EFFECT'}})
        self.assertTrue(reader.called);tools.graph.node_facts.assert_not_called()
        self.assertEqual(answer['verdict'],'not found');self.assertEqual(answer['stop_reason'],'UNIMPLEMENTED_ROUTE')

    def test_pure_model_freshness_uses_existing_fact_route_without_a_number_or_comparison(self):
        text='Is Cash model refresh current?';value=raw(text,target='Cash model',kind='FRESHNESS')
        value['targets'][0]['kind']='MODEL';c={'candidates':[{'id':'model','kind':'MODEL','label':'Cash model'}]}
        parsed=intake.extract(text,Mock(return_value=value),c,retain=lambda _:None)
        admitted=intake.resolve({'text':text},c,parsed)['ticket']
        self.assertEqual(admitted['request']['kind'],'FACT');self.assertEqual(admitted['request']['question'],'REFRESH_STATUS')
        self.assertNotIn('comparison_pending',admitted['request'])
        self.assertEqual(set(admitted['request']),{'kind','subject','question','source'})
        from investigator.evidence_verdicts import explicit_operational_fact
        from test_ledger_investigator import fact,NOW
        native=fact('model','REFRESH_RUN',{'status':'SUCCEEDED','run_id':'native-refresh',
            'start':'2026-10-22T10:00:00Z','end':'2026-10-22T10:01:00Z'})
        selected=explicit_operational_fact(admitted['request'],[{'kind':'FACT','value':native}],NOW,text)
        self.assertEqual(selected['value']['run_id'],'native-refresh')

    def test_provider_failure_is_not_disguised_as_a_user_question(self):
        with self.assertRaisesRegex(ValueError,'PROVIDER_AUTHENTICATION_REFUSED'):
            intake.admit({'text':'Net receipts shows 950.'},catalog(),
                         decide=Mock(side_effect=ValueError('PROVIDER_AUTHENTICATION_REFUSED')),retain=lambda _:None)

    def test_saved_visual_inventory_is_validated_and_composed_once_with_stated_filters(self):
        from test_declaration_inventory import InventoryTests
        declaration=InventoryTests().declaration()
        ticket={'text':'Check my figure.','filters':{'filters':[{'column_id':'field-a','operator':'in','values':['z']}],'dimension_ids':[]}}
        result=intake.apply_saved_scope(ticket,declaration)
        # Saved intersection is y; intersecting z is an explicit empty filter.
        self.assertEqual(result['filters']['filters'],[{'column_id':'field-a','operator':'in','values':[]}])
        self.assertNotIn('scope_gap',result)
        self.assertEqual(result['intake_declarations']['conservation'],'VALIDATED_BY_CONSUMER')

    def test_unaccounted_saved_declaration_or_unsupported_kind_never_becomes_unfiltered_scope(self):
        from test_declaration_inventory import InventoryTests
        declaration=InventoryTests().declaration();declaration['inventory']['discovered'].append({'location':'missed','content_hash':'b'*64})
        invalid=intake.apply_saved_scope({'text':'Check my figure.'},declaration)
        self.assertIn('conservation',invalid['scope_gap']);self.assertNotIn('filters',invalid)
        declaration=InventoryTests().declaration();entry=declaration['inventory']['entries'][0]
        entry.update(disposition='UNSUPPORTED',restrictions=[],effect='EXCLUDED',volatility='UNKNOWN',assumption='APPLICABILITY_UNKNOWN')
        declaration['restrictions']=[];declaration['unsupported_form']='UnfamiliarSyntheticSelection'
        invalid=intake.apply_saved_scope({'text':'Check my figure.'},declaration)
        self.assertIn('UnfamiliarSyntheticSelection',invalid['scope_gap']);self.assertNotIn('filters',invalid)

    def test_saved_default_qualification_and_conditional_exclusion_survive_handoff(self):
        from test_declaration_inventory import InventoryTests
        from investigator.report_scope import inventory_identity
        declaration=InventoryTests().declaration();entry=declaration['inventory']['entries'][0]
        entry.update(volatility='VIEWER_CHANGEABLE',assumption='SAVED_DEFAULT')
        alternative=copy.deepcopy(entry);alternative['source']['location']='stored-alternative'
        alternative.update(id=inventory_identity(alternative['source']),disposition='CONDITIONAL',restrictions=[],
            effect='EXCLUDED',assumption='INVOCATION_UNKNOWN')
        declaration['inventory']['entries'].append(alternative);declaration['inventory']['discovered'].append(alternative['source'])
        admitted=intake.apply_saved_scope({'text':'Check my figure.'},declaration)
        self.assertEqual(admitted['filters']['filters'][0]['values'],['y'])
        self.assertTrue(any('saved default positions'in label for label in admitted['assumptions']))
        self.assertTrue(any('Stored alternatives' in label for label in admitted['assumptions']))
        self.assertEqual({e['disposition']for e in admitted['intake_declarations']['inventory']},{'ACTIVE','CONDITIONAL'})

    def test_enriched_catalog_still_obeys_graph_scope_and_uses_recorded_search_provenance(self):
        from investigator.estate_graph_api import GraphAPI
        repo=Mock();gateway=Mock();gateway.graph_objects.side_effect=lambda estate,ids,identity:list(ids)
        repo.path_records.return_value={'nodes':[{'id':'v','kind':'VISUAL','label':'Net receipts','properties':{},'provenance':{'definition_hash':'a'*64}},
            {'id':'outside','kind':'VISUAL','label':'Outside'}],'edges':[],'truncated':False}
        graph=GraphAPI(repo,gateway,identity='reader',estate='cash',allowed_objects=['v'])
        with patch('investigator.enrichment.EnrichmentStore.projections',return_value={'v':{
            'synonyms':['money received'],'business_meaning':'Received payments','status':'INFERRED',
            'definition_hash':'a'*64,'provenance':{'evidence_ids':['recorded-enrichment']}}})as search:
            result=graph.intake_candidates(enriched=True)
        search.assert_called_once_with('cash',{'v':'a'*64})
        self.assertEqual([n['id']for n in result['candidates']],['v'])
        self.assertEqual(result['candidates'][0]['enrichment']['status'],'INFERRED')
        self.assertEqual(intake.rank('money received',result)[0]['id'],'v')

class GraphIntakeIntegrationTests(unittest.TestCase):
    def test_card_reference_uses_named_measure_and_location_without_dropping_qualifiers(self):
        text='Check the Net amount card on Daily overview for Cash report: 50.'
        extracted=raw(text,'Net amount card',figure='50')
        for kind,quote in [('MEASURE','Net amount'),('PAGE','Daily overview'),('REPORT','Cash report')]:
            extracted['targets'].append({'words':ref(text,quote),'kind':kind,'role':'CONTEXT'})
        cat=catalog();cat['candidates'][2]['label']='Net amount - current'
        value=intake.extract(text,lambda *a,**k:extracted,cat,retain=lambda _:None)
        result=intake.resolve({'text':text},cat,value)
        self.assertEqual(result['status'],'READY')
        self.assertEqual(result['ticket']['visual'],'v')
        # The model need not repeat a named visual's measure as a second target.
        without_duplicate=copy.deepcopy(value)
        without_duplicate['targets']=[n for n in value['targets']if n['kind']!='MEASURE']
        self.assertEqual(intake.resolve({'text':text},cat,without_duplicate)['ticket']['visual'],'v')
        second=copy.deepcopy(cat['candidates'][2]);second['id']='other'
        cat['candidates'].append(second);cat['edges'] +=[
            {'source':'p','target':'other','kind':'CONTAINS'},
            {'source':'other','target':'m','kind':'COMPUTED_FROM'}]
        self.assertEqual(intake.resolve({'text':text},cat,value)['reason'],'CALCULATION_TARGET_TIED')
        qualified=text.replace('Net amount card','Global Net amount card',1)
        q=raw(qualified,'Global Net amount card',figure='50')
        for kind,quote in [('MEASURE','Net amount'),('PAGE','Daily overview'),('REPORT','Cash report')]:
            q['targets'].append({'words':ref(qualified,quote),'kind':kind,'role':'CONTEXT'})
        value=intake.extract(qualified,lambda *a,**k:q,cat,retain=lambda _:None)
        self.assertEqual(intake.resolve({'text':qualified},cat,value)['status'],'CLARIFYING')

    def test_candidate_names_do_not_load_unrelated_outgoing_dependencies(self):
        import tempfile
        from pathlib import Path
        from investigator.shared_state import SharedState
        from investigator.estate_graph_repository import GraphRepository
        from investigator.estate_graph_api import GraphAPI
        from investigator.live_gateway import Gateway
        from test_estate_graph import graph,proof
        from investigator import estate_graph_contract as contract
        with tempfile.TemporaryDirectory()as temporary:
            state=SharedState.offline(Path(temporary)/'state.sqlite')
            repo=GraphRepository(state);repo.migrate();body=graph()
            for i in range(510):
                identity='external'+str(i)
                body['nodes'].append(contract.node(identity,'owner','COLUMN',identity,proof()))
                body['edges'].append(contract.edge('extra'+str(i),'owner','COMPUTED_FROM','measure',identity,proof()))
            repo.replace(body)
            selected=['report','page','visual','measure']
            gateway=Gateway({'version':1,'live_enabled':False,'identities':{'reader':{'role':'investigation','graph':{'estate':selected}}}})
            api=GraphAPI(repo,gateway,identity='reader',estate='estate',allowed_objects=selected)
            catalog=api.intake_candidates(enriched=True,identities=selected)
            self.assertEqual({n['id']for n in catalog['candidates']},set(selected))
            self.assertEqual({(e['source'],e['target'])for e in catalog['edges']},
                {('report','page'),('page','visual'),('visual','measure')})
            # A real upstream walk still preserves its external boundaries.
            path=repo.path_records('estate',['measure'],selected,max_edges=20)
            self.assertTrue(path['truncated'])
            self.assertTrue(any(e['target'].startswith('external')for e in path['edges']))

    def test_real_repository_keeps_container_edges_and_only_named_candidates_from_wider_path_scope(self):
        import tempfile
        from pathlib import Path
        from investigator.shared_state import SharedState
        from investigator.estate_graph_repository import GraphRepository
        from investigator.estate_graph_api import GraphAPI
        from investigator.live_gateway import Gateway
        from test_estate_graph import graph
        with tempfile.TemporaryDirectory()as temporary:
            state=SharedState.offline(Path(temporary)/'state.sqlite')
            repo=GraphRepository(state);repo.migrate();repo.replace(graph())
            scope=['report','page','visual','measure','column']
            gateway=Gateway({'version':1,'live_enabled':False,'identities':{'reader':{'role':'investigation','graph':{'estate':scope}}}})
            api=GraphAPI(repo,gateway,identity='reader',estate='estate',allowed_objects=scope)
            catalog=api.intake_candidates(enriched=True,identities=['report','page','visual','measure'])
            self.assertNotIn('column',{n['id']for n in catalog['candidates']})
            self.assertIn({'source':'report','target':'page','kind':'CONTAINS'},catalog['edges'])
            self.assertIn({'source':'page','target':'visual','kind':'CONTAINS'},catalog['edges'])
            self.assertIn({'source':'visual','target':'measure','kind':'COMPUTED_FROM'},catalog['edges'])
            # Container names can now constrain a target without inventing an
            # ancestry from labels. Its numerical value is never consulted.
            self.assertEqual(api.path_to_source('visual')['nodes'][-1]['id'],'visual')
            with self.assertRaises(PermissionError):api.intake_candidates(identities=['outside'])


if __name__=='__main__':unittest.main()
