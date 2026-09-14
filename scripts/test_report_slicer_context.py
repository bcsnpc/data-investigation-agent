import hashlib
import json
import unittest
from report_slicer_context import assess

PAGE='definition/pages/main/page.json'
VISUAL='slicer1'
def sign(e):
    e.pop('bundle_hash',None);e['bundle_hash']=hashlib.sha256(json.dumps(e,sort_keys=True).encode()).hexdigest();return e

def fixture():
    field={'Column':{'Expression':{'SourceRef':{'Entity':'DimDate'}},'Property':'year_month'}}
    visual={'visual':{'visualType':'slicer','query':{'queryState':{'Values':{'projections':[{'field':field}]}}}}}
    return sign({'scan_id':'scan','report':{'id':'report'},'binding_status':'RESOLVED_EXPLICIT_ID','gaps':[],
      'report_definitions':[{'id':'page','name':PAGE,'metadata':{'content':'{}'}},
       {'id':VISUAL,'name':'definition/pages/main/visuals/s1/visual.json','content_hash':'hash','metadata':{'content':json.dumps(visual)}}],
      'model_assets':[{'id':'table','kind':'SemanticTable','name':'DimDate','parent_id':'model'},
       {'id':'column','kind':'SemanticColumn','name':'year_month','parent_id':'table'}]})

class SlicerTests(unittest.TestCase):
    def test_missing_selection_is_not_all(self):
        result=assess(fixture(),PAGE)
        self.assertEqual(result['status'],'NEEDS_INPUT')
        self.assertIsNone(result['slicers'][0]['selection'])
        self.assertEqual(result['slicers'][0]['column'],'year_month')
    def test_explicit_all_and_values_preserved_without_proof(self):
        for selection in [{'mode':'all'},{'mode':'values','values':['2026-09']}]:
            result=assess(fixture(),PAGE,{VISUAL:selection})
            self.assertEqual(result['status'],'CONTEXT_SUPPLIED')
            self.assertEqual(result['slicers'][0]['selection'],selection)
            self.assertFalse(result['runtime_filter_verified'])
    def test_invalid_and_unknown_selections_rejected(self):
        for selections in [{'unknown':{'mode':'all'}},{VISUAL:None},{VISUAL:{'mode':'values','values':[]}},{VISUAL:{'mode':'values','values':['x','x']}},{VISUAL:{'mode':'range','from':1}}]:
            with self.assertRaises(ValueError):assess(fixture(),PAGE,selections)
    def test_unresolved_model_column_is_unsupported(self):
        e=fixture();e['model_assets']=[]
        self.assertEqual(assess(sign(e),PAGE)['status'],'UNSUPPORTED')
    def test_no_slicer_does_not_prove_unfiltered(self):
        e=fixture();e['report_definitions'].pop()
        result=assess(sign(e),PAGE)
        self.assertEqual(result['status'],'NO_SLICERS_CAPTURED')
        self.assertFalse(result['root_cause_verified'])
    def test_tampered_bundle_and_wrong_page_rejected(self):
        e=fixture();e['gaps']=['changed']
        with self.assertRaises(ValueError):assess(e,PAGE)
        with self.assertRaises(ValueError):assess(fixture(),'definition/pages/other/page.json')
