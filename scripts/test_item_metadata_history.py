import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock,patch

from investigator.adapters.item_metadata_history import ItemMetadataHistory,NAMESPACE
from investigator.adapters.graph_change_collector import FabricChanges
from investigator.adapters.estate_graph_static import extract
from investigator.adapters.explain_history import HistoryPort
from investigator.shared_state import SharedState,encoded
from test_legacy_report_structure import W,R,OWNER,layout,parts
from test_estate_graph import T0,T1


class ItemHistoryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.state=SharedState.offline(Path(self.temp.name)/'state.sqlite');self.state.migrate()
        self.raw={}
        def sink(raw):
            digest=hashlib.sha256(raw).hexdigest();self.raw[digest]=raw
            return {'sha256':digest,'bytes':len(raw),'uri':'cas://fixture/files/'+digest}
        self.sink=sink;self.history=ItemMetadataHistory(self.state,sink)

    def test_same_definition_changed_modified_time_keeps_hash_and_retains_history(self):
        item={'id':R,'type':'Report','displayName':'Report','lastModifiedDateTime':T0,'modifiedBy':{'displayName':'First actor'}}
        http=Mock(side_effect=lambda *_args,**_kwargs:{'status_code':200,'text':{'value':[dict(item)]}})
        clocks=iter((T0,T1))
        collector=FabricChanges(W,[R],http,retain_definition=self.sink,
            item_observer=lambda owner,value:self.history.observe('estate',owner,value,collected_at=next(clocks)))
        with patch('investigator.adapters.graph_change_collector.definition',return_value=parts(layout())):
            first_signal=collector.list_changes();first=collector.fetch(OWNER)
            item.update(lastModifiedDateTime=T1,modifiedBy={'displayName':'Second actor'})
            second_signal=collector.list_changes();second=collector.fetch(OWNER)
        self.assertEqual(first,second)
        self.assertNotEqual(first_signal['items'][0]['fingerprint'],second_signal['items'][0]['fingerprint'])
        old_graph=extract('estate',first['assets'],self.sink,observed_at=T0)
        new_graph=extract('estate',second['assets'],self.sink,observed_at=T1)
        self.assertEqual(old_graph['definition_hash'],new_graph['definition_hash'])
        node={'id':'graph-report','owner':OWNER,'properties':{}}
        observed=self.history.read('estate',node)['observations']
        self.assertEqual([(o['actor'],o['at']) for o in observed],
                         [('Second actor','2026-10-13T01:00:00.000000Z'),('First actor','2026-10-13T00:00:00.000000Z')])
        self.assertEqual(http.call_count,2)  # History consumed no additional API call.
        for row in observed:
            reference=row['provenance']['reference']
            raw=self.raw[reference['sha256']]
            self.assertEqual(hashlib.sha256(raw).hexdigest(),reference['sha256'])
            self.assertIn('lastModifiedDateTime',json.loads(raw)['item'])

    def test_missing_actor_or_modified_time_is_not_collection_time_or_owner(self):
        self.history.observe('estate',OWNER,{'id':R,'type':'Report','lastModifiedDateTime':T0},collected_at=T1)
        node={'id':'graph-report','owner':OWNER,'properties':{}}
        result=HistoryPort(metadata=lambda value:self.history.read('estate',value)).read(node)
        self.assertIsNone(result['observations'][0]['actor'])
        self.assertEqual(result['observations'][0]['at'],'2026-10-13T00:00:00.000000Z')
        self.history.observe('estate',OWNER,{'id':R,'type':'Report','modifiedBy':'Known actor but no date'},collected_at=T1)
        result=self.history.read('estate',node)
        self.assertTrue(any(g['reason']=='MODIFIED_TIME_NOT_RETURNED' for g in result['coverage_gaps']))
        self.assertFalse(any(r['actor']=='Known actor but no date' for r in result['observations']))

    def test_observation_has_explicit_projection_class_and_is_not_definition_bytes(self):
        item={'id':R,'type':'Report','lastModifiedDateTime':T0}
        reference=self.history.observe('estate',OWNER,item,collected_at=T1)
        saved=json.loads(self.raw[reference['sha256']])
        self.assertEqual(saved['recording_class'],'CANONICAL_ITEM_METADATA_PROJECTION')
        self.assertEqual(saved['item'],item)
        self.assertNotIn('parts',saved)

    def test_index_is_bounded_and_immutable_originals_remain(self):
        history=ItemMetadataHistory(self.state,self.sink,limit=1)
        for at in (T0,T1):
            history.observe('estate',OWNER,{'id':R,'type':'Report','lastModifiedDateTime':at},collected_at=T1)
        saved=self.state.get(NAMESPACE,encoded(['estate',OWNER]))['body']
        self.assertTrue(saved['truncated']);self.assertEqual(len(saved['observations']),1)
        self.assertEqual(len(self.raw),2)
        read=history.read('estate',{'id':'graph-report','owner':OWNER,'properties':{}})
        self.assertIn('Older observations remain',read['coverage_gaps'][0]['reason'])

    def test_wrong_owner_or_wrong_cas_reference_is_refused(self):
        with self.assertRaisesRegex(ValueError,'OWNER_BINDING'):
            self.history.observe('estate',OWNER,{'id':W},collected_at=T0)
        bad=ItemMetadataHistory(self.state,lambda raw:{'sha256':'a'*64,'bytes':len(raw),'uri':'cas://fixture/files/not-the-hash'})
        with self.assertRaisesRegex(ValueError,'REFERENCE_DIFFERS'):
            bad.observe('estate',OWNER,{'id':R},collected_at=T0)


if __name__=='__main__':unittest.main()
