import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock
from investigator.shared_state import SharedState,StateConflict,sha
from investigator.artifact_store import Files,LocalObjects
from investigator.graph_definitions import DefinitionSink
from investigator.graph_asset_catalog import AssetCatalog,NAMESPACE
from investigator.estate_graph_repository import GraphRepository
from investigator.adapters.estate_graph_static import extract_partitioned,asset_owners
from investigator.estate_graph_incremental import IncrementalScanner
from investigator.graph_scan_health import record as health
import test_graph_code_columns as code_cases
from test_estate_graph_static import asset

T=['2026-10-13T00:00:00Z','2026-10-13T01:00:00Z','2026-10-13T02:00:00Z']

class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.state=SharedState.offline(Path(self.tmp.name)/'state.sqlite')
        self.repo=GraphRepository(self.state);self.repo.migrate()
        self.sink=DefinitionSink(Files(LocalObjects(Path(self.tmp.name)/'blob')),'cas://definitions',recording_class='EXACT')
        self.assets=code_cases.CodeColumnsTests().notebook()+[asset('unrelated','Report','Unrelated')]
        self.catalog=AssetCatalog(self.repo,self.sink,extract_partitioned,asset_owners,allowed_owners=['book','lake','unrelated'])
        self.catalog.seed('estate',self.assets,observed_at=T[0])
    def payload(self,owner,changed=False):
        owners=asset_owners(self.assets)
        assets=copy.deepcopy([a for a in self.assets if owners[a['id']]==owner])
        if changed:
            for a in assets:
                if a['kind']=='DefinitionPart':a['metadata']['content']=a['metadata']['content'].replace("withColumn('value'","withColumn('adjusted'")
        return {'assets':assets,'source_asset_ids':[]}
    def projection(self):
        graph=self.repo.records('estate')
        for k in ('nodes','edges'):
            for v in graph[k]:
                v.pop('valid_from');v.pop('valid_to');v['provenance'].pop('observed_at')
        return graph
    def test_code_change_updates_affected_table_owner_atomically_revert_exact(self):
        before=self.projection();history=self.repo.changes('estate')
        result=self.catalog.refresh('estate','book',T[1],self.payload('book',True))
        graph=self.repo.records('estate');adjusted=next(n for n in graph['nodes']if n['label']=='adjusted')
        self.assertEqual(adjusted['owner'],'lake')
        self.assertEqual(adjusted['provenance']['observed_at'],T[1].replace('Z','.000000Z'))
        self.assertFalse(any(n['label']=='value'for n in graph['nodes']))
        new=[x for x in self.repo.changes('estate')if x not in history]
        self.assertEqual({x['owner']for x in new},{'book','lake'})
        self.assertEqual(len([x for x in self.repo.changes('estate')if x['owner']=='unrelated']),1)
        self.catalog.refresh('estate','book',T[2],self.payload('book'))
        self.assertEqual(self.projection(),before)
    def test_failed_fetch_leaves_manifest_and_graph_bytes_and_marks_unavailable(self):
        before=self.state.get(NAMESPACE,'estate');history=self.repo.changes('estate')
        source=Mock(identity='source',configured_owners=('book',))
        source.list_changes.return_value={'items':[{'owner':'book','fingerprint':sha('new'),'deleted':False}],'complete':False}
        source.fetch.side_effect=PermissionError('secret')
        result=IncrementalScanner(self.repo,source,None,reconcile=self.catalog.refresh).run('estate',T[1])
        self.assertEqual(result['owners'][0]['status'],'UNAVAILABLE')
        self.assertEqual(self.state.get(NAMESPACE,'estate'),before)
        self.assertEqual(self.repo.changes('estate'),history)
        self.assertIn('book',self.repo.records('estate')['unavailable_owners'])
    def test_failed_extraction_seals_exact_payload_and_reports_only_reference(self):
        before=self.state.get(NAMESPACE,'estate');history=self.repo.changes('estate')
        payload=self.payload('book',True)
        payload['assets'][0]['name']='fresh-metadata-only-sentinel'
        source=Mock(identity='source',configured_owners=('book',))
        source.list_changes.return_value={'items':[{'owner':'book','fingerprint':sha('new'),'deleted':False}],'complete':False}
        source.fetch.return_value=payload
        error=ValueError('GRAPH_UNKNOWN_COLLISION')
        original_partition=self.catalog.partition
        self.catalog.partition=Mock(side_effect=error)
        result=IncrementalScanner(self.repo,source,None,reconcile=self.catalog.refresh).run('estate',T[1])
        reference=result['owners'][0]['payload_reference']
        self.assertEqual(json.loads(self.sink.read(reference)),payload)
        basis_reference=result['owners'][0]['catalog_manifest_reference']
        basis=json.loads(self.sink.read(basis_reference))
        self.assertEqual(basis,{'estate':'estate','refresh_owner':'book','catalog_revision':before['revision'],'catalog':before['body']})
        self.assertNotIn('fresh-metadata-only-sentinel',json.dumps(result))
        self.assertEqual(self.repo.records('estate')['unavailable_owners']['book']['payload_reference'],reference)
        self.assertEqual(self.state.get(NAMESPACE,'estate'),before)
        self.assertEqual(self.repo.changes('estate'),history)
        from investigator.graph_asset_catalog import failure_reference
        self.assertIsNone(failure_reference(error,'other-estate','book'))
        self.assertIsNone(failure_reference(error,'estate','other-owner'))
        forged=ValueError('untrusted');forged._graph_failed_payload={'reference':reference}
        self.assertIsNone(failure_reference(forged,'estate','book'))
        from investigator.graph_asset_catalog import failure_manifest_reference
        self.assertIsNone(failure_manifest_reference(error,'estate','other-owner'))
        self.catalog.partition=original_partition
        self.catalog.refresh('estate','unrelated',T[2],self.payload('unrelated'))
        self.assertNotEqual(self.state.get(NAMESPACE,'estate')['body'],basis['catalog'])
        self.assertEqual(json.loads(self.sink.read(basis_reference)),basis)
        # Every original input remains addressable without querying current PG.
        for entry in basis['catalog']['owners'].values():
            self.assertIn('assets',json.loads(self.sink.read(entry['reference'])))
    def test_cross_owner_payload_refuses_before_capture(self):
        calls=Mock(wraps=self.sink);self.catalog.sink=calls
        with self.assertRaisesRegex(ValueError,'LEAVES_OWNER'):
            self.catalog.refresh('estate','book',T[1],self.payload('lake'))
        calls.assert_not_called()
    def test_failure_reference_rejects_secret_query_and_invalid_hash(self):
        from investigator.graph_scan_health import record
        for reference in ({'sha256':'not-a-sha','bytes':1,'uri':'cas://definitions/files/not-a-sha'},
                          {'sha256':'a'*64,'bytes':1,'uri':'https://example.invalid/files/'+'a'*64+'?sig=secret'}):
            with self.subTest(reference=reference),self.assertRaises(ValueError):
                record(self.state,'estate','book',T[1],'UNAVAILABLE',payload_reference=reference)

    def test_stale_manifest_cannot_overwrite_concurrent_refresh(self):
        old,_,_,_=self.catalog.snapshot('estate');history=self.repo.changes('estate')
        original=self.catalog.partition
        def compete(*args,**kwargs):
            values=original(*args,**kwargs)
            self.state.put(NAMESPACE,'estate',old['body'],revision=old['revision'])
            return values
        self.catalog.partition=compete
        with self.assertRaisesRegex(StateConflict,'REVISION_DIFFERS'):
            self.catalog.refresh('estate','book',T[1],self.payload('book',True))
        self.assertEqual(self.repo.changes('estate'),history)
        self.assertEqual(self.state.get(NAMESPACE,'estate')['body'],old['body'])
    def test_graph_failure_rolls_back_manifest_and_all_partitions(self):
        old=self.state.get(NAMESPACE,'estate');graph=self.projection();original=self.catalog.partition
        def bad(*args,**kwargs):
            values=original(*args,**kwargs)
            next(p for p in values if p['edges'])['edges'][0]['target']='absent'
            return values
        self.catalog.partition=bad
        with self.assertRaises(ValueError):self.catalog.refresh('estate','book',T[1],self.payload('book',True))
        self.assertEqual(self.state.get(NAMESPACE,'estate'),old);self.assertEqual(self.projection(),graph)
    def test_unavailable_other_owner_stays_unavailable_and_observed_time_preserved(self):
        health(self.state,'estate','unrelated',T[1],'UNAVAILABLE','not visible')
        self.catalog.refresh('estate','book',T[2],self.payload('book',True))
        graph=self.repo.records('estate');self.assertIn('unrelated',graph['unavailable_owners'])
        source=next(n for n in graph['nodes']if n['properties'].get('asset_id')=='a/units')
        self.assertEqual(source['provenance']['observed_at'],T[0].replace('Z','.000000Z'))
    def test_unavailable_code_owner_blocks_table_owned_derived_column(self):
        from investigator.estate_graph_api import GraphAPI
        health(self.state,'estate','book',T[1],'UNAVAILABLE','code unavailable')
        graph=self.repo.records('estate')
        value=next(n for n in graph['nodes']if n['label']=='value')
        self.assertEqual(value['owner'],'lake')
        gateway=Mock();gateway.graph_objects.side_effect=lambda estate,objects,**kw:list(objects)
        api=GraphAPI(self.repo,gateway,identity='reader',estate='estate',allowed_objects=[n['id']for n in graph['nodes']])
        result=api._slice([value['id']])
        self.assertEqual(result['stops'][0]['reason'],'code unavailable')
        self.assertIn('book',result['unavailable_owners'])
        self.assertEqual(result['edges'],[])

    def test_multiple_owner_refreshes_use_distinct_real_observation_times(self):
        source=Mock(identity='source',configured_owners=('book','lake'))
        source.list_changes.return_value={'items':[{'owner':owner,'fingerprint':sha(owner),'deleted':False}for owner in ('book','lake')],'complete':False}
        source.fetch.side_effect=lambda owner:self.payload(owner,owner=='book')
        moments=iter(['2026-10-13T01:00:00Z','2026-10-13T01:00:01Z','2026-10-13T01:00:02Z','2026-10-13T01:00:03Z'])
        result=IncrementalScanner(self.repo,source,None,reconcile=self.catalog.refresh,observation_clock=lambda:next(moments)).run('estate',T[1])
        self.assertEqual([o['status']for o in result['owners']],['RESCANNED','RESCANNED'])
        self.assertEqual(self.state.get(NAMESPACE,'estate')['revision'],2)

    def test_secret_payload_rejected_before_blob_or_manifest_write(self):
        before=self.state.get(NAMESPACE,'estate');payload=self.payload('book')
        payload['assets'][0]['metadata']['password']='do-not-persist-secret'
        with self.assertRaisesRegex(ValueError,'SECRET_DETECTED'):self.catalog.refresh('estate','book',T[1],payload)
        self.assertEqual(self.state.get(NAMESPACE,'estate'),before)
    def test_manifest_only_seed_checks_current_graph_and_preserves_history(self):
        old=self.repo.changes('estate')
        with self.state.transaction()as db:
            self.state.sql(db,'DELETE FROM state_documents WHERE namespace=? AND identity=?',(NAMESPACE,'estate'))
        self.catalog.seed('estate',self.assets,observed_at=T[1],source_observations={a['id']:T[0]for a in self.assets},existing_graph_only=True)
        self.assertEqual(self.repo.changes('estate'),old)
        with self.state.transaction()as db:
            self.state.sql(db,'DELETE FROM state_documents WHERE namespace=? AND identity=?',(NAMESPACE,'estate'))
        altered=copy.deepcopy(self.assets);altered[-1]['name']='wrong retained definition'
        with self.assertRaisesRegex(StateConflict,'PARTITION_HASHES_DIFFER'):
            self.catalog.seed('estate',altered,observed_at=T[1],existing_graph_only=True)
        with self.assertRaises(KeyError):self.state.get(NAMESPACE,'estate')
        self.assertEqual(self.repo.changes('estate'),old)

    def test_undeclared_owner_and_cross_owner_payload_refused(self):
        with self.assertRaisesRegex(ValueError,'NOT_APPROVED'):self.catalog.refresh('estate','unknown',T[1],self.payload('book'))
        with self.assertRaisesRegex(ValueError,'LEAVES_OWNER'):self.catalog.refresh('estate','book',T[1],self.payload('lake'))

if __name__=='__main__':unittest.main()
