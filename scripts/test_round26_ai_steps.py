from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock
import unittest
from investigator.ai_steps import Steps
from investigator.shared_state import SharedState


class AIStepsTests(unittest.TestCase):
    def test_prose_helper_response_retries_once_with_explicit_structured_contract(self):
        steps=Steps(configuration={},tenant='t',state=None,record=Mock())
        model=Mock()
        model.complete.side_effect=[{'stop_reason':'end_turn','content':[{'type':'text','text':'A summary.'}]},
            {'stop_reason':'tool_use','content':[{'type':'tool_use','name':'resolve_intake','input':{'ok':True}}]}]
        steps.model=Mock(return_value=model)
        result=steps.generate(step='SUMMARY',case_id='c',instructions='Summarize.',payload={},
                              schema={'type':'object','required':['ok'],'properties':{'ok':{'type':'boolean'}}})
        self.assertEqual(result,{'ok':True})
        self.assertEqual(model.complete.call_count,2)
        first,second=model.complete.call_args_list
        self.assertEqual(first.kwargs['system'],second.kwargs['system'])
        self.assertIn('calling resolve_intake exactly once',second.kwargs['system'])
        self.assertEqual(len(second.kwargs['messages']),2)
        self.assertEqual(steps.record.call_args.args[0]['event'],'STRUCTURED_AI_RETRY')

    def test_azure_runs_end_to_end_with_fake_endpoint_and_owner_funded_offline_budget(self):
        import json,time
        from unittest.mock import patch
        from investigator.adapters.provider_runtime import client
        from investigator.provider_budget import ensure_account
        with TemporaryDirectory() as directory:
            state=SharedState.offline(Path(directory)/'state.sqlite');state.migrate()
            account=ensure_account(state,'azure_openai',time.time())
            self.assertEqual(int(state.totals(account)['ceiling']),0)
            # Test owner provisions the fake-only account. No native Azure call,
            # deployment or live budget is created by this test or the worker.
            with state.transaction() as db:
                db.execute('UPDATE state_accounts SET ceiling=1000000 WHERE identity=?',(account,))
            config={'provider':'azure_openai','endpoint':'https://synthetic.openai.azure.com/openai/v1',
                    'model':'synthetic','gateway_identity':'model','worker_identity':'worker',
                    'secret_reference':{},'rate_card':{'input_rate':'1','output_rate':'2',
                    'source':'https://example.test/pricing','observed_at':'2026-11-01'}}
            send=Mock(return_value={'id':'fake','model':'synthetic','status':'completed',
                'output':[{'type':'function_call','call_id':'one','name':'resolve_intake','arguments':json.dumps({'ok':True})}],
                'usage':{'input_tokens':100,'output_tokens':4,'input_tokens_details':{'cached_tokens':80}}})
            def factory(c,**ports):return client(c,**ports,send=send)
            steps=Steps(configuration={'default':config},tenant='test',state=state,record=Mock(),client_factory=factory)
            with patch('investigator.adapters.managed_identity.validate_secret_reference'), \
                    patch('investigator.provider_budget.policy',return_value={'ceiling_microdollars':1000000,'warning_microdollars':800000}):
                result=steps.generate(step='SUMMARY',case_id='fake-azure',instructions='fixed',payload={},
                    schema={'type':'object','properties':{'ok':{'type':'boolean'}},'required':['ok']})
            self.assertEqual(result,{'ok':True})
            self.assertEqual(send.call_args.args[1],config['endpoint']+'/responses')
            self.assertGreater(int(state.totals(account)['charged']),0)

    def test_all_structured_steps_use_configured_client_and_shared_case_budget(self):
        with TemporaryDirectory() as directory:
            state = SharedState.offline(Path(directory) / 'state.sqlite'); state.migrate()
            config = {'provider': 'openai', 'model': 'synthetic', 'gateway_identity': 'model', 'worker_identity': 'worker',
                      'secret_reference': {}, 'rate_card': {'input_rate': '1', 'output_rate': '2',
                      'source': 'https://example.test/pricing', 'observed_at': '2026-11-01'}}
            transport = Mock(); transport.complete.return_value = {'stop_reason': 'tool_use', 'content': [
                {'type': 'tool_use', 'name': 'resolve_intake', 'input': {'ok': True}}]}
            factory = Mock(return_value=transport)
            steps = Steps(configuration={'default': config}, tenant='test', state=state, record=Mock(), client_factory=factory,
                          investigator_configuration={**config, 'provider': 'anthropic', 'model': 'other'})
            for step in ('SCREENSHOT', 'SUMMARY', 'ENRICHMENT', 'WRITER', 'GRADING', 'REVIEWER', 'SMOKE'):
                value = steps.generate(step=step, case_id='same', instructions='fixed', payload={'data': 'synthetic'},
                    schema={'type': 'object', 'required': ['ok'], 'properties': {'ok': {'type': 'boolean'}}})
                self.assertEqual(value, {'ok': True})
                self.assertEqual(factory.call_args.kwargs['budget'].case_id, 'same')
                self.assertEqual(factory.call_args.kwargs['budget'].provider, 'openai')
            self.assertEqual(factory.call_count, 7)

    def test_live_grading_cannot_omit_measured_provider_or_grade_same_vendor(self):
        config = {'provider': 'openai', 'model': 'synthetic', 'rate_card': {}, 'secret_reference': {},
                  'gateway_identity': 'model', 'worker_identity': 'worker'}
        steps = Steps(configuration={'default': config}, tenant='t', state=None, record=Mock())
        with self.assertRaisesRegex(ValueError, 'MEASURED_INVESTIGATOR'):
            steps.model('GRADING', 'c')
        steps.investigator_configuration = config
        with self.assertRaisesRegex(ValueError, 'DIFFERENT_PROVIDER'):
            steps.model('GRADING', 'c')

    def test_invalid_structured_output_is_not_delivered(self):
        steps = Steps(configuration={}, tenant='t', state=None, record=Mock())
        model = Mock(); model.complete.return_value = {'stop_reason': 'end_turn', 'content': []}
        steps.model = Mock(return_value=model)
        with self.assertRaisesRegex(ValueError, 'UNESTABLISHED'):
            steps.generate(step='WRITER', case_id='c', instructions='s', payload={}, schema={'type': 'object'})
        self.assertEqual(model.complete.call_count,2)
