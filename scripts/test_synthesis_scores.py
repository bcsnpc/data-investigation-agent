import copy,json
from pathlib import Path
import unittest
from investigator.synthesis_scores import score_attempt,score,review_item,score_human,READABILITY_FIELDS


class SynthesisScoresTests(unittest.TestCase):
    def attempt(self):
        return {'payload':{'evidence':[],'layer_tokens':{},'boundaries':[]},'response':{'technical_output':{'text':'The declared join expands the matched movements.'}},
                'schema':{'type':'object','required':['technical_output']},'provider_event_sha256':'a'*64}

    def test_token_and_composition_failures_are_not_a_quality_pass(self):
        a=self.attempt();self.assertFalse(score_attempt(a)['rejected_under_current_rules'])
        a['response']['technical_output']['text']='L0 (SERVING) repeats movements.'
        self.assertFalse(score_attempt(a)['token_valid'])
        a['payload']['layer_tokens']={'L0 (SERVING)':'layer'}
        self.assertTrue(score_attempt(a)['token_valid'])
        a['response']['technical_output']['text']='The declared join expands the'
        self.assertTrue(score_attempt(a)['rejected_under_current_rules'])
        a['response']['technical_output']['text']='The join applies, but matching snapshots are unconfirmed.'
        self.assertTrue(score_attempt(a)['rejected_under_current_rules'])

    def test_missing_mechanism_does_not_become_an_invented_readability_item(self):
        r={'case_id':'refusal','model_version':'recorded','attempts':[]}
        s=score([r],'recorded');self.assertIsNone(s['score']);self.assertEqual(s['no_model_mechanism_cases'],['refusal'])
        with self.assertRaises(ValueError):review_item(r)

    def test_retry_responses_are_counted_and_versions_are_separate(self):
        good=self.attempt();bad=copy.deepcopy(good);bad['response']={}
        s=score([{'case_id':'a','model_version':'old','attempts':[bad,good]},
                 {'case_id':'b','model_version':'new','attempts':[good]}],'old')
        self.assertEqual(s['attempts'],2);self.assertEqual(s['score'],0.5)

    def test_ungraded_flags_are_not_human_scores(self):
        rows=[review_item({'case_id':str(i),'model_version':'old','attempts':[self.attempt()]}) for i in range(10)]
        with self.assertRaises(ValueError):score_human(rows)
        for r in rows:r.update(grader='test human',human_flags={f:True for f in READABILITY_FIELDS})
        self.assertEqual(score_human(rows)['score'],1)
        rows[0]['human_flags']['one_mechanism']=None
        with self.assertRaises(ValueError):score_human(rows)

    def test_all_fifteen_preserved_cases_keep_the_no_call_case_and_rejection(self):
        source=json.loads((Path(__file__).resolve().parents[1]/'acceptance/model_steps/synthesis-recorded.json').read_text())
        self.assertEqual(len(source['records']),15)
        none=score(source['records'],'NO_MODEL_CALL')
        self.assertEqual(none['no_model_mechanism_cases'],['family-C']);self.assertIsNone(none['score'])
        model=score(source['records'],'investigator-quality-54')
        self.assertEqual(model['attempts'],14)
        bad=[r['case_id'] for r in source['records'] for a in r['attempts'] if score_attempt(a)['rejected_under_current_rules']]
        self.assertEqual(bad,['family-A','family-D','family-E','family-G','family-H','family-I','source-consistent','source-latency'])
        self.assertEqual(model['score'],6/14)
        for case in ('family-A','family-E','family-G','family-I'):
            attempt=next(r for r in source['records'] if r['case_id']==case)['attempts'][-1]
            self.assertIn('HEDGE_TWICE',score_attempt(attempt)['errors'])
        attempt=next(r for r in source['records'] if r['case_id']=='source-consistent')['attempts'][-1]
        self.assertIn('LAYER_TOKENS',score_attempt(attempt)['errors'])
        self.assertNotIn('HEDGE_TWICE',score_attempt(attempt)['errors'])


if __name__=='__main__':unittest.main()
