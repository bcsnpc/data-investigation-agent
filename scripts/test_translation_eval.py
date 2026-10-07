import copy,json,unittest
from pathlib import Path
from investigator.translation_eval import request,verify,score
from investigator.model_step_scores import compare


class TranslationEvalTests(unittest.TestCase):
    def setUp(self):self.g=json.loads((Path(__file__).resolve().parents[1]/'acceptance/model_steps/translation.json').read_text())
    def proposal(self,case,expression):
        r=request(case)
        return {**{k:copy.deepcopy(r[k]) for k in ('kind','definition_hash','target_engine','grouping','evaluation_timestamp')},
                'objects':[{'id':'items','kind':'TABLE'}],'expression':expression}
    def test_first_proposals_verify_and_deliberate_wrong_ones_falsify(self):
        expressions=[('k in (select k from items order by v desc,k asc limit 2)','k in (1,2)'),
                     ("day >= '2026-10-01' and day <= '2026-10-06'","day >= '2026-10-02'"),('sum(v)','sum(v)+1')]
        records=[]
        for c,(good,bad) in zip(self.g['cases'],expressions):
            r=verify(c,self.proposal(c,good))
            self.assertEqual(r['verification']['status'],'VERIFIED');self.assertEqual(r['estate_physical_requests'],0)
            self.assertEqual(r['verification_probe_count'],6 if c['kind']=='MEASURE' else 2)
            self.assertEqual(verify(c,self.proposal(c,bad))['verification']['status'],'FALSIFIED')
            records.append({'case_id':c['id'],'model_version':'injected','evaluation':r})
        self.assertEqual(score(self.g,records,'injected')['score'],1)
    def test_model_input_has_no_rows_native_statement_or_expected_answer(self):
        for c in self.g['cases']:
            r=request(c);self.assertNotIn('native_sql',r);self.assertNotIn('rows',r);self.assertNotIn('expected',r)
    def test_declared_table_qualified_expression_survives_explicit_fixture_binding(self):
        c=self.g['cases'][2]
        result=verify(c,self.proposal(c,'SUM(items.v)'))
        self.assertEqual(result['verification']['status'],'VERIFIED')
        self.assertEqual(len(result['verification']['cells']),3)
        self.assertEqual(result['verification_probe_count'],6)
        full=verify(c,self.proposal(c,'SELECT SUM(items.v) AS quantity FROM items'))
        self.assertEqual(full['verification']['status'],'VERIFIED')
        extra=verify(c,self.proposal(c,'SELECT SUM(items.v), COUNT(*) FROM items'))
        self.assertEqual(extra['verification']['status'],'UNVERIFIED')
    def test_unknown_object_and_mutating_query_refuse(self):
        c=self.g['cases'][0];p=self.proposal(c,'1=1');p['objects'][0]['id']='outside'
        with self.assertRaises(ValueError):verify(c,p)
        self.assertEqual(verify(c,self.proposal(c,'1=1; delete from items'))['verification']['status'],'UNVERIFIED')
    def test_missing_and_provider_failed_cases_cannot_pass_gate(self):
        s=score(self.g,[],'model')
        self.assertEqual(compare(s,None,{'maximum_drop':0.02,'reason':'ratchet'})['gate'],'FAILED')
        rows=[{'case_id':c['id'],'model_version':'model','provider_error':{'error_type':'BadRequestError'}} for c in self.g['cases']]
        self.assertEqual(compare(score(self.g,rows,'model'),None,{'maximum_drop':0.02,'reason':'ratchet'})['gate'],'FAILED')


if __name__=='__main__':unittest.main()
