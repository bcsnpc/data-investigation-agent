"""Offline provider/tool fixtures. These are not scored tickets or live runs."""
from contextlib import nullcontext
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock,patch
import unittest
from investigator.shared_state import SharedState
from investigator.reasoning_budget import RateCard,TicketBudget
from investigator.model_spend import SpendHold
from investigator.ai_investigation import Investigator,schema
from investigator.investigative_queries import Queries
from investigator.round23_calendar import require_live_window
from investigator.adapters.reasoning_anthropic import Client,choose_model
from test_round23_intake_queries import sql_objects


NOW=datetime(2026,11,1,tzinfo=timezone.utc).timestamp()


class BudgetTests(unittest.TestCase):
    def test_postgres_charged_query_binds_like_pattern_instead_of_literal_percent(self):
        state=Mock();state.backend='postgresql';state.sql.return_value.fetchall.return_value=[('120',)]
        budget=TicketBudget(state,case_id='case',owner='worker',rate=Mock())
        self.assertEqual(budget._charged('db','month'),120)
        args=state.sql.call_args.args
        self.assertNotIn('%',args[1])
        self.assertEqual(args[2],('model-microdollars:%','case'))

    def setUp(self):
        folder=TemporaryDirectory();self.addCleanup(folder.cleanup)
        self.state=SharedState.offline(Path(folder.name)/'state.sqlite');self.state.migrate()
        self.rate=RateCard(model='offline-claude',input_rate='5',output_rate='20',
                           source='https://example.test/offline-rate',observed_at='2026-10-26')
        self.budget=TicketBudget(self.state,case_id='case',owner='worker',rate=self.rate,clock=lambda:NOW)
    def body(self):return {'model':'offline-claude','max_tokens':100,'system':'test','messages':[],'tools':[]}
    def test_reserved_unknown_and_settled_are_kept_in_existing_month_account(self):
        identity=self.budget.reserve(self.body());self.budget.settle(identity)
        snapshot=self.state.snapshot('model-microdollars:2026-11')
        self.assertEqual(snapshot['reservations'][0]['status'],'UNCERTAIN')
        self.assertGreater(int(snapshot['charged']),0)
        identity=self.budget.reserve(self.body());self.budget.settle(identity,{'input_tokens':100,'output_tokens':10})
        self.budget.settle(identity)
        rows=self.state.snapshot('model-microdollars:2026-11')['reservations']
        self.assertEqual(next(r for r in rows if r['identity']==identity)['status'],'SETTLED')
        self.assertEqual(len(snapshot['reservations']),1)
    def test_ticket_cap_shared_by_workers_and_warning_not_stop(self):
        with patch.object(self.rate,'price',return_value=500000):
            first=self.budget.reserve(self.body())
            self.assertTrue(self.budget.status()['warning'])
            other=TicketBudget(self.state,case_id='case',owner='other',rate=self.rate,clock=lambda:NOW)
            other.reserve(self.body())
            with self.assertRaisesRegex(SpendHold,'TICKET_MODEL_EXHAUSTED'):self.budget.reserve(self.body())
        self.assertEqual(self.budget.status()['charged_microdollars'],1000000)
    def test_authoritative_old_monthly_ceiling_cannot_be_bypassed(self):
        self.budget.status()
        with self.state.transaction() as db:db.execute('UPDATE state_accounts SET ceiling=100')
        with self.assertRaisesRegex(SpendHold,'MONTHLY_MODEL_EXHAUSTED'):self.budget.reserve(self.body())
    def test_month_rolls_without_reset_and_counters_not_refunded(self):
        self.budget.reserve(self.body())
        old=self.state.snapshot('model-microdollars:2026-11')['charged']
        self.budget.clock=lambda:datetime(2026,12,1,tzinfo=timezone.utc).timestamp()
        self.assertEqual(self.budget.status()['charged_microdollars'],int(old))
        self.assertEqual(self.state.snapshot('model-microdollars:2026-12')['charged'],'0')
        self.assertEqual(self.state.snapshot('model-microdollars:2026-11')['charged'],old)
    def test_no_unknown_model_price_fallback(self):
        body=self.body();body['model']='unpriced-model'
        with self.assertRaises(SpendHold):self.budget.reserve(body)
    def test_cache_usage_is_charged_not_free(self):
        identity=self.budget.reserve(self.body())
        self.budget.settle(identity,{'input_tokens':2,'output_tokens':1,'cache_creation_input_tokens':20,'cache_read_input_tokens':30})
        self.assertEqual(self.budget.status()['charged_microdollars'],280)
    def test_owner_policy_migration_preserves_every_charge_and_latch(self):
        from provision_model_month import round23_policy
        self.budget.reserve(self.body())
        with self.state.transaction() as db:db.execute('UPDATE state_accounts SET ceiling=40000000,violated=1')
        before=self.state.snapshot('model-microdollars:2026-11')
        receipt=round23_policy(self.state,NOW)
        self.assertEqual(receipt['after']['ceiling'],'150000000')
        self.assertEqual({k:v for k,v in before.items() if k!='ceiling'},
                         {k:v for k,v in receipt['after'].items() if k!='ceiling'})
        with self.assertRaisesRegex(SpendHold,'VIOLATION'):self.budget.reserve(self.body())

    def test_owner_request_policy_is_cloud_authority_without_counter_reset(self):
        from provision_model_month import round23_request_policy
        from investigator.build_phase import physical_status,check_shared_request_policy
        receipt=round23_request_policy(self.state,NOW)
        self.assertEqual(receipt['before']['total_limit'],6000)
        self.assertEqual(receipt['after']['total_limit'],9000)
        with self.state.transaction() as db:
            status=physical_status([],[],NOW)
            check_shared_request_policy(self.state,db,NOW,status,'INVESTIGATION')
            policy=receipt['after'];policy['limits']['INVESTIGATION']=1
            import json
            db.execute('UPDATE state_documents SET body=? WHERE namespace=?',(json.dumps(policy),'build_phase_policy'))
            status['used']['INVESTIGATION']=1
            from investigator.usage_governance import UsageHold
            with self.assertRaisesRegex(UsageHold,'AUTHORITATIVE'):
                check_shared_request_policy(self.state,db,NOW,status,'INVESTIGATION')


