import copy
import hashlib
import tempfile
from pathlib import Path
import unittest
from investigator.adapters.estate_graph_static import extract_partitioned
from investigator.estate_graph_repository import GraphRepository
from investigator.shared_state import SharedState
import test_estate_graph_static as static_cases
from test_estate_graph import graph,T0,T1,proof
from test_graph_part_b import verification_fixture


class PartitionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.repo=GraphRepository(SharedState.offline(Path(self.tmp.name)/'state.sqlite'));self.repo.migrate()
    def build(self,assets,at=T0):
        return extract_partitioned('estate',assets,lambda raw:{'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'uri':'cas://definitions/'+hashlib.sha256(raw).hexdigest()},observed_at=at)
    def test_one_changed_node_updates_only_that_current_row(self):
        original=graph();self.repo.replace(original)
        with self.repo.state.transaction()as db:
            db.execute('CREATE TABLE projection_writes(operation TEXT, identity TEXT)')
            for table in ('estate_graph_nodes','estate_graph_edges'):
                for operation,record in (('INSERT','NEW'),('UPDATE','NEW'),('DELETE','OLD')):
                    db.execute('CREATE TRIGGER watch_'+table+'_'+operation+' AFTER '+operation+' ON '+table+
                               " BEGIN INSERT INTO projection_writes VALUES('"+operation+"',"+record+'.identity); END')
        changed=copy.deepcopy(original);changed.update(definition_hash='b'*64,observed_at=T1)
        changed['nodes'][0]['label']='Renamed report'
        self.repo.replace(changed)
        with self.repo.state.transaction(_read_only=True)as db:
            writes=db.execute('SELECT operation,identity FROM projection_writes').fetchall()
        self.assertEqual(writes,[('UPDATE','report')])
        self.assertEqual(len(self.repo.records('estate')['nodes']),len(original['nodes']))

    def test_catalog_index_returns_only_requested_estate_addresses(self):
        original=graph();original['nodes'][0]['properties']={'asset_id':'native/report','retained_body':'x'*64000}
        self.repo.replace(original)
        index=self.repo.catalog_index('estate')
        self.assertEqual({n['id']for n in index},{n['id']for n in original['nodes']})
        self.assertEqual(next(n for n in index if n['id']=='report'),
                         {'id':'report','kind':'REPORT','properties':{'asset_id':'native/report'}})
        self.assertTrue(all(set(n)=={'id','kind','properties'}for n in index))
        self.assertEqual(self.repo.catalog_index("estate' OR 1=1 --"),[])
    def test_seed_cross_owner_edges_is_order_independent_and_ids_survive_item_reextract(self):
        assets=static_cases.StaticTests().assets();parts=self.build(assets)
        self.assertEqual({p['owner'] for p in parts},{'r',assets[1]['id']})
        report=next(p for p in parts if p['owner']=='r');model=next(p for p in parts if p['owner']!='r')
        self.assertTrue(any(e['target'] in {n['id'] for n in model['nodes']} for e in report['edges']))
        self.repo.replace_many([report,model]);before=self.repo.records('estate')
        changed=copy.deepcopy(assets);changed[7]['name']='Renamed page'
        # Explicit retained external model symbols are supplied, not queried.
        updated=next(p for p in self.build(changed,T1) if p['owner']=='r')
        self.assertEqual({n['id'] for n in updated['nodes']},{n['id'] for n in report['nodes']})
        self.repo.replace(updated)
        after=self.repo.records('estate')
        self.assertEqual({n['id'] for n in before['nodes']},{n['id'] for n in after['nodes']})
        self.assertTrue(all(e['target'] in {n['id'] for n in after['nodes']} for e in after['edges']))
    def test_missing_external_symbols_remain_unknown_not_name_guessed(self):
        assets=static_cases.StaticTests().assets();report_assets=[a for a in assets if a['id'] not in {x['id'] for x in assets[1:5]}]
        parts=self.build(report_assets);self.assertTrue(any(n['confidence']=='UNKNOWN' for p in parts for n in p['nodes']))
    def test_batch_endpoint_failure_rolls_back_all_owners(self):
        parts=self.build(static_cases.StaticTests().assets());parts[-1]['edges'][0]['target']='missing'
        with self.assertRaisesRegex(ValueError,'ENDPOINT_NOT_DECLARED'):self.repo.replace_many(parts)
        self.assertEqual(self.repo.records('estate')['nodes'],[]);self.assertEqual(self.repo.changes('estate'),[])
    def test_unchanged_owner_skipped_and_single_projection_read_per_kind(self):
        parts=self.build(static_cases.StaticTests().assets());self.repo.replace_many(parts)
        called=[];old=self.repo._current
        self.repo._current=lambda db,estate,kind:(called.append(kind),old(db,estate,kind))[1]
        later=copy.deepcopy(parts)
        for part in later:part['observed_at']=T1
        later[0]['definition_hash']='d'*64;later[0]['nodes'][0]['label']='Changed'
        self.repo.replace_many(later);self.assertEqual(called,['nodes','edges'])
        self.assertEqual(len(self.repo.changes('estate')),3)
    def test_reextracted_changed_declared_edge_keeps_old_verification_as_stale(self):
        self.repo.replace(graph());self.repo.verification_resolver=verification_fixture()[0]
        self.repo.verify_edges('estate',['q'],observed_at='2026-10-13T00:30:00Z')
        changed=graph();changed.update(definition_hash='c'*64,observed_at=T1)
        changed['edges'][2]['provenance']=proof(hash='c'*64)
        self.repo.replace(changed);got=next(e for e in self.repo.records('estate')['edges'] if e['id']=='vm')
        self.assertEqual(got['confidence'],'DECLARED');self.assertEqual(got['verification']['state'],'STALE')
        self.assertEqual(got['verification']['evidence_ids'],['q'])

if __name__=='__main__':unittest.main()
