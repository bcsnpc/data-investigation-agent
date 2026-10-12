import copy,json,unittest
from unittest.mock import patch
import test_page_investigations as fixture
from investigator.metric_visual_checks import MetricVisualChecks,record,load
from investigator.onboarding import digest,encoded,Conflict
from investigator.claim_candidate_checks import match
from investigator.candidate_read_budget import scope,consume
from investigator.form_candidates import NotMeasurable

class MetricChecks(fixture.Tests):
    def setUp(self):
        super().setUp();self.metric()
    def metric(self):
        self.body.update(id='metric-claim',revision=2)
        self.body['claim']['settled']['scope']['kind']='METRIC'
        self.body['claim']['selected_binding']['target_ids']=[v['target_id']for v in self.catalog['models'][0]['visuals']]
        self.body['engine_admission']['claim_hash']=digest(self.body['claim'])
    def test_equal_selects_native_bound_representative(self):
        checks=MetricVisualChecks(self.workspace).run(self.body,self.adapter)
        self.assertIn('metric_selection',checks,checks)
        chosen=load(self.f.store,self.body,self.catalog,self.f.config)
        self.assertEqual(chosen['target_id'],min(chosen['candidate_ids']))
    def test_forged_agreement_recomputed_from_native_values(self):
        self.values=iter([3,5]);checks=self.service.consistency(self.body,self.adapter)
        checks['comparisons'][0].update(outcome='OBSERVED_AGREEMENT',right_value='3')
        record(self.f.store,self.body,self.service.prepare(self.body),checks)
        with self.assertRaisesRegex(Conflict,'comparison differs'):load(self.f.store,self.body,self.catalog,self.f.config)
    def test_forged_scope_hash_recompiled(self):
        MetricVisualChecks(self.workspace).run(self.body,self.adapter)
        with self.f.store.connect()as db:
            value=json.loads(db.execute('SELECT body FROM claim_metric_selections').fetchone()[0])
            value['plan']['candidates'][0]['comparison_scope_hash']='forged'
            db.execute('UPDATE claim_metric_selections SET body=?,hash=?',(encoded(value),digest(value)))
        with self.assertRaisesRegex(Conflict,'plan differs'):load(self.f.store,self.body,self.catalog,self.f.config)
    def test_equal_values_different_filters_not_comparable(self):
        self.f.modify(self.second,lambda doc:doc.update(filterConfig=fixture.fixture.filter_config(fixture.fixture.native_filter(('West',)))))
        self.sync();self.metric();checks=MetricVisualChecks(self.workspace).run(self.body,self.adapter)
        self.assertEqual(checks['reason'],'METRIC_CONTEXT_NOT_COMPARABLE');self.assertNotIn('metric_selection',checks)
    def test_read_failure_not_capability_reason(self):
        bad={'status':'PARTIAL','coverage':{'dispositions':[{'disposition':'UNAVAILABLE'}]},'comparisons':[]}
        with patch.object(self.service.__class__,'consistency',return_value=bad):result=MetricVisualChecks(self.workspace).run(self.body,self.adapter)
        self.assertEqual(result['reason'],'METRIC_CANDIDATE_READ_UNAVAILABLE')

class Matching(unittest.TestCase):
    def body(self,phrase=None):
        from investigator.reported_figure import from_candidates
        figure=from_candidates([{'start':0,'end':3,'quote':'950'}],'950')
        return {'claim':{'settled':{'metric':[]}},'planning_request':{'reported_observations':[{'value':{'role':'OBSERVED','figure':figure,**({'metric_phrase':phrase}if phrase else{})}}]}}
    def rows(self):
        return [{'status':'OBSERVED','group':{'model_id':'m','measure_id':name},'candidate':{'measure_name':name,'label':name,'target_id':name},'observation':{'value':value,'id':name}}for name,value in [('MRR','600'),('Invoice','950')]]
    def test_label_mismatch_never_rebinds(self):
        matches,bindings=match(self.body('MRR'),self.rows());self.assertEqual(bindings,[]);self.assertEqual(matches[0]['status'],'NO_MATCH')
    def test_unique_value_and_tie(self):
        self.assertEqual(match(self.body(),self.rows())[1][0]['measure_id'],'Invoice')
        rows=self.rows();rows[0]['observation']['value']='950';self.assertEqual(match(self.body(),rows)[1],[])
    def test_interleaved_claim_budgets(self):
        with scope('A',10,12)as a:
            self.assertEqual(consume(None),('A',10))
            with scope('B',0,12)as b:self.assertEqual(consume(None),('B',0));self.assertEqual(b['used'],1)
            self.assertEqual(consume(None),('A',11));self.assertEqual(a['used'],12)
            with self.assertRaises(NotMeasurable):consume(None)
    def test_plural_exact_source_spans_match_without_permutation(self):
        from investigator.claim_facts import observation
        text='950, 550 and 600';source={'start':0,'end':len(text),'quote':text}
        parent={'value':observation(source,text,'OBSERVED',None),'source':{'document_id':'doc'}}
        body={'claim':{'settled':{'metric':[]}},'documents':[{'hash':'doc','request':{'text':text}}],
              'planning_request':{'reported_observations':[parent]}}
        rows=self.rows()+[{'status':'OBSERVED','group':{'measure_id':'Cost'},'candidate':{'measure_name':'Cost','label':'Cost','target_id':'Cost'},'observation':{'value':'550','id':'Cost'}}]
        matches,bindings=match(body,rows)
        self.assertEqual(len(bindings),3);self.assertTrue(all(m['source_observation']['parent_observation']==parent for m in matches))
        parent['value']['statement']['quote']='about '+text
        self.assertEqual(match(body,rows)[1],[])
    def test_hostile_complete_disposition_refuses_even_rehashed(self):
        from investigator.claim_candidate_checks import accept,VERSION
        from types import SimpleNamespace
        body={'id':'x','planning_request':{},'claim':{}};catalog={}
        planned=[{'group':{},'target_id':'v','status':'PLANNED','candidate':{}}]
        result={'version':VERSION,'claim_id':'x','request_hash':digest({}),'catalog_hash':digest(catalog),
            'rows':[dict(planned[0],status='UNAVAILABLE')],'status':'COMPLETE','diagnostic_reads':0}
        result['hash']=digest(result)
        with patch('investigator.claim_candidate_checks.inventory',return_value=planned):
            with self.assertRaisesRegex(Conflict,'completion'):
                accept(result,body,catalog,None,workspace=SimpleNamespace(dynamic_read_limit=12))

if __name__=='__main__':unittest.main()
