import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock
from investigator.shared_state import SharedState, sha
from investigator.estate_graph_repository import GraphRepository
from investigator.estate_graph_incremental import IncrementalScanner
from investigator.adapters.graph_change_collector import FabricChanges, SqlSchemaChanges
from investigator import estate_graph_contract as c
from investigator.estate_graph_api import GraphAPI, coverage
from investigator.graph_scan_health import record as health
from scan_estate_graph import Meter, validate

TIMES = ['2026-10-13T00:00:00Z', '2026-10-13T01:00:00Z', '2026-10-13T02:00:00Z']


class IncrementalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.state = SharedState.offline(Path(self.temp.name)/'state.db')
        self.repo = GraphRepository(self.state); self.repo.migrate()
        self.signals = [{'owner': x, 'fingerprint': sha(x), 'deleted': False} for x in ('one', 'two')]
        self.payloads = {x: {'assets': [{'label': x}], 'source_asset_ids': []} for x in ('one', 'two')}
        self.collector = Mock(identity='catalog')
        self.collector.list_changes.side_effect = lambda: {'items': self.signals, 'complete': False}
        self.collector.fetch.side_effect = lambda owner: self.payloads[owner]
        self.extract = Mock(side_effect=self.graph)
        self.scan = IncrementalScanner(self.repo, self.collector, self.extract)
    def graph(self, estate, owner, at, payload):
        proof = {'source': 'STATIC_DEFINITION', 'source_id': owner, 'definition_hash': sha(payload),
                 'observed_at': at, 'span': {'kind': 'JSON_POINTER', 'path': ''}}
        nodes = [c.node(owner, owner, 'VISUAL', payload['assets'][0]['label'], proof)]
        return {'estate': estate, 'owner': owner, 'observed_at': at, 'definition_hash': sha(payload), 'nodes': nodes, 'edges': []}
    def test_only_changed_owner_is_fetched_and_rescanned_change_then_revert_history(self):
        self.scan.run('estate', TIMES[0]); self.collector.fetch.reset_mock(); self.extract.reset_mock()
        self.signals[0]['fingerprint'] = sha('changed'); self.payloads['one']['assets'][0]['label'] = 'hidden filter changed'
        result = self.scan.run('estate', TIMES[1])
        self.collector.fetch.assert_called_once_with('one'); self.assertEqual(self.extract.call_count, 1)
        self.assertEqual([x['status'] for x in result['owners']], ['RESCANNED', 'UNCHANGED_SIGNAL'])
        self.signals[0]['fingerprint'] = sha('revert'); self.payloads['one']['assets'][0]['label'] = 'one'
        self.scan.run('estate', TIMES[2])
        before = self.repo.records('estate', at=TIMES[0]); after = self.repo.records('estate', at=TIMES[2])
        self.assertEqual([x['label'] for x in before['nodes']], [x['label'] for x in after['nodes']])
        self.assertEqual(len(self.repo.changes('estate')), 4)
    def test_changed_timestamp_same_definition_fetches_but_does_not_parse(self):
        self.scan.run('estate', TIMES[0]); self.extract.reset_mock()
        self.signals[0]['fingerprint'] = sha('clock')
        result = self.scan.run('estate', TIMES[1])
        self.extract.assert_not_called(); self.assertEqual(result['owners'][0]['status'], 'UNCHANGED_DEFINITION')
    def test_no_modified_timestamp_polls_hash_without_reextracting_unchanged(self):
        self.signals[0]['fingerprint'] = None; self.scan.run('estate', TIMES[0]); self.extract.reset_mock()
        self.scan.run('estate', TIMES[1]); self.extract.assert_not_called()
        self.assertEqual(self.collector.fetch.call_count, 3)
    def test_incomplete_listing_does_not_remove_missing_owner_but_explicit_tombstone_does(self):
        self.scan.run('estate', TIMES[0]); self.signals = self.signals[:1]
        self.scan.run('estate', TIMES[1]); self.assertEqual(len(self.repo.records('estate')['nodes']), 2)
        self.signals[0]['deleted'] = True; self.scan.run('estate', TIMES[2])
        self.assertEqual([x['id'] for x in self.repo.records('estate')['nodes']], ['two'])
        self.assertEqual(len(self.repo.records('estate', at=TIMES[0])['nodes']), 2)
    def test_permission_failure_does_not_advance_owner_cursor(self):
        self.collector.fetch.side_effect = PermissionError('secret must not reach result')
        result = self.scan.run('estate', TIMES[0]); self.assertNotIn('secret', json.dumps(result))
        self.assertEqual(result['owners'][0]['reason'], 'PermissionError')
        self.collector.fetch.side_effect = lambda owner: self.payloads[owner]
        self.scan.run('estate', TIMES[1]); self.assertEqual(len(self.repo.records('estate')['nodes']), 2)
    def test_failed_refresh_blocks_path_and_old_asof_remains_available(self):
        self.scan.run('estate', TIMES[0]); self.signals[0]['fingerprint']=sha('changed')
        self.collector.fetch.side_effect=PermissionError('not retained')
        self.scan.run('estate', TIMES[1])
        gateway=Mock();gateway.graph_objects.side_effect=lambda estate,objects,**kw:list(objects)
        api=GraphAPI(self.repo,gateway,identity='reader',estate='estate',allowed_objects=['one','two'])
        current=api.path_to_source('one')
        self.assertIn('PermissionError',current['stops'][0]['reason'])
        self.assertIn('one',current['unavailable_owners'])
        self.assertFalse(api.as_of(TIMES[0]).path_to_source('one')['unavailable_owners'])
        self.assertIn('one',coverage(self.repo.records('estate'))['unavailable_owners'])
    def test_failed_listing_then_same_signal_forces_revalidation_and_clears_gap(self):
        self.scan.run('estate', TIMES[0])
        self.collector.list_changes.side_effect=PermissionError('denied')
        with self.assertRaises(PermissionError):self.scan.run('estate', TIMES[1])
        self.assertEqual(len(self.repo.records('estate')['unavailable_owners']),2)
        self.collector.fetch.reset_mock()
        self.collector.list_changes.side_effect=lambda:{'items':self.signals,'complete':False}
        self.scan.run('estate', TIMES[2])
        self.assertEqual(self.collector.fetch.call_count,2)
        self.assertNotIn('unavailable_owners',self.repo.records('estate'))
    def test_inflight_refresh_is_unavailable_if_worker_crashes(self):
        self.scan.run('estate', TIMES[0]);health(self.state,'estate','one',TIMES[1],'REFRESHING','Awaiting collection')
        self.assertEqual(self.repo.records('estate')['unavailable_owners']['one']['status'],'REFRESHING')
    def test_extra_signal_duplicate_and_owner_limit_refuse_before_fetch(self):
        self.signals.append(copy.deepcopy(self.signals[0]))
        with self.assertRaisesRegex(ValueError, 'DUPLICATE'): self.scan.run('estate', TIMES[0])
        self.collector.fetch.assert_not_called()