class ProviderTests(unittest.TestCase):
    def test_screenshot_model_audit_omits_image_and_personal_values(self):
        from investigator.adapters.screenshot_assistance import Assistance
        values={'titles':{'visual':'Selected visual'},'visible_fields':{'name':'PRIVATE-SYNTHETIC-NAME'}}
        response={'content':[{'type':'tool_use','name':'describe_screenshot','input':values}],
                  'usage':{'input_tokens':20,'output_tokens':10}}
        send=Mock(return_value=response);client,budget=self.client(send)
        image=b'\x89PNG\r\n\x1a\n' + b'PRIVATE-SYNTHETIC-IMAGE'
        self.assertEqual(Assistance(client,lambda:{}).extract(image),values)
        import json,base64
        audit=json.dumps(client.record.call_args_list,default=str)
        self.assertNotIn('PRIVATE-SYNTHETIC-NAME',audit)
        self.assertNotIn(base64.b64encode(image).decode(),audit)
        self.assertIn('private_case_content_omitted',audit)
        self.assertEqual(send.call_args.args[2]['messages'][0]['content'][0]['type'],'image')
        budget.reserve.assert_called_once()
        with self.assertRaisesRegex(ValueError,'PNG_OR_JPEG'):
            Assistance(client,lambda:{}).extract(b'not an image')

    def test_live_date_owner_approval_supersedes_november_wait(self):
        with self.assertRaisesRegex(RuntimeError,'OFFLINE_ONLY'):require_live_window(datetime(2026,10,25,23,59,tzinfo=timezone.utc))
        require_live_window(datetime(2026,10,26,tzinfo=timezone.utc))
    def test_discovery_is_actual_listing_not_assumed_access(self):
        self.assertEqual(choose_model({'data':[{'id':'claude-opus-5-5'},{'id':'claude-sonnet-5-5'}]}),'claude-opus-5-5')
        with self.assertRaises(ValueError):choose_model({'data':[]})
        with self.assertRaises(ValueError):choose_model({'has_more':True,'data':[{'id':'claude-opus-5-5'}]})
    def client(self,send):
        budget=Mock();budget.rate.model='offline-claude';budget.reserve.return_value='reservation'
        with patch('investigator.adapters.managed_identity.validate_secret_reference'):
            self.client_value=Client(model='offline-claude',budget=budget,identity='existing-provider',
                secret_reference={'existing':'vault-reference'},record=Mock(),send=send)
        return self.client_value,budget
    def test_standard_native_tool_call_body_and_investigator_budget(self):
        response={'content':[{'type':'tool_use','id':'call','name':'run_sql','input':{}}],
                  'usage':{'input_tokens':10,'output_tokens':20}}
        send=Mock(return_value=response);client,budget=self.client(send)
        self.assertEqual(client.complete(system='stable',messages=[],tools=[]),response)
        body=send.call_args.args[2]
        self.assertEqual(body['system'][0]['text'],'stable');self.assertNotIn('key',body)
        self.assertEqual(body['system'][0]['cache_control'],{'type':'ephemeral'})
        self.assertEqual(budget.settle.call_args_list[0].args,('reservation',response['usage']))
    def test_provider_failure_keeps_charge_uncertain(self):
        client,budget=self.client(Mock(side_effect=RuntimeError('429')))
        with self.assertRaises(RuntimeError):client.complete(system='stable',messages=[],tools=[])
        budget.settle.assert_called_once_with('reservation')
    def test_rate_limit_backs_off_with_new_admissions_not_a_finding(self):
        from investigator.adapters.reasoning_anthropic import ProviderHTTPError
        send=Mock(side_effect=[ProviderHTTPError(429),{'content':[],'usage':{'input_tokens':1,'output_tokens':1}}])
        client,budget=self.client(send);client.sleep=Mock()
        client.complete(system='stable',messages=[],tools=[])
        self.assertEqual(budget.reserve.call_count,2);client.sleep.assert_called_once_with(30)
    def test_authentication_refusal_is_not_retried(self):
        from investigator.adapters.reasoning_anthropic import ProviderHTTPError
        client,budget=self.client(Mock(side_effect=ProviderHTTPError(403)));client.sleep=Mock()
        with self.assertRaises(ProviderHTTPError):client.complete(system='stable',messages=[],tools=[])
        self.assertEqual(budget.reserve.call_count,1);client.sleep.assert_not_called()
    def test_real_transport_refuses_before_reservation_in_october(self):
        client,budget=self.client(None)
        with patch('investigator.adapters.reasoning_anthropic.require_live_window',side_effect=RuntimeError('OFFLINE_ONLY')):
            with self.assertRaises(RuntimeError):client.complete(system='stable',messages=[],tools=[])
        budget.reserve.assert_not_called()


