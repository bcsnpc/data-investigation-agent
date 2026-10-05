import copy,unittest
import test_lineage_binding as fixture
from investigator.lineage_runtime import qualify

class QualificationTests(unittest.TestCase):
    def setup_path(self):
        v,_=fixture.BindingTests().verification()
        self.v=v
        self.estate={'layers':[{'id':'input','asset_id':'input-asset'},{'id':'output','asset_id':'output-asset'}],
            'lineage':{'inference':{'enabled':True},'code_locations':[{'from_layer':'input','to_layer':'output',
                'may_infer_from_code':True,'locations':[{'source':'code-source','path':'unit.py'}]}]}}
        self.path={'layers':[{'id':'presentation'}, {'id':'output-asset','source_column':'amount'},
            {'id':'input-asset','source_column':'amount','compiled':{'query':'original input quantity'},
                'binding':{'provenance':'DECLARED_BY_DEFINITION'}}], 'evidence':{'id':'path'}}
        return dict(estate=self.estate,declared=[],inferred=[v],
            current_hashes={('code-item','unit.py'):'a'*64},
            addresses={'output-asset':'output-table','input-asset':'input-table'},
            context=v['context'],cell=v['cell'],precision=v['precision'])

    def test_verified_binding_qualifies_without_substituting_transformed_source_expression(self):
        args=self.setup_path();original=copy.deepcopy(self.path)
        result=qualify(self.path,**args)
        self.assertEqual(len(result['layers']),3)
        lower=result['layers'][-1]
        self.assertEqual(lower['binding']['provenance'],'INFERRED_FROM_CODE')
        self.assertEqual(lower['compiled'],{'query':'original input quantity'})
        self.assertEqual(self.path,original)

    def test_legacy_static_candidate_cannot_bypass_missing_verified_binding(self):
        args=self.setup_path();args['inferred']=[]
        result=qualify(self.path,**args)
        self.assertEqual(len(result['layers']),2)
        self.assertEqual(result['stopped_by'],'NO_LINEAGE')
        self.assertIn('Neither a declared',result['unresolved_boundary']['reason'])

    def test_changed_code_and_changed_scope_remain_unbound(self):
        for change in ('hash','cell'):
            args=self.setup_path()
            if change=='hash':args['current_hashes'][('code-item','unit.py')]='b'*64
            else:args['cell']={'id':'different-cell'}
            result=qualify(self.path,**args)
            self.assertEqual(len(result['layers']),2)

    def test_producer_verified_label_cannot_replace_original_comparison_evidence(self):
        args=self.setup_path();args['inferred'][0]['observations'][1]['quantity']['value']='8'
        with self.assertRaisesRegex(ValueError,'recomputed falsified'):
            qualify(self.path,**args)

    def test_exact_locations_and_code_declaration_are_required(self):
        for change in ('object','code'):
            args=self.setup_path()
            if change=='object':args['addresses']['input-asset']='some-other-table'
            else:args['estate']['lineage']['code_locations'][0]['locations'][0]['path']='different.py'
            result=qualify(self.path,**args)
            self.assertEqual(len(result['layers']),2)

class EngineGateTests(unittest.TestCase):
    def test_hostile_adapter_cannot_walk_on_an_inferred_label_without_fresh_proof(self):
        from investigator.process_debugging import vertical
        from test_process_debugging import Adapter
        helper=QualificationTests();args=helper.setup_path()
        estate=copy.deepcopy(helper.estate)
        estate['layers'].insert(0,{'id':'presentation','asset_id':'presentation','reachable':True})
        for l in estate['layers']:l['reachable']=True
        estate.update(resources=[],accepted_limits=[])
        estate['lineage']['inference']['code_resources']=[]
        for bad in ('missing','stale','forged'):
            adapter=Adapter(['presentation','output-asset','input-asset'],
                            {'presentation':7,'output-asset':7,'input-asset':7})
            estate['capability_ceiling']=sorted(adapter.capabilities())
            adapter.config={'_estate':estate}
            path=qualify(helper.path,**args)
            path['evidence']['code_source_receipts']=[{'source':'code-source','path':'unit.py','content_hash':'a'*64}]
            binding=path['layers'][-1]['binding']
            if bad=='missing':binding.pop('lineage_verification')
            elif bad=='stale':path['evidence']['code_source_receipts'][0]['content_hash']='b'*64
            else:binding['lineage_verification']['observations'][1]['quantity']['value']='8'
            adapter.resolve_path=lambda measure:path
            if bad=='forged':
                with self.assertRaisesRegex(ValueError,'recomputed falsified'):vertical(adapter,'measure',{})
            else:vertical(adapter,'measure',{})
            self.assertNotIn('input-asset',adapter.evaluated)

if __name__=='__main__':unittest.main()
