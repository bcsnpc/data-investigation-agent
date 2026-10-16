import base64,copy,json,tempfile,unittest
from pathlib import Path
from investigator.estate_readiness import retained_execution_publication,recompile_retained_proposal,sha,validate_scope_constraints,required_code_binding_identities,assess,PINS,STAGES,VERSION
from unittest.mock import patch
from investigator.transformation_reader import static

class RetainedReadinessTests(unittest.TestCase):
    def test_scoped_native_routes_compile_with_approved_full_runtime_manifest(self):
        from investigator.estate_readiness import proposals,verification
        boundary={'from_layer':'low','to_layer':'high'}
        scoped={'lineage':{'bindings':[boundary]}}
        full=dict(scoped,system_of_record='application',layers=[{'id':'low'},{'id':'high'},{'id':'application'}])
        pins={k:'pin'for k in PINS}
        receipt={'pins':pins,'scan':{},'declared_routes':[{}],'proposals':[],'verifications':[],'model_contexts':{}}
        def check(route,*,manifest,scan):
            self.assertEqual(manifest,full)
            return {'boundary':boundary,'route_identity':'native-route'}
        with patch('investigator.adapters.readiness_registry.declared_route_validator',return_value=check):
            proposals(receipt,scoped,pins,runtime_manifest=full)
            verification(receipt,scoped,pins,runtime_manifest=full)

    def test_omitted_auxiliary_writer_is_blocked_even_when_boundary_is_covered(self):
        with tempfile.TemporaryDirectory()as folder:
            p=Path(folder)/'unit.py';text="a=spark.read.format('delta').load('stock-source')\na.write.format('delta').mode('overwrite').save('stock-target')\nb=spark.read.format('delta').load('rates-source')\nb.write.format('delta').mode('overwrite').save('rates-target')\n";p.write_text(text)
            unit={'path':'unit.py','content_hash':sha(p.read_bytes()),'cells':[{'id':'1','language':'python','source':text,'line_start':1,'line_end':4}]}
            schemas={'stock-source':{'units':'bigint'},'rates-source':{'cost':'bigint'}}
            entry={'source_path':str(p),'unit':unit,'schemas':schemas}
            assets=[{'id':n,'parent_id':parent,'metadata':{'location':n}}for n,parent in [('stock-target','upper'),('rates-target','upper'),('stock-source','lower'),('rates-source','lower')]]
            manifest={'layers':[{'id':'high','asset_id':'stock-target'},{'id':'low','asset_id':'stock-source'}],'lineage':{'bindings':[{'from_layer':'low','to_layer':'high'}]}}
            inventory={'discovered_declarations':[{'id':n,'owner':n+'-target','form':'STATIC_WRITER','code_hash':unit['content_hash']}for n in ('stock','rates')],
                'declarations':[{'id':n,'disposition':'RESOLVED','dependencies':[n+'-source']}for n in ('stock','rates')]}
            transform={'scan':{'assets':assets},'compatible_code_units':[entry]}
            self.assertEqual(len(required_code_binding_identities(transform,manifest,inventory)),2)
            stock=static(unit,schemas=schemas,boundary=manifest['lineage']['bindings'][0],item='readiness',target_table='stock-target')['proposals'][0]
            pins={k:'pin'for k in PINS};receipts={s:{'pins':pins}for s in STAGES};receipts['transformations'].update(transform);receipts['bindings']['proposals']=[stock];receipts['reader_verification']['verifications']=[{'proposal':stock}]
            refs={}
            for stage,value in receipts.items():
                q=Path(folder)/(stage+'.json');q.write_text(json.dumps(value));refs[stage]={'path':str(q),'sha256':sha(q.read_bytes())}
            index={'version':VERSION,'pins':pins,'stages':refs}
            # Other stage facts are independently covered by their own tests.
            # The hostile producer supplies internally agreeing stock-only sets.
            with patch('investigator.estate_readiness.bind_sources'),patch('investigator.estate_readiness.CHECKS',{s:(lambda *args:None)for s in STAGES}):
                result=assess(manifest,pins,index,_scope_inventory=inventory)
            self.assertEqual(result['status'],'BLOCKED')
            self.assertEqual(next(r for r in result['stages']if r['stage']=='bindings')['reason'],'SCOPED_CODE_BINDING_CONSERVATION_FAILED')

    def test_component_bridge_recompiles_exact_plan_not_status(self):
        with tempfile.TemporaryDirectory()as folder:
            p=Path(folder)/'unit.py';text="a = spark.read.format('delta').load('source')\na.write.format('delta').mode('overwrite').save('target')\n";p.write_text(text)
            unit={'path':'unit.py','content_hash':sha(p.read_bytes()),'cells':[{'id':'1','language':'python','source':text,'line_start':1,'line_end':2}]}
            entry={'source_path':str(p),'unit':unit,'schemas':{'source':{'units':'bigint'}}}
            proposal=static(unit,schemas=entry['schemas'],boundary={'from_layer':'low','to_layer':'high'},item='code',target_table='target')['proposals'][0]
            recompile_retained_proposal(proposal,[entry])
            relocated=copy.deepcopy(proposal)
            relocated['location'].update(path='capture/unit.py',cell='cell-1')
            retained=copy.deepcopy(relocated)
            recompile_retained_proposal(relocated,[entry])
            self.assertEqual(relocated,retained)
            wrong_span=copy.deepcopy(relocated);wrong_span['location']['line_start']+=1
            with self.assertRaisesRegex(ValueError,'COMPATIBILITY_UNESTABLISHED'):
                recompile_retained_proposal(wrong_span,[entry])
            changed=copy.deepcopy(proposal);changed['expression']['column']='other'
            with self.assertRaisesRegex(ValueError,'COMPATIBILITY_UNESTABLISHED'):recompile_retained_proposal(changed,[entry])
            fake=copy.deepcopy(entry);fake['unit']['cells'][0]['source']=text.replace('source','forged')
            with self.assertRaisesRegex(ValueError,'COMPATIBILITY_UNESTABLISHED'):recompile_retained_proposal(proposal,[fake])
            p.write_text(text+'# changed\n')
            with self.assertRaisesRegex(ValueError,'COMPATIBILITY_UNESTABLISHED'):recompile_retained_proposal(proposal,[entry])

    def execution(self,folder):
        def ref(name,value):
            p=Path(folder)/name;p.write_text(json.dumps(value));return {'path':str(p),'sha256':sha(p.read_bytes())}
        witness={'proposal':{'quantity':'one'},'status':'VERIFIED'}
        from investigator.process_tape import bytes_of
        bodies=[('BOOTSTRAP',{'engine_hash':'old','entry_point':'code_reader','context_identity':'ctx','config':{},'profile':{},'usage_policy':None,'state':{}}),
                ('FINAL',{'result':{'id':'run-unique','witnesses':[witness]},'outputs':{}})]
        events=[]
        for n,(kind,body)in enumerate(bodies,1):
            raw=bytes_of(body);events.append({'ordinal':n,'kind':kind,'body':base64.b64encode(raw).decode(),'sha256':sha(raw),'at':n})
        value={'version':'bounded-worker-tape-v1','exclusions':[],'events':events};value['seal']=sha(bytes_of(value));capture=ref('tape.json',value)
        run=ref('run.json',{'tape_path':capture['path']})
        replay=ref('replay.json',{'status':'COMPLETED','matched':True,'network_requests':0,'recorded_engine_hash':'old','session':bodies[-1][1]['result'],'outputs':{}})
        receipt={'publication':{'kind':'RETAINED_EXECUTION','executions':[{'capture_ref':capture,'run_ref':run,'replay_ref':replay}]},'verifications':[witness]}
        return receipt

    def test_original_captured_witness_and_matched_replay_are_required(self):
        with tempfile.TemporaryDirectory()as folder:
            r=self.execution(folder);retained_execution_publication(r,{})
            bad=copy.deepcopy(r);bad['verifications'][0]['proposal']['quantity']='different'
            with self.assertRaisesRegex(ValueError,'NOT_IN_REPLAYED_CAPTURE'):retained_execution_publication(bad,{})
            bad=copy.deepcopy(r);bad['publication']['executions']=[]
            with self.assertRaisesRegex(ValueError,'RECEIPTS_REQUIRED'):retained_execution_publication(bad,{})

    def test_replay_from_another_capture_or_nonmatching_replay_refuses(self):
        with tempfile.TemporaryDirectory()as folder:
            r=self.execution(folder);x=r['publication']['executions'][0]
            for changes,reason in [({'matched':False},'NOT_MATCHED'),({'network_requests':1},'NOT_MATCHED'),({'recorded_engine_hash':'different'},'ENGINE_DIFFERS'),({'capture_sha256':'another'},'CAPTURE_HASH_DIFFERS'),({'session':{'id':'other'}},'FINAL_ASSOCIATION_UNESTABLISHED')]:
                old=json.loads(Path(x['replay_ref']['path']).read_text());new=dict(old,**changes)
                p=Path(folder)/'changed-replay.json';p.write_text(json.dumps(new));bad=copy.deepcopy(r);bad['publication']['executions'][0]['replay_ref']={'path':str(p),'sha256':sha(p.read_bytes())}
                with self.assertRaisesRegex(ValueError,reason):retained_execution_publication(bad,{})
            p=Path(folder)/'wrong-run.json';p.write_text(json.dumps({'tape_path':'elsewhere'}));x['run_ref']={'path':str(p),'sha256':sha(p.read_bytes())}
            with self.assertRaisesRegex(ValueError,'CAPTURE_DIFFERS'):retained_execution_publication(r,{})

    def test_empty_or_filtered_scope_cannot_be_producer_certified(self):
        for value in ({},{'kind':'WHOLE_ENTITY_QUANTITY','measure_ids':[],'filters':[],'dimension_ids':[]},
                      {'kind':'WHOLE_ENTITY_QUANTITY','measure_ids':['m'],'filters':[1],'dimension_ids':[]}):
            with self.assertRaises(ValueError):validate_scope_constraints(value)
if __name__=='__main__':unittest.main()
