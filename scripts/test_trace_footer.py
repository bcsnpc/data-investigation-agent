import copy
import base64
from types import SimpleNamespace
import unittest
import test_flexible_investigation as fixture
from investigator.adaptive_runtime import AdaptiveRuntime
from investigator import evidence_synthesis
from investigator.process_tape import bytes_of,sha
from investigator.run_recording import attach_trace_footer


class FooterTests(unittest.TestCase):
    def test_footer_is_persisted_in_both_return_views_once_without_changing_evidence(self):
        helper=fixture.DynamicTests();helper.setUp();self.addCleanup(helper.doCleanups)
        agent=AdaptiveRuntime(helper.runtime,lambda _:None)
        identity=agent.create(helper.envelope,'trace-footer-test')['id']
        with agent.runtime.db() as db:
            state=agent.load(db,identity)
            db.execute('CREATE TABLE adaptive_syntheses(session_id TEXT PRIMARY KEY,body TEXT NOT NULL,hash TEXT NOT NULL)')
            record={'status':'COMPLETED','assessment':None,'outputs':{
                'technical_output':{'explanation':{'text':'Original supported explanation.'}},
                'business_output':{'explanation':{'text':'Original business explanation.'}}}}
            evidence_synthesis.save(db,identity,record,source_state=state)
        events=[]
        for kind,at,body in [('BOOTSTRAP',1,{}),('OPERATION_START',2,{'name':'synthesize'}),('OPERATION_END',3,{'name':'synthesize','error':None})]:
            raw=bytes_of(body);events.append({'kind':kind,'ordinal':len(events)+1,'at':at,'body':base64.b64encode(raw).decode(),'sha256':sha(raw)})
        tape=SimpleNamespace(events=events,version='test',engine_revision='abc')
        result=agent.get(identity);before=copy.deepcopy(result['observations'])
        attach_trace_footer(agent,identity,tape,result)
        text=result['synthesis']['outputs']['technical_output']['explanation']['text']
        self.assertTrue(text.endswith('currency cost not recorded.'))
        self.assertIn('compose: 1.000s',text)
        self.assertEqual(result['outcome']['synthesis_outputs'],result['synthesis']['outputs'])
        self.assertEqual(result['observations'],before)
        self.assertEqual(result['synthesis']['outputs']['business_output'],record['outputs']['business_output'])
        self.assertEqual(agent.get(identity)['synthesis']['outputs'],result['synthesis']['outputs'])
        attach_trace_footer(agent,identity,tape,result)
        self.assertEqual(result['synthesis']['outputs']['technical_output']['explanation']['text'],text)
        self.assertEqual(len(tape.events),3)


if __name__=='__main__':unittest.main()
