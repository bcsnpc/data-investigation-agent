"""All nine verdicts are evidence contracts, never model outcome aliases."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock,patch
from investigator.evidence_verdicts import Evidence,check,quantity
from investigator.ledger_investigator_tools import Tools
from investigator.ledger_investigator import Investigator

NOW='2026-10-22T11:00:00Z'


def read(subject,value,context=None):
    return {'subject':subject,'key':'record-1','state':'VALUE','value':value,'context':context or {'warehouse':'North'},
        'receipt_id':'read:'+subject,'route_admitted':True,'read_only_verified':True,'expression_hash':'a'*64,'execution_surface':'declared-surface',
        'warnings':['attestation limited: the engine can’t self-report the calling principal; the token and connection were verified separately']}


def fact(subject,kind,value):
    return {'subject':subject,'kind':kind,'value':value,'state':'OBSERVED','freshness':'CURRENT','collected_at':NOW,'observed_at':NOW,
        'source':'RUNTIME_OBSERVATION','reason':None,'provenance':{'evidence_ids':['native-fact'],'collector':'fixture','locator':subject}}


class VerdictTests(unittest.TestCase):
    def setUp(self):
        self.registry=Evidence(['visual','down','up','job'],lambda value:'persisted:'+str(len(str(value))))
        self.ids=[]
        for subject,value in [('visual',7),('down',7),('up',8)]:self.ids.append(self.registry.add('READ',[subject],read(subject,value)))
        self.comparison=self.registry.add('COMPARISON',['down','up'],{'left':self.ids[1],'right':self.ids[2],'support_ids':self.ids[:3]});self.ids.append(self.comparison)
        self.ids.append(self.registry.add('BOUNDARY',['down','up','job'],{'downstream':'down','upstream':'up','job':'job','quantity_preserving':True,'kind':'LOAD'}))
        self.add_fact('up','TABLE_LOAD',{'last_modified':'2026-10-22T10:00:00Z'})
    def add_fact(self,subject,kind,value):
        self.ids.append(self.registry.add('FACT',[subject],fact(subject,kind,value)))
    def validate(self,verdict):return check(verdict,self.ids,self.registry,now=NOW)
    def test_failed_job_requires_linked_quantity_split_and_failed_run_error(self):
        self.add_fact('job','JOB_RUN',{'status':'FAILED','run_id':'r','start':'2026-10-22T10:01:00Z','end':'2026-10-22T10:02:00Z','error':'copy rejected source row'})
        self.assertEqual(self.validate('failed job')['verdict'],'failed job')
        with self.assertRaisesRegex(ValueError,'DIVERGENT_EQUIVALENT'):check('failed job',self.ids[4:],self.registry,now=NOW)
    def test_waiting_on_job_requires_queued_or_overdue_after_source_changed(self):
        self.add_fact('job','JOB_RUN',{'status':'QUEUED','run_id':'r','start':'2026-10-22T10:01:00Z','end':None})
        self.assertEqual(self.validate('waiting on job')['verdict'],'waiting on job')
    def test_refresh_stale_requires_model_refresh_boundary_and_load_after_refresh(self):
        self.ids[4]=self.registry.add('BOUNDARY',['down','up','job'],{'downstream':'down','upstream':'up','job':'job','quantity_preserving':True,'kind':'MODEL_REFRESH'})
        self.add_fact('job','REFRESH_RUN',{'status':'SUCCEEDED','run_id':'refresh','start':'2026-10-22T08:00:00Z','end':'2026-10-22T09:00:00Z'})
        self.assertEqual(self.validate('refresh stale')['verdict'],'refresh stale')
    def test_latency_requires_not_due_schedule_and_measured_typical_duration(self):
        self.add_fact('job','JOB_RUN',{'status':'SUCCEEDED','run_id':'r','start':'2026-10-22T08:00:00Z','end':'2026-10-22T09:00:00Z'})
        self.add_fact('job','SCHEDULE',{'next_due':'2026-10-22T12:00:00Z'})
        self.add_fact('job','TYPICAL_DURATION',{'median_seconds':60,'sample_count':3})
        result=self.validate('latency');self.assertEqual(result['expected_update_at'],'2026-10-22T12:01:00.000000Z')
    def test_different_question_requires_same_expression_surface_with_observed_context_effect(self):
        other=self.registry.add('READ',['down'],read('down',8,{'warehouse':'South'}))
        self.ids.append(self.registry.add('COMPARISON',['down'],{'left':self.ids[1],'right':other,'support_ids':[self.ids[1],other]}))
        self.assertEqual(self.validate('different question')['verdict'],'different question')
    def witness(self,kind,**extra):
        self.ids.append(self.registry.add(kind,['down','up'],{'checked':True,'mechanism':'The checked retained operation produces the observed split.','support_ids':[self.comparison],**extra}))
    def test_as_designed_requires_checked_design_not_business_correctness(self):
        from test_process_debugging import Adapter
        from investigator.process_debugging import vertical
        from investigator.native_verdict_support import design_witness
        native=vertical(Adapter(['down','up'],{'down':7,'up':8},explain=True),'measure',{})
        observations={o['id']:o for o in native.pop('_observations')}
        registry=Evidence(['down','up'],lambda _: 'retained');ids=[]
        for subject,value in [('down',7),('up',8)]:
            original=observations['read-'+subject];original['declared_context']={'warehouse':'North'};original['test_purpose']='REPRODUCE_MEASURE'
            result={**read(subject,value),'receipt_id':original['id'],'query':original['query'],'execution_surface':original['execution_surface']}
            ids.append(registry.add('READ',[subject],result))
        comparison=registry.add('COMPARISON',['down','up'],{'left':ids[0],'right':ids[1],'support_ids':list(ids)})
        witness=design_witness(native,observations);witness['support_ids']=[comparison]
        identity=registry.add('DESIGN_CHECK',['down','up'],witness)
        self.assertEqual(check('as designed',[identity],registry,now=NOW)['verdict'],'as designed')
        pending={'kind':'COMPARE','comparison_pending':True,'comparison_pending_kind':'own count'}
        qualified=check('as designed',[identity],registry,now=NOW,request=pending)
        self.assertEqual(qualified['claim_scope'],'NATIVE_FINDING_WITH_EXTERNAL_COMPARISON_PENDING')
        self.assertFalse(qualified['comparison_checked'])
        self.assertIn('external comparison has not been checked',qualified['reason'])
        self.witness('DESIGN_CHECK',business_correctness_claim=False)
        with self.assertRaisesRegex(ValueError,'NATIVE_DESIGN_EVIDENCE_REQUIRED'):self.validate('as designed')
        witness['native_observations']['read-down']['query']='another query'
        changed=registry.add('DESIGN_CHECK',['down','up'],witness)
        with self.assertRaises(ValueError):check('as designed',[changed],registry,now=NOW)
        with self.assertRaises(ValueError):check('as designed',[changed],registry,now=NOW,request=pending)
    def test_access_difference_requires_observed_scoped_reads_without_impersonation(self):
        registry=Evidence(['visual'],lambda _: 'retained');refs=[]
        for identity,value in [('reader-a',7),('reader-b',8)]:
            result={**read('visual',value),'receipt_id':identity,'authenticated_identity':identity,'identity_verified':True,
                'query':'SELECT SUM(units) FROM dbo.records','execution_surface':{'engine':'sql','connection':'same','object':'same','identity':identity}}
            refs.append(registry.add('READ',['visual'],result))
        comparison=registry.add('COMPARISON',['visual'],{'left':refs[0],'right':refs[1],'support_ids':refs})
        witness=registry.add('ACCESS_CHECK',['visual'],{'checked':True,'mechanism':'Retained authorized reads.','impersonated':False,'support_ids':[comparison]})
        self.assertEqual(check('access difference',[witness],registry,now=NOW)['verdict'],'access difference')
        self.witness('ACCESS_CHECK',same_query_and_context=True,observed_access_difference=True,impersonated=False)
        with self.assertRaisesRegex(ValueError,'ORIGINAL_PAIRED_AUTHORIZED'):self.validate('access difference')
    def test_source_changed_history_requires_verified_source_row_history(self):
        path=self.registry.add('PATH',['up'],{'nodes':[{'id':'up','properties':{'system_of_record':True}}]})
        history={'subject':'up','receipt_id':'native-history','read_only_verified':True,'route_admitted':True,'key':'record-1','context':{'warehouse':'North'},
            'query':'SELECT before_units,after_units FROM dbo.source_history','read_only_objects':['[dbo].[source_history]'],'execution_surface':'declared-surface',
            'before_quantity':7,'after_quantity':8,'changes':[{'key':'record-1','before':{'units':7},'after':{'units':8},'effective_at':'2026-10-21T00:00:00Z','changed_at':'2026-10-22T10:00:00Z'}]}
        self.ids.append(self.registry.add('HISTORY_CHECK',['up'],{'checked':True,'mechanism':'Retained source history.','native_history':history,'support_ids':[self.comparison,path]}))
        self.assertEqual(self.validate('source changed history')['verdict'],'source changed history')
        self.ids=self.ids[:-1];self.witness('HISTORY_CHECK',system_of_record=True,row_history_verified=True)
        with self.assertRaisesRegex(ValueError,'ORIGINAL_HISTORY_READ'):self.validate('source changed history')
    def test_not_found_never_fabricates_a_cause(self):self.assertEqual(self.validate('not found')['verdict'],'not found')
    def test_mismatched_context_cannot_explain_stale_serving(self):
        other=self.registry.add('READ',['up'],read('up',8,{'warehouse':'South'}))
        ids=[self.registry.add('COMPARISON',['down','up'],{'left':self.ids[1],'right':other,'support_ids':[self.ids[1],other]}),*self.ids[4:]]
        with self.assertRaisesRegex(ValueError,'DIVERGENT_EQUIVALENT'):check('refresh stale',ids,self.registry,now=NOW)
    def test_unknown_subject_unknown_id_and_model_inference_do_not_become_support(self):
        with self.assertRaisesRegex(ValueError,'OUTSIDE'):self.registry.add('FACT',['unrelated'],{})
        with self.assertRaisesRegex(ValueError,'UNKNOWN_EVIDENCE'):check('as designed',['invented'],self.registry,now=NOW)
        for verdict in ('as designed','access difference','source changed history'):
            with self.subTest(verdict=verdict),self.assertRaises(ValueError):self.validate(verdict)
    def test_blank_is_value_not_zero_or_unavailable(self):
        self.assertNotEqual(quantity({'state':'BLANK','value':None}),quantity({'state':'VALUE','value':0}))
        with self.assertRaises(ValueError):quantity({'state':'UNAVAILABLE','value':None})
    def test_stale_or_future_failed_run_is_not_current_cause(self):
        value=fact('job','JOB_RUN',{'status':'FAILED','run_id':'r','start':'2026-10-22T10:01:00Z','end':'2026-10-22T10:02:00Z','error':'retained error'})
        value['freshness']='STALE';self.ids.append(self.registry.add('FACT',['job'],value))
        with self.assertRaises(ValueError):self.validate('failed job')


class OperationalFactTests(unittest.TestCase):
    def test_when_last_refreshed_reports_the_recorded_finish_not_the_observation_time(self):
        end='2026-10-22T09:42:00Z'
        engine,ticket,reader,decide=self.status_engine([fact('job','REFRESH_STATE',
            {'state':'SUCCEEDED','run_id':'refresh-1','last_end':end})])
        engine.tools.nodes['job']['kind']='MODEL';engine.tools.nodes['job']['label']='Inventory model'
        text='When was Inventory model last refreshed?'
        ticket.update(text=text,request={'kind':'FACT','subject':'job','question':'REFRESH_STATUS',
            'source':{'start':0,'end':len(text),'quote':text}})
        result=engine.run(ticket)
        self.assertEqual(result['support']['claim_scope'],'OPERATIONAL_FACT_ONLY')
        for output in result['outputs'].values():
            self.assertIn('end: '+end,output)
            self.assertIn('observed: '+NOW,output)
        reader.assert_not_called();decide.assert_not_called()

    def status_engine(self,values):
        text='Did the latest Copy Job run fail?'
        request={'kind':'FACT','subject':'job','question':'RUN_STATUS','source':{'start':0,'end':len(text),'quote':text}}
        graph=Mock();graph._slice.return_value={'nodes':[{'id':'job','kind':'PIPELINE','label':'Primary copy'}],'edges':[],'stops':[],'truncated':False}
        graph.node_facts.return_value={'facts':values}
        reader=Mock();decide=Mock()
        tools=Tools(graph,object(),visual='job',now=NOW,persist=lambda _:'retained',value_reader=reader,request_kind='FACT')
        engine=Investigator(tools,decide=decide,persist=lambda _:'retained',admit=lambda *_:None,clock=lambda:1.0)
        return engine,{'text':text,'request':request},reader,decide
    def test_success_is_an_answered_operational_fact_not_a_numeric_or_business_verdict(self):
        success=fact('job','JOB_RUN',{'status':'SUCCEEDED','run_id':'last-success','start':'2026-10-22T10:00:00Z','end':'2026-10-22T10:01:00Z'})
        engine,ticket,reader,decide=self.status_engine([success])
        result=engine.run(ticket)
        self.assertEqual(result['verdict'],'not found');self.assertEqual(result['support']['claim_scope'],'OPERATIONAL_FACT_ONLY')
        self.assertEqual(result['support']['operational_fact']['value']['run_id'],'last-success')
        self.assertEqual(result['stop_reason'],'OPERATIONAL_STATUS_PROVEN')
        reader.assert_not_called();decide.assert_not_called()
        for text in result['outputs'].values():
            self.assertIn('Answer status: answered',text);self.assertIn('SUCCEEDED',text);self.assertIn('last-success',text)
            self.assertIn('no numerical cause was established',text);self.assertNotIn('Furthest measured point',text)
    def test_newer_unknown_stale_empty_history_or_ambiguous_status_is_not_answered(self):
        success=fact('job','JOB_RUN',{'status':'SUCCEEDED','run_id':'r','start':'2026-10-22T09:00:00Z','end':'2026-10-22T09:01:00Z'})
        unknown=fact('job','JOB_RUN',{'status':'UNKNOWN','run_id':'newer','start':'2026-10-22T10:00:00Z','end':None})
        conflict={**copy.deepcopy(success),'value':{**success['value'],'status':'FAILED'}}
        unavailable={**copy.deepcopy(success),'state':'UNAVAILABLE','collected_at':'2026-10-22T11:00:00Z'}
        stale={**copy.deepcopy(success),'freshness':'STALE'}
        empty=fact('job','RUN_HISTORY',{'runs':[],'listing_complete':True})
        for values in ([success,unknown],[stale],[success,empty],[success,conflict],[success,unavailable]):
            with self.subTest(values=values):
                engine,ticket,reader,decide=self.status_engine(values);result=engine.run(ticket)
                self.assertEqual(result['verdict'],'not found');self.assertNotIn('claim_scope',result['support'])
                self.assertIn('Answer status: not answered',result['outputs']['business'])
                reader.assert_not_called();decide.assert_not_called()
    def test_newer_success_does_not_resurrect_old_failure_and_quote_is_verified(self):
        old=fact('job','JOB_RUN',{'status':'FAILED','run_id':'old','start':'2026-10-22T08:00:00Z','end':'2026-10-22T08:01:00Z'})
        success=fact('job','JOB_RUN',{'status':'COMPLETED','run_id':'new','start':'2026-10-22T10:00:00Z','end':'2026-10-22T10:01:00Z'})
        engine,ticket,reader,decide=self.status_engine([old,success]);result=engine.run(ticket)
        self.assertEqual(result['support']['operational_fact']['value']['status'],'COMPLETED')
        ticket['request']['source']['quote']='X'+ticket['request']['source']['quote'][1:]
        engine,ticket2,_,_=self.status_engine([success]);ticket2['request']=ticket['request']
        result=engine.run(ticket2);self.assertNotIn('claim_scope',result['support'])
    def test_explicit_run_status_needs_no_numeric_reads_and_cannot_explain_a_number(self):
        registry=Evidence(['job'],lambda value:'retained')
        text='Did the latest Copy Job run fail?'
        request={'kind':'FACT','subject':'job','question':'RUN_STATUS','source':{'start':0,'end':len(text),'quote':text}}
        identity=registry.add('FACT',['job'],fact('job','JOB_RUN',{'status':'FAILED','run_id':'r','start':'2026-10-22T10:00:00Z','end':'2026-10-22T10:01:00Z','error':'copy failed'}))
        result=check('failed job',[identity],registry,now=NOW,request=request,ticket_text=text)
        self.assertEqual(result['claim_scope'],'OPERATIONAL_FACT_ONLY')
        self.assertEqual(result['claim_scope'],'OPERATIONAL_FACT_ONLY')
        with self.assertRaisesRegex(ValueError,'DIVERGENT_EQUIVALENT'):check('failed job',[identity],registry,now=NOW)
        wrong='Why is the quantity wrong?'
        invalid={**request,'source':{'start':0,'end':len(wrong),'quote':wrong}}
        with self.assertRaisesRegex(ValueError,'EXPLICIT_OPERATIONAL'):check('failed job',[identity],registry,now=NOW,request=invalid,ticket_text=wrong)

    def test_specific_error_and_times_appear_in_both_outputs_without_model_or_value_read(self):
        run={'status':'FAILED','run_id':'run-specific','start':'2026-10-22T10:00:00Z',
             'end':'2026-10-22T10:01:00Z','error':{'code':'2011','message':'Source rejected row 900'}}
        engine,ticket,reader,decide=self.status_engine([fact('job','JOB_RUN',run)])
        result=engine.run(ticket)
        for output in result['outputs'].values():
            for literal in ('Primary copy','run-specific','FAILED',run['start'],run['end'],'Source rejected row 900','2011'):
                self.assertIn(literal,output)
            self.assertIn('answered: the explicit operational-status question',output)
            self.assertIn('Job-reported failure cause:',output)
            self.assertIn('The ledger establishes this reported operational failure.',output)
        reader.assert_not_called();decide.assert_not_called()

    def test_declarative_still_running_status_reports_recorded_schedule_not_speculated_lock(self):
        values=[fact('job','JOB_RUN',{'status':'RUNNING','run_id':'in-flight','start':'2026-10-22T10:00:00Z','end':None}),
                fact('job','SCHEDULE',{'next_due':'2026-10-22T12:00:00Z'})]
        engine,ticket,reader,decide=self.status_engine(values)
        ticket['text']='Pipeline Primary copy still running. Stuck because of a lock?'
        ticket['request']['source']={'start':0,'end':len(ticket['text']),'quote':ticket['text']}
        result=engine.run(ticket)
        self.assertEqual(result['verdict'],'waiting on job')
        for output in result['outputs'].values():
            self.assertIn('run ID: in-flight; status: RUNNING',output)
            self.assertIn('end: not finished at observation',output)
            self.assertIn('Next scheduled run: 2026-10-22T12:00:00Z',output)
            self.assertIn('Recorded job error: unavailable (not recorded)',output)
        self.assertNotIn('lock',result['support']['reason'])
        reader.assert_not_called();decide.assert_not_called()

    def test_missing_run_fields_are_explicitly_unavailable_never_filled_from_other_run(self):
        old=fact('job','JOB_RUN',{'status':'FAILED','run_id':'older','start':'2026-10-22T08:00:00Z',
                               'end':'2026-10-22T08:01:00Z','error':'old error must not substitute'})
        current=fact('job','JOB_RUN',{'status':'FAILED','run_id':'current'})
        engine,ticket,_,_=self.status_engine([old,current]);result=engine.run(ticket)
        text=result['outputs']['business']
        self.assertIn('run ID: current',text);self.assertIn('start: unavailable; end: unavailable',text)
        self.assertIn('Recorded job error: unavailable (not recorded)',text)
        self.assertNotIn('old error',text)
    def test_newer_empty_history_cannot_resurrect_an_older_failed_run(self):
        registry=Evidence(['job'],lambda value:'retained')
        text='Did the latest Copy Job run fail?'
        request={'kind':'FACT','subject':'job','question':'RUN_STATUS','source':{'start':0,'end':len(text),'quote':text}}
        old=fact('job','JOB_RUN',{'status':'FAILED','run_id':'r','start':'2026-10-22T10:00:00Z','end':'2026-10-22T10:01:00Z','error':'copy failed'})
        old['collected_at']='2026-10-22T10:50:00Z';old['observed_at']='2026-10-22T10:01:00Z'
        ids=[registry.add('FACT',['job'],old),registry.add('FACT',['job'],fact('job','RUN_HISTORY',{'runs':[],'listing_complete':True}))]
        with self.assertRaisesRegex(ValueError,'CURRENT_OPERATIONAL'):check('failed job',ids,registry,now=NOW,request=request,ticket_text=text)


class ToolLoopTests(unittest.TestCase):
    def test_untranslatable_scope_is_gap_without_source_outage_or_availability_fact(self):
        from investigator.source_availability import QuantityNotComparable
        tools,engine,reader,_=self.build()
        reader.side_effect=QuantityNotComparable('The selected scope cannot be translated faithfully.')
        before=set(tools.evidence._values)
        gap=tools.evidence.get(tools._read('down',tools.context))
        self.assertEqual(gap['value']['code'],'NOT_COMPARABLE')
        self.assertNotIn('availability',gap['value'])
        self.assertEqual([tools.evidence.get(k)['kind']for k in set(tools.evidence._values)-before],['GAP'])
        reader.assert_called_once()

    def test_unmapped_graph_table_is_a_route_gap_not_a_source_outage(self):
        tools,engine,reader,_=self.build();reader.layers={'visual':{},'up':{}}
        ref=tools._read('down',tools.context)
        gap=tools.evidence.get(ref)
        self.assertEqual(gap['kind'],'GAP')
        self.assertEqual(gap['value']['code'],'QUANTITY_ROUTE_NOT_INSTALLED')
        self.assertNotIn('availability',gap['value'])
        self.assertEqual(tools.pending_quantity_nodes(),['up'])
        reader.assert_not_called()
        self.assertEqual(tools.evidence.get(tools._read('up',tools.context))['kind'],'READ')
        reader.assert_called_once()

    def test_saved_definition_gap_does_not_invent_a_user_filter_question(self):
        tools,engine,reader,_=self.build();tools.scope_gap='Saved visual scope unavailable.'
        result=engine.run({'visual':'visual','text':'Verify this card.',
            'intake_scope':{'filters':[],'periods':[]}})
        self.assertEqual(result['verdict'],'not found')
        self.assertNotIn('question',result)
        self.assertNotIn('filter or period you stated',result['outputs']['business'])
        reader.assert_not_called()
        tools,engine,reader,_=self.build();tools.scope_gap='Unbound selected field.'
        result=engine.run({'visual':'visual','text':'Verify the selected period.',
            'intake_scope':{'filters':[],'periods':[{'quote':'selected period'}]}})
        self.assertEqual(result['question']['code'],'SCOPE_REQUIRED')
        reader.assert_not_called()

    def test_planner_never_receives_correlation_label_and_output_keeps_original_ticket(self):
        tools,engine,reader,events=self.build(step_cap=1);requests=[]
        def decide(payload,**kwargs):
            requests.append(payload)
            self.assertNotIn('id',payload['ticket']);self.assertNotIn('ticket_id',payload['case_file'])
            self.assertEqual(payload['ticket']['text'],'Why does this number differ?')
            return {'action':'VERDICT','summary':'Need support.','hypotheses':['not found'],
                'verdict':'not found','evidence_ids':list(tools.evidence._values)}
        engine.decide=decide
        result=engine.run({'id':'expected-latency-experiment','visual':'visual','text':'Why does this number differ?'})
        self.assertTrue(requests)
        self.assertEqual(result['ticket']['id'],'expected-latency-experiment')
        self.assertEqual(result['case_file']['ticket_id'],'expected-latency-experiment')

    def test_definition_question_quotes_implementation_without_quantity_or_model_calls(self):
        import hashlib
        tools,engine,reader,_=self.build();tools.request_kind='DEFINITION'
        body='{"expression":"AGGREGATE(Entries[Quantity])"}'
        value={'node':'visual','provenance':{'source':'STATIC_DEFINITION'},
               'definition':{'sha256':hashlib.sha256(body.encode()).hexdigest()},
               'content':body,'collection_unavailable':None}
        tools.graph.definition_of.return_value=value;engine.decide=Mock()
        result=engine.run({'visual':'visual','text':'How is this calculation implemented?',
                           'request':{'kind':'DEFINITION','subject':'visual'}})
        self.assertEqual(result['verdict'],'as designed')
        self.assertEqual(result['support']['claim_scope'],'RETAINED_DEFINITION_ONLY')
        for output in result['outputs'].values():
            self.assertIn(body,output)
            self.assertIn('does not establish a numerical result, business correctness',output)
        reader.assert_not_called();engine.decide.assert_not_called()
        tools.graph.definition_of.assert_called_once_with(node='visual')
        self.assertEqual(result['cost']['model_calls'],0)

    def test_definition_reference_or_proposal_never_becomes_implemented_answer(self):
        import hashlib
        for change in ({'content':None},{'provenance':{'source':'MODEL_PROPOSAL'}},
                       {'content':'different'},{'node':'up'}):
            with self.subTest(change=change):
                tools,engine,reader,_=self.build();tools.request_kind='DEFINITION';engine.decide=Mock()
                body='retained implementation'
                value={'node':'visual','provenance':{'source':'STATIC_DEFINITION'},
                       'definition':{'sha256':hashlib.sha256(body.encode()).hexdigest()},'content':body}
                value.update(change);tools.graph.definition_of.return_value=value
                result=engine.run({'visual':'visual','text':'How is this implemented?',
                    'request':{'kind':'DEFINITION','subject':'visual'}})
                self.assertEqual(result['verdict'],'not found')
                self.assertIn('No calculation or business policy was inferred',result['outputs']['business'])
                reader.assert_not_called();engine.decide.assert_not_called()

    def test_definition_collection_gap_qualifies_retained_content_without_blocking(self):
        import hashlib
        tools,engine,reader,_=self.build();tools.request_kind='DEFINITION';engine.decide=Mock()
        body='retained implementation'
        tools.graph.definition_of.return_value={'node':'visual','provenance':{'source':'STATIC_DEFINITION'},
            'definition':{'sha256':hashlib.sha256(body.encode()).hexdigest()},'content':body,
            'collection_unavailable':{'reason':'Metadata collection unavailable'}}
        result=engine.run({'visual':'visual','request':{'kind':'DEFINITION','subject':'visual'}})
        self.assertEqual(result['verdict'],'as designed')
        for output in result['outputs'].values():
            self.assertIn('retained version, not a newly collected definition',output)
        reader.assert_not_called();engine.decide.assert_not_called()

    def test_empty_complete_history_reaches_tool_despite_older_unavailable_run(self):
        old=fact('job','REFRESH_RUN',None);old.update(state='UNAVAILABLE',reason='READ_FAILED:MetadataUnavailable:403',freshness='STALE')
        history=fact('job','RUN_HISTORY',{'runs':[],'listing_complete':True});history['state']='OBSERVED_NEGATIVE'
        coverage=fact('job','COVERAGE',{'history_empty':True,'listing_complete':True});coverage['state']='OBSERVED_NEGATIVE'
        tools,_,reader,_=self.build()
        tools.graph.node_facts.side_effect=lambda node,**kw:{'facts':copy.deepcopy([old,history,coverage])}
        for name,args in (('last_refresh',{'model':'job'}),('last_run',{'job':'job'})):
            result=tools.invoke(name,args)
            self.assertEqual(result['status'],'OBSERVED')
            self.assertIn(history,result['facts']);self.assertIn(coverage,result['facts'])
        reader.assert_not_called()

    def test_failed_or_stale_facts_do_not_become_observed_tool_results(self):
        for state,freshness in (('UNAVAILABLE','CURRENT'),('OBSERVED','STALE'),('UNKNOWN','CURRENT'),('OBSERVED',None)):
            tools,_,reader,_=self.build()
            row=fact('job','REFRESH_RUN',{'status':'SUCCEEDED','run_id':'old'})
            row.update(state=state,freshness=freshness)
            if state=='UNAVAILABLE':row.update(value=None,reason='READ_FAILED:MetadataUnavailable:403')
            tools.graph.node_facts.side_effect=lambda node,**kw:{'facts':[row]}
            self.assertEqual(tools.invoke('last_refresh',{'model':'job'})['status'],'UNAVAILABLE')
            reader.assert_not_called()

    def build(self,decide=None,step_cap=3):
        graph=Mock();graph.path_to_source.return_value={'nodes':[{'id':n,'kind':'VISUAL' if n=='visual' else 'TABLE','label':n} for n in ('visual','down','up','job')],
            'edges':[{'id':'boundary','source':'down','target':'up','confidence':'DECLARED','provenance':{'source':'STATIC_DEFINITION'},'properties':{'comparison_contract':{'job':'job','quantity_preserving':True,'kind':'LOAD'}}}], 'stops':[],'truncated':False}
        graph.node_facts.side_effect=lambda node,**kw:{'facts':[fact('up','TABLE_LOAD',{'last_modified':'2026-10-22T10:00:00Z'})] if node=='up' else [fact('job','JOB_RUN',{'status':'FAILED','run_id':'r','start':'2026-10-22T10:01:00Z','end':'2026-10-22T10:02:00Z','error':'copy failed'})] if node=='job' else []}
        events=[]
        def persist(event):events.append(copy.deepcopy(event));return 'record:'+str(len(events))
        reader=Mock(side_effect=lambda node,key,context:read(node,8 if node=='up' else 7,context))
        tools=Tools(graph,object(),visual='visual',key='record-1',context={'warehouse':'North'},now=NOW,persist=persist,value_reader=reader)
        return tools,Investigator(tools,decide=decide,persist=persist,admit=lambda *_:None,step_cap=step_cap,clock=lambda:1.0),reader,events
    def test_model_selects_registered_read_then_code_validates_one_verdict_with_labels(self):
        tools,engine,reader,events=self.build()
        decisions=[{'action':'TOOL','summary':'Compare the declared boundary.','hypotheses':['failed job'],'tool':'compare_layers','arguments':{'key':'record-1','layers':['down','up'],'filters':{'warehouse':'North'}}}]
        def decide(payload,**kw):
            if decisions:return decisions.pop()
            return {'action':'VERDICT','summary':'The failed run explains this boundary.','hypotheses':['failed job'],'verdict':'failed job','evidence_ids':list(tools.evidence._values)}
        engine.decide=decide
        result=engine.run({'visual':'visual','text':'Why is this lower?'},warnings=['verification: not verified'])
        self.assertEqual(result['verdict'],'failed job');self.assertEqual(result['cost']['model_calls'],2)
        for text in result['outputs'].values():self.assertIn('attestation limited:',text);self.assertIn('verification: not verified',text)
        self.assertEqual(result['stop_reason'],'EVIDENCE_PROVEN')
        self.assertEqual(reader.call_count,3)
    def test_repeated_call_reuses_result_and_forbids_query_and_context_substitution(self):
        tools,engine,reader,_=self.build()
        args={'key':'record-1','layers':['down','up'],'filters':{'warehouse':'North'}}
        first=tools.invoke('compare_layers',args);second=tools.invoke('compare_layers',args)
        self.assertTrue(second['already_obtained']);self.assertEqual(first['evidence_ids'],second['evidence_ids']);self.assertEqual(reader.call_count,2)
        for invalid in ({**args,'query':'DELETE FROM t'},{**args,'filters':{}},{**args,'layers':['unrelated','up']}):
            with self.assertRaises(Exception):tools.invoke('compare_layers',invalid)
    def test_comparison_operands_persist_across_stateless_calls_and_repeated_fetch_is_short(self):
        from investigator.ledger_investigator import evidence_context
        tools,engine,reader,_=self.build()
        refs=tools.invoke('compare_layers',{'key':'record-1','layers':['down','up'],'filters':{'warehouse':'North'}})['evidence_ids']
        cid=refs[-1];first=tools.invoke('get_evidence',{'id':cid});second=tools.invoke('get_evidence',{'id':cid})
        self.assertTrue(second['already_obtained']);self.assertNotIn('evidence',second);self.assertEqual(second['evidence_ids'],[cid])
        other=tools.invoke('get_evidence',{'id':refs[0]})
        index={r['id']:r for r in evidence_context(tools.evidence)}
        comparison=index[cid]['observation']
        self.assertEqual(comparison['left_observation']['value'],7)
        self.assertEqual(comparison['right_observation']['value'],8)
        self.assertEqual(comparison['left_observation']['context'],{'warehouse':'North'})
        self.assertNotIn('native_evidence',str(index));self.assertEqual(reader.call_count,2)
        self.assertNotIn('cause_verified',comparison)

    def test_terminal_source_gap_does_not_justify_skipping_available_prefix(self):
        tools,engine,reader,events=self.build(step_cap=3)
        tools.evidence.add('GAP',['up'],{'reason':'NO_LINEAGE'})
        def decide(payload,**kw):
            if len([x for x in events if x.get('event')=='INVESTIGATOR_DECISION'])==0:
                return {'action':'VERDICT','summary':'Source unavailable.','hypotheses':['not found'],'verdict':'not found','evidence_ids':[tools.path_id]}
            if payload['pending_quantity_nodes']:
                self.assertEqual(payload['feedback']['reason'],'DECLARED_PREFIX_NOT_CHECKED')
                return {'action':'TOOL','summary':'Read the admitted prefix.','hypotheses':['not found'],'tool':'compare_layers','arguments':{'key':'record-1','layers':['down','up','job'],'filters':{'warehouse':'North'}}}
            return {'action':'VERDICT','summary':'No proven cause.','hypotheses':['not found'],'verdict':'not found','evidence_ids':list(tools.evidence._values)}
        engine.decide=decide;result=engine.run({'visual':'visual'})
        self.assertEqual(result['stop_reason'],'EVIDENCE_PROVEN_CODE_FRONTIER');self.assertEqual(result['verdict'],'failed job');self.assertEqual(reader.call_count,4)
        self.assertTrue(any(x.get('reason')=='DECLARED_PREFIX_NOT_CHECKED'for x in events))
    def test_unresolved_named_comparison_keeps_valid_prefix_finding_partial(self):
        tools,engine,reader,events=self.build(step_cap=2)
        tools.comparison={'kind':'source','node':None}
        def decide(payload,**kw):
            if payload['steps_remaining']==2:return {'action':'TOOL','summary':'Compare prefix.','hypotheses':['failed job'],'tool':'compare_layers','arguments':{'key':'record-1','layers':['down','up'],'filters':{'warehouse':'North'}}}
            return {'action':'VERDICT','summary':'Failed run on this boundary.','hypotheses':['failed job'],'verdict':'failed job','evidence_ids':list(tools.evidence._values)}
        engine.decide=decide;result=engine.run({'visual':'visual','text':'Compare with the application.'})
        self.assertEqual(result['verdict'],'failed job')
        for output in result['outputs'].values():self.assertIn('partly answered: the named comparison target was unavailable',output)

    def test_rejected_claim_and_budget_stop_keep_outputs_and_furthest_point(self):
        tools,engine,reader,_=self.build(step_cap=1)
        engine.decide=lambda *a,**kw:{'action':'VERDICT','summary':'Unsupported guess.','hypotheses':['as designed'],'verdict':'as designed','evidence_ids':[tools.path_id]}
        result=engine.run({'visual':'visual'});self.assertEqual(result['verdict'],'not found');self.assertEqual(result['stop_reason'],'TICKET_BUDGET_REACHED')
        self.assertEqual(result['furthest_measured_node'],'visual');self.assertTrue(result['outputs']['technical'])
    def test_budget_refusal_delivers_not_found_without_another_provider_send(self):
        from investigator.usage_governance import UsageHold
        tools,engine,reader,_=self.build()
        engine.admit=Mock(side_effect=UsageHold('ticket budget reached'))
        result=engine.run({'visual':'visual'})
        self.assertEqual(result['verdict'],'not found');self.assertEqual(result['stop_reason'],'TICKET_BUDGET_REACHED');reader.assert_not_called()
    def test_reported_precision_and_non_reproduction_are_always_rendered(self):
        tools,engine,reader,_=self.build()
        text='The card shows 8.'
        reported={'state':'NUMBER','value':'8','source':{'start':15,'end':16,'quote':'8'},'precision':{'state':'EXACT'}}
        result=engine.run({'visual':'visual','text':text,'reported_figure':reported})
        self.assertIn('NOT_REPRODUCED',result['outputs']['business'])
        self.assertTrue(any(r['kind']=='REPRODUCTION' for r in result['evidence'].values()))

    def test_stale_operational_fact_is_topped_up_only_on_its_admitted_node(self):
        graph=Mock();graph._slice.return_value={'nodes':[{'id':'job','kind':'PIPELINE','label':'Load'}],'edges':[],'stops':[],'truncated':False}
        old=fact('job','JOB_RUN',{'status':'FAILED','run_id':'old'});old['freshness']='STALE'
        current=fact('job','JOB_RUN',{'status':'FAILED','run_id':'current','error':'copy failed'})
        graph.node_facts.return_value={'facts':[old]};graph.refresh_facts.return_value={'facts':[current]}
        reader=Mock();collector=Mock();text='Did the latest Copy Job run fail?'
        request={'kind':'FACT','subject':'job','question':'RUN_STATUS','source':{'start':0,'end':len(text),'quote':text}}
        tools=Tools(graph,object(),visual='job',now=NOW,persist=lambda _: 'record',value_reader=reader,collector=collector,request_kind='FACT')
        result=Investigator(tools,decide=None,persist=lambda _: 'record',admit=lambda *_:None,clock=lambda:1.0).run({'text':text,'request':request})
        self.assertEqual(result['verdict'],'failed job');self.assertEqual(result['support']['operational_fact']['value']['run_id'],'current')
        self.assertEqual(graph.refresh_facts.call_args.args[0],['job']);reader.assert_not_called()

    def test_projected_capture_refuses_before_any_graph_read_or_raw_persistence(self):
        graph=Mock();persist=Mock()
        with self.assertRaisesRegex(ValueError,'PROJECTED_CAPTURE_NOT_INSTALLED'):
            Tools(graph,object(),visual='visual',now=NOW,persist=persist,recording_class='PRIVACY_PROJECTED')
        graph.path_to_source.assert_not_called();persist.assert_not_called()

    def test_hostile_reader_cannot_return_another_cell_or_unadmitted_read(self):
        tools,_,reader,_=self.build();reader.side_effect=lambda *args:{**read('down',7),'route_admitted':False}
        with self.assertRaisesRegex(ValueError,'ADMISSION_OR_SCOPE'):tools.reproduce()

class OperationalDeliveryTests(unittest.TestCase):
    def test_boundary_verdicts_keep_their_exact_witness_and_render_it_in_both_outputs(self):
        for verdict in ('failed job','waiting on job','latency'):
            with self.subTest(verdict=verdict):
                tools,engine,_,_=ToolLoopTests().build()
                run={'run_id':'selected-run','start':'2026-10-22T10:01:00Z','end':'2026-10-22T10:02:00Z',
                     'status':'FAILED','error':'copy rejected source row'}
                if verdict=='waiting on job':run.update(status='QUEUED',end=None,error=None)
                if verdict=='latency':run.update(status='SUCCEEDED',start='2026-10-22T08:00:00Z',end='2026-10-22T09:00:00Z',error=None)
                values=[fact('job','JOB_RUN',run),fact('job','SCHEDULE',{'next_due':'2026-10-22T12:00:00Z'}),
                        fact('job','TYPICAL_DURATION',{'median_seconds':60,'sample_count':3})]
                tools.graph.node_facts.side_effect=lambda node,**kw:{'facts':values if node=='job' else
                    [fact('up','TABLE_LOAD',{'last_modified':'2026-10-22T10:00:00Z'})] if node=='up' else []}
                choices=[{'action':'TOOL','summary':'Read boundary.','hypotheses':[verdict],'tool':'compare_layers',
                          'arguments':{'key':'record-1','layers':['down','up'],'filters':{'warehouse':'North'}}},
                         {'action':'VERDICT','summary':'Checked witness.','hypotheses':[verdict],'verdict':verdict}]
                def decide(*args,**kw):
                    choice=choices.pop(0)
                    if choice['action']=='VERDICT':choice['evidence_ids']=list(tools.evidence._values)
                    return choice
                engine.decide=decide;answer=engine.run({'visual':'visual','text':'Why does this differ?'})
                self.assertEqual(answer['verdict'],verdict)
                self.assertEqual(answer['support']['operational_fact']['value'],run)
                for output in answer['outputs'].values():
                    for literal in ('Ledger job details: job','run ID: selected-run','status: '+run['status'],run['start']):self.assertIn(literal,output)
                    if verdict=='failed job':self.assertIn('Job-reported failure cause: copy rejected source row',output)
                    else:self.assertIn('Next scheduled run: 2026-10-22T12:00:00Z',output)
                    if verdict=='latency':self.assertIn('Estimated update after the scheduled start',output)

    def test_schedule_is_same_producer_current_unambiguous_and_overdue_does_not_invent_run(self):
        from investigator.evidence_verdicts import operational_support,current_facts
        from investigator.operational_delivery import details
        selected=fact('job','OVERDUE',{'overdue':True,'due_at':'2026-10-22T10:00:00Z'})
        unrelated=fact('other','SCHEDULE',{'next_due':'2026-10-22T12:00:00Z'})
        stale=fact('job','SCHEDULE',{'next_due':'2026-10-22T13:00:00Z'});stale['freshness']='STALE'
        conflicting=[fact('job','SCHEDULE',{'next_due':at}) for at in ('2026-10-22T14:00:00Z','2026-10-22T15:00:00Z')]
        for schedules in ([unrelated,stale],conflicting):
            entries=[{'kind':'FACT','value':row} for row in schedules]
            result=operational_support({'verdict':'waiting on job'},selected,current_facts(entries,NOW))
            text=details(result,{'job':{'label':'Owned pipeline'}})
            self.assertIn('run ID: unavailable (no run recorded); status: OVERDUE',text)
            self.assertIn('Next scheduled run: unavailable',text)
            self.assertIn('Declared due time for the unstarted run: 2026-10-22T10:00:00Z',text)
            self.assertNotIn('12:00:00',text);self.assertNotIn('13:00:00',text)

    def test_requested_historical_run_details_never_substitute_latest(self):
        from investigator.operational_run_selection import from_text
        engine,ticket,_,_=OperationalFactTests().status_engine([
            fact('job','JOB_RUN',{'run_id':'requested','status':'FAILED','start':'2026-10-22T08:00:00Z','end':'2026-10-22T08:01:00Z','error':'requested error'}),
            fact('job','JOB_RUN',{'run_id':'latest','status':'FAILED','start':'2026-10-22T10:00:00Z','end':'2026-10-22T10:01:00Z','error':'unrelated newer error'})])
        text='Did the Copy Job run starting 2026-10-22T08:00:00Z fail?'
        ticket['text']=text;ticket['request'].update(source={'start':0,'end':len(text),'quote':text},run_selector=from_text(text))
        result=engine.run(ticket)
        for output in result['outputs'].values():
            # The full technical pack also preserves other observed runs; only
            # the answer must select the requested witness.
            answer=output.split('\nTechnical evidence pack:')[0]
            self.assertIn('run ID: requested',answer);self.assertIn('Job-reported failure cause: requested error',answer)
            self.assertNotIn('unrelated newer error',answer)


class PendingComparisonTests(unittest.TestCase):
    def test_comparison_question_waits_until_every_declared_read_agrees(self):
        tools,engine,reader,_=ToolLoopTests().build()
        tools.nodes['job']['kind']='PIPELINE'
        tools.graph.node_facts.side_effect=lambda node,**kwargs:{'facts':[]}
        reader.side_effect=lambda node,key,context:read(node,7,context)
        result=engine.run({'visual':'visual','text':'Why is this wrong?',
            'request':{'kind':'COMPARE','comparison_pending':True}})
        self.assertEqual(result['question']['code'],'COMPARISON_REQUIRED')
        self.assertEqual({c.args[0]for c in reader.call_args_list},{'visual','down','up'})
        self.assertFalse(any(r['kind']=='GIVEN_COMPARISON'for r in result['evidence'].values()))

    def test_missing_comparison_walks_declared_path_without_inventing_a_value(self):
        tools,engine,reader,_=ToolLoopTests().build(step_cap=5)
        tools.nodes['job']['kind']='PIPELINE'
        decisions=[{'action':'TOOL','summary':'Compare the declared layers.','hypotheses':['failed job'],
            'tool':'compare_layers','arguments':{'key':tools.key,'layers':['down','up'],'filters':tools.context}}]
        def decide(payload,**kwargs):
            if decisions:return decisions.pop()
            return {'action':'VERDICT','verdict':'failed job','summary':'The measured boundary and job agree.',
                'hypotheses':['failed job'],'evidence_ids':list(tools.evidence._values)}
        engine.decide=decide
        result=engine.run({'visual':'visual','text':'Why is this number wrong?',
            'request':{'kind':'COMPARE','comparison_pending':True}})
        self.assertEqual(result['verdict'],'failed job')
        self.assertNotIn('question',result)
        self.assertEqual({c.args[0]for c in reader.call_args_list},{'visual','down','up'})
        self.assertFalse(any(r['kind']=='GIVEN_COMPARISON'for r in result['evidence'].values()))
        for output in result['outputs'].values():
            self.assertTrue(output.startswith('The job run r failed at 2026-10-22T10:02:00Z: copy failed'))

    def test_native_split_is_not_confused_with_the_missing_external_value(self):
        tools,engine,reader,_=ToolLoopTests().build()
        decisions=[{'action':'TOOL','summary':'Compare the native boundary.','hypotheses':['failed job'],
            'tool':'compare_layers','arguments':{'key':'record-1','layers':['down','up'],'filters':tools.context}}]
        def decide(payload,**kwargs):
            if decisions:return decisions.pop()
            return {'action':'VERDICT','verdict':'failed job','summary':'Report only the measured native split.',
                'hypotheses':['failed job'],'evidence_ids':list(tools.evidence._values)}
        engine.decide=decide
        answer=engine.run({'visual':'visual','text':'The report differs from my own count.',
            'request':{'kind':'COMPARE','comparison_pending':True,'comparison_pending_kind':'own count'}})
        self.assertEqual(answer['verdict'],'failed job')
        self.assertEqual(answer['support']['claim_scope'],'NATIVE_FINDING_WITH_EXTERNAL_COMPARISON_PENDING')
        for output in answer['outputs'].values():
            self.assertIn('partly answered',output)
            self.assertIn('external comparison has not been checked',output)
        self.assertFalse(any(e['kind']=='GIVEN_COMPARISON'for e in answer['evidence'].values()))

    def test_named_external_count_without_value_still_allows_the_native_investigation(self):
        decide=Mock(return_value={'action':'VERDICT','verdict':'not found','summary':'No checked mechanism yet.',
            'hypotheses':[],'evidence_ids':[]})
        tools,engine,reader,_=ToolLoopTests().build(decide=decide,step_cap=1)
        answer=engine.run({'visual':'visual','text':'The report differs from my own count.',
            'request':{'kind':'COMPARE','comparison_pending':True,'comparison_pending_kind':'own count'}})
        self.assertGreater(reader.call_count,1)
        self.assertNotEqual(answer['stop_reason'],'COMPARISON_REQUIRED_AFTER_QUICK_CHECKS')
        self.assertFalse(any(e['kind']=='GIVEN_COMPARISON'for e in answer['evidence'].values()))

    def engine(self,*,related=True,stale=False,comparison=None):
        graph=Mock();snapshot={'nodes':[{'id':'visual','kind':'VISUAL','label':'Inventory card'},
            {'id':'job','kind':'PIPELINE','label':'Nightly load'}],
            'edges':[{'id':'producer','source':'visual','target':'job','kind':'DERIVED_IN_STEP',
                'confidence':'DECLARED','provenance':{'source':'STATIC_DEFINITION'}}] if related else [],'stops':[],'truncated':False}
        graph.path_to_source.return_value=snapshot
        status=fact('job','JOB_RUN',{'status':'FAILED','run_id':'r','start':'2026-10-22T10:00:00Z','end':'2026-10-22T10:01:00Z','error':'copy failed'})
        if stale:status['freshness']='STALE'
        graph.node_facts.side_effect=lambda node,**kwargs:{'facts':[status] if node=='job' else []}
        events=[]
        def persist(value):events.append(value);return 'record:'+str(len(events))
        reader=Mock(side_effect=lambda node,key,context:{**read(node,8765,context),'key':key})
        decide=Mock()
        tools=Tools(graph,object(),visual='visual',now=NOW,persist=persist,key=None,context={'warehouse':'North'},value_reader=reader,comparison=comparison)
        engine=Investigator(tools,decide=decide,persist=persist,admit=lambda *_:None,clock=lambda:1.0)
        return engine,reader,decide
    def test_missing_comparison_recreates_then_reports_only_relevant_operational_status(self):
        engine,reader,decide=self.engine()
        result=engine.run({'visual':'visual','text':'Inventory card shows 8765. Why?',
            'request':{'kind':'COMPARE','comparison_pending':True},
            'assumptions':['Report assumed from the only high-confidence graph match.']})
        self.assertEqual(result['verdict'],'failed job');self.assertEqual(result['cost']['model_calls'],0)
        self.assertEqual(result['support']['claim_scope'],'OPERATIONAL_STATUS_WITH_COMPARISON_PENDING')
        self.assertEqual(reader.call_count,1);decide.assert_not_called();self.assertNotIn('question',result)
        for output in result['outputs'].values():
            self.assertIn('comparison has not been checked',output)
            self.assertIn('no numerical cause has been established',output)
            self.assertIn('Assumption: Report assumed',output)
        reads=[entry['value'] for entry in result['evidence'].values() if entry['kind']=='READ']
        self.assertEqual(reads[0]['value'],8765)
    def test_unrelated_or_stale_failure_does_not_substitute_for_native_path_checks(self):
        for kwargs in ({'related':False},{'stale':True}):
            with self.subTest(kwargs=kwargs):
                engine,reader,decide=self.engine(**kwargs)
                engine.decide=None
                result=engine.run({'visual':'visual','text':'Inventory card shows 8765. Why?',
                    'request':{'kind':'COMPARE','comparison_pending':True}})
                self.assertEqual(result['verdict'],'not found');self.assertNotIn('question',result)
                self.assertEqual(reader.call_count,1);decide.assert_not_called()
                self.assertEqual(result['tools'][1]['tool'],'parallel_simple_hypotheses')
    def test_normal_numeric_comparison_gate_is_unchanged_and_pending_conflict_refuses(self):
        engine,reader,decide=self.engine()
        engine.tools.reproduce();engine.tools.quick_checks()
        with self.assertRaisesRegex(ValueError,'DIVERGENT_EQUIVALENT_CONTEXT'):
            check('failed job',list(engine.tools.evidence._values),engine.tools.evidence,now=NOW,request={'kind':'COMPARE'},target='visual')
        engine,reader,decide=self.engine(comparison={'kind':'spreadsheet','value':7})
        with self.assertRaisesRegex(ValueError,'CONTRACT_CONFLICT'):
            engine.run({'visual':'visual','request':{'kind':'COMPARE','comparison_pending':True}})
        reader.assert_not_called()
    def test_named_unresolved_source_keeps_own_read_and_gap_in_both_outputs(self):
        engine,reader,decide=self.engine(comparison={'kind':'source','node':None})
        engine.decide=None
        result=engine.run({'visual':'visual','text':'Inventory card is higher than the application source.',
            'request':{'kind':'COMPARE'}})
        self.assertEqual(result['verdict'],'not found');self.assertNotIn('question',result)
        self.assertEqual(reader.call_count,1)
        for output in result['outputs'].values():
            self.assertIn('ticket names a source comparison',output)
            self.assertIn('No comparison read was made',output)


class RealGraphTests(unittest.TestCase):
    def test_explicit_operational_fact_uses_real_ledger_with_zero_queries_or_models(self):
        from investigator.shared_state import SharedState
        from investigator.estate_graph_repository import GraphRepository
        from investigator.estate_graph_api import GraphAPI
        from investigator.facts_ledger import FactLedger
        from investigator.facts_collectors import observation
        from investigator.live_gateway import Gateway
        from investigator.estate_graph_contract import node
        from test_estate_graph import graph,proof
        text='Did the latest Copy Job run fail?'
        request={'kind':'FACT','subject':'job','question':'RUN_STATUS','source':{'start':0,'end':len(text),'quote':text}}
        with tempfile.TemporaryDirectory() as temporary:
            state=SharedState.offline(Path(temporary)/'state.sqlite');repository=GraphRepository(state);repository.migrate()
            snapshot=graph();snapshot['nodes'].append(node('job','owner','PIPELINE','Load pipeline',proof()));repository.replace(snapshot)
            ledger=FactLedger(state);ledger.append('estate',[observation('job','JOB_RUN',{'status':'FAILED','run_id':'r','start':'2026-10-22T10:00:00Z','end':'2026-10-22T10:01:00Z','error':'copy failed'},NOW,['native-history-read'],'fixture')])
            gateway=Gateway({'version':1,'live_enabled':False,'identities':{'reader':{'role':'investigation','graph':{'estate':['job']}}}})
            api=GraphAPI(repository,gateway,identity='reader',estate='estate',allowed_objects=['job']);reader=Mock();decide=Mock()
            with patch.object(repository,'records',side_effect=AssertionError('whole catalog forbidden')):
                tools=Tools(api,ledger,visual='job',now=NOW,persist=lambda _: 'retained',value_reader=reader,request_kind='FACT')
                result=Investigator(tools,decide=decide,persist=lambda _: 'retained',admit=lambda *_:None,clock=lambda:1.0).run({'text':text,'request':request})
            self.assertEqual(result['verdict'],'failed job');self.assertEqual(result['support']['claim_scope'],'OPERATIONAL_FACT_ONLY');self.assertEqual(result['cost']['model_calls'],0)
            reader.assert_not_called();decide.assert_not_called()

    def test_real_ledger_and_graph_load_only_admitted_path(self):
        from investigator.shared_state import SharedState
        from investigator.estate_graph_repository import GraphRepository
        from investigator.estate_graph_api import GraphAPI
        from investigator.facts_ledger import FactLedger
        from investigator.facts_collectors import observation
        from investigator.live_gateway import Gateway
        from test_estate_graph import graph
        with tempfile.TemporaryDirectory() as temporary:
            state=SharedState.offline(Path(temporary)/'state.sqlite')
            repository=GraphRepository(state);repository.migrate();repository.replace(graph())
            ledger=FactLedger(state)
            ledger.append('estate',[observation('visual','REFRESH_STATE',{'state':'IDLE'},NOW,['real-retained-read'],'test')])
            gateway=Gateway({'version':1,'live_enabled':False,'identities':{'reader':{'role':'investigation','graph':{'estate':['visual','measure','column']}}}})
            api=GraphAPI(repository,gateway,identity='reader',estate='estate',allowed_objects=['visual','measure','column'])
            recorded=[]
            def persist(value):recorded.append(copy.deepcopy(value));return 'record:'+str(len(recorded))
            with patch.object(repository,'records',side_effect=AssertionError('whole historical catalog forbidden')):
                tools=Tools(api,ledger,visual='visual',now=NOW,persist=persist,value_reader=lambda node,key,context:read(node,7,context),key='record-1',context={'warehouse':'North'})
                result=Investigator(tools,decide=None,persist=persist,admit=lambda *_:None,clock=lambda:1.0).run({'visual':'visual','text':'Why did this change?'})
            self.assertEqual(result['verdict'],'not found')
            self.assertEqual(set(tools.nodes),{'visual','measure','column'})
            self.assertEqual(result['cost']['model_calls'],0)
            self.assertIn('Question: Why did this change?',result['outputs']['business'])
            self.assertTrue(any(entry['kind']=='FACT' for entry in result['evidence'].values()))

class FetchedWitnessTests(unittest.TestCase):
    def test_model_view_omits_duplicate_native_receipts_without_changing_sealed_witness(self):
        import json
        from investigator.ledger_investigator import fetched_context
        original={'evidence_ids':['proof'],'evidence':{'id':'proof','kind':'DESIGN_CHECK','subjects':['down','up'],'value':{
            'checked':True,'mechanism':'A retained join repeats the carried quantity.','support_ids':['comparison'],
            'business_correctness_claim':False,'native_assessment':{'classification':'TRANSFORMATION_LOGIC','support':{'ids':['comparison']},'observations':['large native receipt'*10000]},
            'native_observations':['duplicate native receipt'*10000]}}}
        before=copy.deepcopy(original);view=fetched_context(original)
        self.assertEqual(original,before)
        self.assertEqual(view['evidence']['value']['native_assessment']['classification'],'TRANSFORMATION_LOGIC')
        self.assertEqual(view['evidence']['value']['support_ids'],['comparison'])
        self.assertLess(len(json.dumps(view)),2000)
        self.assertNotIn('native_observations',view['evidence']['value'])

class IntegratedCaseTests(unittest.TestCase):
    def test_status_run_delivers_its_code_owned_case_and_retains_snapshots(self):
        success=fact('job','JOB_RUN',{'status':'SUCCEEDED','run_id':'last','start':'2026-10-22T10:00:00Z','end':'2026-10-22T10:01:00Z'})
        engine,ticket,_,_=OperationalFactTests().status_engine([success]);events=[]
        engine.persist=lambda event:events.append(copy.deepcopy(event)) or 'retained'
        answer=engine.run(ticket)
        self.assertEqual(answer['case_file']['current_step'],'deliver')
        self.assertEqual(answer['case_file']['final_outcome']['status'],answer['status'])
        self.assertTrue(answer['case_file']['evidence_summaries'])
        self.assertTrue(any(v.get('event')=='INVESTIGATOR_CASE_FILE'for v in events))

class JustInTimeTests(unittest.TestCase):
    def test_ordinary_tool_context_contains_summary_and_id_not_raw_definition(self):
        import json
        tools,engine,_,_=ToolLoopTests().build();raw='PRIVATE_RAW_DEFINITION_SENTINEL'
        tools.graph.definition_of.return_value={'definition':{'source':raw}}
        payloads=[]
        def decide(payload,**kwargs):
            payloads.append(copy.deepcopy(payload))
            if len(payloads)==1:return {'action':'TOOL','summary':'Read definition','hypotheses':['not found'],'tool':'definition_of','arguments':{'node':'down'}}
            return {'action':'VERDICT','verdict':'not found','summary':'No supported cause','hypotheses':['not found'],'evidence_ids':list(tools.evidence._values)}
        engine.decide=decide;engine.step_cap=2;engine.run({'visual':'visual'})
        self.assertEqual(len(payloads),2)
        self.assertNotIn(raw,json.dumps(payloads[1]))
        ids=[key for key,row in payloads[1]['case_file']['evidence_summaries'].items()if row['kind']=='GRAPH']
        self.assertTrue(ids)
        result=tools.invoke('get_evidence',{'id':ids[-1]})
        self.assertEqual(result['evidence']['value']['definition']['source'],raw)
    def test_explicit_raw_fetch_is_cleared_after_the_next_model_call(self):
        import json
        tools,engine,_,_=ToolLoopTests().build(step_cap=5);engine.phase_limit=5;raw='TRANSIENT_RAW_DEFINITION_SENTINEL'
        tools.graph.definition_of.return_value={'definition':{'source':raw}};payloads=[]
        def decide(payload,**kwargs):
            payloads.append(copy.deepcopy(payload));step=len(payloads)
            if step==1:return {'action':'TOOL','summary':'Read definition','hypotheses':['not found'],'tool':'definition_of','arguments':{'node':'down'}}
            if step==2:
                identity=next(k for k,v in payload['case_file']['evidence_summaries'].items()if v['kind']=='GRAPH')
                return {'action':'TOOL','summary':'Read retained details','hypotheses':['not found'],'tool':'get_evidence','arguments':{'id':identity}}
            if step==3:return {'action':'TOOL','summary':'Inspect declared path','hypotheses':['not found'],'tool':'path_to_source','arguments':{'visual':'visual'}}
            return {'action':'VERDICT','verdict':'not found','summary':'No supported cause','hypotheses':['not found'],'evidence_ids':list(tools.evidence._values)}
        engine.decide=decide;engine.step_cap=4;engine.run({'visual':'visual'})
        self.assertIn(raw,json.dumps(payloads[2]['fetched_evidence']))
        self.assertNotIn(raw,json.dumps(payloads[3]))

    def test_large_raw_result_is_retrievable_in_exact_hash_bound_parts_without_context_growth(self):
        import json,hashlib
        from investigator.ledger_investigator import fetched_context
        from investigator.estate_graph_contract import canonical
        tools,_,_,_=ToolLoopTests().build()
        identity=tools.evidence.add('GRAPH',['down'],{'definition':'raw-secret-free-fixture-'*10000})
        full=tools.invoke('get_evidence',{'id':identity});raw=canonical(full['evidence'])
        view=fetched_context(full)
        self.assertLess(len(json.dumps(view)),2000)
        self.assertEqual(view['raw_details']['sha256'],hashlib.sha256(raw.encode()).hexdigest())
        chunks=[];offset=0
        while offset is not None:
            result=tools.invoke('get_evidence_part',{'id':identity,'offset':offset,'limit':4096})
            chunks.append(result['raw_part']);offset=result['next_offset']
        self.assertEqual(''.join(chunks),raw)
        self.assertEqual(canonical(tools.evidence.get(identity)),raw)

class FailedRepeatTests(unittest.TestCase):
    def test_same_failed_signature_is_blocked_different_arguments_are_allowed(self):
        tools,engine,_,_=ToolLoopTests().build();tools.graph.definition_of.side_effect=ValueError('definition unavailable')
        steps=[]
        def decide(payload,**kwargs):
            steps.append(1)
            return {'action':'TOOL','summary':'Inspect retained definition','hypotheses':['not found'],'tool':'definition_of','arguments':{'node':'up'if len(steps)==3 else 'down'}}
        engine.decide=decide;engine.step_cap=3
        result=engine.run({'visual':'visual'})
        self.assertEqual(tools.graph.definition_of.call_count,2)
        self.assertEqual(len(result['case_file']['calls_blocked']),1)
        self.assertEqual(result['case_file']['calls_blocked'][0]['arguments'],{'node':'down'})
        errors=[v for v in result['case_file']['errors']if v.get('tool')=='definition_of']
        self.assertEqual([v['arguments']['node']for v in errors],['down','up'])
        self.assertTrue(errors[0]['result']['evidence_ids'])

class ProviderRejectionTests(unittest.TestCase):
    def test_consumer_schema_rejection_returns_feedback_then_valid_call_can_complete(self):
        from jsonschema import ValidationError
        tools,engine,_,_=ToolLoopTests().build();calls=[]
        def decide(payload,**kwargs):
            calls.append(1)
            if len(calls)==1:raise ValidationError('Unknown admitted node')
            self.assertTrue(any(e['reason']=='PROVIDER_DECISION_SCHEMA'for e in payload['case_file']['errors']))
            if len(calls)==2:return {'action':'TOOL','summary':'Compare admitted nodes','hypotheses':['failed job'],'tool':'compare_layers','arguments':{'key':'record-1','layers':['down','up'],'filters':tools.context}}
            return {'action':'VERDICT','verdict':'failed job','summary':'Report evidenced failure','hypotheses':['failed job'],'evidence_ids':list(tools.evidence._values)}
        engine.decide=decide;answer=engine.run({'visual':'visual'})
        self.assertEqual(answer['verdict'],'failed job');self.assertEqual(answer['cost']['model_calls'],3)
    def test_secret_or_unrelated_value_error_is_not_converted_to_schema_feedback(self):
        tools,engine,_,_=ToolLoopTests().build()
        engine.decide=lambda *_a,**_k:(_ for _ in ()).throw(ValueError('SECRET_DETECTED'))
        with self.assertRaisesRegex(ValueError,'SECRET_DETECTED'):engine.run({'visual':'visual'})

if __name__=='__main__':unittest.main()
