import copy,unittest
from investigator.claim_clarification import candidates,plan,interpretation
from investigator.claim_facts import fact,settled,linked_text,resolve_native_scope

CAT={'models':[{'id':'model','measures':[{'id':'quantity','name':'Quantity'}],
    'reports':[{'id':'report','name':'Activity'}],
    'visuals':[{'target_id':'card','report_id':'report','page_id':'page','names':['Global card'],'page_names':['Overview'],'measure_ids':['quantity']},
               {'target_id':'other','report_id':'report','page_id':'other-page','names':['Regional card'],'page_names':['Regional'],'measure_ids':['quantity']}]}]}


class Glossary:
    def __init__(self,rows):self.rows=rows
    def resolve(self,*args):return copy.deepcopy(self.rows)


class PolicyRepairTests(unittest.TestCase):
    def test_declared_link_uses_existing_exact_native_identity_binding(self):
        workspace='22222222-2222-4222-8222-222222222222';report='11111111-1111-4111-8111-111111111111'
        native='fabric://'+workspace+'/'+report
        catalog=copy.deepcopy(CAT);catalog['models'][0]['reports'][0]['id']=native
        for v in catalog['models'][0]['visuals']:v['report_id']=native;v['page_id']=native+'/page/Overview'
        source=linked_text('https://app.powerbi.com/groups/'+workspace+'/reports/'+report+'/Overview','doc')[0]
        derived=resolve_native_scope(source,catalog)
        self.assertEqual(source['value']['report_id'],report)
        self.assertEqual(derived['value']['report_id'],native)
        self.assertEqual(derived['value']['page_id'],native+'/page/Overview')
        self.assertEqual(derived['source']['source_fact_id'],source['id'])
        wrong=linked_text('https://app.powerbi.com/groups/33333333-3333-4333-8333-333333333333/reports/'+report,'doc')[0]
        with self.assertRaisesRegex(ValueError,'UNRESOLVED'):resolve_native_scope(wrong,catalog)
    def test_catalog_alias_and_definition_same_visual_scope_deduplicate(self):
        catalog=copy.deepcopy(CAT);catalog['models'][0]['visuals']=catalog['models'][0]['visuals'][:1]
        rows=[{'model_id':'model','measure_id':'quantity','label':'Quantity','status':'CONFIRMED','evidence_ids':['native-name']},
              {'model_id':'model','measure_id':'quantity','label':'Quantity','status':'CONFIRMED','report_id':'report','page_id':'page','target_ids':['card'],'evidence_ids':['native-label']}]
        result=candidates({'metric':[{'phrase':'Quantity'}]},catalog,Glossary(rows))
        self.assertEqual(len(result),1)
        self.assertEqual(result[0]['target_ids'],['card'])
        self.assertIsNone(result[0]['report_id'])
        self.assertEqual(set(result[0]['evidence_ids']),{'native-name','native-label'})
    def test_distinct_native_targets_and_concrete_scopes_do_not_collapse(self):
        rows=[{'model_id':'model','measure_id':'quantity','label':'Quantity','status':'CONFIRMED','report_id':'report','page_id':'page','target_ids':['card'],'evidence_ids':['first']},
              {'model_id':'model','measure_id':'quantity','label':'Quantity','status':'CONFIRMED','report_id':'report','page_id':'other-page','target_ids':['other'],'evidence_ids':['second']}]
        self.assertEqual(len(candidates({'metric':[{'phrase':'Quantity'}]},CAT,Glossary(rows))),2)
    def test_general_difference_refines_only_one_compatible_specific_direction(self):
        def records(values):return [fact('direction',v,{'kind':'USER_EXAMPLE','sequence':i},authority='USER_TEXT')for i,v in enumerate(values)]
        self.assertEqual(settled(records(['DIFFERENT','LESS']))[0]['direction'],'LESS')
        self.assertEqual(settled(records(['UNKNOWN','MORE']))[0]['direction'],'MORE')
        for values in (['LESS','MORE'],['STALE','DIFFERENT']):self.assertIn('direction',settled(records(values))[1])
    def test_plural_time_clauses_stay_visible_without_selecting_a_date(self):
        fs=[fact('time',v,{'kind':'USER_EXAMPLE','sequence':i},authority='USER_TEXT')for i,v in enumerate(['October 3','October 4'])]
        values,conflicts=settled(fs);self.assertEqual(values['time'],['October 3','October 4']);self.assertEqual(conflicts,[])
        output=interpretation({'settled':values,'facts':fs,'selected_binding':None},CAT)['text']
        self.assertIn('October 3; October 4',output)
    def test_unresolved_unknown_direction_and_comparator_still_ask(self):
        claim={'settled':{'metric':[{'phrase':'Quantity'}],'comparator':'UNKNOWN','direction':'UNKNOWN','scope':{'kind':'PAGE','report_id':'report','page_id':'page'}},
            'facts':[],'conflicts':[],'selected_binding':{'model_id':'model','measure_id':'quantity','label':'Quantity','target_ids':['card']},'candidate_bindings':[]}
        self.assertEqual(plan(claim,CAT)[0]['field'],'comparator')
        claim['settled']['comparator']='NONE';self.assertEqual(plan(claim,CAT)[0]['field'],'direction')


if __name__=='__main__':unittest.main()
