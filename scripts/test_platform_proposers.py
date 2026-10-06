import copy,json,unittest,tempfile
from pathlib import Path
from unittest.mock import Mock
from investigator import lineage_proposer as lineage,assistant_proposer as assistant
from investigator.estate_manifest import load,validate as validate_manifest
from investigator.adapters.platform_lineage import FabricLineageProposer,UnityCatalogLineageStub
from investigator.adapters.assistant_stub import GenieStub

ROOT=Path(__file__).resolve().parents[1]

class ProposerTests(unittest.TestCase):
    def manifest(self):return load(ROOT/'infra/estates/fixture.json')
    def graph(self):
        return {'provenance':'PROPOSED_BY_PLATFORM','items':[
            {'id':i,'platform_type':'Opaque','category':c,'workspace':'w','name':i}
            for i,c in [('upper','VALUE_OBJECT'),('lower','VALUE_OBJECT'),('writer','CODE')]],
            'edges':[{'source':'upper','target':'lower','kind':'READS_FROM','columns':None},
                     {'source':'writer','target':'lower','kind':'WRITES_TO','columns':None}],
            'workspaces':[{'id':'w','name':'Workspace'}]}

    def test_default_off_never_calls_either_proposer(self):
        manifest=self.manifest();manifest.pop('lineage_proposer',None);manifest.pop('assistant_proposer',None)
        p=Mock();record=Mock();model=Mock()
        self.assertIsNone(lineage.at_approval(manifest,p,record))
        self.assertIsNone(assistant.propose(manifest,'Question',p,model))
        p.assert_not_called();p.propose.assert_not_called();record.assert_not_called();model.assert_not_called()
        for key in ('lineage_proposer','assistant_proposer'):
            bad=copy.deepcopy(manifest);bad[key]='false'
            with self.assertRaises(ValueError):validate_manifest(bad)

    def test_closed_graph_rejects_hostile_producer(self):
        for mutate in (lambda g:g.update(provenance='VERIFIED'),
                       lambda g:g['edges'][0].update(kind='Unfamiliar'),
                       lambda g:g['edges'][0].update(target='not-returned'),
                       lambda g:g['items'].append(copy.deepcopy(g['items'][0])),
                       lambda g:g['edges'][0].update(columns={'source_column':'a','target_column':'b'})):
            g=self.graph();mutate(g)
            with self.assertRaises(Exception):lineage.validate(g)

    def test_optional_column_lineage_validates_without_native_branching(self):
        g=self.graph();g['edges'][0].update(kind='COLUMN_LINEAGE',columns={'source_column':'a','target_column':'b'})
        self.assertEqual(lineage.validate(g),g)

    def test_approval_findings_record_missing_and_unmanifested_edges_and_writers(self):
        m={'layers':[{'id':'u'},{'id':'l'},{'id':'absent'}],
           'lineage':{'bindings':[{'from_layer':'l','to_layer':'u'},{'from_layer':'absent','to_layer':'l'}]}}
        mapping={'u':'upper','l':'lower','absent':None}
        f=lineage.findings(m,self.graph(),mapping)
        self.assertTrue(f['nonblocking']);self.assertEqual(len(f['missing_declared_paths']),1)
        self.assertEqual(f['code_source_proposals'][0]['decision'],'PENDING_APPROVER')
        self.assertEqual(f['undeclared_writers'][0]['id'],'writer')
        g=self.graph();g['edges'].append({'source':'lower','target':'upper','kind':'READS_FROM','columns':None})
        self.assertEqual(len(lineage.findings(m,g,mapping)['unmanifested_edges']),1)
        with self.assertRaises(ValueError):lineage.findings(m,g,{'u':'upper'})

    def test_opaque_native_type_content_cannot_change_engine_findings(self):
        m={'layers':[{'id':'u'},{'id':'l'}],'lineage':{'bindings':[{'from_layer':'l','to_layer':'u'}]}}
        a=self.graph();b=copy.deepcopy(a)
        for row in b['items']:row['platform_type']='DifferentNativeVocabulary'
        # Type text is evidence; operational categories are adapter-owned.
        fa=lineage.findings(m,a,{'u':'upper','l':'lower'});fb=lineage.findings(m,b,{'u':'upper','l':'lower'})
        # The evidence copy differs; decisions and proposal identities do not.
        for f in (fa,fb):
            for row in f['undeclared_writers']:row.pop('platform_type')
        self.assertEqual(json.dumps(fa,sort_keys=True),json.dumps(fb,sort_keys=True))

    def test_item_api_is_one_request_and_unknown_kind_is_not_omitted(self):
        workspace='00000000-0000-0000-0000-000000000001';root='00000000-0000-0000-0000-000000000002'
        child='00000000-0000-0000-0000-000000000003'
        anchor={'workspace':workspace,'item':root,'type':'SemanticModel','name':'Declared root'}
        m={'layers':[{'id':'x','asset_id':f'fabric://{workspace}/{root}/table/T'}]}
        response={'status':200,'body':{'items':[{'id':child,'type':'Lakehouse','workspaceId':workspace,'displayName':'Data'}],
            'workspaces':[],'relations':[{'itemId':root,'dependentOnItemId':child,'relationType':'Datasource'}]}}
        request=Mock(return_value=response);meter=Mock(side_effect=lambda call:call())
        p=FabricLineageProposer(request,meter,[anchor]);g=p.propose(m)
        request.assert_called_once_with('GET',f'workspaces/{workspace}/items/{root}/relations/upstream?beta=true')
        meter.assert_called_once();self.assertEqual(g['edges'][0]['kind'],'READS_FROM')
        self.assertTrue(all(e['columns'] is None for e in g['edges']))
        with self.assertRaises(ValueError):FabricLineageProposer(request,meter,[anchor,anchor])
        response['body']['relations'][0]['relationType']='Unfamiliar'
        with self.assertRaisesRegex(ValueError,'Unfamiliar'):FabricLineageProposer(request,meter,[anchor]).propose(m)

    def test_assistant_results_cannot_enter_candidate_or_compiler_contract(self):
        p={'provenance':'PROPOSED_BY_ASSISTANT','objects':[{'id':'t','kind':'TABLE'}],'expression':'candidate'}
        compiler=Mock(return_value='governed compiler result')
        self.assertEqual(assistant.compile_candidate(p,{'t':'TABLE'},compiler),'governed compiler result')
        for extra in ('rows','result','receipt','value','verified'):
            bad={**p,extra:16}
            with self.assertRaises(Exception):assistant.compile_candidate(bad,{'t':'TABLE'},compiler)
        self.assertEqual(compiler.call_count,1)
        with self.assertRaises(ValueError):assistant.compile_candidate(p,{'t':'MEASURE'},compiler)

    def test_assistant_model_call_is_once_and_before_compilation(self):
        p={'provenance':'PROPOSED_BY_ASSISTANT','objects':[{'id':'t','kind':'TABLE'}],'expression':'candidate'}
        proposer=Mock();proposer.propose.return_value=p
        call=Mock(side_effect=lambda question,execute:execute())
        result=assistant.propose({'assistant_proposer':True},'Question',proposer,call)
        self.assertEqual(result,p);call.assert_called_once();proposer.propose.assert_called_once_with('Question')

    def test_proposal_model_call_records_request_response_timing_and_replays_without_transport(self):
        from investigator.process_tape import Tape,active
        from test_process_tape import bootstrap
        proposal={'provenance':'PROPOSED_BY_ASSISTANT','objects':[{'id':'t','kind':'TABLE'}],'expression':'candidate'}
        meter=Mock(side_effect=lambda q,execute:execute())
        call=assistant.RecordedModelCall(meter)
        transport=Mock(return_value=proposal)
        with tempfile.TemporaryDirectory() as folder:
            tape=Tape(Path(folder)/'proposal.json',bootstrap())
            with active(tape):self.assertEqual(call('Question',transport),proposal)
            tape.finish({});original=tape.path.read_bytes()
            self.assertEqual([e['kind'] for e in tape.events],['BOOTSTRAP','CLOCK','PROVIDER_REQUEST','PROVIDER_RESPONSE','CLOCK','FINAL'])
            replay=Tape(tape.path);never=Mock(side_effect=AssertionError('network during replay'))
            with active(replay):self.assertEqual(call('Question',never),proposal)
            replay.finish({});never.assert_not_called()
            self.assertEqual(tape.path.read_bytes(),original)
        transport.assert_called_once()

    def test_assistant_failure_is_preserved_and_not_retried(self):
        from investigator.process_tape import Tape,active
        from test_process_tape import bootstrap
        call=assistant.RecordedModelCall(lambda q,execute:execute())
        with tempfile.TemporaryDirectory() as folder:
            tape=Tape(Path(folder)/'failure.json',bootstrap())
            transport=Mock(side_effect=TimeoutError('do not retain message'))
            with active(tape),self.assertRaises(TimeoutError):call('Question',transport)
            tape.finish({});transport.assert_called_once()
            replay=Tape(tape.path);never=Mock()
            with active(replay),self.assertRaisesRegex(assistant.RecordedAssistantFailure,'TimeoutError'):call('Question',never)
            replay.finish({});never.assert_not_called()

    def test_uninstalled_stubs_validate_manifest_and_never_query(self):
        m=load(ROOT/'infra/estates/databricks.json')
        for p in (UnityCatalogLineageStub(m),GenieStub(m)):
            with self.assertRaises(NotImplementedError):p.propose(m if isinstance(p,UnityCatalogLineageStub) else 'Question')
        with self.assertRaises(ValueError):UnityCatalogLineageStub(self.manifest())

if __name__=='__main__':unittest.main()
