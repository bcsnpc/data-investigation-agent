import unittest
from investigator import ticket_protocol as protocol


def question(field):
    return {'id':field.lower(),'field':field,'question':'Choose '+field,
            'choices':[{'id':'first','label':'First option','highlight':None},
                       {'id':'second','label':'Second option','highlight':None}]}


class TicketProtocolTests(unittest.TestCase):
    def test_unique_referent_requires_original_intake_validation_and_never_selects_comparison(self):
        from test_intake_extraction import fixture
        from investigator import intake_extraction
        raw,payload=fixture('In Report, Global card Quantity shows 16.',
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}],
            figures=[{'quote':'16','role':'PRIMARY','state':'NUMBER','precision_quote':None}])
        proposal=intake_extraction.resolve(raw,payload)
        ticket=protocol.settle_from_intake(protocol.new('ticket'),proposal,payload)
        self.assertEqual(set(ticket['settled']),{'NUMBER','REPORT_PAGE'})
        with self.assertRaisesRegex(ValueError,'consequential'):
            protocol.transition(ticket,'INVESTIGATING',actor='AGENT',detail={})
        required=protocol.settle_from_intake(protocol.new('ticket'),proposal,payload,must_confirm=['NUMBER'])
        self.assertNotIn('NUMBER',required['settled'])
        import copy
        tampered=copy.deepcopy(proposal);tampered['target_visual']['target_id']='matrix'
        with self.assertRaises(ValueError):protocol.settle_from_intake(protocol.new('ticket'),tampered,payload)

    def ready(self):
        ticket=protocol.ask(protocol.new('ticket'),[question(f) for f in protocol.FIELDS])
        ticket=protocol.answer(ticket,[{'question_id':f.lower(),'choice_id':'first'} for f in protocol.FIELDS])
        return protocol.transition(ticket,'INVESTIGATING',actor='AGENT',detail={})

    def test_only_three_user_uncertainties_are_expressible(self):
        for field in ('FILTER','DEFINITION','LINEAGE','DATE'):
            with self.assertRaises(Exception):protocol.validate_questions([question(field)])

    def test_unsettled_fields_cannot_proceed(self):
        with self.assertRaisesRegex(ValueError,'consequential'):
            protocol.transition(protocol.new('ticket'),'INVESTIGATING',actor='AGENT',detail={})
        ticket=protocol.ask(protocol.new('ticket'),[question('NUMBER')])
        ticket=protocol.answer(ticket,[{'question_id':'number','choice_id':'first'}])
        with self.assertRaisesRegex(ValueError,'consequential'):
            protocol.transition(ticket,'INVESTIGATING',actor='AGENT',detail={})

    def test_closed_answers_cannot_inject_a_scope_or_unoffered_choice(self):
        questions=[question('NUMBER')]
        for answers in ([{'question_id':'number','choice_id':'missing'}],
                        [{'question_id':'number','choice_id':'first','target_id':'invented'}],
                        [{'question_id':'wrong','choice_id':'first'}],
                        [{'question_id':'number','choice_id':'first'}]*2):
            with self.assertRaises(Exception):protocol.confirmed(questions,answers)

    def test_confirmation_is_not_itself_a_dispatch(self):
        t=protocol.ask(protocol.new('ticket'),[question('NUMBER')])
        result=protocol.answer(t,[{'question_id':'number','choice_id':'first'}])
        self.assertEqual(result['state'],'CLARIFYING')
        self.assertEqual(result['confirmed']['NUMBER']['authority'],'USER_CONFIRMED')
        self.assertEqual(result['questions'],[])
        self.assertEqual(t['confirmed'],{})

    def test_questions_conserved_and_distinct(self):
        q=question('NUMBER')
        with self.assertRaises(ValueError):protocol.validate_questions([q,q])
        q['choices'].append(q['choices'][0])
        with self.assertRaises(ValueError):protocol.validate_questions([q])

    def test_highlight_bounds(self):
        q=question('NUMBER');q['choices'][0]['highlight']={'image_id':'image','x':.9,'y':0,'width':.2,'height':1}
        with self.assertRaisesRegex(ValueError,'outside'):protocol.validate_questions([q])

    def test_limit_holds_without_discarding_choices(self):
        ticket=protocol.ask(protocol.new('ticket'),[question('NUMBER')],maximum=1)
        result=protocol.ask(ticket,[question('COMPARISON')],maximum=1)
        self.assertEqual(result['state'],'HELD')
        self.assertEqual(result['questions'][0]['field'],'COMPARISON')
        self.assertEqual(result['rounds'],1)

    def test_follow_up_reuses_only_the_same_context_scope_and_cell(self):
        ticket=self.ready()
        ticket=protocol.retain(ticket,context='context',scope={'filter':'North'},cell='card',receipt={'id':'receipt'})
        ticket=protocol.transition(ticket,'FINDINGS_SHARED',actor='AGENT',detail={})
        ticket=protocol.transition(ticket,'INVESTIGATING',actor='USER',detail={'follow_up':True})
        reused=protocol.reuse(ticket,context='context',scope={'filter':'North'},cell='card',purpose='EXPLAIN_RECORDED_RESULT')
        self.assertEqual(reused['receipt'],{'id':'receipt'})
        self.assertIn('not a new reading',reused['qualification'])
        self.assertIsNone(protocol.reuse(ticket,context='context',scope={'filter':'North'},cell='card',purpose='CURRENT_VALUE'))
        for context,scope,cell in [('changed',{'filter':'North'},'card'),('context',{'filter':'South'},'card'),('context',{'filter':'North'},'other')]:
            self.assertIsNone(protocol.reuse(ticket,context=context,scope=scope,cell=cell,purpose='EXPLAIN_RECORDED_RESULT'))
        with self.assertRaises(ValueError):
            protocol.retain(ticket,context='context',scope={'filter':'North'},cell='card',receipt={'id':'replacement'})

    def test_nothing_closes_without_a_human(self):
        ticket=protocol.transition(self.ready(),'FINDINGS_SHARED',actor='AGENT',detail={})
        with self.assertRaisesRegex(ValueError,'cannot close'):
            protocol.transition(ticket,'CLOSED',actor='AGENT',detail={})
        self.assertEqual(protocol.transition(ticket,'CLOSED',actor='USER',detail={})['state'],'CLOSED')

    def test_business_and_technical_states_leave_original_evidence_intact(self):
        ticket=protocol.transition(self.ready(),'FINDINGS_SHARED',actor='AGENT',detail={'receipt':'receipt'})
        for state in ('BUSINESS_VALIDATION','TECH_HANDOFF'):
            routed=protocol.transition(ticket,state,actor='AGENT',detail={'owner':'configured-owner'})
            self.assertEqual(routed['history'][-2]['detail'],{'receipt':'receipt'})
            self.assertEqual(routed['state'],state)

    def test_owner_closure_requires_the_named_handoff_owner(self):
        ticket=protocol.transition(self.ready(),'FINDINGS_SHARED',actor='AGENT',detail={})
        ticket=protocol.transition(ticket,'BUSINESS_VALIDATION',actor='AGENT',detail={'owner':'business-owner'})
        for detail in ({},{'owner':'someone-else'}):
            with self.assertRaisesRegex(ValueError,'named handoff owner'):
                protocol.transition(ticket,'CLOSED',actor='OWNER',detail=detail)
        self.assertEqual(protocol.transition(ticket,'CLOSED',actor='OWNER',detail={'owner':'business-owner'})['state'],'CLOSED')


if __name__=='__main__':unittest.main()
