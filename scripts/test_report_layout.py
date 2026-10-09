"""Layout previews cannot manufacture values or select a ticket referent."""
import copy
import json
import unittest
from unittest.mock import MagicMock
from investigator.adapters import report_layout


class LayoutTests(unittest.TestCase):
    def setUp(self):
        self.report='fabric://11111111-1111-1111-1111-111111111111/22222222-2222-2222-2222-222222222222'
        def part(name,body):return {'id':name,'name':name,'metadata':{'content':json.dumps(body)}}
        self.visual=part('definition/pages/PageA/visuals/CardA/visual.json',{
            'position':{'x':100,'y':50,'width':200,'height':100},
            'visual':{'visualContainerObjects':{'title':[{'properties':{'text':{'expr':{'Literal':{'Value':"'Revenue card'"}}}}}]}}})
        self.model={'id':'model','enabled':True,'context_id':'pinned', 'context':{'reports':[{
            'report':{'id':self.report,'name':'Revenue'},'report_definitions':[
                part('definition/pages/PageA/page.json',{'displayName':'Overview','width':1000,'height':500}),self.visual]}]}}
        self.workspace=MagicMock();self.workspace.store.list.return_value=[{'id':'model'}]
        self.workspace.store.get.return_value=self.model

    def test_retained_geometry_is_normalized_without_values_or_scope_authority(self):
        page=report_layout.pages(self.model)[0];visual=page['visuals'][0]
        self.assertEqual(visual['name'],'Revenue card')
        self.assertEqual(visual['box'],{'x':.1,'y':.1,'width':.2,'height':.2})
        self.assertEqual(page['source'],'RETAINED_DEFINITION_LAYOUT_NOT_LIVE_VALUES')
        self.assertNotIn('value',visual);self.assertNotIn('measure_id',visual)

    def test_missing_or_out_of_page_geometry_is_not_fabricated(self):
        for position in ({},{'x':-1,'y':0,'width':10,'height':10},{'x':900,'y':0,'width':200,'height':10}):
            with self.subTest(position=position):
                self.visual['metadata']['content']=json.dumps({'position':position})
                self.assertEqual(report_layout.pages(self.model)[0]['visuals'],[])

    def test_link_preview_is_local_and_never_selects_a_visual(self):
        link='https://app.powerbi.com/groups/11111111-1111-1111-1111-111111111111/reports/22222222-2222-2222-2222-222222222222/PageA'
        result=report_layout.preview(self.workspace,{'report_link':link})
        self.assertEqual(len(result['pages']),1)
        self.assertNotIn('target_id',result)
        self.workspace.smart_intake.submit.assert_not_called()
        self.workspace.agent.runtime.native_transport.assert_not_called()
        with self.assertRaisesRegex(ValueError,'UNSUPPORTED'):
            report_layout.preview(self.workspace,{'report_link':link+'?bookmarkGuid=Other'})

    def test_only_saved_offered_choices_receive_layout_and_ticket_is_unchanged(self):
        from investigator.onboarding import digest
        question={'id':'number','choices':[{'id':'offered'}]}
        ticket={'questions':[question],'choice_values':{digest(question)+'/offered':{'target_id':self.visual['id']}}}
        original=copy.deepcopy(ticket);self.workspace.smart_intake.tickets.get.return_value={'ticket':ticket}
        result=report_layout.choices(self.workspace,'ticket')
        self.assertEqual(set(result['choices']),{'offered'})
        self.assertEqual(ticket,original)
        self.workspace.store.list.return_value=[{'id':'model'},{'id':'duplicate'}]
        self.assertEqual(report_layout.choices(self.workspace,'ticket')['choices'],{})

if __name__=='__main__':unittest.main()
