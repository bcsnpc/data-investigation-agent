import copy,json,unittest
from unittest.mock import patch
from investigator import evidence_synthesis as synthesis
from investigator import synthesis_digest
from investigator.onboarding import digest,encoded,Conflict
from investigator.adaptive_runtime import AdaptiveRuntime
import test_flexible_investigation as fixture

class SynthesisTests(unittest.TestCase):
    def setUp(self):
        self.f=fixture.DynamicTests();self.f.setUp();self.addCleanup(self.f.doCleanups)
        self.policy={'environment':self.f.store.environment,'daily_limits':{'planner_calls':50,'cloud_calls':50,'input_characters':1000000,'output_tokens':100000},'max_inflight_planners':1,'no_progress_limit':3}

    def stopped(self,query='EVALUATE ROW("value", [Total])'):
        envelope=copy.deepcopy(self.f.envelope);envelope['limits']['cloud_calls']=1
        agent=AdaptiveRuntime(self.f.runtime,lambda _:self.f.decision('QUERY',query={'tool':'bounded_dax','text':query,'max_rows':20}),usage_policy=self.policy)
        state=agent.run(agent.create(envelope,'synthesis-test')['id'])
        self.assertEqual(state['stop_reason'],'BUDGET_LIMIT')
        return agent,state

    def answer(self,payload):
        ids=[e['id'] for e in payload['evidence']]
        return {'classification':'BUSINESS_CONTEXT_REQUIRED','claim':'The observed value alone does not establish the intended rule.',
          'evidence_ids':ids,'alternatives':['Different intended meanings remain possible.'],'limits':['No authoritative business rule supplied.'],
          'support':{'mechanism':'A scoped value was observed.','mechanism_evidence_ids':ids,'intent_dependency':'UNKNOWN',
                     'intent_basis':'Intent is not established.','intent_evidence_ids':[],'remaining_test':'Obtain the intended rule.'}}

    def test_independent_call_no_trajectory_or_raw_rows_full_reservation_idempotent(self):
        agent,state=self.stopped();calls=[]
        def provider(payload,options):
            calls.append(copy.deepcopy(payload))
            self.assertFalse(set(payload)&{'observations','decisions','action_history','directory','context_entry_points','candidates'})
            self.assertNotIn('values',payload['evidence'][0])
            return self.answer(payload),{'usage':{'input_tokens':100,'output_tokens':10}}
        before=agent.governor.snapshot()['reserved_today']
        result=agent.synthesize(state['id'],provider)
        self.assertEqual(result['synthesis']['status'],'COMPLETED')
        self.assertEqual(result['investigation_outcome']['classification'],'UNRESOLVED')
        self.assertEqual(result['outcome']['classification'],'BUSINESS_CONTEXT_REQUIRED')
        self.assertFalse(result['outcome']['cause_verified'])
        self.assertEqual(result['planner_calls'],state['planner_calls'])
        after=agent.governor.snapshot()['reserved_today']
        self.assertEqual(after['planner_calls'],before['planner_calls']+1)
        self.assertEqual(after['cloud_calls'],before['cloud_calls'])
        self.assertEqual(after['output_tokens'],before['output_tokens']+1500)
        self.assertEqual(agent.synthesize(state['id'],provider)['synthesis'],result['synthesis'])
        self.assertEqual(len(calls),1)

    def test_tampered_receipt_blocks_before_provider(self):
        agent,state=self.stopped();receipt=state['observations'][0]['id']
        with self.f.store.connect() as db:db.execute('UPDATE flexible_diagnostics SET result=? WHERE id=?',('{}',receipt))
        result=agent.synthesize(state['id'],lambda *_:self.fail('tampered evidence dispatched'))
        self.assertEqual(result['synthesis']['status'],'BLOCKED')
        self.assertEqual(result['synthesis']['calls'],0)

    def test_invalid_citation_fails_without_refund(self):
        agent,state=self.stopped()
        def provider(p,o):
            a=self.answer(p);a['evidence_ids']=['fabricated'];return a,{'usage':{'output_tokens':10}}
        r=agent.synthesize(state['id'],provider)
        self.assertEqual(r['synthesis']['status'],'FAILED');self.assertIsNone(r['synthesis']['assessment'])
        self.assertEqual(agent.governor.snapshot()['reserved_today']['planner_calls'],2)

    def test_provider_usage_violation_rejects_assessment(self):
        agent,state=self.stopped()
        r=agent.synthesize(state['id'],lambda p,o:(self.answer(p),{'usage':{'output_tokens':1501}}))
        self.assertEqual(r['synthesis']['status'],'FAILED')
        self.assertIsNone(r['synthesis']['assessment'])
        self.assertEqual(agent.governor.snapshot()['reservation_states']['VIOLATION'],1)

    def test_cancel_fences_late_result(self):
        agent,state=self.stopped()
        def provider(p,o):
            agent.cancel(state['id']);return self.answer(p),{}
        r=agent.synthesize(state['id'],provider)
        self.assertEqual(r['synthesis']['status'],'CANCELLED')
        self.assertNotIn('assessment_phase',r['outcome'])

    def test_uncertain_provider_is_not_retried(self):
        agent,state=self.stopped();calls=[]
        def provider(*_):calls.append(1);raise TimeoutError()
        r=agent.synthesize(state['id'],provider)
        self.assertEqual(r['synthesis']['status'],'FAILED')
        agent.synthesize(state['id'],provider);self.assertEqual(len(calls),1)
        self.assertEqual(agent.governor.snapshot()['reservation_states']['UNCERTAIN'],1)

    def test_investigation_payload_coverage_unchanged(self):
        agent,state=self.stopped()
        captured=agent.clock();agent.clock=lambda:captured
        from investigator.adaptive_candidates import catalog
        candidates,_=catalog(self.f.store,self.f.config,state['envelope'])
        before=agent.payload(state,candidates)
        agent.synthesize(state['id'],lambda p,o:(self.answer(p),{}))
        after=agent.payload(state,candidates)
        self.assertEqual(encoded(before),encoded(after))
        self.assertEqual(before['context_entry_points'],after['context_entry_points'])

    def test_mutated_provider_input_is_not_new_evidence(self):
        agent,state=self.stopped()
        def provider(p,o):
            p['evidence'][0]['id']='fabricated'
            return self.answer(p),{}
        self.assertEqual(agent.synthesize(state['id'],provider)['synthesis']['status'],'FAILED')

    def test_raw_records_are_omitted_and_aggregate_alias_lineage_selected(self):
        # Isolate deterministic projection with a synthetic sealed receipt adapter.
        agent,state=self.stopped();o=state['observations'][0]
        o.update(tool='bounded_sql',values=[{'id':{'type':'decimal','value':'123'},'n':{'type':'decimal','value':'2'}}])
        q='WITH x AS (SELECT id, COUNT(*) AS n FROM t GROUP BY id) SELECT id,n FROM x'
        request={'plan':{'query':q},'query':q};result={'rows':o['values']};o['request_hash']=digest({'query':q})
        class DB:
            def execute(self,*args):return self
            def fetchone(self):return (state['model_id'],'COMPLETED',encoded(request),encoded(result))
        with patch.object(synthesis_digest,'verify',return_value={'state':'SEALED','hash':'seal'}):
            payload=synthesis_digest.build(state,DB())
        facts=payload['evidence'][0]['result']['aggregate_outputs']
        self.assertEqual(set(facts),{'n'});self.assertEqual(facts['n']['values'],['2'])
        self.assertNotIn('123',encoded(payload))

if __name__=='__main__':unittest.main()
