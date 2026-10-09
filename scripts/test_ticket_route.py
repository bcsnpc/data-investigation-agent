import copy
import unittest
from investigator import ticket_protocol as protocol, intake_confirmation, ticket_route
from investigator.onboarding import digest
from investigator.question_kind import UnimplementedRoute


def route(value):
    q={'id':'comparison','field':'COMPARISON','question':'What are you comparing against?',
       'choices':[{'id':value,'label':value,'highlight':None}]}
    ticket=intake_confirmation.offer(protocol.new('ticket'),[q],{
        digest(q)+'/'+value:{'route':value}},request_text='Question',models=[])
    ticket=protocol.answer(ticket,[{'question_id':'comparison','choice_id':value}])
    return ticket_route.declared(intake_confirmation.build(ticket,'Question'))


class TicketRouteTests(unittest.TestCase):
    def test_only_recorded_comparison_can_establish_route(self):
        value=route('APPLICATION');self.assertEqual(ticket_route.validate(value,'Question'),value)
        for wrong in ('STALE','invented'):
            bad=copy.deepcopy(value);bad['route']=wrong
            with self.assertRaises(Exception):ticket_route.validate(bad)
        with self.assertRaises(ValueError):ticket_route.validate(value,'Different question')

    def test_stale_and_looks_wrong_request_available_freshness_without_a_schedule_claim(self):
        for value in ('STALE','LOOKS_WRONG'):
            self.assertTrue(ticket_route.wants_freshness({'ticket_route':route(value)}))
        self.assertFalse(ticket_route.wants_freshness({'ticket_route':route('APPLICATION')}))
        self.assertTrue(ticket_route.wants_freshness({'question_kind':{'kind':'FRESHNESS'}}))

    def test_unimplemented_report_and_business_routes_refuse_before_any_adapter_work(self):
        from investigator.process_debugging import vertical
        class NeverRead:
            def __getattr__(self,name):raise AssertionError('Adapter was called: '+name)
        for value in ('OTHER_REPORT','BUSINESS_MEANING'):
            with self.subTest(route=value),self.assertRaises(UnimplementedRoute):
                vertical(NeverRead(),'measure',{'ticket_route':route(value)})

    def test_procedure_projection_carries_the_original_route_unchanged(self):
        from investigator.definition_target import server_evidence,procedure_scope
        value=route('LOOKS_WRONG')
        envelope={'filters':[],'dimension_ids':[],'ticket_route':value}
        self.assertEqual(server_evidence(envelope)['ticket_route'],value)
        self.assertEqual(procedure_scope(envelope)['ticket_route'],value)
        copied=procedure_scope(envelope);copied['ticket_route']['route']='APPLICATION'
        self.assertEqual(envelope['ticket_route'],value)


if __name__=='__main__':unittest.main()
