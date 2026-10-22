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
        self.witness('DESIGN_CHECK',business_correctness_claim=False)
        self.assertEqual(self.validate('as designed')['verdict'],'as designed')
    def test_access_difference_requires_observed_scoped_reads_without_impersonation(self):
        self.witness('ACCESS_CHECK',same_query_and_context=True,observed_access_difference=True,impersonated=False)
        self.assertEqual(self.validate('access difference')['verdict'],'access difference')
    def test_source_changed_history_requires_verified_source_row_history(self):
        self.witness('HISTORY_CHECK',system_of_record=True,row_history_verified=True)
        self.assertEqual(self.validate('source changed history')['verdict'],'source changed history')
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
    def test_explicit_run_status_needs_no_numeric_reads_and_cannot_explain_a_number(self):
        registry=Evidence(['job'],lambda value:'retained')
        text='Did the latest Copy Job run fail?'
        request={'kind':'FACT','subject':'job','question':'RUN_STATUS','source':{'start':0,'end':len(text),'quote':text}}
        identity=registry.add('FACT',['job'],fact('job','JOB_RUN',{'status':'FAILED','run_id':'r','start':'2026-10-22T10:00:00Z','end':'2026-10-22T10:01:00Z','error':'copy failed'}))
        result=check('failed job',[identity],registry,now=NOW,request=request,ticket_text=text)
        self.assertEqual(result['claim_scope'],'OPERATIONAL_FACT_ONLY')
        self.assertIn('no numerical cause',result['reason'])
        with self.assertRaisesRegex(ValueError,'DIVERGENT_EQUIVALENT'):check('failed job',[identity],registry,now=NOW)
        wrong='Why is the quantity wrong?'
        invalid={**request,'source':{'start':0,'end':len(wrong),'quote':wrong}}
        with self.assertRaisesRegex(ValueError,'EXPLICIT_OPERATIONAL'):check('failed job',[identity],registry,now=NOW,request=invalid,ticket_text=wrong)
    def test_newer_empty_history_cannot_resurrect_an_older_failed_run(self):
        registry=Evidence(['job'],lambda value:'retained')
        text='Did the latest Copy Job run fail?'
        request={'kind':'FACT','subject':'job','question':'RUN_STATUS','source':{'start':0,'end':len(text),'quote':text}}
        old=fact('job','JOB_RUN',{'status':'FAILED','run_id':'r','start':'2026-10-22T10:00:00Z','end':'2026-10-22T10:01:00Z','error':'copy failed'})
        old['collected_at']='2026-10-22T10:50:00Z';old['observed_at']='2026-10-22T10:01:00Z'
        ids=[registry.add('FACT',['job'],old),registry.add('FACT',['job'],fact('job','RUN_HISTORY',{'runs':[],'listing_complete':True}))]
        with self.assertRaisesRegex(ValueError,'CURRENT_OPERATIONAL'):check('failed job',ids,registry,now=NOW,request=request,ticket_text=text)


class ToolLoopTests(unittest.TestCase):
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

if __name__=='__main__':unittest.main()
