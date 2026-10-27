"""Submit/poll and CAS claims against disposable offline shared state."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock
import unittest
from investigator.shared_state import SharedState,StateConflict
from investigator.guided_cases import Cases
from test_round23_intake_queries import graph,request,sql_objects


class Tests(unittest.TestCase):
    def setUp(self):
        folder=TemporaryDirectory();self.addCleanup(folder.cleanup)
        self.state=SharedState.offline(Path(folder.name)/'state.sqlite');self.state.migrate()
        self.graph=Mock();self.graph.intake_catalog.return_value=graph()
        self.engine=Mock();self.engine.run.return_value={'status':'ANSWERED','business':'The native total is 7.'}
        self.factory=Mock(return_value=self.engine)
        self.cases=Cases(state=self.state,graph=self.graph,estate='estate',engine_factory=self.factory)
    def submit(self):return self.cases.submit({'request_key':'test','intake':request()})
    def test_submit_poll_then_installed_worker_runs_once(self):
        case=self.submit();self.assertEqual(case['status'],'QUEUED');self.factory.assert_not_called()
        result=self.cases.run(case['id']);self.assertEqual(result['status'],'ANSWERED')
        self.assertEqual(self.cases.poll(case['id'])['outcome']['business'],'The native total is 7.')
        self.cases.run(case['id']);self.engine.run.assert_called_once()
    def test_repeated_submission_is_idempotent_but_changed_input_is_not(self):
        first=self.submit();self.assertEqual(self.submit()['id'],first['id'])
        item=request();item['reported_figure']['value']='8'
        with self.assertRaises(StateConflict):self.cases.submit({'request_key':'test','intake':item})
    def test_dropped_execution_is_interrupted_not_counted_as_finding(self):
        self.engine.run.side_effect=RuntimeError('private diagnostics')
        result=self.cases.run(self.submit()['id'])
        self.assertEqual(result['status'],'INTERRUPTED');self.assertNotIn('private diagnostics',str(result))
    def test_no_raw_fallback_for_projected_installation(self):
        with self.assertRaisesRegex(ValueError,'NO_RAW_FALLBACK'):
            Cases(state=self.state,graph=self.graph,estate='estate',engine_factory=self.factory,
                  recording_class='PRIVACY_PROJECTED')
    def test_form_to_model_authored_native_query_to_grounded_answer_end_to_end(self):
        from investigator.guided_investigator_installation import Factory
        from types import SimpleNamespace
        from investigator.adapters.investigative_native import NativeQueries
        from test_round23_reasoning import MemoryCheckpoint,tool
        events=[];native_read=Mock(return_value={'rows':[{'quantity':7}],'read_only_verified':True})
        path=graph();path['nodes'].append({'id':'table-node','kind':'TABLE','label':'Items'})
        self.graph.allowed={n['id'] for n in path['nodes']};self.graph.path_to_source.return_value=path
        route={'kind':'SOURCE_SQL','config':{},'objects':sql_objects(),'asset_ids':['table'],
               'path_nodes':['table-node'],'label':'Serving','dialect':'T-SQL'}
        native=NativeQueries({'gold':route},source=native_read,fabric=Mock(),dax=Mock(),offline=True)
        model=Mock();step=[0]
        def complete(**kwargs):
            step[0]+=1
            if step[0]==1:return tool('run_sql',{'layer':'gold','query':'SELECT SUM(quantity) AS quantity FROM dbo.Items','purpose':'recreate'})
            q=next(event['query'] for _,event in events if event['event']=='QUERY_RESULT')
            return tool('submit_finding',{'verdict':'observed value','cause':'The native quantity is 7.',
                'numbers':[7],'checked':['gold'],'evidence_ids':[q['id']]})
        model.complete.side_effect=complete
        factory=Factory(state=self.state,graph=self.graph,routes={'gold':route},native=native,
            context_for=lambda p,i:{},triage_for=lambda *a:SimpleNamespace(run=lambda:{'facts':[]}),
            model_for=lambda _:model,reserve=Mock(),persist=lambda case,event:events.append((case,event)),
            job_runs=Mock(),refresh_history=Mock(),checkpoint_for=lambda _:MemoryCheckpoint())
        cases=Cases(state=self.state,graph=self.graph,estate='estate',engine_factory=factory)
        item=request();item['reported_figure']['value']='7'
        saved=cases.submit({'request_key':'end-to-end','intake':item})
        result=cases.run(saved['id'])
        self.assertEqual(result['status'],'ANSWERED')
        self.assertIn('Serving',result['outcome']['business'])
        self.assertEqual(result['outcome']['technical']['numbers'],[7]);native_read.assert_called_once()
        self.assertEqual(cases.poll(saved['id'])['outcome']['technical']['queries'][0]['status'],'SUCCEEDED')
    def test_candidate_discovery_can_open_an_existing_route_beyond_the_initial_path(self):
        from investigator.guided_investigator_installation import Factory
        from types import SimpleNamespace
        from investigator.adapters.investigative_native import NativeQueries
        from test_round23_reasoning import MemoryCheckpoint,tool
        initial=graph();initial['nodes'].append({'id':'gold-node','kind':'TABLE','label':'Serving'})
        source_node={'id':'source-node','kind':'TABLE','label':'Movements'}
        catalog={'nodes':[*initial['nodes'],source_node],'edges':initial['edges']}
        self.graph.allowed={n['id'] for n in catalog['nodes']}
        self.graph.intake_catalog.return_value=catalog
        self.graph.path_to_source.side_effect=lambda root:{'nodes':[source_node],'edges':[]} if root=='source-node' else initial
        route={'kind':'SOURCE_SQL','config':{},'objects':sql_objects(),'asset_ids':['table'],'dialect':'T-SQL'}
        routes={'gold':{**route,'path_nodes':['gold-node'],'label':'Serving'},
                'source':{**route,'path_nodes':['source-node'],'label':'Application'}}
        native_read=Mock(return_value={'rows':[{'quantity':9}],'read_only_verified':True})
        native=NativeQueries(routes,source=native_read,fabric=Mock(),dax=Mock(),offline=True)
        events=[];step=[0];model=Mock()
        def complete(**kwargs):
            step[0]+=1
            if step[0]==1:return tool('list_candidates',{'words':'Movements'})
            if step[0]==2:return tool('get_lineage',{'node':'source-node'})
            if step[0]==3:
                sql=next(t for t in kwargs['tools'] if t['name']=='run_sql')
                self.assertIn('source',sql['input_schema']['properties']['layer']['enum'])
                return tool('run_sql',{'layer':'source','query':'SELECT SUM(quantity) AS quantity FROM dbo.Items','purpose':'compare'})
            q=next(event['query'] for _,event in events if event['event']=='QUERY_RESULT')
            return tool('submit_finding',{'verdict':'observed value','cause':'The application quantity is 9.',
                        'numbers':[9],'checked':['source'],'evidence_ids':[q['id']]})
        model.complete.side_effect=complete
        factory=Factory(state=self.state,graph=self.graph,routes=routes,native=native,
            context_for=lambda *a:{},triage_for=lambda *a:SimpleNamespace(run=lambda:{'facts':[]}),
            model_for=lambda _:model,reserve=Mock(),persist=lambda c,e:events.append((c,e)),
            job_runs=Mock(),refresh_history=Mock(),checkpoint_for=lambda _:MemoryCheckpoint())
        cases=Cases(state=self.state,graph=self.graph,estate='estate',engine_factory=factory)
        result=cases.run(cases.submit({'request_key':'expansion','intake':request()})['id'])
        self.assertEqual(result['status'],'ANSWERED');native_read.assert_called_once()
        self.assertIn('Application',result['outcome']['business'])
        self.assertIn('source-node',{n['id'] for n in result['outcome']['case']['context']['path']['nodes']})


if __name__=='__main__':unittest.main()