class MemoryCheckpoint:
    def __init__(self):self.value=None
    def load(self):return deepcopy(self.value)
    def save(self,value):self.value=deepcopy(value)


def tool(name,args,identity='call'):
    return {'content':[{'type':'tool_use','id':identity,'name':name,'input':args}]}


class LoopTests(unittest.TestCase):
    def assemble(self,responses,validator=None):
        self.calls=[];self.events=[]
        self.execute=Mock(return_value={'rows':[[7]]})
        queries=Queries({'gold':{'dialect':'T-SQL','objects':sql_objects()}},execute=self.execute,
                        reserve=Mock(),save=self.events.append)
        self.model=Mock();self.model.complete.side_effect=responses
        self.checkpoint=MemoryCheckpoint()
        self.candidates=Mock(return_value={'candidates':[]})
        reads={'list_candidates':{'description':'Check actual admitted candidates',
                                 'schema':schema({}),'run':self.candidates}}
        self.validator=validator or Mock(return_value={'business':'The checked quantity is 7.'})
        self.loop=Investigator(queries=queries,model=self.model,read_tools=reads,
            validate_finding=self.validator,validate_question=lambda a,c:{'question':a['question'],'choices':a['choices']},
            checkpoint=self.checkpoint,case_id='case',context={'intake':{'report':'report'},'path':['gold']},triage=[])
        return self.loop
    def test_ai_chooses_queries_not_frontier_and_repeats_use_stored_evidence(self):
        query={'layer':'gold','query':'SELECT SUM(quantity) AS total FROM dbo.Items','purpose':'recreate'}
        def finish(**kwargs):
            return tool('submit_finding',{'verdict':'as designed','cause':'Native value is 7','numbers':[7],
                        'checked':['gold'],'evidence_ids':list(self.loop.state['evidence'])[:1]})
        loop=self.assemble([tool('run_sql',query),tool('run_sql',query),finish])
        self.model.complete.side_effect=lambda **kw: self.model_responses.pop(0)(**kw) if callable(self.model_responses[0]) else self.model_responses.pop(0)
        self.model_responses=[tool('run_sql',query),tool('run_sql',query),finish]
        result=loop.run();self.assertEqual(result['status'],'ANSWERED')
        self.execute.assert_called_once();self.assertEqual(result['model_calls'],3)
        self.assertIn('Already have this as evidence',str(self.checkpoint.value['messages']))
        self.assertEqual(len({call.kwargs['system'] for call in self.model.complete.call_args_list}),1)
    def test_validation_rejection_is_specific_and_does_not_end_ticket(self):
        args={'verdict':'as designed','cause':'unsupported','numbers':[],'checked':[],'evidence_ids':['bad']}
        loop=self.assemble([tool('submit_finding',args),tool('run_sql',{'layer':'gold','query':'SELECT id FROM dbo.Items','purpose':'recreate'})])
        loop.tool_limit=2
        result=loop.run();self.assertEqual(result['status'],'UNRESOLVED')
        self.assertIn('UNKNOWN_EVIDENCE_REFERENCE',str(self.checkpoint.value['messages']))
        self.execute.assert_called_once();self.assertEqual(len(result['handoff']['queries']),1)
    def test_asking_before_checks_rejected(self):
        loop=self.assemble([tool('ask_user_choice',{'question':'Which policy applies?','choices':['A','B'],
                 'reason':'BUSINESS_POLICY','evidence_ids':[]})]);loop.tool_limit=1
        self.assertEqual(loop.run()['status'],'UNRESOLVED')
        self.assertIn('ASK_LAST_RESORT',str(self.checkpoint.value['messages']))
    def test_query_rejection_can_be_corrected_and_error_retained(self):
        loop=self.assemble([tool('run_sql',{'layer':'gold','query':'DELETE FROM dbo.Items','purpose':'recreate'}),
                            tool('run_sql',{'layer':'gold','query':'SELECT id FROM dbo.Items','purpose':'recreate'})]);loop.tool_limit=2
        result=loop.run();self.execute.assert_called_once()
        self.assertEqual(result['status'],'UNRESOLVED');self.assertEqual(len(result['handoff']['queries']),1)
    def test_unknown_pending_request_is_not_reissued_on_resume(self):
        loop=self.assemble([])
        from investigator.estate_graph_contract import digest
        self.checkpoint.value={'pins':digest(['case',loop.context,loop.triage]),'outcome':None,
            'pending':{'kind':'MODEL'},'evidence':{},'model_calls':1,'tools_used':0}
        self.assertEqual(loop.run()['status'],'UNESTABLISHED');self.model.complete.assert_not_called()
    def test_budget_stop_not_mistaken_for_empty_query(self):
        loop=self.assemble([tool('run_sql',{'layer':'gold','query':'SELECT id FROM dbo.Items','purpose':'recreate'})])
        loop.queries.reserve.side_effect=SpendHold('ticket cap')
        result=loop.run();self.assertEqual(result['status'],'BLOCKED');self.execute.assert_not_called()
    def test_completed_checkpoint_keeps_full_query_records_without_new_model_or_read(self):
        query={'layer':'gold','query':'SELECT SUM(quantity) AS total FROM dbo.Items','purpose':'recreate'}
        loop=self.assemble([tool('run_sql',query)]);loop.tool_limit=1
        first=loop.run();self.assertEqual(len(first['case']['queries']),1)
        new_queries=Queries(loop.queries.layers,execute=Mock(side_effect=AssertionError('no new read')),
                            reserve=Mock(),save=lambda _:None)
        model=Mock(side_effect=AssertionError('no new model'))
        resumed=Investigator(queries=new_queries,model=model,read_tools=loop.read_tools,checkpoint=self.checkpoint,
            case_id='case',context=loop.context,triage=loop.triage)
        result=resumed.run();self.assertEqual(result['case']['queries'],first['case']['queries'])
        model.complete.assert_not_called();new_queries.execute.assert_not_called()


if __name__=='__main__':unittest.main()
