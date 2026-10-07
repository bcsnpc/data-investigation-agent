import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import check_model_scores as gate


class ModelScoreGateTests(unittest.TestCase):
    def test_rejected_translation_is_a_scored_failure_not_a_crash_or_cached_success(self):
        from investigator.translation_eval import request,score
        root=Path(__file__).resolve().parents[1]
        golden=json.loads((root/'acceptance/model_steps/translation.json').read_text())
        case=golden['cases'][0];r=request(case)
        proposal={k:r[k] for k in ('kind','definition_hash','target_engine','grouping','evaluation_timestamp')}
        proposal.update(objects=[{'id':'outside','kind':'TABLE'}],expression='1=1')
        original={'case_id':case['id'],'model_version':'injected','proposal':proposal,
                  'evaluation':{'verification':{'status':'VERIFIED'}}}
        scored=gate.translation_records(golden,[original])
        self.assertIsNone(scored[0]['evaluation'])
        self.assertEqual(original['evaluation']['verification']['status'],'VERIFIED')
        result=score(golden,scored,'injected')
        self.assertEqual(result['score'],0);self.assertEqual(result['validation_failures'],1)

    def test_four_recorded_steps_score_but_missing_human_grades_do_not_pass(self):
        root=Path(__file__).resolve().parents[1]
        config=json.loads((root/'acceptance/model_steps/config.json').read_text())
        review=json.loads((root/config['human_reviews']).read_text())
        for item in review['items']:
            item['grader']=None
            item['human_flags']={key:None for key in item['human_flags']}
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'ungraded.json';path.write_text(json.dumps(review))
            config['human_reviews']=str(path)
            result=gate.evaluate(root,config)
        self.assertEqual([r['step'] for r in result['steps']],['intake','reader','synthesis','translation'])
        self.assertTrue(all(r['gate']=='PASSED' for r in result['steps'][:-1]))
        self.assertEqual(result['steps'][-1]['gate'],'FAILED')
        self.assertEqual(result['steps'][-1]['score'],0)
        self.assertEqual(result['gate'],'FAILED');self.assertIsNone(result['human_readability'])
        self.assertEqual(result['provider_calls'],0);self.assertEqual(result['estate_physical_requests'],0)

    def test_existing_results_cannot_invent_human_grades(self):
        from investigator.synthesis_scores import score_human
        with self.assertRaises(ValueError):score_human([{'case_id':str(i),'grader':'','human_flags':{}} for i in range(10)])

    def test_a_different_paragraph_cannot_receive_a_grade_for_the_sealed_one(self):
        root=Path(__file__).resolve().parents[1]
        config=json.loads((root/'acceptance/model_steps/config.json').read_text())
        review=json.loads((root/config['human_reviews']).read_text())
        review['items'][0]['text']='Changed mechanism paragraph.'
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'changed.json';path.write_text(json.dumps(review))
            config['human_reviews']=str(path)
            result=gate.evaluate(root,config)
        self.assertEqual(result['gate'],'FAILED')
        self.assertEqual(result['human_review_error'],'Human review paragraph or provenance differs from sealed response')


if __name__=='__main__':unittest.main()
