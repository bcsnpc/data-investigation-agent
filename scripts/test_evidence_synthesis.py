import copy,json,unittest
from pathlib import Path
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

    def test_ingestion_context_preserves_report_without_inventing_metadata(self):
        agent,state=self.stopped()
        observation={'id':'ingestion-receipt','tool':'context','status':'COMPLETED',
            'completeness':'COMPLETE_RESPONSE','process_roles':['ingestion'],'asset_id':'asset://table',
            'delta_commit':{'status':'AVAILABLE','latest_commit':'table/log/000.json',
                'commit_info':{'timestamp':123,'operation':'WRITE','operationMetrics':{'rows':'7'}}}}
        original=copy.deepcopy(observation);state['observations'].append(observation)
        with agent.runtime.db() as db:payload=synthesis_digest.build(state,db)
        entry=payload['evidence'][-1]
        self.assertEqual(entry['result']['delta_commit'],original['delta_commit'])
        self.assertEqual(entry['result']['asset_id'],original['asset_id'])
        self.assertEqual(entry['provenance']['hash'],digest(original))
        self.assertEqual(entry['process_roles'],['ingestion'])
        entry['result']['delta_commit']['commit_info']['timestamp']=456
        self.assertEqual(observation,original)
        self.assertNotIn('metadata',observation)

    def test_ingestion_missing_fields_and_unknown_context_fail_loudly(self):
        base={'process_roles':['ingestion'],'asset_id':'asset://table',
              'delta_commit':{'status':'AVAILABLE','latest_commit':'log','commit_info':{}}}
        bad=[]
        for field in ('asset_id','delta_commit'):
            item=copy.deepcopy(base);del item[field];bad.append(item)
        for field in ('status','latest_commit','commit_info'):
            item=copy.deepcopy(base);del item['delta_commit'][field];bad.append(item)
        bad.extend([{'lookup':{'operation':'content'}}, {'process_roles':['unknown']},
                    {**base,'metadata':{}}, {**base,'delta_commit':{}}])
        for observation in bad:
            with self.subTest(observation=observation),self.assertRaises(Conflict):
                synthesis_digest._context_evidence(observation)

    def test_ingestion_empty_and_unavailable_remain_explicit(self):
        for report in ({'status':'EMPTY_RESPONSE','latest_commit':None},
                       {'status':'EMPTY_RESPONSE','latest_commit':'log'},
                       {'status':'UNAVAILABLE','error_type':'TimeoutError'}):
            observation={'process_roles':['ingestion'],'asset_id':'asset://table','delta_commit':report}
            result=synthesis_digest._context_evidence(observation)
            self.assertEqual(result['result']['delta_commit'],report)
            self.assertNotIn('commit_info',result['result']['delta_commit'])

    def test_support_is_never_clipped_by_repair_or_wire_bound(self):
        from investigator.proposal_repairs import repair
        from investigator.assessment_support import validate, SCHEMA
        from investigator import proposal_limits
        for field in ('mechanism','intent_basis','remaining_test'):
            with self.subTest(field=field):
                answer=self.answer({'evidence':[]})
                answer['support'][field]='x'*(proposal_limits.ASSESSMENT_DETAIL+1)+' Complete ending.'
                original=copy.deepcopy(answer)
                repaired,events=repair({'assessment':answer})
                self.assertEqual(repaired['assessment']['support'],original['support'])
                self.assertFalse(events)
                with self.assertRaisesRegex(ValueError,'Support '+field+' exceeds'):
                    validate(repaired['assessment'],{})
                self.assertEqual(repaired['assessment'],original)
                self.assertNotIn('maxLength',SCHEMA['properties'][field])
                self.assertNotIn('maxLength',synthesis.schema()['properties']['support']['properties'][field])

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

    def test_runtime_validation_retains_every_original_field_including_future_fields(self):
        agent,state=self.stopped()
        with agent.runtime.db() as db:
            source=agent.load(db,state['id'])
            source['observations'][0]['future_validation_fact']={'nested':[{'required':'kept'}]}
            agent.save(db,source,'TEST_SOURCE_EXTENSION',{})
        originals=copy.deepcopy(source['observations'])
        from investigator.dynamic_reasoning import validate as existing
        seen=[]
        def downstream(proposal,context):
            self.assertEqual(context['observations'],originals)
            self.assertEqual(context['observations'][0]['future_validation_fact']['nested'][0]['required'],'kept')
            seen.append(True)
            result=existing(proposal,context)
            context['observations'][0]['future_validation_fact']['nested'].clear()
            return result
        def provider(payload,options):
            self.assertNotIn('future_validation_fact',encoded(payload))
            return self.answer(payload),{}
        with patch('investigator.dynamic_reasoning.validate',side_effect=downstream):
            result=agent.synthesize(state['id'],provider)
        self.assertEqual(result['synthesis']['status'],'COMPLETED')
        self.assertEqual(seen,[True])
        with agent.runtime.db() as db:self.assertEqual(agent.load(db,state['id'])['observations'],originals)

    def test_changed_original_source_is_fenced_even_when_digest_omits_changed_field(self):
        agent,state=self.stopped()
        def provider(payload,options):
            with agent.runtime.db() as db:
                changed=agent.load(db,state['id'])
                changed['observations'][0]['future_validation_fact']={'new':'value'}
                agent.save(db,changed,'TEST_SOURCE_CHANGED',{})
            return self.answer(payload),{}
        result=agent.synthesize(state['id'],provider)
        self.assertEqual(result['synthesis']['status'],'FAILED')
        self.assertIsNone(result['synthesis']['assessment'])

    def test_original_evidence_cannot_expand_citation_visibility_or_be_omitted(self):
        payload={'evidence':[{'id':'visible'}]}
        source={'observations':[{'id':key,'tool':'context','status':'COMPLETED','completeness':'COMPLETE_RESPONSE'}
                                for key in ('visible','hidden')]}
        value=self.answer({'evidence':[{'id':'hidden'}]})
        with self.assertRaisesRegex(ValueError,'Unknown assessment evidence'):
            synthesis.validate(value,payload,source_state=source)
        with self.assertRaises(TypeError):synthesis.validate(value,payload)
        for invalid in ({'observations':[]}, {'observations':[dict(source['observations'][0],status='FAILED')]},
                        {'observations':[source['observations'][0]]*2}):
            with self.assertRaises(Conflict):synthesis.validate(value,payload,source_state=invalid)

    def test_process_contract_uses_original_fields_not_digest_rendering(self):
        from test_process_debugging import OutcomeContractTests
        base,observations=OutcomeContractTests().valid('CONSISTENT_TO_BOUNDARY')
        for role,o in observations.items():
            o.update(tool='process' if role=='comparison' else 'bounded_dax',completeness='COMPLETE_RESPONSE')
        observations['baseline']['test_purpose']='ESTABLISH_BASELINE'
        payload={'evidence':[{'id':key} for key in observations]}
        value=self.answer(payload)
        value['classification']='CONSISTENT_TO_BOUNDARY'
        value['support'].update(intent_dependency='NOT_REQUIRED',measure_connection='ESTABLISHED',
            measure_connection_basis='A scoped baseline was observed.',measure_connection_evidence_ids=['baseline'],
            process=base['support']['process'])
        source={'observations':list(observations.values()),'assessment':copy.deepcopy(value)}
        synthesis.validate(copy.deepcopy(value),payload,source_state=source)
        # The renderer may drop or contradict fields; it is not validation authority.
        for e in payload['evidence']:e.update(comparison_status='WITHIN_LAYER_CHECK',values_equal=False)
        synthesis.validate(copy.deepcopy(value),payload,source_state=source)
        changed=copy.deepcopy(source);next(o for o in changed['observations'] if o['id']=='comparison')['values_equal']=False
        with self.assertRaisesRegex(ValueError,'successful equal boundary'):
            synthesis.validate(copy.deepcopy(value),payload,source_state=changed)
        changed=copy.deepcopy(source);del next(o for o in changed['observations'] if o['id']=='comparison')['upper_surface_attestation']
        with self.assertRaisesRegex(ValueError,'both surfaces to be attested'):
            synthesis.validate(copy.deepcopy(value),payload,source_state=changed)

    def test_s7_support_citations_are_assembled_into_outer_list(self):
        # Recorded S7 omitted valid support receipt 0dd from the outer list.
        outer=['bcb2f0ac-61d2-4926-8384-23eb58230634',
               '91b223d0-4fcf-43b2-9085-3f449287daba',
               '7aeca75e-5f56-4834-8eed-919f0264da79',
               '0cd0119a-9229-47f9-8439-ae7cd5faf0b8']
        missing='0dd49072-a9ed-4acb-8f82-7755cd446d6a'
        answer={'evidence_ids':outer.copy(),'support':{
            'mechanism_evidence_ids':outer.copy(),
            'intent_evidence_ids':[missing,outer[0],outer[1]]}}
        repaired=synthesis.assemble_citations(answer)
        self.assertEqual(repaired['evidence_ids'],outer+[missing])
        self.assertEqual(repaired['support']['intent_evidence_ids'],[missing,outer[0],outer[1]])

    def test_all_four_226_recorded_contract_failures_normalize_and_validate(self):
        fixture=Path(__file__).with_name('fixtures')/'synthesis_failures_226.json'
        cases=json.loads(fixture.read_text(encoding='utf-8'))
        self.assertEqual([c['label'] for c in cases],['M2','M3','M4','M9'])
        for case in cases:
            with self.subTest(case=case['label']):
                # These historical response-shape fixtures have no full source
                # tape. Supply an explicit synthetic source for that narrow test.
                source={'observations':[{**e,'status':'COMPLETED'} for e in case['payload']['evidence']]}
                value=case['assessment'];synthesis.validate(value,case['payload'],source_state=source)
                for key in ('mechanism','intent_basis','measure_connection_basis','remaining_test'):
                    self.assertLessEqual(len(value['support'][key]),500)
                cited=set(value['evidence_ids'])
                self.assertTrue(set(value['support']['measure_connection_evidence_ids'])<=cited)

    def test_normalization_labels_truncation_and_cannot_supply_missing_support(self):
        value=self.answer({'evidence':[]});value['support']['mechanism']='x'*501
        synthesis.normalize(value)
        self.assertTrue(value['support']['mechanism'].endswith(synthesis.TRUNCATION_LABEL))
        self.assertEqual(len(value['support']['mechanism']),500)
        value['support']['mechanism_evidence_ids']=['missing'];value['evidence_ids']=[]
        with self.assertRaises(ValueError):synthesis.validate(value,{'evidence':[]},source_state={'observations':[]})

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

    def test_arbitrary_asset_metadata_cannot_smuggle_embedded_records_into_digest(self):
        agent,state=self.stopped()
        state['observations']=[{'id':'metadata','tool':'context','status':'COMPLETED',
          'completeness':'COMPLETE_RESPONSE','lookup':{'operation':'find','value':'notebook'},
          'metadata':{'content':'rows = [[123, "raw-secret-record"]]',
                      'matches':[{'excerpt':'rows = [[456, "raw-secret-record"]]'}],
                      'asset':{'kind':'Notebook','name':'Transform','metadata':{'expression':'raw-secret-record'}}}}]
        with self.f.store.connect() as db:payload=synthesis_digest.build(state,db)
        self.assertNotIn('raw-secret-record',encoded(payload))
        self.assertTrue(payload['evidence'][0]['result']['unstructured_metadata_omitted'])
        self.assertEqual(payload['evidence'][0]['result']['asset_name'],'Transform')

    def test_explicit_definition_excerpt_is_bounded_and_labelled(self):
        agent,state=self.stopped();content='SELECT movement_id, units FROM source '+('x'*3000)
        state['observations']=[{'id':'metadata','tool':'context','status':'COMPLETED',
          'completeness':'PARTIAL','lookup':{'operation':'content','value':'part','offset':0},
          'metadata':{'asset_id':'part','content_hash':digest(content),'content':content,'offset':0,
                      'total_characters':len(content),'truncated':True}}]
        with self.f.store.connect() as db:payload=synthesis_digest.build(state,db)
        excerpt=payload['evidence'][0]['result']['transformation_excerpt']
        self.assertIn('movement_id',excerpt['text']);self.assertTrue(excerpt['truncated'])
        self.assertEqual(excerpt['displayed_characters'],synthesis_digest.EXCERPT_CHARACTERS)

    def test_bounded_rows_group_keys_and_aggregate_lineage_are_explicit(self):
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
        result=payload['evidence'][0]['result']
        self.assertEqual(result['group_keys']['id']['values'],['123'])
        self.assertEqual(result['displayed_rows'],o['values'])
        self.assertEqual(payload['evidence'][0]['asked']['query'],q)
        self.assertFalse(result['rows_truncated'])

    def test_process_comparison_is_derived_from_two_receipt_backed_observations(self):
        agent,state=self.stopped();query=state['observations'][0]
        lower=copy.deepcopy(query);lower['id']='lower-receipt'
        upper_surface={'engine':'POWER_BI_DAX','connection':'workspace','object':'model'}
        lower_surface={'engine':'FABRIC_SQL','connection':'endpoint','object':'table'}
        query['execution_surface']=upper_surface;lower['execution_surface']=lower_surface
        process={'id':'comparison','tool':'process','status':'COMPLETED','completeness':'COMPLETE_RESPONSE',
          'comparison_status':'CROSS_SURFACE_VERIFIED','upper_layer':'semantic','lower_layer':'gold',
          'values_equal':True,'upper_evidence_id':query['id'],'lower_evidence_id':lower['id'],
          'upper_execution_surface':upper_surface,'lower_execution_surface':lower_surface}
        state['observations']=[query,lower,process]
        derived=synthesis_digest._process_evidence(process,{x['id']:x for x in state['observations']})
        self.assertEqual(derived['comparison_status'],'CROSS_SURFACE_VERIFIED')
        self.assertEqual(derived['referenced_evidence_ids'],[query['id'],lower['id']])

    def test_process_comparison_rejects_same_surface_or_value_mismatch(self):
        observation={'id':'comparison','tool':'process','status':'COMPLETED','completeness':'COMPLETE_RESPONSE',
          'comparison_status':'CROSS_SURFACE_VERIFIED','upper_layer':'semantic','lower_layer':'gold',
          'values_equal':True,'upper_evidence_id':'upper','lower_evidence_id':'lower',
          'upper_execution_surface':{'engine':'x','connection':'x','object':'x'},
          'lower_execution_surface':{'engine':'x','connection':'x','object':'x'}}
        state={'observations':[{'id':'upper','status':'COMPLETED','values':[1]},
              {'id':'lower','status':'COMPLETED','values':[1]},observation]}
        with self.assertRaisesRegex(Conflict,'Cross-surface'):
            synthesis_digest._process_evidence(observation,{x['id']:x for x in state['observations']})

    def test_process_surface_identity_is_evidence_never_surface_equality(self):
        receipts={key:{'id':key,'status':'COMPLETED','values':[1]} for key in ('upper','lower')}
        for identity in (None,'same-reader','different-reader'):
            with self.subTest(identity=identity):
                upper={'engine':'engine','connection':'connection','object':'object','identity':'same-reader'}
                lower={**upper}
                if identity is None:lower.pop('identity')
                else:lower['identity']=identity
                observation={'comparison_status':'CROSS_SURFACE_VERIFIED','values_equal':True,
                    'upper_evidence_id':'upper','lower_evidence_id':'lower',
                    'upper_execution_surface':upper,'lower_execution_surface':lower}
                with self.assertRaisesRegex(Conflict,'Cross-surface'):
                    synthesis_digest._process_evidence(observation,receipts)
                for field in ('engine','connection','object'):
                    distinct={**lower,field:'other'}
                    observation['lower_execution_surface']=distinct
                    result=synthesis_digest._process_evidence(observation,receipts)
                    self.assertEqual(result['upper_execution_surface'],upper)
                    self.assertEqual(result['lower_execution_surface'],distinct)

    def test_process_comparison_normalizes_aliases_but_rejects_different_quantity(self):
        from investigator.process_quantity import quantity
        upper={'id':'upper','status':'COMPLETED','values':[{'[baseline]':{'value':'12.00'},
              '[surface_identity]':{'value':'reader'}}]}
        lower={'id':'lower','status':'COMPLETED','values':[{'quantity':{'value':'12'}}]}
        refs={'upper':upper,'lower':lower}
        observation={'comparison_status':'CROSS_SURFACE_VERIFIED','values_equal':True,
            'upper_evidence_id':'upper','lower_evidence_id':'lower',
            'upper_execution_surface':{'engine':'a','connection':'a','object':'a','identity':'reader'},
            'lower_execution_surface':{'engine':'b','connection':'b','object':'b','identity':'reader'}}
        quantities={'upper':quantity(upper['values'],{'identity':'surface_identity'}),
                    'lower':quantity(lower['values'])}
        self.assertTrue(synthesis_digest._process_evidence(observation,refs,quantities)['values_equal'])
        quantities['lower']={'quantity':'13'}
        with self.assertRaisesRegex(Conflict,'differs from referenced'):
            synthesis_digest._process_evidence(observation,refs,quantities)
        with self.assertRaisesRegex(Conflict,'verified quantity receipts'):
            synthesis_digest._process_evidence(observation,refs,{})

if __name__=='__main__':unittest.main()
