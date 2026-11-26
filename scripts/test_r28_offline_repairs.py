"""Saved-confirmation shapes and negative controls; no providers or estate ports."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
from investigator.delivery_coverage import conditional_definition, candidate_resolution, source_comparison, canonical_selected_target
from investigator.intake_candidates import select_unique
from investigator.daily_smoke import guided_demo_matches


class DefinitionCoverageTests(unittest.TestCase):
    def setUp(self):
        self.inventory={'exhaustive':True,'candidates':[
            {'id':name,'name':name,'explicit':{}} for name in ('global','filtered')]}
        self.observations=[{'candidate':name,'evidence_id':identity,'status':'SUCCEEDED',
                            'truncated':False,'value':value}
                           for name,identity,value in [('global','q1',8765),('filtered','q2',16)]]
        self.case={'intake':{'issue_type':'HOW_IS_THIS_CALCULATED','compared_with':{'kind':'NOTHING'}},
                   'context':{'candidate_inventory':self.inventory,'conclusion_contract':'question-first-v1'},
                   'evidence':{},'queries':[{'id':q,'status':'SUCCEEDED'} for q in ('q1','q2')]}
        self.args={'selected_target':None,'verdict':'as designed','verdict_class':'AS DESIGNED',
                   'undecided':['Which saved visual scope the user meant; no visual was selected.'],
                   'evidence_ids':['q1','q2']}

    def resolution(self):
        return select_unique(self.inventory,self.observations,None)

    def test_r17_10_all_measured_definitions_need_no_arbitrary_selection(self):
        resolution=self.resolution()
        self.assertTrue(resolution['exhaustive']);self.assertIsNone(resolution['selected'])
        self.assertTrue(conditional_definition(self.args,self.case,resolution))

    def test_missing_failed_truncated_or_uncited_candidate_still_blocks(self):
        for change in ('missing','failed','truncated','uncited','invented'):
            with self.subTest(change=change):
                observations=deepcopy(self.observations);args=deepcopy(self.args)
                if change=='missing':observations.pop()
                if change=='failed':observations[-1]['status']='ERROR'
                if change=='truncated':observations[-1]['truncated']=True
                if change=='uncited':args['evidence_ids']=['q1']
                if change=='invented':observations[-1]['evidence_id']='made-up'
                resolution=select_unique(self.inventory,observations,None)
                self.assertFalse(conditional_definition(args,self.case,resolution))

    def test_no_loophole_for_value_matching_comparison_or_confident_target_choice(self):
        for change in ('figure','comparison','choice','no_limitation','truncated_inventory'):
            with self.subTest(change=change):
                case=deepcopy(self.case);args=deepcopy(self.args);resolution=self.resolution()
                if change=='figure':case['intake']['reported_figure']={'state':'NUMBER','value':'8765','precision':'EXACT'}
                if change=='comparison':case['intake']['compared_with']={'kind':'SOURCE_SYSTEM'}
                if change=='choice':args['selected_target']='global'
                if change=='no_limitation':args['undecided']=[]
                if change=='truncated_inventory':case['context']['candidate_inventory']['exhaustive']=False
                self.assertFalse(conditional_definition(args,case,resolution))

    def test_repaired_draft_must_still_match_observed_resolution(self):
        self.case['evidence']['check']={'tool':'check_target_candidates','result':self.resolution()}
        self.assertIsNone(candidate_resolution(self.args,self.case)['selected'])
        self.args['selected_target']='global'
        with self.assertRaisesRegex(ValueError,'TARGET_NOT_A_UNIQUE'):candidate_resolution(self.args,self.case)

    def test_exact_admitted_measure_definition_does_not_require_every_visual(self):
        self.inventory.update(exhaustive=False,total_candidates=32)
        self.case['context']['intake']=self.case['intake']
        self.case['intake']['measure']='metric'
        self.case['context']['path']={'nodes':[{'id':'metric','kind':'MEASURE','properties':{'asset_id':'native-measure'}}]}
        self.case['queries'][0]['asset_ids']=['native-measure']
        self.case['evidence']['definition']={'kind':'RETAINED_DEFINITION_REFERENCE','asset_id':'native-measure'}
        self.args['evidence_ids'].append('definition')
        self.assertTrue(conditional_definition(self.args,self.case,self.resolution()))
        self.assertFalse(self.inventory['exhaustive'])
        self.case['queries'][0]['asset_ids']=['different-measure']
        self.assertFalse(conditional_definition(self.args,self.case,self.resolution()))

    def test_only_cited_unique_value_match_can_fill_an_omitted_selected_field(self):
        figure={'state':'NUMBER','value':'8765','precision':'EXACT'}
        resolution=select_unique(self.inventory,self.observations,figure)
        self.case['evidence']['check']={'tool':'check_target_candidates','result':resolution}
        args,proof=canonical_selected_target(self.args,self.case)
        self.assertEqual(args['selected_target'],'global');self.assertEqual(proof['query_id'],'q1')
        self.assertIsNone(self.args['selected_target'])
        explicit={**self.args,'selected_target':'filtered'}
        self.assertEqual(canonical_selected_target(explicit,self.case),(explicit,None))
        self.args['evidence_ids']=['q2']
        self.assertIsNone(canonical_selected_target(self.args,self.case)[1])

    def test_checked_unresolved_handoff_does_not_claim_a_target(self):
        self.args.update(verdict='not found',verdict_class='UNRESOLVED')
        self.assertEqual(candidate_resolution(self.args,self.case)['reason'],'UNMEASURED_TARGET_EXPLICIT_HANDOFF')
        self.args['evidence_ids']=[]
        with self.assertRaisesRegex(ValueError,'CHECK_TARGET_CANDIDATES'):candidate_resolution(self.args,self.case)


class SupersededNativeAttemptTests(unittest.TestCase):
    def test_saved_export_handoff_normalizes_detail_without_upgrading_verdict(self):
        from investigator.delivery_references import reformat
        args={'verdict_class':'UNRESOLVED','verdict':'observed value',
              'undecided':['The earliest retained source version is not known.']}
        fixed,changes=reformat(args,queries=[],evidence={},layers={})
        self.assertEqual(fixed['verdict'],'not found');self.assertEqual(fixed['verdict_class'],'UNRESOLVED')
        self.assertEqual(fixed['undecided'],args['undecided']);self.assertEqual(args['verdict'],'observed value')
        self.assertEqual(changes[0]['basis'],'PRESERVE_UNRESOLVED_DISPOSITION')

    def test_exact_cited_successful_retry_does_not_promote_the_failed_attempt(self):
        from investigator.grounded_answers import cited
        failed={'id':'q1','layer':'semantic','text':'EVALUATE ROW("units",[Units])','parameters':[],
                'asset_ids':['native-measure'],'status':'ERROR','error':'timeout'}
        succeeded={**failed,'id':'q2','status':'SUCCEEDED','time':'recorded','result':{'rows':[{'units':8765}]}}
        case={'queries':[failed,succeeded],'evidence':{}}
        args={'verdict':'definition explained','evidence_ids':['q1','q2']}
        records=cited(args,case)
        self.assertNotIn('native_result',records[0]);self.assertEqual(records[0]['successful_retry_query_id'],'q2')
        self.assertEqual(records[1]['native_result'],succeeded['result'])
        for change in ('uncited','different_scope','different_query','truncated'):
            with self.subTest(change=change):
                c=deepcopy(case);a=deepcopy(args)
                if change=='uncited':a['evidence_ids']=['q1']
                if change=='different_scope':c['queries'][1]['parameters']=[17]
                if change=='different_query':c['queries'][1]['text']='EVALUATE ROW("units",[Other])'
                if change=='truncated':c['queries'][1]['result']['truncated']=True
                with self.assertRaisesRegex(ValueError,'FAILED_QUERY_DOES_NOT_SUPPORT'):cited(a,c)


class SourceComparisonTests(unittest.TestCase):
    def setUp(self):
        self.source='sql://synthetic/db/object/1'
        self.case={'intake':{'compared_with':{'kind':'SOURCE_SYSTEM'}},
                   'context':{'layers':{'source':{'objects':[{'id':self.source}]},
                                        'gold':{'objects':[{'id':'fabric://synthetic/gold'}]}},
                              'system_of_record':{'declared':False,'reachable':False}},
                   'queries':[],'evidence':{}}
        self.args={'verdict_class':'AS DESIGNED','evidence_ids':[]}

    def test_source_is_required_even_when_sor_metadata_is_incomplete(self):
        with self.assertRaisesRegex(ValueError,'SOURCE_COMPARISON_REQUIRES'):source_comparison(self.args,self.case)

    def test_gold_metadata_uncited_failed_or_wrong_object_does_not_count(self):
        for change in ('gold','metadata','uncited','failed','wrong_object','truncated','top_truncated'):
            with self.subTest(change=change):
                case=deepcopy(self.case);args=deepcopy(self.args)
                query={'id':'q','layer':'source','purpose':'compare','asset_ids':[self.source],
                       'status':'SUCCEEDED','text':'SELECT SUM(amount) AS amount FROM app.payments','result':{'rows':[{'amount':550}]}}
                if change=='gold':query.update(layer='gold',asset_ids=['fabric://synthetic/gold'])
                if change=='metadata':query['text']='SELECT name FROM sys.columns'
                if change=='failed':query['status']='ERROR'
                if change=='wrong_object':query['asset_ids']=['sql://synthetic/other/object/1']
                if change=='truncated':query['result']['truncated']=True
                if change=='top_truncated':query['truncated']=True
                case['queries']=[query];args['evidence_ids']=[] if change=='uncited' else ['q']
                with self.assertRaisesRegex(ValueError,'SOURCE_COMPARISON_REQUIRES'):source_comparison(args,case)

    def test_cited_source_data_is_accepted_not_declared_consistent(self):
        self.case['queries']=[{'id':'q','layer':'source','purpose':'compare','asset_ids':[self.source],
            'status':'SUCCEEDED','text':'SELECT SUM(amount) AS amount FROM app.payments','result':{'rows':[{'amount':550}]}}]
        self.args['evidence_ids']=['q'];source_comparison(self.args,self.case)

    def test_honest_missing_source_handoff_is_deliverable(self):
        self.args.update(verdict_class='UNRESOLVED',undecided=['Source could not be read; only the warehouse was checked.'])
        source_comparison(self.args,self.case)

    def test_saved_billing_definition_asks_are_not_source_comparisons(self):
        fixture=json.loads((Path(__file__).parent/'fixtures/r28-confirmation-shapes.json').read_text())
        for intake in fixture['billing_intakes']:
            self.case['intake']=deepcopy(intake);source_comparison(self.args,self.case)
            self.case['intake']['compared_with']={'kind':'SOURCE_SYSTEM'}
            with self.assertRaisesRegex(ValueError,'SOURCE_COMPARISON_REQUIRES'):source_comparison(self.args,self.case)


class LiteralHeadingTests(unittest.TestCase):
    def test_saved_r17_05_headings_never_need_numeric_queries(self):
        from investigator.adapters.native_literal_visual import nonmatching_literal
        fixture=json.loads((Path(__file__).parent/'fixtures/r28-confirmation-shapes.json').read_text())
        for visual in fixture['headers']:
            for figure in (None,{'state':'NUMBER','value':'8765','precision':'EXACT'}):
                proof=nonmatching_literal(visual,figure)
                self.assertIsNotNone(proof);self.assertEqual(proof['asset_id'],visual['id'])
        dynamic=deepcopy(fixture['headers'][0]);dynamic['metadata']['visual']['query']={}
        self.assertIsNone(nonmatching_literal(dynamic,None))

    def test_static_annotation_with_spelled_number_is_not_a_data_candidate(self):
        from investigator.adapters.native_literal_visual import nonmatching_literal
        asset={'id':'header','kind':'ReportVisual','metadata':{'visual':{'visualType':'textbox','objects':{'general':[{'properties':{'paragraphs':[{'textRuns':[{'value':'thirty units'}]}]}}]}}}}
        self.assertIsNotNone(nonmatching_literal(asset,None))


class GuidedSmokeColumnsTests(unittest.TestCase):
    def setUp(self):
        self.bundle={'status':'ANSWERED','verdict':'deviation','outputs':{'business':'answer','technical':'queries'},
            'case':{'queries':[{'status':'SUCCEEDED','asset_ids':[a],'layer':a,
                              'result':{'rows':[{'units':v,'row_count':360}]}}
                             for a,v in [('gold',8765),('silver',7661)]]}}
        self.expected={'verdict':'deviation','reads':{a:{'column':'units','value':v} for a,v in [('gold',8765),('silver',7661)]}}

    def test_sum_and_count_uses_declared_column(self):
        self.assertTrue(guided_demo_matches(self.bundle,self.expected))

    def test_matching_count_cannot_substitute_for_wrong_sum(self):
        self.bundle['case']['queries'][0]['result']['rows']=[{'units':0,'row_count':8765}]
        self.assertFalse(guided_demo_matches(self.bundle,self.expected))

    def test_missing_column_multiple_rows_or_undeclared_multicolumn_result_fails(self):
        for change in ('missing','many_rows','undeclared'):
            with self.subTest(change=change):
                bundle=deepcopy(self.bundle);expected=deepcopy(self.expected)
                if change=='missing':expected['reads']['gold']['column']='not_units'
                if change=='many_rows':bundle['case']['queries'][0]['result']['rows']*=2
                if change=='undeclared':expected['reads']['gold']=8765
                self.assertFalse(guided_demo_matches(bundle,expected))

    def test_single_column_legacy_contract_still_works(self):
        for query in self.bundle['case']['queries']:query['result']['rows'][0].pop('row_count')
        self.expected['reads']={'gold':8765,'silver':7661}
        self.assertTrue(guided_demo_matches(self.bundle,self.expected))


if __name__=='__main__':unittest.main()
