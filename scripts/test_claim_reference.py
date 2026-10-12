import copy, unittest
from unittest.mock import patch
import test_claim_intake as fixture
from investigator import claim_reference, visual_target, report_scope
from investigator.onboarding import Conflict


class ConfirmedClaimReferenceTests(unittest.TestCase):
    def setUp(self):
        self.h=fixture.ClaimTests();self.h.setUp();self.addCleanup(self.h.doCleanups)
        self.catalog=copy.deepcopy(fixture.CAT)
        for visual in self.catalog['models'][0]['visuals']:
            visual.update(grouping_columns=[],declared_scopes={'quantity':{'state':'COMPLETE','restrictions':[]}})
        p=patch.object(self.h.controller,'_catalog',return_value=self.catalog);p.start();self.addCleanup(p.stop)
        request=self.h.request(scope={'kind':'VISUALS','report_id':'report','page_id':'page','visual_ids':['card']})
        submitted=self.h.controller.submit(request)
        confirmed=self.h.controller.confirm({'id':submitted['id'],'revision':submitted['revision'],'request_key':'confirm','accepted':True})
        with self.h.workspace.store.connect() as db:self.body=self.h.controller._load(db,confirmed['id'])[1]

    def envelope(self):
        compiled=claim_reference.compile(self.body,self.catalog)
        return {'model_id':'model','measure_id':'quantity',**{k:compiled[k]for k in('target_visual','report_binding','reported_figure')}}

    def test_real_retained_confirmation_creates_distinct_provenance_not_fake_span(self):
        envelope=self.envelope(); proof=envelope['target_visual']['match_basis']['confirmed_claim']
        claim_reference.validate_envelope(envelope,self.h.workspace.store,self.catalog)
        self.assertEqual(proof['target_id'],'card');self.assertEqual(proof['claim_id'],self.body['id'])
        self.assertIsNone(envelope['target_visual']['source'])
        self.assertEqual(envelope['reported_figure']['value'],'950')
        self.assertEqual(envelope['report_binding']['resolution_kind'],'USER_CONFIRMED_CLAIM')
        visual_target.validate(envelope['target_visual'],ticket='not a fabricated numeral quote',
            candidates=self.catalog['models'][0]['visuals'],report_id='report',measure_id='quantity')
        report_scope.report_binding(envelope['report_binding'],reports=[{'id':'report','name':'Activity Report'}])

    def test_altered_claim_or_confirmation_never_earns_provenance(self):
        for key in('claim','confirmation'):
            body=copy.deepcopy(self.body)
            if key=='claim':body['claim']['settled']['direction']='MORE'
            else:body['confirmation']['request_hash']='0'*64
            with self.subTest(key=key),self.assertRaises(Conflict):claim_reference.compile(body,self.catalog)

    def test_model_measure_target_substitution_is_rejected_against_immutable_claim(self):
        for key in('model_id','measure_id'):
            envelope=self.envelope();envelope[key]='foreign'
            with self.subTest(key=key),self.assertRaises(Conflict):
                claim_reference.validate_envelope(envelope,self.h.workspace.store,self.catalog)
        envelope=self.envelope();envelope['target_visual']['target_id']='other'
        with self.assertRaises(Conflict):claim_reference.validate_envelope(envelope,self.h.workspace.store,self.catalog)

    def test_filtered_missing_or_partial_declared_context_is_refused(self):
        for declaration in(None,{'state':'PARTIAL','restrictions':[]},
                           {'state':'COMPLETE','restrictions':[{'field_id':'warehouse','operator':'IN','values':['North']}]}):
            catalog=copy.deepcopy(self.catalog);v=catalog['models'][0]['visuals'][0]
            v['declared_scopes']={}if declaration is None else{'quantity':declaration}
            with self.subTest(declaration=declaration),self.assertRaises(Conflict):claim_reference.compile(self.body,catalog)

    def test_grouped_or_added_unconsumed_scope_is_refused(self):
        catalog=copy.deepcopy(self.catalog);catalog['models'][0]['visuals'][0]['grouping_columns']=['warehouse']
        with self.assertRaises(Conflict):claim_reference.compile(self.body,catalog)
        for key in('field_id','dimension_id'):
            body=copy.deepcopy(self.body);body['claim']['settled']['scope'][key]='field'
            with self.subTest(key=key),self.assertRaises(Conflict):claim_reference.compile(body,self.catalog)

    def test_unknown_or_changed_immutable_revision_is_refused(self):
        envelope=self.envelope();envelope['target_visual']['match_basis']['confirmed_claim']['revision']+=1
        with self.assertRaisesRegex(Conflict,'not retained'):
            claim_reference.validate_envelope(envelope,self.h.workspace.store,self.catalog)

if __name__=='__main__':unittest.main()
