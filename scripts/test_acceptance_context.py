import copy,json,sqlite3,tempfile,unittest
from pathlib import Path
from contextlib import contextmanager
from unittest.mock import patch
from investigator.acceptance_context import require_state,select_store,approve_state_context,declared_role_view
from investigator.onboarding import Conflict,digest

class AcceptanceContextTests(unittest.TestCase):
    def fixture(self):return {'fixture_states':[{'id':'baseline','description':'No rows changed','arithmetic':'Independent seed sum','evidence':['seed']},{'id':'gap','description':'One missing row','arithmetic':'Seed plus one','evidence':['mutation']}], 'layers':[]}
    def binding(self,name='baseline',context=None):return {'name':name,'definition_hash':digest(next(r for r in self.fixture()['fixture_states'] if r['id']==name)),'context':context,'approval_reference':'test decision'}
    def test_two_context_ids_for_same_state_both_satisfy(self):
        for identity in ('first','recollected'):
            require_state({'fixture_state':'baseline','model_id':'model'},self.binding(context={'context_id':identity}),self.fixture())
    def test_different_state_names_refuse_before_store_or_transport(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'case';p.write_text(json.dumps({'fixture_state':'baseline','model_id':'model'}))
            with patch('investigator.acceptance_context.ModelStore',side_effect=AssertionError('no transport')):
                with self.assertRaises(Conflict) as e:select_store(p,None,'model',fixture=self.fixture(),invoked_state=self.binding('gap'))
        self.assertIn('baseline',str(e.exception));self.assertIn('gap',str(e.exception))
    def test_changed_definition_under_same_name_refuses(self):
        binding=self.binding();fixture=self.fixture();fixture['fixture_states'][0]['description']='Different rows'
        with self.assertRaisesRegex(Conflict,'definition differs'):require_state({'fixture_state':'baseline','model_id':'model'},binding,fixture)
    def test_runner_selects_latest_approved_context_and_no_approval_refuses(self):
        with tempfile.TemporaryDirectory() as d:
            db=sqlite3.connect(':memory:');db.row_factory=sqlite3.Row
            @contextmanager
            def connect():yield db
            store=type('Store',(),{'connect':staticmethod(connect),'database':'db','inventory':'inventory','environment':'env'})()
            p=Path(d)/'case';p.write_text(json.dumps({'fixture_state':'baseline','model_id':'model'}))
            with self.assertRaisesRegex(Conflict,'No approved context'):select_store(p,store,'model',fixture=self.fixture())
            with patch('investigator.acceptance_context.ModelStore') as ctor:
                ctor.return_value.get.return_value={'enabled':True}
                pins=[{'context_id':f'00000000-0000-4000-8000-{i:012d}','hash':str(i)*64} for i in (1,2)]
                for pin in pins:approve_state_context(store,self.fixture(),'baseline','model',pin,approval_reference='independent setup receipt')
                selected=select_store(p,store,'model',fixture=self.fixture())
                self.assertEqual(ctor.call_args.kwargs['context_pins'],{'model':pins[1]})
                for pin in pins:
                    select_store(p,store,'model',fixture=self.fixture(),invoked_context=pin)
                self.assertEqual(selected.acceptance_fixture_state['name'],'baseline')
                gap={'context_id':'00000000-0000-4000-8000-000000000003','hash':'3'*64}
                approve_state_context(store,self.fixture(),'gap','model',gap,approval_reference='different independently established fixture')
                with self.assertRaises(Conflict) as e:select_store(p,store,'model',fixture=self.fixture(),invoked_context=gap)
                self.assertIn('baseline',str(e.exception));self.assertIn('gap',str(e.exception))
                with self.assertRaisesRegex(Conflict,'No approved context'):select_store(p,store,'model',fixture=self.fixture(),invoked_context={'context_id':'other','hash':'a'*64})
            db.close()
    def test_declared_roles_are_grading_view_not_evidence_mutation(self):
        fixture=self.fixture();fixture['layers']=[{'asset_id':'asset','role':'LANDING','business_name':'landing table'}]
        original={'layer_labels':{'asset':{'name':'object'},'unknown':{}}};saved=copy.deepcopy(original)
        view=declared_role_view(original,fixture)
        self.assertEqual(original,saved);self.assertEqual(view['layer_labels']['asset']['role'],'LANDING');self.assertNotIn('role',view['layer_labels']['unknown'])

if __name__=='__main__':unittest.main()
