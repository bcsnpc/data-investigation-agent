import json,socket,unittest
from unittest.mock import Mock,patch
from investigator.source_availability import classify,call,result,fact
from investigator.adapters.metadata_error import MetadataUnavailable
from investigator.live_gateway import GatewayDenied
import test_ledger_investigator as fixtures
from test_ledger_investigator import read,fact as runtime_fact,NOW

class AvailabilityTests(unittest.TestCase):
    def test_all_seven_classes_have_plain_messages_without_exception_text(self):
        cases=[(TimeoutError('private'),'TIMEOUT'),(socket.gaierror('private'),'UNREACHABLE'),
            (MetadataUnavailable(503),'CAPACITY_UNAVAILABLE'),(MetadataUnavailable(401),'AUTHENTICATION_EXPIRED'),
            (MetadataUnavailable(403),'PERMISSION_REFUSED'),(MetadataUnavailable(429),'THROTTLED'),(ValueError('private'),'QUERY_ERROR')]
        for error,kind in cases:
            with self.subTest(kind=kind):
                self.assertEqual(classify(error),kind)
                value=result(error,at=NOW);self.assertNotIn('private',json.dumps(value));self.assertTrue(value['message'])
    def test_transient_retries_are_retained_before_outage_and_charge_original_operation(self):
        events=[];operation=Mock(side_effect=[ConnectionError(),ConnectionError(),7]);sleep=Mock()
        self.assertEqual(call(operation,observe=events.append,clock=lambda:NOW,sleep=sleep),7)
        self.assertEqual([v['reachable'] for v in events],[False,False,True]);self.assertEqual(operation.call_count,3)
        self.assertEqual(events[-1]['attempts'],3);self.assertEqual(sleep.call_count,2)
    def test_guard_refusal_is_never_an_outage_or_a_retry(self):
        observe=Mock();sleep=Mock()
        with self.assertRaises(GatewayDenied):call(Mock(side_effect=GatewayDenied('read-only')),observe=observe,sleep=sleep)
        observe.assert_not_called();sleep.assert_not_called()
    def test_access_check_exposes_permission_class_to_ledger_sink(self):
        from investigator.access_check import check
        from test_access_check import mapping
        backend=Mock();backend.probe.side_effect=MetadataUnavailable(403)
        sink=Mock();answer=check(mapping(),backend=backend,now=NOW,availability_sink=sink)
        self.assertEqual(answer['rows'][0]['availability']['failure_class'],'PERMISSION_REFUSED')
        self.assertEqual(backend.probe.call_count,1);sink.assert_called_once()
    def test_collector_retains_reachability_as_a_fact_without_turning_refusal_into_no_runs(self):
        from investigator.adapters.runtime_facts_microsoft import MicrosoftRuntimeFacts
        from test_runtime_facts_microsoft import retained,route
        adapter=MicrosoftRuntimeFacts({'job':route()},http=Mock(side_effect=MetadataUnavailable(403)),retain=retained,now=lambda:NOW)
        adapter.list_changes(['job']);values=adapter.fetch('job',now=NOW)
        observed=next(v for v in values if v['kind']=='AVAILABILITY')
        self.assertEqual(observed['state'],'OBSERVED');self.assertFalse(observed['value']['reachable'])
        self.assertEqual(observed['value']['failure_class'],'PERMISSION_REFUSED')
        self.assertEqual(next(v for v in values if v['kind']=='JOB_RUN')['state'],'UNAVAILABLE')
        self.assertFalse(any(v['kind']=='RUN_HISTORY' and v['state']=='OBSERVED_NEGATIVE'for v in values))
    def test_unreachable_mid_investigation_is_blocked_with_reachable_conclusion_and_owner(self):
        tools,engine,reader,_=fixtures.ToolLoopTests().build()
        def fetch(node,key,context):
            if node=='up':raise ConnectionError('private route')
            return read(node,7,context)
        reader.side_effect=fetch
        def decide(*a,**kw):return {'action':'TOOL','tool':'compare_layers','arguments':{'key':'record-1','layers':['down','up'],'filters':{'warehouse':'North'}},'summary':'Compare declared boundary','hypotheses':['not found']}
        engine.decide=decide
        with patch('investigator.model_transport_retry.backoff'):
            answer=engine.run({'visual':'visual'})
        self.assertEqual(answer['status'],'blocked');self.assertEqual(answer['blocked'][0]['layer'],'up')
        self.assertEqual(answer['blocked'][0]['failure_class'],'UNREACHABLE')
        for output in answer['outputs'].values():
            self.assertIn('Blocked: up',output);self.assertIn(tools.now,output);self.assertIn('Owner:',output);self.assertIn('Reachable layers checked:',output)
            self.assertNotIn('private route',output)
    def test_load_failure_with_observed_outage_keeps_failed_job_verdict_and_root_cause(self):
        outage=result(ConnectionError(),at=NOW,attempts=3)
        run=runtime_fact('job','JOB_RUN',{'status':'FAILED','run_id':'failed-copy','start':'2026-10-22T10:00:00Z','end':'2026-10-22T10:01:00Z','error':'source connection failed','source_availability':outage})
        engine,ticket,reader,decide=fixtures.OperationalFactTests().status_engine([run])
        answer=engine.run(ticket)
        self.assertEqual(answer['verdict'],'failed job');reader.assert_not_called();decide.assert_not_called()
        for output in answer['outputs'].values():self.assertIn('source unreachable at '+NOW,output)

if __name__=='__main__':unittest.main()
