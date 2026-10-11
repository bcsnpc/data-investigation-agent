import copy,unittest
from types import SimpleNamespace
from unittest.mock import Mock,patch
from investigator import hybrid_ticket
from investigator.onboarding import Conflict,digest
from investigator.investigation_tools import InvestigationTools,schemas
from test_investigation_tools import PersistedBoundary
from test_process_debugging import Adapter
from investigator.process_debugging import vertical
from investigator.agent_loop import AgentLoop


class HybridTests(unittest.TestCase):
    def saved(self):
        return {'revision':2,'ticket':{'id':'ticket','state':'HELD','history':[{'detail':{'reason':'TARGET_UNRESOLVED'}}],
                'source_intake':'intake','form_candidate_diagnostic_reads':3}}

    def workspace(self):
        w=SimpleNamespace(agent=SimpleNamespace(config={'_estate':{'investigation':{'mode':'HYBRID'}}},get=Mock()),
            intake=SimpleNamespace(get=Mock(return_value={'id':'intake','status':'NEEDS_INPUT','error':'TARGET_UNRESOLVED'})),
            smart_intake=SimpleNamespace(tickets=SimpleNamespace(update=Mock())))
        w.smart_intake.tickets.update.side_effect=lambda identity,revision,apply:{'revision':revision+1,'ticket':apply(copy.deepcopy(self.saved()['ticket']))}
        return w

    def test_held_pipeline_is_preserved_and_prior_candidates_are_carried(self):
        w=self.workspace();saved=self.saved();original=copy.deepcopy(saved)
        with patch('investigator.agent_ticket.AgentTicket.run',return_value='fallback') as fallback:
            self.assertEqual(hybrid_ticket.complete(w,saved),'fallback')
        current=fallback.call_args.args[0];parent=fallback.call_args.kwargs['pipeline_result']
        self.assertEqual(saved,original);self.assertEqual(parent['saved_ticket'],original)
        self.assertEqual(parent['intake']['error'],'TARGET_UNRESOLVED')
        self.assertEqual(current['ticket']['agent_diagnostic_reads'],3)
        self.assertEqual(current['ticket']['agent_intake_diagnostic_reads'],3)
        unhashed=copy.deepcopy(parent);seal=unhashed.pop('hash');self.assertEqual(seal,digest(unhashed))
        self.assertNotIn('source_intake',current['ticket'])

    def test_intake_only_fallback_never_reopens_an_admitted_pipeline_gap(self):
        w=self.workspace();w.agent.config['_estate']['investigation']['fallback_scope']='INTAKE_ONLY'
        saved=self.saved();saved['ticket'].update(state='FINDINGS_SHARED',session_id='run')
        w.agent.get.return_value={'status':'HELD','stop_reason':'NOT_COMPARABLE'}
        with patch('investigator.agent_ticket.AgentTicket.run') as fallback:
            self.assertEqual(hybrid_ticket.complete(w,saved),saved)
        fallback.assert_not_called()
        saved=self.saved()
        with patch('investigator.agent_ticket.AgentTicket.run',return_value='intake repair') as fallback:
            self.assertEqual(hybrid_ticket.complete(w,saved),'intake repair')
        fallback.assert_called_once()

    def test_hybrid_cannot_be_started_without_pipeline_authority(self):
        from investigator.agent_ticket import AgentTicket
        with self.assertRaisesRegex(Conflict,'retained pipeline result'):
            AgentTicket(self.workspace()).run(self.saved())

    def test_shared_figure_guidance_does_not_remove_competing_candidate_validation(self):
        from investigator import intake_extraction,agent_intake_settlement
        self.assertIn(intake_extraction.FIGURE_INSTRUCTIONS,intake_extraction.INSTRUCTIONS)
        self.assertIn(intake_extraction.FIGURE_INSTRUCTIONS,agent_intake_settlement.DESCRIPTION)
        from investigator import reported_figure
        text='The visual shows 950 or 550.'
        spans=[{'start':text.index(q),'end':text.index(q)+len(q),'quote':q} for q in ('950','550')]
        with self.assertRaises(reported_figure.AmbiguousFigure):
            reported_figure.from_candidates(spans,text)

    def test_hybrid_gap_cap_and_request_bound_are_separate_from_pipeline(self):
        from investigator.estate_manifest import validate
        from test_estate_manifest import ManifestTests
        from investigator.agent_provider import request_bound
        m=ManifestTests().fixture();m['investigation']={'mode':'HYBRID','step_cap':12,'wall_seconds':900,'input_characters_per_request':150000}
        self.assertEqual(validate(m)['investigation']['step_cap'],12)
        m['investigation']['step_cap']=13
        with self.assertRaises(ValueError):validate(m)
        runtime=SimpleNamespace(config={'_estate':{'investigation':{'mode':'HYBRID','input_characters_per_request':150000}}},generation_options={'max_payload_characters':48000})
        self.assertEqual(request_bound(runtime),150000)
        runtime.config['_estate']['investigation']={'mode':'PIPELINE'}
        self.assertEqual(request_bound(runtime),48000)

    def test_answered_validated_pipeline_bypasses_agent_despite_snapshot_limit(self):
        w=self.workspace();saved=self.saved();saved['ticket'].update(state='FINDINGS_SHARED',session_id='run')
        state={'synthesis':{'status':'COMPLETED'},'cloud_calls':4};w.agent.get.return_value=state
        findings={'assessment':{'limits':['SNAPSHOT_UNVERIFIED']},'outputs':{k:{'question_account':{'status':'ANSWERED'}} for k in ('business_output','technical_output')}}
        with patch('investigator.ticket_findings.from_state',return_value=findings) as validate,patch('investigator.agent_ticket.AgentTicket.run') as fallback:
            self.assertEqual(hybrid_ticket.complete(w,saved),saved)
        validate.assert_called_once_with(state);fallback.assert_not_called()

    def test_partial_answer_is_a_named_gap(self):
        saved=self.saved();saved['ticket']['state']='FINDINGS_SHARED'
        findings={'assessment':{'classification':'TRANSFORMATION_LOGIC'},'evidence_ids':['read'],
            'outputs':{k:{'question_account':{'status':'PARTLY_ANSWERED','reason':'Currency not established'}} for k in ('business_output','technical_output')}}
        with patch('investigator.ticket_findings.from_state',return_value=findings):
            result=hybrid_ticket.gap(saved,{'synthesis':{'status':'COMPLETED'}})
        self.assertEqual(result['reason'],'QUESTION_NOT_FULLY_ANSWERED');self.assertEqual(result['evidence_ids'],['read'])

    def test_pipeline_first_and_nested_submission_never_runs_two_fallbacks(self):
        w=self.workspace();controller=SimpleNamespace(workspace=w);order=[]
        def pipeline(request):
            order.append('pipeline');return hybrid_ticket.submit(controller,request,lambda r:self.saved())
        with patch('investigator.hybrid_ticket.complete',side_effect=lambda w,s:order.append('fallback') or s):
            hybrid_ticket.submit(controller,{},pipeline)
        self.assertEqual(order,['pipeline','fallback']);self.assertFalse(w._hybrid_pipeline_active)

    def test_standard_tool_uses_original_candidate_and_cannot_change_outcome_or_drop_evidence(self):
        class BoundAdapter(Adapter):
            def evaluate(self,*args):
                probe=super().evaluate(*args)
                probe.evidence['test_purpose']='REPRODUCE_MEASURE'
                return probe
        assessment=vertical(BoundAdapter(['top','lower'],{'top':5,'lower':5}),'m',{'filters':[]})
        observations={o['id']:o for o in assessment.pop('_observations')}
        candidate={'status':'AVAILABLE','assessment':assessment,'observations':observations}
        standard=Mock(return_value=candidate)
        tools=InvestigationTools(object(),{'t':{'measure_id':'m','scope_id':'s'}},{'s':{'filters':[]}},PersistedBoundary(),standard=standard)
        result=tools.invoke('run_standard_investigation',{'target_id':'t','scope_id':'s'})
        self.assertEqual(result['evidence_ids'],[result['facade_evidence_id']])
        self.assertTrue(set(assessment['evidence_ids'])<=set(result['native_evidence_ids']))
        refs=result['evidence_ids'];support=tools.terminal_support('CONSISTENT_TO_BOUNDARY','t',refs)
        self.assertEqual(support['assessment'],assessment);self.assertEqual(support['observations'],observations)
        with self.assertRaisesRegex(ValueError,'outcome differs'):tools.terminal_support('TRANSFORMATION_LOGIC','t',refs)
        with self.assertRaisesRegex(ValueError,'coverage incomplete'):tools.terminal_support('CONSISTENT_TO_BOUNDARY','t',[])
        unrelated=tools.invoke('run_standard_investigation',{'target_id':'t','scope_id':'other'})
        with self.assertRaisesRegex(ValueError,'coverage incomplete'):tools.terminal_support('CONSISTENT_TO_BOUNDARY','t',unrelated['evidence_ids'])
        refused=tools.invoke('run_standard_investigation',{'target_id':'t','scope_id':'other'})
        self.assertEqual(refused['status'],'UNDECLARED');self.assertEqual(standard.call_count,1)
        self.assertNotIn('run_standard_investigation',{s['name'] for s in schemas()})
        self.assertIn('run_standard_investigation',{s['name'] for s in schemas(include_standard=True)})

    def test_pipeline_evidence_fetch_is_preserved_without_reading(self):
        calls=Mock(side_effect=[{'action':'TOOL','summary':'Inspect prior refusal','tool':'get_evidence','arguments':{'id':'old'}},
            {'action':'HOLD','summary':'No scope authority','reason':'TARGET_UNRESOLVED'}])
        events=[]
        loop=AgentLoop(tools={},schemas={},decide=calls,persist=lambda x:events.append(copy.deepcopy(x)) or 'receipt:'+str(len(events)),
            validate_delivery=Mock(side_effect=AssertionError('no answer')),outcomes=['NO_COMPARABLE_PATH'],admit=lambda *a:None,step_cap=2)
        original={'id':'old','status':'UNAVAILABLE','reason':'TARGET_UNRESOLVED'}
        result=loop.run({},fixed_facts={},context_id='c',starting_evidence={'old':original})
        self.assertEqual(result['status'],'HELD')
        self.assertEqual(calls.call_args.args[0]['fetched_evidence']['result'],original)
        self.assertEqual(events[1]['result'],original)

    def test_standard_result_references_seeded_pipeline_evidence_without_rebinding_it(self):
        class BoundAdapter(Adapter):
            def evaluate(self,*args):
                probe=super().evaluate(*args)
                probe.evidence['test_purpose']='REPRODUCE_MEASURE'
                return probe
        assessment=vertical(BoundAdapter(['top','lower'],{'top':5,'lower':5}),'m',{'filters':[]})
        observations={o['id']:o for o in assessment.pop('_observations')}
        candidate={'status':'AVAILABLE','assessment':assessment,'observations':observations}
        tools=InvestigationTools(object(),{'t':{'measure_id':'m','scope_id':'s'}},{'s':{'filters':[]}},PersistedBoundary(),standard=lambda *a:candidate)
        original_id=next(iter(observations));original=copy.deepcopy(observations[original_id]);events=[]
        decide=Mock(side_effect=[{'action':'TOOL','summary':'Use retained walk','tool':'run_standard_investigation','arguments':{'target_id':'t','scope_id':'s'}},
            {'action':'TOOL','summary':'Inspect original observation','tool':'get_evidence','arguments':{'id':original_id}},
            {'action':'HOLD','summary':'Remaining gap unavailable','reason':'CAPABILITY_UNAVAILABLE'}])
        loop=AgentLoop(tools={'run_standard_investigation':lambda **args:tools.invoke('run_standard_investigation',args)},
            schemas={'run_standard_investigation':next(s['parameters'] for s in schemas(include_standard=True) if s['name']=='run_standard_investigation')},decide=decide,
            persist=lambda e:events.append(copy.deepcopy(e)) or 'receipt:'+str(len(events)),validate_delivery=Mock(),
            outcomes=['CONSISTENT_TO_BOUNDARY'],admit=lambda *a:None,step_cap=3)
        loop.run({},fixed_facts={},context_id='c',starting_evidence=observations)
        self.assertFalse(any(e['event']=='TOOL_FAILED' for e in events))
        fetch=next(e for e in events if e['event']=='EVIDENCE_FETCH')
        self.assertEqual(fetch['evidence']['result'],original)
        self.assertEqual(observations[original_id],original)

    def test_standard_candidate_executes_same_walk_and_remains_nonterminal_until_support_gate(self):
        import test_flexible_investigation as fixture
        from investigator.adaptive_runtime import AdaptiveRuntime
        from investigator.process_debugging import VERSION
        helper=fixture.DynamicTests();helper.setUp();self.addCleanup(helper.doCleanups)
        helper.config['_estate']={'investigation':{'mode':'HYBRID','step_cap':12,'wall_seconds':900}}
        from investigator.enterprise_discovery import Discovery
        helper.fixture.discovery=Discovery(helper.store,helper.config);helper.fixture.scan()
        envelope=copy.deepcopy(helper.envelope);envelope['strategy']=VERSION
        model=helper.store.list(True)[0]
        envelope.update(context_id=model['context_id'],revision=model['revision'])
        runtime=AdaptiveRuntime(helper.runtime,lambda _:self.fail('No planner'))
        identity=runtime.create(envelope,'hybrid-standard-candidate')['id']
        runtime.begin_agent_process(identity)
        class BoundAdapter(Adapter):
            _runtime_local_execution=True
            _runtime_meter_read=staticmethod(lambda *a:None)
            _runtime_stage_event=staticmethod(lambda *a:None)
            def evaluate(self,*args):
                p=super().evaluate(*args);p.evidence['test_purpose']='REPRODUCE_MEASURE';return p
        adapter=BoundAdapter(['top','lower'],{'top':5,'lower':5})
        with patch.object(runtime,'process_adapter',return_value=adapter):
            candidate=runtime.run_process(identity,agent_candidate=True)
        self.assertEqual(candidate['status'],'AVAILABLE')
        self.assertEqual(candidate['assessment']['classification'],'CONSISTENT_TO_BOUNDARY')
        self.assertEqual(adapter.evaluated,['top','lower'])
        self.assertEqual(runtime.get(identity)['status'],'EXECUTING')
        self.assertEqual({o['id']:o for o in runtime.get(identity)['observations']},candidate['observations'])
        runtime.config['_estate']['investigation']['mode']='PIPELINE'
        with self.assertRaises(Conflict):runtime.run_process(identity,agent_candidate=True)

    def test_actual_fallback_admission_carries_prior_reads_and_full_pipeline_state(self):
        from test_agent_intake_settlement import SettlementTests
        from investigator.agent_ticket import AgentTicket
        fixture=SettlementTests();fixture.setUp();self.addCleanup(fixture.doCleanups)
        w=fixture.workspace
        w.agent.config['_estate']={'investigation':{'mode':'HYBRID','step_cap':3,'wall_seconds':900}}
        fixture.f.helper.h.model['discovery']['policy_hash']=digest(w.agent.config)
        saved=w.smart_intake.tickets.submit({'text':fixture.form['description'],'request_key':'hybrid-intake-test'},'hybrid-intake-test')
        parent={'saved_ticket':copy.deepcopy(saved),'session':None,'gap':{'reason':'TARGET_UNRESOLVED'},'intake':None}
        parent['hash']=digest(parent)
        def retain(t):
            t.update(form_input=copy.deepcopy(fixture.form),form_catalog_hash=digest(fixture.catalog),
                     hybrid_pipeline=copy.deepcopy(parent),agent_diagnostic_reads=2)
            return t
        saved=w.smart_intake.tickets.update(saved['ticket']['id'],saved['revision'],retain)
        decide=Mock(side_effect=[{'action':'TOOL','summary':'Resolve the named scope','tool':'resolve_ticket','arguments':{'extraction':fixture.raw}},
            {'action':'HOLD','summary':'No additional evidence','reason':'GAP_NOT_CLOSED'}])
        with patch('investigator.agent_ticket.snapshot',return_value=fixture.catalog),patch('investigator.context_search.latest',return_value={'version':'synthetic','assets':[]}),patch('investigator.agent_ticket.GovernedDecision',return_value=decide),patch.object(w.agent,'process_adapter',return_value=Mock()):
            result=AgentTicket(w).run(saved,pipeline_result=parent)
        self.assertEqual(result['ticket']['hybrid_pipeline'],parent)
        self.assertEqual(w.agent.get(result['ticket']['session_id'])['cloud_calls'],2)
        self.assertEqual(decide.call_args.args[0]['ticket']['pipeline_starting_state'],parent)
        self.assertIn('run_standard_investigation',{x['name'] for x in decide.call_args.args[0]['tool_catalog']})


if __name__=='__main__':unittest.main()
