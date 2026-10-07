import copy,json,unittest
from pathlib import Path
from investigator.model_step_scores import score_reader
from investigator.lineage_binding import validate
from investigator.code_sources import normalize
from investigator.transformation_reader import static
from investigator.code_static import Unsupported


class ReaderScoresTests(unittest.TestCase):
    def golden(self):return json.loads((Path(__file__).resolve().parents[1]/'acceptance/model_steps/reader.json').read_text())

    def test_six_new_dynamic_and_udf_cases_distinguish_static_controls_from_fallback(self):
        cases=[c for c in self.golden()['cases'] if c['origin']=='ROUND_NINE_AUTHORED']
        self.assertEqual(len(cases),6)
        for c in cases:
            params=dict(unit=normalize('unit.py',c['code'].encode()),schemas=c['schemas'],boundary={'from_layer':'input','to_layer':'output'},item='code-item',target_table='output-table')
            if c['id'] in ('dynamic-concatenation','dynamic-dictionary'):
                self.assertEqual(static(**params)['proposals'],c['expected_bindings'])
            else:
                with self.subTest(case=c['id']),self.assertRaises((Unsupported,TypeError,KeyError)):static(**params)
            for binding in c['expected_bindings']:validate(binding)

    def test_missing_and_invalid_proposals_cannot_get_precision_credit(self):
        g=self.golden();self.assertEqual(score_reader(g,[],'test')['score'],0)
        c=next(c for c in g['cases'] if c['expected_bindings']);good=copy.deepcopy(c['expected_bindings'][0]);good.update(extractor='MODEL',confidence=0.5)
        rows=[{'case_id':c['id'],'model_version':'test','proposals':[good,{},good]}]
        result=score_reader(g,rows,'test')
        self.assertAlmostEqual(result['precision'],1/3);self.assertEqual(result['status'],'INCOMPLETE')
        self.assertFalse(result['verification_performed'])

    def test_transport_failure_is_not_a_correct_semantic_refusal(self):
        g=self.golden();c=next(c for c in g['cases'] if c['should_refuse'])
        row={'case_id':c['id'],'model_version':'test','proposals':[],'semantic_refusal':False}
        self.assertEqual(score_reader(g,[row],'test')['correct_semantic_refusals'],0)
        row['semantic_refusal']=True
        self.assertEqual(score_reader(g,[row],'test')['correct_semantic_refusals'],1)


if __name__=='__main__':unittest.main()
