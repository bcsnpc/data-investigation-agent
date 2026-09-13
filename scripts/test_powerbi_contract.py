"""Offline integration checks for the committed semantic model and PBIR bindings."""
import json
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/'infra/powerbi'

class PowerBIContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=json.loads((ROOT/'OrderOps.SemanticModel/model.bim').read_text())['model']
        cls.tables={t['name']:t for t in cls.model['tables']}
    def test_names_are_unique_case_insensitively(self):
        for t in self.tables.values():
            names=[c['name'].casefold() for c in t['columns']+t.get('measures',[])]
            self.assertEqual(len(names),len(set(names)),t['name'])
    def test_relationships_have_one_unambiguous_filter_path(self):
        edges={t:[] for t in self.tables}
        for r in self.model['relationships']:
            self.assertEqual(r['crossFilteringBehavior'],'oneDirection')
            self.assertEqual(r['toCardinality'],'one')
            for side in ('from','to'):
                self.assertIn(r[side+'Column'],[c['name'] for c in self.tables[r[side+'Table']]['columns']])
            edges[r['toTable']].append(r['fromTable'])
        def walk(node,path,seen):
            self.assertNotIn(node,path,'Relationship cycle')
            self.assertNotIn(node,seen,'Ambiguous filtering path')
            seen.add(node)
            for child in edges[node]:walk(child,path+[node],seen)
        for t in edges:walk(t,[],set())
    def test_every_visual_field_resolves(self):
        def walk(obj):
            if isinstance(obj,dict):
                for kind in ('Column','Measure'):
                    if kind in obj:
                        ref=obj[kind];table=ref['Expression']['SourceRef']['Entity']
                        self.assertIn(table,self.tables)
                        self.assertIn(ref['Property'],[c['name'] for c in self.tables[table]['columns' if kind=='Column' else 'measures']])
                for v in obj.values():walk(v)
            elif isinstance(obj,list):
                for v in obj:walk(v)
        visuals=list(ROOT.glob('*.Report/definition/pages/*/visuals/*/visual.json'))
        self.assertGreater(len(visuals),30)
        for p in visuals:walk(json.loads(p.read_text()))
    def test_visuals_fit_pages_and_page_order_is_valid(self):
        for report in ROOT.glob('*.Report'):
            meta=json.loads((report/'definition/pages/pages.json').read_text())
            self.assertIn(meta['activePageName'],meta['pageOrder'])
            for page in meta['pageOrder']:
                folder=report/'definition/pages'/page
                info=json.loads((folder/'page.json').read_text())
                for p in folder.glob('visuals/*/visual.json'):
                    pos=json.loads(p.read_text())['position']
                    self.assertGreaterEqual(pos['x'],0);self.assertGreaterEqual(pos['y'],0)
                    self.assertLessEqual(pos['x']+pos['width'],info['width'])
                    self.assertLessEqual(pos['y']+pos['height'],info['height'])
    def test_drillthrough_parameter_binds_order_filter(self):
        pages=[json.loads(p.read_text()) for p in (ROOT/'OrderOperations.Report').glob('definition/pages/*/page.json')]
        drill=next(p for p in pages if p.get('pageBinding',{}).get('type')=='Drillthrough')
        filters={f['name']:f for f in drill['filterConfig']['filters']}
        param=drill['pageBinding']['parameters'][0]
        self.assertEqual(param['fieldExpr'],filters[param['boundFilter']]['field'])
        self.assertEqual(param['fieldExpr']['Column']['Property'],'order_id')

if __name__=='__main__':unittest.main()
