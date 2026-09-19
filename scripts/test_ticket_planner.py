import copy
from contextlib import closing
import json
from pathlib import Path
import tempfile
import unittest
from uuid import uuid4
from unittest.mock import patch, MagicMock
from types import SimpleNamespace

from lineage_graph import Graph
from ticket_workflow import TicketStore
from ticket_planner import validate_plan, plan_ticket, azure_generate


class PlannerTests(unittest.TestCase):
    def setUp(self):
        self.ticket = dict(title='Cash question', report='Executive Sales', description='Check USD net cash',
                           metric='Net Cash', currency='USD')
        self.reports = [dict(id='report1', name='Executive Sales', metrics=['Net Cash', 'Order Count'])]
        self.plan = dict(report_id='report1', metric='Net Cash', currency='USD', order_id=None, questions=[])

    def test_valid_plan_never_executes(self):
        result = validate_plan(self.plan, self.ticket, self.reports)
        self.assertEqual(result['status'], 'DRAFT_REQUIRES_REVIEW')
        self.assertFalse(result['executable'])
        self.assertFalse(result['automatic_defect_routing'])

    def test_rejects_invented_scope_and_execution_fields(self):
        for changes in [{'report_id': 'invented'}, {'metric': 'Revenue'}, {'currency': 'EUR'},
                        {'order_id': "'; DROP TABLE orders"}, {'sql': 'SELECT 1'},
                        {'classification': 'TECHNICAL_DEFECT'}, {'questions': [42]}]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                validate_plan({**self.plan, **changes}, self.ticket, self.reports)

    def test_missing_scope_requires_question(self):
        ticket = {k: v for k, v in self.ticket.items() if k not in ('metric', 'currency')}
        plan = {**self.plan, 'currency': None}
        with self.assertRaises(ValueError):
            validate_plan(plan, ticket, self.reports)
        plan['questions'] = ['Which currency?']
        self.assertEqual(validate_plan(plan, ticket, self.reports)['status'], 'NEEDS_INPUT')

    def test_explicit_order_cannot_be_changed(self):
        with self.assertRaises(ValueError):
            validate_plan(self.plan, {**self.ticket, 'order_id': 'ORD-000002'}, self.reports)

    def test_persisted_draft_and_failure_leave_ticket_untouched(self):
        with tempfile.TemporaryDirectory() as directory:
            store = TicketStore(Path(directory) / 'workflow.sqlite')
            identity, _ = store.submit(self.ticket, str(uuid4()), str(uuid4()))
            graph = Graph([dict(id='report1', kind='Report', name='Executive Sales'),
                           dict(id='measure1', kind='Measure', name='Net Cash')])
            graph.edge('measure1', 'report1', 'binding', 'report1', 'test')
            draft = plan_ticket(store, identity, graph, lambda _: (copy.deepcopy(self.plan), {'model': 'test-double'}))
            self.assertEqual(draft['status'], 'DRAFT_REQUIRES_REVIEW')
            def fail(_): raise RuntimeError('secret provider response')
            failure = plan_ticket(store, identity, graph, fail)
            self.assertEqual(failure['status'], 'PLANNING_FAILED')
            self.assertNotIn('secret', json.dumps(failure))
            self.assertEqual(store.get(identity)['status'], 'QUEUED')
            with closing(store.connect()) as db:
                self.assertEqual(db.execute('SELECT COUNT(*) FROM ticket_plans').fetchone()[0], 2)

    def test_missing_or_untrusted_endpoint_fails_before_sdk(self):
        for endpoint in ['', 'http://example.com', 'https://x.openai.azure.com.evil.org',
                         'https://x.openai.azure.com/?redirect=evil']:
            with patch.dict('os.environ', {'AZURE_OPENAI_ENDPOINT': endpoint}, clear=True), self.assertRaises(ValueError):
                azure_generate({})


    def test_provider_contract_refusal_and_incomplete(self):
        sdk = MagicMock()
        client = sdk.OpenAI.return_value.__enter__.return_value
        response = SimpleNamespace(status='completed', output=[], output_text=json.dumps(self.plan),
                                   id='response-test', model='deployment-test', usage=None)
        client.responses.create.return_value = response
        env = dict(AZURE_OPENAI_ENDPOINT='https://test.openai.azure.com',
                   AZURE_OPENAI_DEPLOYMENT='deployment-test', AZURE_OPENAI_API_KEY='test-placeholder')
        with patch.dict('os.environ', env, clear=True), patch.dict('sys.modules', {'openai': sdk}):
            value, metadata = azure_generate({'ticket': self.ticket})
            self.assertEqual(value, self.plan)
            self.assertEqual(metadata['response_id'], 'response-test')
            request = client.responses.create.call_args.kwargs
            self.assertFalse(request['store'])
            self.assertTrue(request['text']['format']['strict'])
            self.assertNotIn('tools', request)
            azure_generate({},generation_options={'timeout_seconds':120,'max_output_tokens':4000,'reasoning_effort':'medium'})
            request=client.responses.create.call_args.kwargs
            self.assertEqual(request['reasoning'],{'effort':'medium'})
            self.assertEqual(request['max_output_tokens'],4000)
            self.assertEqual(sdk.OpenAI.call_args.kwargs['timeout'],120)
            self.assertEqual(sdk.OpenAI.call_args.kwargs['max_retries'],0)
            for options in ({'max_output_tokens':True},{'timeout_seconds':121},{'reasoning_effort':'unknown'},{'endpoint':'untrusted'}):
                with self.assertRaises(ValueError):azure_generate({},generation_options=options)
            response.status = 'incomplete'
            with self.assertRaises(ValueError): azure_generate({})
            response.status = 'completed'
            response.output = [SimpleNamespace(type='message', content=[SimpleNamespace(type='refusal')])]
            with self.assertRaises(ValueError): azure_generate({})

    def test_provider_failure_categories_never_preserve_output_or_messages(self):
        from investigator.generation_policy import ProviderResponseError,error_summary
        sdk=MagicMock();client=sdk.OpenAI.return_value.__enter__.return_value
        response=SimpleNamespace(status='incomplete',output=[],output_text='secret partial text',
            incomplete_details=SimpleNamespace(reason='max_output_tokens'),
            usage=SimpleNamespace(model_dump=lambda:{'input_tokens':10,'output_tokens':1500,'secret':'private'}))
        client.responses.create.return_value=response
        env={'AZURE_OPENAI_ENDPOINT':'https://test.openai.azure.com','AZURE_OPENAI_DEPLOYMENT':'test','AZURE_OPENAI_API_KEY':'placeholder'}
        with patch.dict('os.environ',env,clear=True),patch.dict('sys.modules',{'openai':sdk}):
            for status,reason,code in [('incomplete','max_output_tokens','OUTPUT_TOKEN_LIMIT'),
                    ('incomplete','content_filter','CONTENT_FILTER'),('incomplete','secret','INCOMPLETE'),
                    ('failed',None,'RESPONSE_NOT_COMPLETED')]:
                response.status=status;response.incomplete_details.reason=reason
                with self.assertRaises(ProviderResponseError) as caught:azure_generate({})
                self.assertEqual(error_summary(caught.exception)['response_failure'],code)
                self.assertEqual(caught.exception.usage,{'input_tokens':10,'output_tokens':1500})
                self.assertNotIn('secret',str(caught.exception)+json.dumps(error_summary(caught.exception)))
            response.status='completed'
            with self.assertRaises(ProviderResponseError) as caught:azure_generate({})
            self.assertEqual(caught.exception.code,'INVALID_JSON')
            response.output_text='{}'
            with self.assertRaises(ProviderResponseError) as caught:azure_generate({},decision_tool=True)
            self.assertEqual(caught.exception.code,'DECISION_CALL_SHAPE')
            response.output=[SimpleNamespace(type='message',content=[SimpleNamespace(type='refusal',refusal='private')])]
            with self.assertRaises(ProviderResponseError) as caught:azure_generate({})
            self.assertEqual(caught.exception.code,'REFUSAL')


if __name__ == '__main__': unittest.main()
