import copy,json,sqlite3,unittest
from investigator.onboarding import digest,encoded
from investigator.run_history import capture,attach


class RunHistoryTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(':memory:');self.db.row_factory=sqlite3.Row
        self.db.execute('CREATE TABLE adaptive_sessions(id TEXT,model_id TEXT,state TEXT,state_hash TEXT)')
        self.db.execute('CREATE TABLE adaptive_syntheses(id TEXT,body TEXT,body_hash TEXT)')
        self.addCleanup(self.db.close)

    def state(self,id,text='Exact ticket.',model='model',cell=False):
        address={'target_id':'visual','measure_id':'measure','grouping_columns':[],'key_restrictions':[],'mode':'UNGROUPED'}
        address={'id':digest(address),**address}
        return {'id':id,'model_id':model,'envelope':{'symptom':text},'observations':[{'read_address':{'kind':'CELL','cell':address}}] if cell else []}

    def put(self,s):
        self.db.execute('INSERT INTO adaptive_sessions VALUES(?,?,?,?)',(s['id'],s['model_id'],encoded(s),digest(s)))

    def test_ticket_and_native_cell_links_are_independent_and_only_earlier_same_model(self):
        prior=self.state('old-ticket');cell=self.state('old-cell','Different ticket.',cell=True)
        current=self.state('current',cell=True)
        for s in (prior,cell,self.state('other-model',model='other',cell=True),current,self.state('later',cell=True)):self.put(s)
        before=list(self.db.execute('SELECT state,state_hash FROM adaptive_sessions'))
        result=capture(self.db,current)
        self.assertEqual(result['same_ticket'],['old-ticket'])
        self.assertEqual(result['same_cells'][0]['run_ids'],['old-cell'])
        self.assertEqual([tuple(x) for x in before],[tuple(x) for x in self.db.execute('SELECT state,state_hash FROM adaptive_sessions')])
        self.assertNotIn('Exact ticket.',json.dumps(result))

    def test_missing_historical_address_is_not_inferred_and_partial_invalid_record_is_visible(self):
        legacy=self.state('legacy','Other.');legacy['observations']=[{'cell_address':{'id':'guessed'}}]
        current=self.state('current',cell=True)
        for s in (legacy,current):self.put(s)
        self.assertEqual(capture(self.db,current)['same_cells'][0]['run_ids'],[])
        self.db.execute("UPDATE adaptive_sessions SET state_hash='wrong' WHERE id='legacy'")
        self.assertEqual(capture(self.db,current),{'version':1,'status':'UNAVAILABLE','reason':'PRIOR_RECORD_INTEGRITY_DIFFERS','record_id':'legacy'})
        self.db.execute("UPDATE adaptive_sessions SET state='not-json' WHERE id='legacy'")
        self.assertEqual(capture(self.db,current),{'version':1,'status':'UNAVAILABLE','reason':'PRIOR_RECORD_INVALID','record_id':'legacy'})

    def test_technical_identifier_line_does_not_change_business_or_historical_outputs(self):
        outputs={'business_output':{'explanation':{'text':'Business body.'}},'technical_output':{'explanation':{'text':'Mechanism.'}}}
        before=copy.deepcopy(outputs);attach(outputs,{})
        self.assertEqual(outputs,before)
        state=self.state('current');self.put(state);state['previous_runs']=capture(self.db,state)
        attach(outputs,state)
        self.assertEqual(outputs['business_output'],before['business_output'])
        self.assertEqual(outputs['technical_output']['explanation']['text'],'Mechanism.\n\nPrevious runs: same ticket none.')

    def test_real_composition_keeps_business_byte_identical_and_provider_input_unchanged(self):
        from test_synthesis_narrative import NarrativeContractTests
        from investigator import synthesis_narrative as narrative
        fixture=NarrativeContractTests();state,payload=fixture.source('CONSISTENT_TO_BOUNDARY')
        response=fixture.response(payload);original=copy.deepcopy(payload)
        _,before=narrative.assemble(narrative.Response(copy.deepcopy(response)),payload,state)
        state['previous_runs']={'version':1,'status':'RECORDED','ticket_key':'key','same_ticket':['run-a'],'same_cells':[]}
        _,after=narrative.assemble(narrative.Response(copy.deepcopy(response)),payload,state)
        from investigator.evidence_synthesis import save
        save(self.db,'composed',{'status':'COMPLETED','outputs':after},source_state=state)
        self.assertEqual(encoded(before['business_output']),encoded(after['business_output']))
        self.assertEqual(payload,original)
        self.assertEqual(after['technical_output']['explanation']['text'],before['technical_output']['explanation']['text']+'\n\nPrevious runs: same ticket run-a.')

    def test_completed_refusal_and_degraded_outputs_use_the_same_history_finalizer(self):
        from investigator.evidence_synthesis import save
        from investigator import process_receipts,refusal_synthesis
        state={'text':'What happened?','observations':[process_receipts.refusal('WALK_REFUSED','Retained refusal.','refusal')],
               'previous_runs':{'version':1,'status':'RECORDED','ticket_key':'key','same_ticket':['prior'],'same_cells':[]}}
        refusal=refusal_synthesis.render(state)
        for provenance in ('DETERMINISTIC_REFUSAL_RENDERING','DETERMINISTIC_BOUNDED_SPINE_RENDERING','LLM_INFERRED'):
            with self.subTest(provenance=provenance):
                outputs=copy.deepcopy(refusal);business=encoded(outputs['business_output'])
                body={'status':'COMPLETED','outputs':outputs,'provenance':provenance}
                with self.assertRaisesRegex(ValueError,'original history source state'):save(self.db,provenance,body)
                save(self.db,provenance,body,source_state=state)
                save(self.db,provenance,body,source_state=state)
                self.assertEqual(encoded(outputs['business_output']),business)
                self.assertEqual(outputs['technical_output']['explanation']['text'].count('Previous runs:'),1)

    def test_actual_runtime_persists_links_without_adding_them_to_planner_context(self):
        from test_adaptive_investigation import AdaptiveTests
        from investigator.adaptive_candidates import catalog
        helper=AdaptiveTests();helper.setUp();self.addCleanup(helper.doCleanups)
        first=helper.agent.create(helper.envelope,'history-first')
        second=helper.agent.create(helper.envelope,'history-second')
        self.assertEqual(second['previous_runs']['same_ticket'],[first['id']])
        self.assertEqual(helper.agent.get(first['id'])['previous_runs']['same_ticket'],[])
        candidates,_=catalog(helper.store,helper.config,helper.envelope)
        without=copy.deepcopy(second);without.pop('previous_runs')
        self.assertEqual(encoded(helper.agent.payload(second,candidates)),encoded(helper.agent.payload(without,candidates)))


if __name__=='__main__':unittest.main()
