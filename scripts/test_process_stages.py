import unittest
from types import SimpleNamespace
from investigator.process_stages import Adapter, label


class StageTests(unittest.TestCase):
    def test_started_is_visible_while_call_is_running_and_result_is_unchanged(self):
        events=[];result=object();arg=object()
        def evaluate(*args, **kwargs):
            self.assertEqual(events, [('PROCESS_STAGE_STARTED',{'stage':'walk','operation':'evaluate'})])
            self.assertEqual(args,(arg,));self.assertEqual(kwargs,{'scope':'original'})
            return result
        observed=Adapter(SimpleNamespace(evaluate=evaluate),lambda k,d:events.append((k,d)))
        self.assertIs(observed.evaluate(arg,scope='original'),result)
        self.assertEqual(events[-1],('PROCESS_STAGE_FINISHED',{'stage':'walk','operation':'evaluate','error_type':None}))

    def test_failure_records_the_same_exception_without_a_value_or_extra_read(self):
        error=ValueError('original');events=[]
        def execute(*args):raise error
        observed=Adapter(SimpleNamespace(ingestion=execute),lambda k,d:events.append((k,d)))
        with self.assertRaises(ValueError) as caught:observed.ingestion('original')
        self.assertIs(caught.exception,error)
        self.assertEqual(events[-1][1],{'stage':'source','operation':'ingestion','error_type':'ValueError'})
        self.assertNotIn('original',str(events))

    def test_application_stage_requires_declared_role_and_nonstage_calls_are_not_wrapped(self):
        events=[];delegate=SimpleNamespace(evaluate=lambda x:42, capabilities=lambda: {'evaluate'},config={
            '_estate':{'layers':[{'asset_id':'app','role':'APPLICATION'}]}})
        observed=Adapter(delegate,lambda k,d:events.append((k,d)))
        self.assertEqual(observed.capabilities(),{'evaluate'});self.assertEqual(events,[])
        self.assertEqual(observed.evaluate({'id':'app'}),42);self.assertEqual(events[0][1]['stage'],'source')
        observed.evaluate({'id':'other'});self.assertEqual(events[2][1]['stage'],'walk')
        observed.resolve_path=lambda _: 'original path'
        self.assertEqual(delegate.resolve_path('x'),'original path')
        self.assertEqual(observed.resolve_path('x'),'original path')

    def test_labels_are_engine_stage_facts_and_do_not_include_native_operation_or_error_text(self):
        self.assertEqual(label({'kind':'PROCESS_STAGE_STARTED','detail':{'stage':'reproduce','operation':'secret'}}),
                         'Checking declared report context started')
        self.assertEqual(label({'kind':'PROCESS_STAGE_FINISHED','detail':{'stage':'source','error_type':'ValueError'}}),
                         'Checking source and load evidence failed')
        self.assertIsNone(label({'kind':'CREATED'}))
        with self.assertRaises(ValueError):label({'kind':'PROCESS_STAGE_STARTED','detail':{'stage':'unknown'}})


if __name__ == '__main__':unittest.main()
