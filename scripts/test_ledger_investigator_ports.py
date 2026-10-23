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

    def test_checkpoint_restores_original_native_probes_for_later_design_checks(self):
        from investigator.shared_state import StateConflict
        first=self.port();first('lower',None,{})
        snapshot=first.checkpoint_state();second=self.port();second.restore_checkpoint(snapshot)
        self.assertEqual(second.probes['receipt'].query,first.probes['receipt'].query)
        self.assertEqual(second.probes['receipt'].value,first.probes['receipt'].value)
        self.assertEqual(second.probes['receipt'].execution_surface,first.probes['receipt'].execution_surface)
        self.assertEqual(len(self.calls),1)
        snapshot['path_sha256']='wrong'
        with self.assertRaises(StateConflict):second.restore_checkpoint(snapshot)

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

    def test_bound_case_recitation_is_required_on_wire_and_mismatch_cannot_change_state(self):
        from investigator.investigator_case import CaseFile
        case=CaseFile({'id':'one'});events=[]
        def provider(payload,**kwargs):
            self.assertEqual(payload['code_case_state']['current_step'],'recreate')
            self.assertIn('recitation',kwargs['schema']['required'])
            return {'decision':{'action':'VERDICT'},'recitation':{'plan':['wrong'],'current_step':'deliver'}},{'usage':{'input_tokens':10,'output_tokens':3}}
        with tempfile.TemporaryDirectory()as tmp:
            port=AzureDecision(self.governor,session='one',directory=tmp,retain=events.append,producer=provider,recording_mode='NORMAL')
            port.bind_case(case,events.append)
            self.assertEqual(port({},instructions='Read only',schema={'type':'object'})['action'],'VERDICT')
        self.assertEqual(case.snapshot()['current_step'],'recreate')
        self.assertTrue(any(v.get('event')=='INVESTIGATOR_RECITATION_MISMATCH'for v in events))
        self.assertEqual(self.events[-1][0],'settle')

    def test_reserve_capture_send_settle_and_unknown_usage_on_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            @contextlib.contextmanager
            def recording(*a,**k):
                self.events.append(('capture',));yield SimpleNamespace(path=Path(tmp),safe_write=lambda *a:None)
            def provider(*a,**kw):
                self.events.append(('send',));return {'decision':{'action':'VERDICT'}},{'usage':{'input_tokens':10,'output_tokens':3}}
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

    def test_provider_object_envelope_leaves_core_union_and_decision_unchanged(self):
        import copy,json
        from jsonschema import Draft202012Validator
        from investigator.ledger_investigator import schema as decision_schema
        from investigator.estate_graph_contract import canonical
        core=decision_schema(SimpleNamespace(schemas={}));before=copy.deepcopy(core)
        decision={'action':'VERDICT','summary':'No supported cause.','hypotheses':['not found'],
                  'verdict':'not found','evidence_ids':[]}
        Draft202012Validator(core).validate(decision)
        with tempfile.TemporaryDirectory() as tmp:
            captures=[]
            @contextlib.contextmanager
            def recording(*a,**k):yield SimpleNamespace(path=Path(tmp),safe_write=lambda name,data:captures.append((name,data)))
            def provider(*a,**kw):
                wire=kw['schema'];self.assertEqual(wire['type'],'object')
                self.assertEqual(set(wire),{'type','properties','required','additionalProperties'})
                self.assertEqual(wire['required'],['summary','hypotheses','decision']);self.assertFalse(wire['additionalProperties'])
                self.assertNotIn('summary',wire['properties']['decision']['anyOf'][0]['properties'])
                self.assertNotIn('anyOf',wire)
                envelope={k:decision[k]for k in ('summary','hypotheses')}
                envelope['decision']={k:v for k,v in decision.items()if k not in envelope}
                Draft202012Validator(wire).validate(envelope)
                return envelope,{'usage':{'input_tokens':10,'output_tokens':3}}
            port=AzureDecision(self.governor,session='s',directory=tmp,retain=lambda value:None,producer=provider)
            with patch('investigator.planner_recording.recording',recording):
                actual=port({},instructions='investigate',schema=core)
            self.assertEqual(canonical(actual),canonical(decision));self.assertEqual(core,before)
            Draft202012Validator(core).validate(actual)
            body=json.loads(captures[0][1]);self.assertEqual(body['tools'][0]['parameters']['type'],'object')

    def test_malformed_provider_envelopes_refuse_and_known_usage_settles(self):
        with tempfile.TemporaryDirectory() as tmp:
            @contextlib.contextmanager
            def recording(*a,**k):yield SimpleNamespace(path=Path(tmp),safe_write=lambda *a:None)
            for invalid in ({'action':'VERDICT'},{'decision':{} ,'extra':True},{'decision':None},[],{'decision':[]}):
                with self.subTest(answer=invalid):
                    port=AzureDecision(self.governor,session='s',directory=tmp,retain=lambda v:None,
                        producer=lambda *a,**kw:(invalid,{'usage':{'input_tokens':10,'output_tokens':3}}))
                    with patch('investigator.planner_recording.recording',recording),self.assertRaisesRegex(ValueError,'DECISION_ENVELOPE_REQUIRED'):
                        port({},instructions='investigate',schema={'type':'object'})
                    self.assertFalse(self.events[-1][2]['uncertain'])

    def test_wire_subset_does_not_weaken_consumer_bounds(self):
        from investigator.adapters.ledger_investigator_ports import decision_transport
        from jsonschema import ValidationError
        core={'type':'object','properties':{'labels':{'type':'array','minItems':1,'uniqueItems':True,'items':{'type':'string','minLength':2}}},'required':['labels'],'additionalProperties':False}
        wire,hoisted=decision_transport(core)
        self.assertEqual(hoisted,());self.assertNotIn('minItems',wire['properties']['decision']['properties']['labels'])
        with tempfile.TemporaryDirectory()as tmp:
            @contextlib.contextmanager
            def recording(*a,**k):yield SimpleNamespace(path=Path(tmp),safe_write=lambda *a:None)
            for value in ([],['x'],['ok','ok']):
                port=AzureDecision(self.governor,session='s',directory=tmp,retain=lambda v:None,
                    producer=lambda *a,**kw:({'decision':{'labels':value}},{'usage':{'input_tokens':10,'output_tokens':3}}))
                with patch('investigator.planner_recording.recording',recording),self.assertRaises(ValidationError):
                    port({},instructions='x',schema=core)
                self.assertFalse(self.events[-1][2]['uncertain'])

    def test_declared_context_empty_arrays_are_typed_on_wire_and_exact_in_consumer(self):
        from investigator.adapters.ledger_investigator_ports import decision_transport
        from investigator.ledger_investigator_tools import literal_schema
        from investigator.refresh_comparison import whole_entity_context
        from jsonschema import Draft202012Validator,ValidationError
        core=literal_schema(whole_entity_context());wire,_=decision_transport(core)
        filters=wire['properties']['decision']['properties']['filters']
        self.assertEqual(filters,{'type':'array','items':{'type':'string'}})
        Draft202012Validator(wire).validate({'decision':whole_entity_context()})
        changed={**whole_entity_context(),'filters':['invented']}
        Draft202012Validator(wire).validate({'decision':changed})
        with self.assertRaises(ValidationError):Draft202012Validator(core).validate(changed)

    def test_real_tool_union_stays_within_azure_property_limit(self):
        from investigator.adapters.ledger_investigator_ports import decision_transport
        from investigator.ledger_investigator import schema
        tools=SimpleNamespace(schemas={str(i):{'type':'object','properties':{'node':{'type':'string','minLength':1}},'required':['node'],'additionalProperties':False}for i in range(16)})
        core=schema(tools);wire,hoisted=decision_transport(core)
        self.assertEqual(set(hoisted),{'summary','hypotheses'})
        def walk(v):
            if isinstance(v,list):
                for x in v:yield from walk(x)
            elif isinstance(v,dict):
                yield v
                for x in v.values():yield from walk(x)
        self.assertLessEqual(sum(len(x.get('properties',{}))for x in walk(wire)),100)
        self.assertFalse(any(set(x)&{'minLength','maxLength','minItems','maxItems','uniqueItems'}for x in walk(wire)))
        self.assertTrue(any('uniqueItems'in x for x in walk(core)))

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