class LiveCollectorTests(unittest.TestCase):
    workspace = '00000000-0000-0000-0000-000000000001'
    item = '00000000-0000-0000-0000-000000000002'
    def test_live_listing_is_bounded_and_absence_is_not_a_deletion(self):
        call = Mock(return_value={'status_code': 200, 'text': {'value': [], 'continuationToken': 'next'}})
        source = FabricChanges(self.workspace, [self.item], call, max_pages=2)
        self.assertEqual(source.list_changes(), {'items': [], 'complete': False})
        self.assertEqual(call.call_count, 2)
    def test_missing_modified_time_does_not_invent_unchanged_signal(self):
        call = Mock(return_value={'status_code': 200, 'text': {'value': [{'id': self.item, 'type': 'Report', 'displayName': 'Name'}]}})
        source = FabricChanges(self.workspace, [self.item], call)
        self.assertIsNone(source.list_changes()['items'][0]['fingerprint'])
        with self.assertRaisesRegex(ValueError, 'SCOPE'): source.fetch('other')
    def test_off_origin_and_foreign_workspace_continuations_refuse(self):
        for target in ('https://evil.invalid/items', 'https://api.fabric.microsoft.com/v1/workspaces/other/items?x=1'):
            call = Mock(return_value={'status_code': 200, 'text': {'value': [], 'continuationUri': target}})
            with self.assertRaises(ValueError): FabricChanges(self.workspace, [self.item], call).list_changes()
            self.assertEqual(call.call_count, 1)
    def test_schema_reader_requires_existing_attested_control(self):
        source = SqlSchemaChanges('sql', {'object': {}}, lambda _: ([], {}), Mock())
        with self.assertRaisesRegex(ValueError, 'ATTESTATION'): source.list_changes()
    def test_schema_equality_without_modify_date_does_not_hide_sql_logic_changes(self):
        source = SqlSchemaChanges('sql', {'object': {}}, lambda _: ([], {'kind': 'NATIVE_TARGET_CATALOG'}), Mock())
        self.assertIsNone(source.list_changes()['items'][0]['fingerprint'])


class ScheduleTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.state=SharedState.offline(Path(self.temp.name)/'budget.sqlite');self.state.migrate()
        self.retained={'policy':{'environment':'estate','daily_limits':{'planner_calls':20,'cloud_calls':2,
            'input_characters':100000,'output_tokens':30000},'max_inflight_planners':1,'no_progress_limit':2},
            'round_policy':{'id':'ROUND_TEST','physical_requests':3,'restoration_reserved':1,'starts_at_epoch':0}}
        self.state.put('usage_policy','estate',self.retained)
        self.budget={'environment':'estate','policy_sha256':sha(self.retained),'round_id':'ROUND_TEST','rolling_limit':2}
    def meter(self,limit):
        value=Meter(self.state,self.budget,limit,clock=lambda:1000)
        self.addCleanup(value.close);return value
    def test_meter_counts_failures_and_keeps_existing_accounts(self):
        meter=self.meter(1)
        with self.assertRaises(RuntimeError): meter(lambda: (_ for _ in ()).throw(RuntimeError('403')))
        self.assertEqual(meter.used, 1)
        self.assertEqual(meter.usage.snapshot()['read_allowance']['ordinary_charged'],1)
        with self.assertRaisesRegex(ValueError, 'CAP'): meter(lambda: None)
        with self.state.transaction() as db:
            self.assertEqual(db.execute('SELECT count(*) FROM state_accounts').fetchone()[0],0)
            self.assertEqual(db.execute('SELECT status FROM state_usage').fetchone()[0],'UNCERTAIN')
        self.assertEqual(self.state.get('usage_policy','estate')['body'],self.retained)
    def test_round_reserve_and_rolling_share_existing_admission_atomically(self):
        from investigator.usage_governance import UsageHold
        first=self.meter(5);first(lambda:None);second=self.meter(5);second(lambda:None)
        call=Mock()
        with self.assertRaisesRegex(UsageHold,'restoration'):second(call)
        call.assert_not_called()
        self.assertEqual(second.usage.snapshot()['read_allowance']['ordinary_charged'],2)
    def test_wrong_existing_policy_pin_refuses_without_admission(self):
        self.budget['policy_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'PIN_DIFFERS'):self.meter(2)
        with self.state.transaction() as db:self.assertEqual(db.execute('SELECT count(*) FROM state_usage').fetchone()[0],0)
    def test_owner_approval_required_before_scheduling(self):
        config = dict.fromkeys(('estate', 'workspace', 'owners', 'authentication', 'storage', 'definition_uri_prefix', 'budget', 'max_requests', 'approval'))
        with self.assertRaisesRegex(ValueError, 'APPROVAL'): validate(config)


if __name__ == '__main__': unittest.main()
