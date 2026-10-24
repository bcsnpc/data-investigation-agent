import copy
from pathlib import Path
import tempfile
import unittest
from investigator import estate_graph_contract as c
from investigator.estate_graph_repository import GraphRepository
from investigator.estate_graph_api import GraphAPI,coverage
from investigator.shared_state import SharedState,StateConflict
from investigator.live_gateway import Gateway,GatewayDenied

T0='2026-10-13T00:00:00Z';T1='2026-10-13T01:00:00Z'
def proof(hash='a'*64,source='STATIC_DEFINITION'):
    return {'source':source,'source_id':'retained-part','definition_hash':hash,'observed_at':T0,'span':{'kind':'JSON_POINTER','path':'/visual'}}
def graph():
    nodes=[c.node('report','owner','REPORT','Report',proof()),c.node('page','owner','PAGE','Page',proof()),
        c.node('visual','owner','VISUAL','Quantity',proof()),c.node('measure','owner','MEASURE','Units',proof()),
        c.node('column','owner','COLUMN','Value',proof())]
    edges=[c.edge('rp','owner','CONTAINS','report','page',proof()),c.edge('pv','owner','CONTAINS','page','visual',proof()),
        c.edge('vm','owner','COMPUTED_FROM','visual','measure',proof()),c.edge('mc','owner','COMPUTED_FROM','measure','column',proof())]
    return {'estate':'estate','owner':'owner','definition_hash':'a'*64,'observed_at':T0,'nodes':nodes,'edges':edges}

class GraphContractTests(unittest.TestCase):
    def test_model_cannot_promote_itself_verified_or_drop_unknown_reason(self):
        edge=graph()['edges'][0];edge['confidence']='VERIFIED';edge['provenance']=proof(source='MODEL_PROPOSAL')
        edge['verification']={'state':'CURRENT','evidence_ids':['query'],'scope_hash':'c'*64}
        with self.assertRaisesRegex(ValueError,'VERIFIED_PRODUCER'):c.record(edge,edge=True)
        edge['confidence']='UNKNOWN';edge['verification']['state']='NOT_VERIFIED'
        with self.assertRaisesRegex(ValueError,'UNKNOWN_NEEDS_REASON'):c.record(edge,edge=True)
    def test_closed_schema_and_span(self):
        node=graph()['nodes'][0]
        with self.assertRaisesRegex(ValueError,'RECORD_SHAPE'):c.record({**node,'native_secret':'not permitted'})
        node['provenance']['span']={'kind':'TEXT','start':8,'end':3}
        with self.assertRaisesRegex(ValueError,'TEXT_SPAN'):c.record(node)

class GraphRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.state=SharedState.offline(Path(self.temp.name)/'graph.sqlite');self.repo=GraphRepository(self.state);self.repo.migrate()
    def test_large_projection_batches_writes_and_rolls_back_a_late_failure(self):
        from unittest.mock import patch
        first=graph();self.repo.replace(first)
        changed=copy.deepcopy(first);changed.update(definition_hash='c'*64,observed_at=T1)
        changed['nodes'] += [c.node('extra'+str(i),'owner','COLUMN',str(i),proof()) for i in range(80)]
        original=self.state.sqlmany;calls=[]
        def fail_late(db,query,rows):
            calls.append(query)
            if 'estate_graph_nodes VALUES' in query:raise RuntimeError('injected write failure')
            return original(db,query,rows)
        with patch.object(self.state,'sqlmany',side_effect=fail_late):
            with self.assertRaisesRegex(RuntimeError,'injected'):self.repo.replace(changed)
        self.assertEqual(len(self.repo.records('estate')['nodes']),5)
        self.assertEqual(len(self.repo.changes('estate')),1)
        with patch.object(self.state,'sql',wraps=self.state.sql)as queries:
            self.repo.replace(changed)
        self.assertLess(queries.call_count,15)
        self.assertEqual(len(self.repo.records('estate')['nodes']),85)
        self.assertEqual(len(self.repo.records('estate',at=T0)['nodes']),5)
    def test_history_hash_skip_and_deleted_versions(self):
        first=graph();self.assertEqual(self.repo.replace(first)['changed'],9)
        self.assertEqual(self.repo.replace(first),{'status':'UNCHANGED','changed':0})
        second=copy.deepcopy(first);second.update(definition_hash='b'*64,observed_at=T1)
        second['nodes']=[n for n in second['nodes'] if n['id']!='column'];second['edges']=[e for e in second['edges'] if e['id']!='mc']
        self.repo.replace(second)
        self.assertEqual(len(self.repo.records('estate',at=T0)['nodes']),5)
        self.assertEqual(len(self.repo.records('estate',at=T1)['nodes']),4)
        self.assertEqual(len(self.repo.changes('estate')),2)
    def test_reextracted_changed_declared_edge_keeps_old_verification_as_stale(self):
        value=graph();edge=value['edges'][2];edge.update(confidence='VERIFIED',provenance=proof(source='QUERY_VERIFICATION'),
            verification={'state':'CURRENT','evidence_ids':['q'],'scope_hash':'b'*64})
        from test_graph_part_b import verification_fixture
        self.repo.verification_resolver=verification_fixture()[0]
        self.repo.replace(value)
        changed=graph();changed.update(definition_hash='c'*64,observed_at=T1)
        changed['edges'][2]['provenance']=proof(hash='c'*64)
        self.repo.replace(changed)
        got=next(e for e in self.repo.records('estate')['edges'] if e['id']=='vm')
        self.assertEqual(got['confidence'],'DECLARED');self.assertEqual(got['verification']['state'],'STALE')
        self.assertEqual(got['verification']['evidence_ids'],['q'])
    def test_collection_failure_downgrades_earned_proof_without_rewriting_history(self):
        from investigator.graph_scan_health import record
        value=graph();edge=value['edges'][2];edge.update(confidence='VERIFIED',provenance=proof(source='QUERY_VERIFICATION'),
            verification={'state':'CURRENT','evidence_ids':['q'],'scope_hash':'b'*64})
        from test_graph_part_b import verification_fixture
        self.repo.verification_resolver=verification_fixture()[0]
        self.repo.replace(value)
        record(self.state,'estate','owner',T1,'UNAVAILABLE','Definition read permission refused')
        got=next(e for e in self.repo.records('estate')['edges'] if e['id']=='vm')
        self.assertEqual(got['confidence'],'DECLARED');self.assertEqual(got['verification']['state'],'STALE')
        old=next(e for e in self.repo.records('estate',at=T0)['edges'] if e['id']=='vm')
        self.assertEqual(old['confidence'],'VERIFIED')
        self.assertEqual(len(self.repo.changes('estate')),1)
    def test_foreign_owner_and_dangling_links_refuse_transactionally(self):
        original=graph();self.repo.replace(original)
        bad={**graph(),'owner':'other','definition_hash':'b'*64,'observed_at':T1}
        for item in bad['nodes']+bad['edges']:item['owner']='other'
        with self.assertRaisesRegex(StateConflict,'OWNED_BY_ANOTHER'):self.repo.replace(bad)
        bad=graph();bad.update(definition_hash='c'*64,observed_at=T1);bad['edges'][0]['target']='missing'
        with self.assertRaisesRegex(ValueError,'ENDPOINT'):self.repo.replace(bad)
        self.assertEqual(len(self.repo.changes('estate')),1)
    def test_verified_edge_needs_existing_matching_producer_receipt(self):
        value=graph();edge=value['edges'][2];edge.update(confidence='VERIFIED',provenance=proof(source='QUERY_VERIFICATION'),
            verification={'state':'CURRENT','evidence_ids':['q'],'scope_hash':'b'*64})
        with self.assertRaisesRegex(ValueError,'RESOLVER_REQUIRED'):self.repo.replace(value)
        from test_graph_part_b import verification_fixture
        self.repo.verification_resolver=verification_fixture()[0]
        self.repo.replace(value)
        second=copy.deepcopy(value);second.update(definition_hash='c'*64,observed_at=T1);second['nodes'][2]['label']='Changed visual'
        self.repo.replace(second)
        got=next(e for e in self.repo.records('estate')['edges'] if e['id']=='vm')
        self.assertEqual(got['confidence'],'DECLARED');self.assertEqual(got['verification']['state'],'STALE')
        old=next(e for e in self.repo.records('estate',at=T0)['edges'] if e['id']=='vm')
        self.assertEqual(old['confidence'],'VERIFIED')
    def test_unrelated_definition_change_keeps_verified_edge_and_original_observation(self):
        value=graph();edge=value['edges'][2];edge.update(confidence='VERIFIED',provenance=proof(source='QUERY_VERIFICATION'),
            verification={'state':'CURRENT','evidence_ids':['q'],'scope_hash':'b'*64})
        from test_graph_part_b import verification_fixture
        self.repo.verification_resolver=verification_fixture()[0]
        self.repo.replace(value)
        second=copy.deepcopy(value);second.update(definition_hash='c'*64,observed_at=T1)
        for item in second['nodes']+second['edges']:item['provenance']['observed_at']=T1
        second['nodes'][0]['label']='Changed report title only'
        self.repo.replace(second)
        edge=next(e for e in self.repo.records('estate')['edges'] if e['id']=='vm')
        self.assertEqual(edge['confidence'],'VERIFIED');self.assertEqual(edge['provenance']['observed_at'],T0)

    def test_deleted_cross_owner_endpoint_becomes_named_unknown_boundary(self):
        upstream={'estate':'estate','owner':'upstream','definition_hash':'a'*64,'observed_at':T0,
            'nodes':[c.node('source','upstream','COLUMN','Source',proof())],'edges':[]}
        downstream={'estate':'estate','owner':'downstream','definition_hash':'b'*64,'observed_at':T0,
            'nodes':[c.node('visual','downstream','VISUAL','Value',proof())],
            'edges':[c.edge('dependency','downstream','COMPUTED_FROM','visual','source',proof())]}
        self.repo.replace(upstream);self.repo.replace(downstream)
        self.repo.replace({**upstream,'definition_hash':'c'*64,'observed_at':T1,'nodes':[]})
        current=self.repo.records('estate');edge=current['edges'][0]
        self.assertEqual(edge['confidence'],'UNKNOWN');self.assertIn('source',edge['unknown']['reason'])
        self.assertNotIn('source',{n['id'] for n in current['nodes']})
        self.assertIn(edge['target'],{n['id'] for n in current['nodes']})
        self.assertIn('source',{n['id'] for n in self.repo.records('estate',at=T0)['nodes']})

    def test_history_tampering_refused(self):
        self.repo.replace(graph())
        with self.state.transaction() as db:db.execute("UPDATE estate_graph_history SET body_hash='wrong'")
        with self.assertRaisesRegex(StateConflict,'HASH_DIFFERS'):self.repo.records('estate')

    def test_query_proof_promotes_without_changing_definition_hash_and_history_survives(self):
        from test_graph_part_b import verification_fixture
        self.repo.replace(graph());self.repo.verification_resolver=verification_fixture()[0]
        self.assertEqual(self.repo.verify_edges('estate',['q'],observed_at=T1),{'status':'UPDATED','changed':1})
        current=next(e for e in self.repo.records('estate')['edges'] if e['id']=='vm')
        self.assertEqual(current['confidence'],'VERIFIED');self.assertEqual(current['provenance']['definition_hash'],'a'*64)
        self.assertIn('semantic correctness',current['properties']['query_verification']['qualification'])
        self.assertEqual(current['properties']['query_verification']['snapshot'],'SNAPSHOT_UNVERIFIED')
        old=next(e for e in self.repo.records('estate',at=T0)['edges'] if e['id']=='vm')
        self.assertEqual(old['confidence'],'DECLARED')
        self.assertEqual(self.repo.replace(graph()),{'status':'UNCHANGED','changed':0})
        self.assertEqual(self.repo.changes('estate')[0]['changes'][0]['change'],'QUERY_VERIFIED')

    def test_same_values_from_other_estate_cannot_promote(self):
        from test_graph_part_b import verification_fixture
        resolver,check,binding,reads=verification_fixture()
        check['estate']=binding['estate']='other'
        for read in reads.values():read['estate']='other'
        self.repo.replace(graph());self.repo.verification_resolver=resolver
        with self.assertRaisesRegex(ValueError,'ESTATE_DIFFERS'):self.repo.verify_edges('estate',['q'],observed_at=T1)
        self.assertEqual(len(self.repo.changes('estate')),1)

