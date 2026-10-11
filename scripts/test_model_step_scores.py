import copy
import json
from pathlib import Path
import unittest
from investigator.model_step_scores import score_intake,compare


class ModelScoresTests(unittest.TestCase):
    def golden(self):return json.loads((Path(__file__).resolve().parents[1]/'acceptance/model_steps/intake.json').read_text(encoding='utf-8'))

    def test_authored_set_covers_nine_families_subjects_and_named_edge_shapes(self):
        golden=self.golden();cases=golden['cases']
        self.assertGreaterEqual(len(cases),60);self.assertEqual(len({c['id'] for c in cases}),len(cases))
        self.assertEqual(set('ABCDEFGHI'),{c['family'] for c in cases if not c['should_hold']})
        from investigator.question_kind import LEGACY_KINDS
        self.assertEqual(set(LEGACY_KINDS),{c['expected']['question_kind'] for c in cases if not c['should_hold']})
        self.assertTrue(any('\n' in c['text'] for c in cases))
        self.assertTrue(any(c['expected']['figure_state']=='EMPTY' for c in cases))
        self.assertTrue(any(c['expected']['dimension_ids'] for c in cases))
        self.assertTrue(any(c['expected']['selection_value'] for c in cases))
        self.assertTrue(all(c['hold_reason'] for c in cases if c['should_hold']))

    def test_unattempted_cases_cannot_be_scored_as_correct_or_a_complete_gate(self):
        score=score_intake(self.golden(),[],'self-test')
        self.assertEqual(score['score'],0);self.assertEqual(score['evaluated'],0)
        self.assertIsNone(score['hold_rate']);self.assertEqual(score['correct_holds'],0)
        self.assertEqual(compare(score,None,{'maximum_drop':0.02,'reason':'test threshold'})['gate'],'FAILED')

    def test_transport_hold_is_not_counted_as_correct_semantic_hold_and_retry_is_recorded(self):
        golden=self.golden();case=next(c for c in golden['cases'] if c['should_hold'])
        rows=[{'case_id':case['id'],'model_version':'self-test','intake':{'status':'HELD','resolution_attempts':[{},{}]}}]
        score=score_intake(golden,rows,'self-test')
        self.assertEqual(score['correct_holds'],0);self.assertEqual(score['hold_rate'],1);self.assertEqual(score['retry_rate'],1)
        self.assertEqual(score['score'],0)
        rows[0]['intake']['status']='NEEDS_INPUT'
        self.assertEqual(score_intake(golden,rows,'self-test')['correct_holds'],1)
        with self.assertRaisesRegex(ValueError,'Mixed model'):score_intake(golden,rows,'another-model')
        with self.assertRaisesRegex(ValueError,'duplicate'):score_intake(golden,rows+rows,'self-test')

    def test_drop_threshold_and_baseline_cannot_silently_accept_missing_cases(self):
        score={'step':'intake','model_version':'new','suite_hash':'same golden hash','cases':60,'score':0.85,'status':'COMPLETE'}
        previous={**score,'score':0.9,'model_version':'old'}
        result=compare(score,previous,{'maximum_drop':0.02,'reason':'provisional ratchet'})
        self.assertAlmostEqual(result['delta'],-0.05);self.assertEqual(result['gate'],'FAILED')
        with self.assertRaises(ValueError):compare(score,{**previous,'cases':59},{'maximum_drop':0.02,'reason':'ratchet'})
        with self.assertRaises(ValueError):compare(score,{**previous,'suite_hash':'changed goldens'},{'maximum_drop':0.02,'reason':'ratchet'})
        with self.assertRaises(ValueError):compare(score,{**previous,'status':'INCOMPLETE'},{'maximum_drop':0.02,'reason':'ratchet'})
        with self.assertRaises(ValueError):compare(score,previous,{'maximum_drop':0.02,'reason':''})

    def test_named_semantic_hold_is_scored_but_a_budget_hold_never_is(self):
        golden={'cases':[{'id':'missing-target','should_hold':True,
            'expected':{'status':'HELD','error':'TARGET_UNRESOLVED'}}]}
        row={'case_id':'missing-target','model_version':'test',
             'intake':{'status':'HELD','error':'TARGET_UNRESOLVED'}}
        self.assertEqual(score_intake(golden,[row],'test')['correct_holds'],1)
        row['intake']['error']='BUDGET_LIMIT'
        result=score_intake(golden,[row],'test')
        self.assertEqual(result['correct_holds'],0);self.assertEqual(result['score'],0)

    def test_all_thirteen_misses_are_sealed_source_cases_with_explicit_records(self):
        import hashlib
        root=Path(__file__).resolve().parents[1]
        golden=json.loads((root/'acceptance/model_steps/intake-round-ten-misses.json').read_text())
        self.assertEqual(golden['step'],'intake')
        self.assertEqual(len(golden['cases']),13)
        self.assertEqual(len({c['id'] for c in golden['cases']}),13)
        fields={'status','error','target_id','cell_mode','action','model_id','measure_id','ticket_shape',
            'comparison_mode','question_kind','dimension_ids','filters','figure_state','figure_value','figure_precision','selection_value'}
        for case in golden['cases']:
            self.assertEqual(set(case['expected']),fields)
            source=root/case['source']['ticket_file']
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),case['source']['ticket_file_sha256'])
            self.assertEqual(json.loads(source.read_text())['ticket_text'],case['text'])



if __name__=='__main__':unittest.main()
