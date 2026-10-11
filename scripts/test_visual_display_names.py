"""Visual titles are display evidence, while page aliases remain lookup evidence."""
from io import BytesIO
import json
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from investigator.adapters import report_cells
import test_report_cells as fixture


class VisualDisplayTests(unittest.TestCase):
    def test_live_report_binding_preserves_projected_visual_title_in_submitted_facts(self):
        from investigator.form_controller import Forms
        original={'models':[{'id':'model','visuals':[{'target_id':'card','names':['Inventory Health','Movement Units']}]}]}
        class Lists:
            def bound_catalog(self,models,refresh=False):
                return {'models':models,'source':'LIVE_READER','unbound_reports':[],
                        'cached':True,'cache_ttl_seconds':60,'identity':'reader'}
        workspace=SimpleNamespace(intake_configuration=None,report_lists=Lists(),
                                  visual_display_names=lambda identity:{'card':['Movement Units']})
        with patch('investigator.form_controller.snapshot',return_value=original):
            result=Forms(workspace).catalog()
        visual=result['models'][0]['visuals'][0]
        self.assertEqual(visual['display_names'],['Movement Units'])
        self.assertEqual(visual['names'],['Inventory Health','Movement Units'])
        self.assertNotIn('display_names',original['models'][0]['visuals'][0])

    def test_actual_family_a_alias_shape_does_not_display_page_as_visual(self):
        helper=fixture.CellTests();helper.setUp();self.addCleanup(helper.doCleanups)
        helper.modify(helper.page,lambda d:d.update(displayName='Inventory Health'))
        helper.modify(helper.visual,lambda d:d['visual'].update(visualContainerObjects={'title':[{'properties':{'text':{'expr':{'Literal':{'Value':"'Movement Units'"}}}}}]}))
        original=next(v for v in report_cells.catalog(helper.model) if v['target_id']==helper.visual['id'])
        shown=next(v for v in report_cells.catalog(helper.model,include_display_names=True) if v['target_id']==helper.visual['id'])
        self.assertEqual(original['names'],['Inventory Health','Movement Units'])
        self.assertNotIn('display_names',original)
        self.assertEqual(shown['display_names'],['Movement Units'])
        self.assertEqual({k:v for k,v in shown.items() if k!='display_names'},original)

    def test_title_equal_to_page_name_is_still_a_real_title(self):
        helper=fixture.CellTests();helper.setUp();self.addCleanup(helper.doCleanups)
        helper.modify(helper.page,lambda d:d.update(displayName='Sales'))
        helper.modify(helper.visual,lambda d:d['visual'].update(visualContainerObjects={'title':[{'properties':{'text':{'expr':{'Literal':{'Value':"'Sales'"}}}}}]}))
        visual=next(v for v in report_cells.catalog(helper.model,include_display_names=True) if v['target_id']==helper.visual['id'])
        self.assertEqual(visual['display_names'],['Sales'])

    def test_api_preserves_four_distinct_declared_titles_not_first_alias(self):
        from investigator.workspace_api import create_app
        titles=['Movement Units','Net Movement Units','Movement Value','Receipt Share']
        visuals=[{'target_id':'visual-'+str(i),'report_id':'report','page_id':'page','names':['Inventory Health',title]} for i,title in enumerate(titles)]
        workspace=SimpleNamespace(visual_display_names=lambda identity:{v['target_id']:[title] for v,title in zip(visuals,titles)})
        token='synthetic-local-key-of-at-least-32-characters'
        app=create_app(workspace,token,8791);body=json.dumps({'report_id':'report','page_id':'page'}).encode();statuses=[]
        with patch('investigator.question_intake.snapshot',return_value={'models':[{'id':'model','visuals':visuals}]}):
            result=b''.join(app({'HTTP_HOST':'127.0.0.1:8791','HTTP_AUTHORIZATION':'Bearer '+token,'REQUEST_METHOD':'POST','PATH_INFO':'/api/workspace/questionnaire/visuals','CONTENT_TYPE':'application/json','CONTENT_LENGTH':str(len(body)),'wsgi.input':BytesIO(body)},lambda status,headers:statuses.append(status)))
        self.assertEqual(statuses,['200 OK'])
        self.assertEqual([v['name'] for v in json.loads(result)['visuals']],titles)


if __name__=='__main__':unittest.main()
