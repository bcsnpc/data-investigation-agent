import copy, unittest
from unittest.mock import patch
from investigator import continuation_catalog as continuation, intake_extraction
from investigator.onboarding import Conflict
from test_input_reference import setup_reference

class ReferentTests(unittest.TestCase):
    def setUp(self):
        self.raw,self.payload,self.request=setup_reference()
        self.proposal=intake_extraction.resolve(self.raw,self.payload)
        self.catalog={'models':self.payload['models'],'versions':[]}
        self.source={'text':self.payload['text'],'proposal':self.proposal,
            'retained_extraction':self.raw,'catalog_referents':continuation.referents(self.catalog)}
        self.ticket={'confirmed':{},'settled':{}}

    def test_revision_and_display_change_keep_stable_objects_scope_and_precision(self):
        original=copy.deepcopy(self.source)
        self.catalog['versions']=['new context'];self.catalog['models'][0]['name']='Renamed'
        result,_=continuation.resolve(self.source,self.ticket,self.catalog,{},self.request)
        self.assertEqual(result['reported_figure'],self.proposal['reported_figure'])
        self.assertEqual(result['filters'],self.proposal['filters'])
        self.assertEqual(self.source,original)

    def test_same_visual_id_moved_to_another_page_refuses(self):
        self.catalog['models'][0]['visuals'][0]['page_id']='different-page'
        with self.assertRaises((ValueError,Conflict)):
            continuation.resolve(self.source,self.ticket,self.catalog,{},self.request)

    def test_keyed_address_and_precision_cannot_disappear(self):
        base=copy.deepcopy(self.proposal);base['target_visual']['mode']='KEYED'
        base['filters']=[{'column_id':'warehouse','operator':'in','values':['North']}]
        first=continuation.identity(base,self.source['catalog_referents'])
        for changed in ('key','precision','grouping'):
            with self.subTest(changed=changed):
                other=copy.deepcopy(base);refs=copy.deepcopy(self.source['catalog_referents'])
                if changed=='key':other['filters'][0]['values']=['South']
                if changed=='precision':other['reported_figure']['precision']={'kind':'other'}
                if changed=='grouping':refs[0]['grouping_columns']=['another-key']
                self.assertNotEqual(first,continuation.identity(other,refs))

    def test_legacy_target_without_page_evidence_is_not_silently_rebound(self):
        self.source.pop('catalog_referents')
        with self.assertRaisesRegex(Conflict,'page and cell identity'):
            continuation.resolve(self.source,self.ticket,self.catalog,{},self.request)

    def test_changed_stable_visual_refuses_even_when_title_is_the_same(self):
        self.catalog['models'][0]['visuals'][0]['target_id']='new-object'
        with self.assertRaisesRegex(Conflict,'different stable objects'):
            continuation.resolve(self.source,self.ticket,self.catalog,{},self.request)

class ReplyBudgetTests(unittest.TestCase):
    def test_real_hybrid_reply_gets_fresh_gap_cap_both_numbers_recorded(self):
        from investigator.agent_phase_budget import budget
        journal=[{'event':'DECISION'} for _ in range(12)]
        ticket={'agent_consumed_replies':['reply'],'hybrid_reply_budget':
            {'reply_id':'reply','prior_decisions':12,'previous_budget':{'steps_remaining':0}}}
        before=budget({},journal,{'step_cap':12},hybrid=True)
        after=budget(ticket,journal,{'step_cap':12},hybrid=True)
        self.assertEqual(before['steps_remaining'],0);self.assertEqual(after['steps_remaining'],12)
        self.assertEqual(after['cumulative_decisions'],12)
        journal.append({'event':'DECISION_REJECTED'})
        self.assertEqual(budget(ticket,journal,{'step_cap':12},hybrid=True)['steps_remaining'],11)
        self.assertEqual(budget(ticket,journal,{'step_cap':12},hybrid=False)['steps_remaining'],-1)

    def test_unconsumed_reply_cannot_reset_budget(self):
        from investigator.agent_phase_budget import budget
        with self.assertRaisesRegex(Conflict,'consumed user reply'):
            budget({'hybrid_reply_budget':{'reply_id':'invented','prior_decisions':0}},[],{'step_cap':12},hybrid=True)

    def test_page_choice_never_displays_opaque_identifier(self):
        from investigator.clarification_grounding import render,label
        opaque='ReportSection123456abcdef'
        catalog={'models':[{'reports':[{'id':'fabric://report','name':'Billing'}],
            'visuals':[{'report_id':'fabric://report','page_id':opaque,'page_names':[opaque,'Collections'],
                        'target_id':'visual-id','names':['Revenue']}]}]}
        choice=render('PAGE',catalog,{},report_id='fabric://report')
        self.assertEqual(choice['choices'],['Collections'])
        with self.assertRaises(Conflict):label([opaque,'fabric://internal'])

if __name__=='__main__':unittest.main()
