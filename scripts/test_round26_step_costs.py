from unittest.mock import Mock
import unittest
from investigator.ai_cost_report import summarize
from investigator.guided_intake import Catalog
from investigator.guided_text_resolver import Resolver
from test_round23_intake_queries import graph


class StepCostTests(unittest.TestCase):
    def test_extraction_tool_declares_actual_target_identifiers(self):
        from investigator.guided_text_resolver import extraction_tools
        tools=extraction_tools(Catalog(graph()))
        fields=tools[1]['input_schema']['properties']['proposal']['properties']
        self.assertEqual(fields['report']['enum'],['other','report'])
        self.assertEqual(fields['visual']['enum'],['card','othercard'])

    def test_named_visual_resolves_its_unique_native_page(self):
        from investigator.guided_intake import prefill
        value=prefill('Report Card is wrong',{'report':'report','visual':'card',
            'issue_type':'NUMBER_LOOKS_WRONG'},Catalog(graph()),provenance={'visual':[2,2]})
        self.assertEqual(value['status'],'READY')
        self.assertEqual(value['visual'],'card')
        self.assertEqual(value['page'],'page')

    def test_costs_are_actual_and_cache_ratio_is_token_weighted(self):
        events = [{'event':'AI_NORMALIZED_USAGE','step':'INTAKE','provider':'openai','model':'cheap',
                   'cost_microdollars':cost,'normalized_usage':{'input_tokens':total,'cached_input_tokens':cached}}
                  for cost,total,cached in [(10,100,0),(2,900,900)]]
        row = summarize(events)[0]
        self.assertEqual(row['actual_microdollars'],12)
        self.assertEqual(row['mean_microdollars_per_call'],6)
        self.assertEqual(row['cache_read_ratio'],.9)
        self.assertEqual([c['actual_microdollars']for c in row['calls_detail']],[10,2])

    def test_intake_prefix_is_identical_across_tickets_and_retries(self):
        model = Mock(); model.complete.return_value = {'content':[]}
        resolver = Resolver(catalog=Catalog(graph()),model=model,record=Mock())
        resolver.resolve('First report concern')
        resolver.resolve('A different figure and a different date')
        systems = [c.kwargs['system']for c in model.complete.call_args_list]
        self.assertEqual(len(set(systems)),1)
        self.assertIn('native_objects',systems[0])
        self.assertNotIn('First report concern',systems[0])

    def test_intake_is_a_separately_configurable_step(self):
        from investigator.adapters.provider_runtime import select
        from test_round26_provider_runtime import config
        routing={'default':config('openai','strong'),
                 'steps':{k:config('openai','cheap')for k in ('INTAKE','SCREENSHOT','SUMMARY')}}
        for step in ('INTAKE','SCREENSHOT','SUMMARY'):
            self.assertEqual(select(routing,tenant='fixture',step=step)['model'],'cheap')
        self.assertEqual(select(routing,tenant='fixture',step='INVESTIGATOR')['model'],'strong')
