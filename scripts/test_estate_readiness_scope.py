import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import Mock,patch
from investigator.estate_readiness import (PINS,discovery,scope_closure,
    assess_named_scope,score_named_scope,sha)

def dependency():
    return {'status':'COMPLETE','discovered_declarations':[
        {'id':'one','content_hash':'h1','form':'reference','operation':'REFERENCE'},
        {'id':'two','content_hash':'h2','form':'source','operation':'DIRECT_REFERENCE'}],
        'declarations':[{'id':'one','content_hash':'h1','disposition':'RESOLVED','dependencies':['b']},
                        {'id':'two','content_hash':'h2','disposition':'DIRECT','dependencies':[]}],
        'nodes':[{'asset_id':'a','declarations':['one']},{'asset_id':'b','declarations':['two']}]}

class ScopedReadinessTests(unittest.TestCase):
    def setUp(self):
        self.pins={k:'pin-'+k for k in PINS}
        self.manifest={'layers':[{'id':'one','asset_id':'a'},{'id':'two','asset_id':'b'},
                                 {'id':'other','asset_id':'c'}],
            'resources':[{'id':'optional','asset_id':'d'}],
            'lineage':{'bindings':[{'from_layer':'two','to_layer':'one'},
                                   {'from_layer':'other','to_layer':'other'}]}}

    def test_complete_closure_includes_dependency_not_just_root(self):
        self.assertEqual(scope_closure(dependency(),['a']),{'a','b'})

    def test_omitted_declaration_and_unassigned_declaration_are_defects(self):
        d=dependency();d['declarations'].pop()
        with self.assertRaisesRegex(ValueError,'CONSERVATION'):scope_closure(d,['a'])
        d=dependency();d['nodes'][0]['declarations']=[]
        with self.assertRaisesRegex(ValueError,'CONSERVATION'):scope_closure(d,['a'])

    def test_unknown_form_disposition_blocks_loudly(self):
        d=dependency();d['discovered_declarations'][0]['form']='unfamiliar-selection'
        d['declarations'][0]['disposition']='UNSUPPORTED'
        with self.assertRaisesRegex(ValueError,'UNSUPPORTED:unfamiliar-selection'):scope_closure(d,['a'])

    def test_missing_reference_node_is_not_a_direct_source(self):
        d=dependency();d['declarations'][0]['dependencies']=['unknown']
        with self.assertRaisesRegex(ValueError,'UNESTABLISHED:unknown'):scope_closure(d,['a'])

    def test_direct_requires_positive_declaration(self):
        d=dependency();d['declarations'][0].update(disposition='DIRECT',dependencies=[])
        with self.assertRaisesRegex(ValueError,'DIRECT_SOURCE'):scope_closure(d,['a'])

    def test_partial_inventory_never_becomes_complete_because_no_warnings(self):
        d=dependency();d.update(status='PARTIAL',warnings=[])
        with self.assertRaisesRegex(ValueError,'INCOMPLETE'):scope_closure(d,['a'])

    def test_missing_hashes_cannot_compare_equal(self):
        d=dependency();d['declarations'][0].pop('content_hash');d['discovered_declarations'][0].pop('content_hash')
        with self.assertRaisesRegex(ValueError,'HASH_REQUIRED'):scope_closure(d,['a'])

    def test_declaration_cannot_be_assigned_to_a_different_owner(self):
        d=dependency();d['discovered_declarations'][0]['owner']='b'
        with self.assertRaisesRegex(ValueError,'OWNER_DIFFERS'):scope_closure(d,['a'])

    def test_scoped_coverage_does_not_promote_global_partial(self):
        m={'layers':[{'asset_id':'a'}],'resources':[]}
        r={'pins':self.pins,'scan':{'status':'PARTIAL','coverage':{
            'a-schema':{'status':'COMPLETE'},'unrelated':{'status':'UNSUPPORTED'}},
            'assets':[{'id':'a','availability':'CURRENT','content_hash':'definition',
                       'coverage_scope':'a-schema'}]}}
        discovery(r,m,self.pins,scope_assets={'a'})
        self.assertEqual(r['scan']['status'],'PARTIAL')
        with self.assertRaisesRegex(ValueError,'NOT_COMPLETE'):discovery(r,m,self.pins)
        r['scan']['coverage']['a-schema']['status']='UNSUPPORTED'
        with self.assertRaisesRegex(ValueError,'COVERAGE_INCOMPLETE'):discovery(r,m,self.pins,scope_assets={'a'})

    def receipt(self,folder):
        original={'scope':{'name':'chain','roots':['a'],'assets':['a','b']},
                  'dependency_inventory':dependency()}
        source=Path(folder)/'original.json';source.write_text(json.dumps(original))
        receipt=dict(original,pins=self.pins,sources=[{'path':str(source),
            'sha256':sha(source.read_bytes()),'field':k,'pointer':'/'+k}for k in original])
        path=Path(folder)/'scope.json';path.write_text(json.dumps(receipt))
        return {'path':str(path),'sha256':sha(path.read_bytes())}

    def test_scope_filters_only_proven_closure_without_editing_manifest(self):
        with tempfile.TemporaryDirectory()as folder:
            ref=self.receipt(folder);original=copy.deepcopy(self.manifest)
            with patch('investigator.estate_readiness.assess',return_value={'status':'READY','scoring':'ADMITTED'})as check:
                result=assess_named_scope(self.manifest,self.pins,{},ref)
            self.assertEqual(result['scope']['assets'],['a','b'])
            self.assertEqual(result['estate_status'],'NOT_ESTABLISHED_BY_SCOPED_ASSESSMENT')
            self.assertEqual(self.manifest,original)
            self.assertEqual([l['id']for l in check.call_args.args[0]['layers']],['one','two'])
            self.assertEqual(check.call_args.kwargs['_approved_manifest'],original)
            self.assertEqual(check.call_args.args[0]['lineage']['bindings'],
                             [{'from_layer':'two','to_layer':'one'}])

    def test_missing_stage_proofs_blocks_even_complete_scope_inventory(self):
        with tempfile.TemporaryDirectory()as folder:
            result=assess_named_scope(self.manifest,self.pins,None,self.receipt(folder))
            self.assertEqual(result['status'],'BLOCKED')

    def test_scoring_cannot_escape_named_scope_or_accept_ready_label(self):
        with tempfile.TemporaryDirectory()as folder:
            readiness={'manifest':self.manifest,'pins':self.pins,'index':{},'scope_ref':self.receipt(folder)}
            score=Mock(return_value={'passed':True})
            with patch('investigator.estate_readiness.assess',return_value={'status':'READY','scoring':'ADMITTED'}):
                refused=score_named_scope(score,readiness=readiness,requested_assets=['c'])
                self.assertEqual(refused['scope_reason'],'REQUEST_OUTSIDE_VERIFIED_SCOPE');score.assert_not_called()
                self.assertTrue(score_named_scope(score,readiness=readiness,requested_assets=['a'])['passed'])

    def test_ready_label_without_evidence_cannot_invoke_scorer(self):
        scorer=Mock()
        r=score_named_scope(scorer,readiness={'status':'READY'},requested_assets=['a'])
        self.assertEqual(r['scoring'],'NOT_SCORED');scorer.assert_not_called()

if __name__=='__main__':unittest.main()
