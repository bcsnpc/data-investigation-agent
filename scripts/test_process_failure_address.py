import copy
import unittest
from unittest.mock import patch
import test_flexible_investigation as fixture
import test_report_scoped_cells as cells
from test_process_debugging import Adapter
from investigator import read_address,process_failure,process_outcomes,refusal_synthesis
from investigator.adaptive_runtime import AdaptiveRuntime
from investigator.process_debugging import VERSION,Probe,vertical


def broken_walk(*args):
    raise ValueError('Synthetic walk failed.')


class ProcessFailureAddressTests(unittest.TestCase):
    def test_walk_exception_retains_type_message_location_and_renders_failure(self):
        helper=fixture.DynamicTests();helper.setUp();self.addCleanup(helper.doCleanups)
        envelope=copy.deepcopy(helper.envelope);envelope['strategy']=VERSION
        agent=AdaptiveRuntime(helper.runtime,lambda _:self.fail('No planner'))
        identity=agent.create(envelope,'synthetic-process-failure')['id']
        with patch('investigator.process_debugging.vertical',side_effect=broken_walk):state=agent.run(identity)
        self.assertEqual(state['stop_reason'],'PROCESS_FAILED')
        detail=next(e['detail'] for e in state['events'] if e['kind']=='PROCESS_FAILED')
        self.assertEqual((detail['error_type'],detail['message'],detail['module']),
                         ('ValueError','Synthetic walk failed.','test_process_failure_address.py'))
        self.assertIsInstance(detail['line'],int)
        for output in refusal_synthesis.render(state).values():
            if isinstance(output,dict) and 'explanation' in output:
                self.assertIn('Reason: Synthetic walk failed.',output['explanation']['text'])
                self.assertEqual(output['explanation']['text'].count('Synthetic walk failed.'),1)
                self.assertNotIn('TOOL_UNAVAILABLE',output['explanation']['text'])

    def test_dynamic_exception_data_is_not_recorded(self):
        secret_business_value='sensitive customer value'
        try:raise ValueError(secret_business_value)
        except ValueError as exc:detail=process_failure.capture(exc)
        self.assertNotIn(secret_business_value,str(detail));self.assertTrue(detail['message_redacted'])

    def test_failure_without_diagnostics_cannot_be_constructed(self):
        from investigator.process_receipts import refusal
        with self.assertRaisesRegex(ValueError,'safe message and failing location'):
            refusal('PROCESS_FAILED','A failure.','failed')

    def test_missing_baseline_is_a_valid_refusal_not_no_comparable_path(self):
        adapter=Adapter(['top','lower'],{},not_comparable=('lower',))
        original=adapter.evaluate
        adapter.evaluate=lambda layer,m,s:Probe('UNAVAILABLE','top',reason='Diagnostic read cap stopped the presentation quantity probe.') if layer['id']=='top' else original(layer,m,s)
        assessment=vertical(adapter,'measure',{})
        observations=assessment.pop('_observations')
        process_outcomes.validate(assessment,{o['id']:o for o in observations})
        self.assertEqual(assessment['classification'],'NO_KNOWN_PATTERN')
        self.assertEqual(assessment['support']['process']['baseline_above']['status'],'NOT_ESTABLISHED')

    def test_address_kind_is_required_even_for_empty_baseline(self):
        for bad in (None,{}, {'restrictions':[]},{'kind':'BASELINE'}):
            with self.subTest(bad=bad),self.assertRaises(ValueError):read_address.validate(bad)
        self.assertEqual(read_address.validate(read_address.baseline([])),{'kind':'BASELINE','restrictions':[]})


class AddressMemoizationTests(unittest.TestCase):
    setUp=cells.ScopedTests.setUp
    part=cells.ScopedTests.part
    modify=cells.ScopedTests.modify
    no_predicates=cells.ScopedTests.no_predicates
    def test_baseline_and_unrestricted_cell_are_distinct_original_probes(self):
        self.no_predicates()
        from investigator import declared_reproduction
        result=declared_reproduction.run(self.adapter,self.layer,self.measure['id'],self.scope)
        reads=[o for o in result['observations'] if 'declared_context_read' in o.get('process_roles',[])]
        self.assertEqual({o['read_address']['kind'] for o in reads},{'BASELINE','CELL'})
        self.assertEqual(len({o['id'] for o in reads}),2)
        self.assertEqual(len(self.requests),2)
        self.assertEqual(len({r['query'] for r in self.requests}),1)
        marker=result['cells'][0]['finding'];originals={o['id']:o for o in result['observations']}
        baseline=next(o for o in reads if o['read_address']['kind']=='BASELINE')
        del baseline['read_address']
        with self.assertRaisesRegex(ValueError,'explicit address kind'):declared_reproduction.validate(marker,originals)
