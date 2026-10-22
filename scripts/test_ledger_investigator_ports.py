import contextlib
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from investigator.adapters.ledger_investigator_ports import ProcessValues,AzureDecision,ProcessChecks
from investigator.process_debugging import Probe
from investigator.refresh_comparison import whole_entity_context


class Values(unittest.TestCase):
    def setUp(self):
        self.calls=[];self.saved=[]
        self.graph={'nodes':[{'id':'visual','kind':'VISUAL','properties':{'asset_id':'v'}},
            {'id':'measure','kind':'MEASURE','properties':{'asset_id':'m'}},
            {'id':'lower','kind':'TABLE','properties':{'asset_id':'physical'}}],
            'edges':[{'source':'visual','target':'measure'},{'source':'measure','target':'lower'}]}
        self.process=SimpleNamespace(meter_read=lambda *a:None,
            resolve_path=lambda m:{'layers':[{'id':'semantic','kind':'presentation'},
                                             {'id':'physical','kind':'declared_source'}]},evaluate=self.evaluate)
        self.value='16'

    def evaluate(self,layer,measure,scope):
        self.calls.append((layer,measure,scope))
        if layer['kind']=='declared_source' and scope.get('filters'):
            return Probe('NOT_COMPARABLE',layer['id'],reason='Declared source comparison does not yet translate filtered scope faithfully.')
        return Probe('OBSERVED',layer['id'],value={'quantity':self.value},query='SELECT SUM([x]) FROM [dbo].[t]',
            evidence={'id':'receipt','declared_context':whole_entity_context()},
            execution_surface={'identity':'reader','object':'db'},surface_report={'identity':'reader','object':'db'},
            surface_reportable=('identity','object'),surface_report_binding='VALUE_QUERY')

    def port(self):return ProcessValues(self.process,graph_slice=self.graph,visual='visual',measure_id='m',retain=self.saved.append)

    def test_compiled_read_has_original_receipt_scope_and_warning(self):
        result=self.port()('lower',None,{})
        self.assertEqual(result['value'],'16');self.assertEqual(result['receipt_id'],'receipt')
        self.assertEqual(self.calls[0][0]['id'],'physical');self.assertIn('SNAPSHOT_UNVERIFIED',result['warnings'])

    def test_blank_is_value_and_failure_is_not_blank(self):
        self.value=None;self.assertEqual(self.port()('visual',None,{})['state'],'BLANK')
        self.process.evaluate=lambda *a:Probe('UNAVAILABLE','semantic',reason='query failed')
        with self.assertRaisesRegex(ValueError,'query failed'):self.port()('visual',None,{})
        self.assertEqual(self.saved[-1]['status'],'UNAVAILABLE')

    def test_unknown_target_measure_key_and_scope_never_dispatch(self):
        port=self.port()
        for args in [('unknown',None,{}),('visual','record1',{}),('visual',None,{'SQL':'injected'})]:
            with self.assertRaises(ValueError):port(*args)
        self.assertEqual(self.calls,[])
        self.graph['edges']=[]
        with self.assertRaisesRegex(ValueError,'NOT_CONNECTED'):self.port()

    def test_filtered_lower_refusal_unchanged(self):
        with self.assertRaisesRegex(ValueError,'does not yet translate filtered scope faithfully'):
            self.port()('lower',None,{'filters':[{'column':'day','value':'today'}]})
        self.assertEqual(self.saved[-1]['status'],'NOT_COMPARABLE')

    def test_unmetered_adapter_refused(self):
        self.process.meter_read=None
        with self.assertRaisesRegex(ValueError,'GOVERNED_PROCESS'):self.port()


