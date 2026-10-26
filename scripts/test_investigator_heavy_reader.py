import json
import unittest
from investigator.investigator_heavy_reader import HeavyReader


class HeavyReaderTests(unittest.TestCase):
    def test_default_off_and_enabled_step_receives_clean_context_and_returns_small_summary(self):
        calls = []
        def decide(payload, **kwargs):
            calls.append(payload)
            self.assertNotIn('ticket', payload)
            self.assertNotIn('case_file', payload)
            self.assertNotIn('tool_transcript', payload)
            return {'summary': 'Read the retained evidence; causal conclusions remain unestablished.',
                    'evidence_ids': payload['evidence_ids']}
        record = {'kind': 'GRAPH', 'subjects': ['node'], 'value': {'definition': 'large-fixture-content-'*12000}}
        self.assertIsNone(HeavyReader(decide).read('e1', record, step='investigate'))
        self.assertEqual(calls, [])
        reader = HeavyReader(decide, enabled_steps=['investigate'])
        self.assertIsNone(reader.read('e1', record, step='quick_facts'))
        value = reader.read('e1', record, step='investigate')
        self.assertGreater(len(calls), 1)
        self.assertEqual(value['support_ids'], ['e1'])
        self.assertTrue(value['not_finding'])
        self.assertLess(len(json.dumps(value)), 1000)
        self.assertTrue(all(len(call['raw_part']) <= 12000 for call in calls))
        self.assertEqual(value['child_model_calls'], len(calls))

    def test_child_cannot_introduce_an_evidence_reference_or_enable_itself(self):
        reader = HeavyReader(lambda *_args, **_kw: {'summary': 'Read it', 'evidence_ids': ['invented']},
                             enabled_steps=['investigate'])
        with self.assertRaisesRegex(ValueError, 'REFERENCE_OUTSIDE'):
            reader.read('e1', {'value': 'large-text'*1000}, step='investigate')


class ParentContextTests(unittest.TestCase):
    def test_enabled_reader_returns_summary_to_real_parent_loop_without_raw_growth(self):
        import test_ledger_investigator as fixtures
        tools,engine,_,_=fixtures.ToolLoopTests().build();raw='LARGE_RETAINED_DEFINITION_SENTINEL'*8000
        tools.graph.definition_of.return_value={'definition':raw};payloads=[];child_calls=[]
        def child(payload,**kwargs):
            child_calls.append(payload)
            return {'summary':'A retained definition was inspected; no cause is established by this note.','evidence_ids':payload['evidence_ids']}
        engine.heavy_reader=HeavyReader(child,enabled_steps=['investigate'])
        def parent(payload,**kwargs):
            payloads.append(payload)
            if len(payloads)==1:return {'action':'TOOL','summary':'Inspect definition','hypotheses':['not found'],'tool':'definition_of','arguments':{'node':'down'}}
            if len(payloads)==2:
                identity=next(k for k,v in payload['case_file']['evidence_summaries'].items()if v['kind']=='GRAPH')
                return {'action':'TOOL','summary':'Read the retained definition','hypotheses':['not found'],'tool':'get_evidence','arguments':{'id':identity}}
            return {'action':'VERDICT','summary':'No proved cause','hypotheses':['not found'],'verdict':'not found','evidence_ids':list(tools.evidence._values)}
        engine.decide=parent;engine.run({'visual':'visual'})
        self.assertGreater(len(child_calls),1)
        self.assertNotIn('LARGE_RETAINED_DEFINITION_SENTINEL',json.dumps(payloads[2]))
        self.assertTrue(payloads[2]['fetched_evidence']['summary_is_untrusted'])
        self.assertTrue(any(v['kind']=='READING_NOTE'for v in tools.evidence._values.values()))

if __name__ == '__main__':
    unittest.main()
