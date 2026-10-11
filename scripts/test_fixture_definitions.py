import copy,json,unittest
from fixture.definitions import bind,definition,model_slots
from fixture.rebuild import templates

class FixtureDefinitionTest(unittest.TestCase):
    def test_model_database_is_endpoint_id_never_lakehouse_item_id(self):
        lakehouse={'id':'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa','properties':{'sqlEndpointProperties':{'id':'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb','provisioningStatus':'Success','connectionString':'fixture.datawarehouse.fabric.microsoft.com'}}}
        slots=model_slots(lakehouse,'cccccccc-cccc-cccc-cccc-cccccccccccc','ITEM_2')
        self.assertEqual(slots['ITEM_2'],lakehouse['properties']['sqlEndpointProperties']['id'])
        self.assertNotEqual(slots['ITEM_2'],lakehouse['id'])
        lakehouse['properties']['sqlEndpointProperties']['id']=lakehouse['id']
        with self.assertRaisesRegex(ValueError,'confused'):model_slots(lakehouse,'cccccccc-cccc-cccc-cccc-cccccccccccc','ITEM_2')
    def test_every_missing_slot_refuses_instead_of_reusing_original_id(self):
        for name,t in templates().items():
            with self.subTest(name=name),self.assertRaisesRegex(ValueError,'Unbound fixture slot'):
                bind(t['definition'],{})
    def test_nested_binding_keeps_input_unchanged_and_does_not_interpret_kind(self):
        before={'kind':'unfamiliar','nested':['${ITEM_1}',{'source':'${ITEM_2}'}]};original=copy.deepcopy(before)
        after=bind(before,{'ITEM_1':'first','ITEM_2':'second'})
        self.assertEqual(before,original);self.assertEqual(after,{'kind':'unfamiliar','nested':['first',{'source':'second'}]})
    def test_slots_cannot_inject_model_expression_or_json(self):
        for value in ('bad"text','bad\\text','bad\ntext',''):
            with self.subTest(value=value),self.assertRaisesRegex(ValueError,'Unsafe fixture slot'):bind('${ITEM_1}',{'ITEM_1':value})
    def test_retained_report_parts_and_predicates_survive_binding(self):
        template=templates()['predicate-report']['definition'];r=definition(template,{'ITEM_1':'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa','ITEM_4':'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'})
        self.assertEqual([p['path'] for p in r['parts']],[p['path'] for p in template['parts']])
        self.assertEqual(len(r['parts']),len(template['parts']))

if __name__=='__main__':unittest.main()