class Decisions(unittest.TestCase):
    def setUp(self):
        self.events=[]
        @contextlib.contextmanager
        def db():yield object()
        self.governor=SimpleNamespace(runtime=SimpleNamespace(db=db),
            reserve=lambda *a,**k:self.events.append(('reserve',a[1:],k)),
            settle=lambda *a,**k:self.events.append(('settle',a[1:],k)))

    def test_reserve_capture_send_settle_and_unknown_usage_on_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            @contextlib.contextmanager
            def recording(*a,**k):
                self.events.append(('capture',));yield SimpleNamespace(path=Path(tmp),safe_write=lambda *a:None)
            def provider(*a,**kw):
                self.events.append(('send',));return {'action':'VERDICT'},{'usage':{'input_tokens':10,'output_tokens':3}}
            port=AzureDecision(self.governor,session='ticket-1',directory=tmp,retain=lambda v:None,producer=provider)
            with patch('investigator.planner_recording.recording',recording):
                self.assertEqual(port({'ticket':'x'},instructions='investigate',schema={'type':'object'})['action'],'VERDICT')
            self.assertEqual([e[0] for e in self.events],['reserve','capture','send','settle'])
            self.assertFalse(self.events[-1][2]['uncertain'])
            self.events=[]
            def failed(*a,**k):raise RuntimeError('transport failed')
            port.producer=failed
            with patch('investigator.planner_recording.recording',recording),self.assertRaises(RuntimeError):
                port({},instructions='investigate',schema={'type':'object'})
            self.assertTrue(self.events[-1][2]['uncertain'])

    def test_oversized_provider_body_not_admitted(self):
        port=AzureDecision(self.governor,session='ticket-1',directory='unused',retain=lambda v:None)
        with self.assertRaisesRegex(ValueError,'INPUT_BOUND'):
            port({'ticket':'x'*40000},instructions='investigate',schema={'type':'object'})
        self.assertEqual(self.events,[])


class NativeChecks(unittest.TestCase):
    def test_exact_original_boundary_produces_revalidated_native_design(self):
        from test_process_debugging import Adapter
        from investigator.process_debugging import attest
        from investigator.native_verdict_support import validate_design
        adapter=Adapter(['down','up'],{'down':7,'up':8},explain=True)
        adapter.judge_definition=lambda _:None
        layers=[{'id':'down'},{'id':'up'}]
        upper=attest(adapter.evaluate(layers[0],'measure',{}));lower=attest(adapter.evaluate(layers[1],'measure',{}))
        for probe in (upper,lower):probe.evidence['declared_context']=whole_entity_context()
        upper.evidence['test_purpose']='ESTABLISH_BASELINE'
        originals={upper.evidence['id']:upper,lower.evidence['id']:lower};saved=[]
        values=SimpleNamespace(probes=originals,path={'layers':layers},process=adapter,retain=saved.append)
        records={}
        for ref,node,probe in [('left','down',upper),('right','up',lower)]:
            records[ref]={'value':{'subject':node,'key':None,'context':whole_entity_context(),'state':'VALUE',
                'value':probe.value,'receipt_id':probe.evidence['id'],'query':probe.query,
                'execution_surface':probe.execution_surface,'route_admitted':True,'read_only_verified':True}}
        witness=ProcessChecks(values)('DESIGN_CHECK',{'value':{'left':'left','right':'right'}},records)
        self.assertEqual(validate_design(witness,{r:v['value'] for r,v in records.items()},[{'left':'left','right':'right'}]),witness['mechanism'])
        self.assertEqual(len(saved),1)
        witness['native_observations'][upper.evidence['id']]['query']='changed'
        with self.assertRaisesRegex(ValueError,'RECEIPTS_OR_CONTEXT_DIFFER'):
            validate_design(witness,{r:v['value'] for r,v in records.items()},[{'left':'left','right':'right'}])
        values.path={'layers':list(reversed(layers))}
        with self.assertRaisesRegex(ValueError,'ADJACENT'):
            ProcessChecks(values)('DESIGN_CHECK',{'value':{'left':'left','right':'right'}},records)


if __name__=='__main__':unittest.main()
