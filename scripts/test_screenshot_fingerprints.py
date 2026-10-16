import json,unittest
from types import SimpleNamespace
from unittest.mock import Mock,patch
from investigator.adapters.screenshot_fingerprints import catalog

class Tests(unittest.TestCase):
    def test_visible_literal_text_contributes_but_style_literals_do_not(self):
        parts=[{'id':'page','name':'definition/pages/p/page.json','metadata':{'content':json.dumps({'displayName':'Overview'})}},
               {'id':'slicer','name':'definition/pages/p/visuals/s/visual.json','metadata':{'content':json.dumps({'visual':{
                   'visualContainerObjects':{'title':[{'properties':{'text':{'expr':{'Literal':{'Value':"'Region'"}}},
                    'fontFamily':{'expr':{'Literal':{'Value':"'Arial'"}}},'color':{'expr':{'Literal':{'Value':"'#ffffff'"}}}}}]}}})}}]
        model={'id':'m','enabled':True,'context':{'reports':[{'report':{'id':'r','name':'Report'},'report_definitions':parts}]}}
        workspace=SimpleNamespace(store=SimpleNamespace(list=lambda enabled:[model]),model=lambda id:{'measures':[]})
        with patch('investigator.adapters.report_cells.catalog',return_value=[]):pages=catalog(workspace)
        self.assertEqual(pages[0]['anchors'],['Region'])
        self.assertEqual(pages[0]['page_id'],'r/page/p')

if __name__=='__main__':unittest.main()
