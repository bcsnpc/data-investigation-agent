import copy
import unittest
from investigator.layer_roles import apply, declarations, name
from investigator.output_contract import business_text, action
from investigator.narrative_form import technical, business
from test_path_narrative import PathNarrativeTests


class LayerRoleTests(unittest.TestCase):
    def payload(self, original=False):
        p=PathNarrativeTests().payload()
        roles=[('report','SEMANTIC','semantic model'),('prepared','LANDING','landing table'),('original','APPLICATION','application')]
        if original:roles=[('report','SEMANTIC','semantic model'),('prepared','SERVING','serving data'),('original','REFINED','refined data')]
        for e in p['evidence']:
            if e.get('result',{}).get('comparison_status')=='CROSS_SURFACE_VERIFIED':e['result']['surface_difference']={'grade':'ENGINE_INDEPENDENT'}
        p['layer_labels']=apply({},[{'id':i} for i,_,_ in roles],
            [{'asset_id':i,'role':r,'business_name':n} for i,r,n in roles])
        return p

    def test_three_layer_source_walk_names_application_not_report_preparation(self):
        p=self.payload();text=business(business_text('NO_KNOWN_PATTERN',p),p)
        self.assertIn('application contained 7,661',text)
        self.assertIn('between the application and the landing table',text)
        self.assertIn('For the landing table and the application',text)
        self.assertNotIn('during preparation',text)
        source={'limits':[],'technical_output':{'layer_labels':p['layer_labels']}}
        output=technical('The compared operation carries the quantity unchanged.',p,source,action('NO_KNOWN_PATTERN'))
        self.assertIn('role APPLICATION',output);self.assertIn('role LANDING',output)

    def test_original_estate_renders_declared_serving_and_refined_roles(self):
        p=self.payload(True);text=business_text('TRANSFORMATION_LOGIC',p)
        self.assertIn('refined data contained 7,661',text)
        self.assertIn('between the refined data and the serving data',text)
        self.assertNotIn('application',text)

    def test_roles_never_inferred_from_position_or_object_names(self):
        p=self.payload();p.pop('layer_labels')
        self.assertEqual(name(p,'application'), 'declared layer')
        self.assertNotIn('during preparation',business_text('NO_KNOWN_PATTERN',p))

    def test_closed_declarations_reject_unknown_role_or_technical_name(self):
        row={'asset_id':'asset','role':'APPLICATION','business_name':'application'}
        for bad in ({**row,'role':'GOLD'},{**row,'business_name':'app.stock_movements'},
                    {**row,'business_name':'a_b'}, {**row,'extra':'inferred'}):
            with self.assertRaises(ValueError):declarations([bad])
        with self.assertRaises(ValueError):declarations([row,row])

    def test_rendering_does_not_drop_directory_or_sql_objects(self):
        p=self.payload();p['context_entry_points']=[{'id':str(i),'kind':'SqlObject' if i<11 else 'SemanticTable'} for i in range(28)]
        original=copy.deepcopy(p);business_text('NO_KNOWN_PATTERN',p)
        self.assertEqual(p,original)