class GraphAPITests(GraphRepositoryTests):
    def test_definition_tool_reads_retained_content_and_keeps_historical_reader(self):
        from investigator.artifact_store import Files,LocalObjects
        from investigator.graph_definitions import DefinitionSink
        sink=DefinitionSink(Files(LocalObjects(Path(self.temp.name)/'definitions')),
            'cas://definitions',recording_class='EXACT')
        raw=b'{"expression":"SUM(Entries[Quantity])"}'
        record=graph();reference=sink(raw)
        record['nodes'][3]['properties']['definition']=reference
        self.repo.replace(record);reads=[]
        def read(ref):
            reads.append(ref);return sink.read(ref)
        api=self.api(definition_reader=read)
        for selected in (api,api.as_of(T0)):
            result=selected.definition_of('measure')
            self.assertEqual(result['content'],raw.decode())
            self.assertEqual(result['definition'],reference)
            self.assertEqual(result['provenance'],record['nodes'][3]['provenance'])
        self.assertEqual(reads,[reference,reference])
        from unittest.mock import patch
        api.unavailable={'owner':{'reason':'Current collection unavailable'}}
        with patch.object(api,'_read',return_value=({'measure':record['nodes'][3]},[])):
            retained=api.definition_of('measure')
        self.assertEqual(retained['content'],raw.decode())
        self.assertEqual(retained['collection_unavailable']['reason'],'Current collection unavailable')
        self.assertNotIn('content',self.api().definition_of('measure'))
        limited=self.api(['visual'],definition_reader=read)
        with self.assertRaises(GatewayDenied):limited.definition_of('measure')
        self.assertEqual(len(reads),3)

    def api(self,allowed=None,**kwargs):
        allowed=allowed or ['report','page','visual','measure','column']
        gateway=Gateway({'version':1,'live_enabled':False,'identities':{'reader':{'graph':{'estate':allowed}}}})
        return GraphAPI(self.repo,gateway,identity='reader',estate='estate',allowed_objects=allowed,**kwargs)
    def test_exact_slice_and_historical_variant(self):
        self.repo.replace(graph());api=self.api()
        self.assertEqual({n['id'] for n in api.path_to_source('visual')['nodes']},{'visual','measure','column'})
        self.assertEqual(api.visual_context('report','page','visual')['edges'][0]['id'],'vm')
        self.assertEqual(api.as_of(T0).definition_of('visual')['provenance']['definition_hash'],'a'*64)
    def test_unauthorized_neighbor_not_returned_and_root_refused(self):
        self.repo.replace(graph());api=self.api(['visual'])
        result=api.path_to_source('visual')
        self.assertEqual([n['id'] for n in result['nodes']],['visual']);self.assertEqual(result['edges'],[])
        self.assertIn('outside',result['stops'][0]['reason'])
        with self.assertRaises(GatewayDenied):api.definition_of('column')
    def test_bounds_fail_closed_with_explicit_truncation(self):
        self.repo.replace(graph());result=self.api(max_nodes=1,max_edges=1).path_to_source('visual')
        self.assertTrue(result['truncated']);self.assertEqual(len(result['nodes']),1)
    def test_serialized_response_has_a_hard_bound(self):
        self.repo.replace(graph())
        with self.assertRaisesRegex(ValueError,'SLICE_BYTE_BOUND'):self.api(max_bytes=1024).path_to_source('visual')

    def test_gateway_no_wildcards_or_implicit_whole_estate(self):
        gateway=Gateway({'version':1,'live_enabled':False,'identities':{'reader':{'graph':{'estate':['*']}}}})
        with self.assertRaises(GatewayDenied):gateway.graph_objects('estate',['x'],identity='reader')

if __name__=='__main__':unittest.main()
