import copy,json,unittest
from investigator.code_sources import normalize
from investigator.transformation_reader import propose
from test_lineage_binding import proposal

class ReaderTests(unittest.TestCase):
    def params(self,code):
        unit=normalize('unit.py',code.encode())
        return dict(unit=unit,schemas={'input':{'amount':'int'}},boundary={'from_layer':'input','to_layer':'output'},
                    item='code-item',target_table='output-table',layers=[{'id':'input'},{'id':'output'}])
    def test_static_proposal_is_consumer_valid_and_other_writes_are_not_mislabelled(self):
        p=self.params("a=spark.table('input')\na.write.format('delta').mode('overwrite').save('output-table')\na.write.format('delta').mode('overwrite').save('another-target')\n")
        result=propose(**p)
        self.assertEqual(len(result['proposals']),1);self.assertEqual(result['proposals'][0]['target']['table'],'output-table')
        self.assertEqual(result['other_writes'][0]['table'],'another-target')
        self.assertEqual(result['proposals'][0]['location']['line_start'],2)
    def test_dynamic_name_handoff_reads_only_code_and_layers(self):
        p=self.params("a=spark.table(dynamic_name())\na.write.format('delta').mode('overwrite').save('output-table')\n")
        calls=[]
        def model(payload,schema):
            calls.append(payload);self.assertEqual(set(payload),{'code','layers'})
            self.assertEqual(schema['properties']['extractor'],{'type':'string','const':'MODEL'})
            self.assertIn('confidence',schema['required'])
            candidate=proposal();candidate['extractor']='MODEL';candidate['confidence']=0.5
            candidate['sources'][0]['table']='input';candidate['expression']['relation']['table']='input'
            candidate['location']['content_hash']=p['unit']['content_hash']
            return [candidate]
        result=propose(**p,model=model)
        self.assertEqual(len(calls),1);self.assertEqual(result['proposals'][0]['extractor'],'MODEL')
    def test_model_cannot_self_verify_or_redirect_to_unrelated_target(self):
        p=self.params("a=spark.table(dynamic_name())\na.write.format('delta').mode('overwrite').save('output-table')\n")
        def candidate():
            c=proposal();c['extractor']='MODEL';c['confidence']=0.5;c['location']['content_hash']=p['unit']['content_hash'];return c
        c=candidate();c['status']='VERIFIED'
        with self.assertRaises(ValueError):propose(**p,model=lambda *_:[c])
        c=candidate();c['target']['table']='another-target'
        with self.assertRaisesRegex(ValueError,'outside declared boundary'):propose(**p,model=lambda *_:[c])
    def test_multicell_notebook_retains_write_cell_local_address(self):
        document={'nbformat':4,'metadata':{'language_info':{'name':'python'}},'cells':[
            {'cell_type':'code','source':["a=spark.table('input')\n"]},
            {'cell_type':'markdown','source':['not code']},
            {'cell_type':'code','source':["a.write.format('delta').mode('overwrite').save('output-table')\n"]}]}
        p=self.params('');p['unit']=normalize('unit.ipynb',json.dumps(document).encode())
        location=propose(**p)['proposals'][0]['location']
        self.assertEqual((location['cell'],location['line_start'],location['line_end']),('2',1,1))
    def test_model_location_outside_retained_code_refuses(self):
        p=self.params("a=spark.table(dynamic_name())\n")
        c=proposal();c.update(extractor='MODEL',confidence=0.5)
        c['sources'][0]['table']='input';c['expression']['relation']['table']='input'
        c['location'].update(content_hash=p['unit']['content_hash'],line_end=100)
        with self.assertRaisesRegex(ValueError,'outside retained code cell'):propose(**p,model=lambda *_:[c])

if __name__=='__main__':unittest.main()
