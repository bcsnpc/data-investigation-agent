import copy,tempfile,unittest
from pathlib import Path
from investigator.lineage_binding import validate,verify,Ledger,require_declared_approval
from investigator.process_debugging import attest_surface

def proposal():
    return {'boundary':{'from_layer':'input','to_layer':'output'},'sources':[{'table':'input-table','columns':['amount']}],
        'target':{'table':'output-table','column':'amount'},'expression':{'relation':{'kind':'SCAN','table':'input-table','columns':['amount']},'column':'amount'},
        'location':{'item':'code-item','path':'unit.py','cell':'0','line_start':1,'line_end':2,'content_hash':'a'*64},'extractor':'STATIC'}

class BindingTests(unittest.TestCase):
    def test_hostile_scalar_tree_is_bounded_before_schema_recursion(self):
        p=proposal();expr={'kind':'COLUMN','name':'amount'}
        for _ in range(100):expr={'kind':'NOT','operand':expr}
        p['expression']['relation']={'kind':'FILTER','input':p['expression']['relation'],'predicate':expr}
        with self.assertRaisesRegex(ValueError,'structural bound'):validate(p)
    def verification(self,values=('7','7'),*,compile_error=False,blank=False,same_surface=False):
        calls=[];context='pinned-context';cell={'id':'selected-cell'};precision={'state':'EXACT'}
        def compiler(binding,side,*args):
            if compile_error and side=='SOURCE':raise ValueError('Untranslatable operation')
            return side
        def execute(side,plan):
            calls.append(side);index=('TARGET','SOURCE').index(side)
            surface={'engine':'sql-engine','connection':'declared-connection','object':'same' if same_surface else side,'identity':'reader'}
            evidence={'id':'receipt-'+side,'execution_surface':surface,'surface_report':surface,
                'surface_report_binding':'VALUE_QUERY','surface_report_receipt_id':'receipt-'+side,
                'surface_report_types':{'engine':'ENGINE_PRODUCT','object':'DATABASE'}}
            evidence['surface_attestation']=attest_surface(surface,surface,tuple(surface))
            return {'status':'COMPLETED','context':context,'cell':cell,'precision':precision,'evidence':evidence,
                    'quantity':{'state':'BLANK'} if blank else {'state':'NUMBER','value':values[index]}}
        result=verify(proposal(),context=context,cell=cell,precision=precision,compiler=compiler,execute=execute)
        return result,calls
    def test_only_verifier_can_emit_verification_static_cannot_claim_confidence(self):
        p=proposal();validate(p)
        for field,value in [('status','VERIFIED'),('confidence',1)]:
            bad=copy.deepcopy(p);bad[field]=value
            with self.assertRaises(ValueError):validate(bad)
        p['extractor']='MODEL';p['confidence']=0.8;validate(p)
    def test_false_scan_inventory_cannot_validate(self):
        p=proposal();p['sources'][0]['table']='unrelated'
        with self.assertRaisesRegex(ValueError,'scan inventory'):validate(p)
    def test_equal_verifies_only_sampled_scope_and_different_falsifies(self):
        result,calls=self.verification();self.assertEqual(result['status'],'VERIFIED');self.assertEqual(calls,['TARGET','SOURCE'])
        self.assertEqual(result['snapshot_status'],'SNAPSHOT_UNVERIFIED')
        result,calls=self.verification(('7','8'));self.assertEqual(result['status'],'FALSIFIED')
        self.assertEqual([o['quantity']['value'] for o in result['observations']],['7','8'])
        with self.assertRaisesRegex(ValueError,'Declared binding falsified'):require_declared_approval([result])
    def test_compile_both_before_any_read(self):
        result,calls=self.verification(compile_error=True)
        self.assertEqual(result['status'],'UNVERIFIED');self.assertEqual(calls,[])
    def test_blank_is_value_not_absence_or_zero(self):
        result,_=self.verification(blank=True);self.assertEqual(result['status'],'VERIFIED')
        result,_=self.verification(('0','7'));self.assertEqual(result['status'],'FALSIFIED')
    def test_within_layer_agreement_cannot_verify_lineage(self):
        result,_=self.verification(same_surface=True);self.assertEqual(result['status'],'UNVERIFIED')
    def test_changed_code_hash_is_stale_and_ledger_remains_unchanged(self):
        with tempfile.TemporaryDirectory() as d:
            ledger=Ledger(Path(d)/'lineage.jsonl');result,_=self.verification();ledger.append(result)
            original=ledger.path.read_bytes()
            self.assertEqual(ledger.view({('code-item','unit.py'):'a'*64})[0]['status'],'VERIFIED')
            self.assertEqual(ledger.view({('code-item','unit.py'):'b'*64})[0]['status'],'STALE')
            self.assertEqual(ledger.view({})[0]['status'],'STALE')
            self.assertEqual(ledger.path.read_bytes(),original)
    def test_deliberately_wrong_binding_falsifies_against_executed_synthetic_expressions(self):
        import sqlite3
        from investigator.transformation_sql import compile_quantity
        p=proposal();p['expression']['relation']={'kind':'PROJECT','input':p['expression']['relation'],
            'columns':[{'name':'amount','expression':{'kind':'MULTIPLY','left':{'kind':'COLUMN','name':'amount'},'right':{'kind':'LITERAL','value':2}}}]}
        catalog={name:{'id':name,'metadata':{'schema_name':schema,'name':'items','type_desc':'USER_TABLE',
                     'columns':[{'name':'amount','data_type':'int'}]}} for name,schema in [('input-table','lower_data'),('output-table','upper_data')]}
        with sqlite3.connect(':memory:') as db:
            db.executescript("ATTACH DATABASE ':memory:' AS lower_data; ATTACH DATABASE ':memory:' AS upper_data; CREATE TABLE lower_data.items(amount INT); CREATE TABLE upper_data.items(amount INT); INSERT INTO lower_data.items VALUES (3),(4); INSERT INTO upper_data.items VALUES (3),(4);")
            def compiler(binding,side,*args):
                relation=binding['expression']['relation'] if side=='SOURCE' else {'kind':'SCAN','table':binding['target']['table'],'columns':['amount']}
                return compile_quantity(relation,'amount',catalog)
            def execute(side,query):
                surface={'engine':'sqlite','connection':'memory-session','object':'upper_data' if side=='TARGET' else 'lower_data','identity':'offline-test'}
                evidence={'id':side,'execution_surface':surface,'surface_report':surface,'surface_report_binding':'VALUE_QUERY',
                    'surface_report_receipt_id':side,'surface_report_types':{'engine':'ENGINE_PRODUCT','object':'DATABASE'}}
                evidence['surface_attestation']=attest_surface(surface,surface,tuple(surface))
                value=db.execute(query).fetchone()[0]
                return {'status':'COMPLETED','context':'synthetic','cell':{'id':'cell'},'precision':{'state':'EXACT'},'evidence':evidence,
                        'quantity':{'state':'NUMBER','value':str(value)}}
            result=verify(p,context='synthetic',cell={'id':'cell'},precision={'state':'EXACT'},compiler=compiler,execute=execute)
        self.assertEqual(result['status'],'FALSIFIED')
        self.assertEqual([o['quantity']['value'] for o in result['observations']],['7','14'])

if __name__=='__main__':unittest.main()
