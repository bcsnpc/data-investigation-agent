import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock
from cloud_offline_worker import TEST_MODULES, partition, replay, sealed_file
from build_cloud_image_context import admitted


class CloudOfflineWorkerTests(unittest.TestCase):
    def test_non_root_worker_has_explicit_writable_job_directories(self):
        dockerfile=(Path(__file__).parents[1]/'infra/cloud-worker/Dockerfile').read_text()
        self.assertIn('mkdir /results /work /inputs',dockerfile)
        self.assertIn('chown dia:dia /results /work /inputs',dockerfile)
        self.assertIn('USER 10001:10001',dockerfile)

    def test_public_build_context_excludes_private_and_untyped_material(self):
        for name in ['.local/tape.json', 'acceptance/answer.json', 'scripts/reader-secret.txt',
                     'scripts/cache.sqlite', '.git/config', 'scripts/__pycache__/x.py', 'docs/receipt.md',
                     'infra/estates/real-installation.json']:
            self.assertFalse(admitted(name), name)
        for name in ['scripts/investigator/live_gateway.py', 'scripts/test_live_gateway.py',
                     'scripts/requirements-cloud-worker.txt', 'infra/scripts/Read-Source.ps1',
                     'acceptance/unknown_domain/recorded_engine.py', 'infra/cloud-worker/Dockerfile']:
            self.assertTrue(admitted(name), name)
        self.assertTrue(admitted('infra/scripts/WorkerResponseBounds.json'))
        self.assertTrue(admitted('acceptance/model_steps/intake-resolution-policy.json'))
        self.assertTrue(admitted('scripts/investigator/windows_ocr.ps1'))
        self.assertTrue(admitted('apps/investigator-workspace/essentials.html'))
        self.assertTrue(admitted('apps/investigator-workspace/essentials.js'))
        self.assertFalse(admitted('apps/investigator-workspace/credentials.json'))
        self.assertFalse(admitted('apps/investigator-workspace/.local/private.js'))

    def test_eight_shards_cover_each_entry_once(self):
        entries = list(range(63))
        buckets = [partition(entries, n, 8) for n in range(8)]
        self.assertEqual(sorted(x for bucket in buckets for x in bucket), entries)
        self.assertGreaterEqual(len(TEST_MODULES), 8)
        self.assertEqual(len(TEST_MODULES), len(set(TEST_MODULES)))
        module_buckets = [partition(TEST_MODULES, n, 8) for n in range(8)]
        self.assertTrue(all(module_buckets))
        self.assertEqual(sorted(x for bucket in module_buckets for x in bucket), sorted(TEST_MODULES))
        self.assertTrue({'test_investigator_frontier.py','test_fixture_failure_scenarios.py','test_operational_run_selection.py','test_operational_intake.py','test_control_meter_reporting.py'}<=set(TEST_MODULES))
        self.assertIn('test_shared_usage_replay.py', TEST_MODULES)
        self.assertTrue({'test_round_twenty_state.py','test_shared_read_transactions.py',
                         'test_build_phase.py','test_scan_budget_reallocation.py'}<=set(TEST_MODULES))
        self.assertIn('test_shared_catalog_capture.py', TEST_MODULES)
        self.assertTrue(admitted('scripts/test_shared_catalog_capture.py'))
        self.assertIn('test_cloud_verification_first_error.py', TEST_MODULES)
        required={'test_streaming_verification_snapshot.py','test_batched_database_audit.py',
                  'test_run_database_audits.py','test_cloud_verification_window.py',
                  'test_cloud_runner_context.py','test_unified_runner.py',
                  'test_runner_graph_schedule.py','test_cloud_verification_capture.py'}
        self.assertTrue(required<=set(TEST_MODULES))
        with self.assertRaises(ValueError): partition(entries, 8, 8)

    def test_hash_and_path_refuse_before_replay(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); (root / 'tape.json').write_bytes(b'original')
            executor = Mock(return_value={'matched': True})
            entry = {'id': 'one', 'tape_path': 'tape.json', 'tape_sha256': '0' * 64, 'engine_revision': 'a' * 40}
            result = replay({'version': 1, 'entries': [entry]}, root, root / 'out', 0, 8, executor)
            self.assertEqual(result['matched'], 0); executor.assert_not_called()
            with self.assertRaises(ValueError): sealed_file(root, '../outside', '0' * 64)
            entry['tape_sha256'] = hashlib.sha256(b'original').hexdigest()
            result = replay({'version': 1, 'entries': [entry]}, root, root / 'out', 0, 8, executor)
            self.assertEqual(result['matched'], 1)
            self.assertEqual((root / 'tape.json').read_bytes(), b'original')

    def test_exception_text_is_not_published_in_summary(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); (root / 'tape').write_bytes(b'tape')
            entry = {'id': 'one', 'tape_path': 'tape', 'tape_sha256': hashlib.sha256(b'tape').hexdigest(), 'engine_revision': 'a' * 40}
            private = []
            result = replay({'version': 1, 'entries': [entry]}, root, root / 'out', 0, 8,
                            Mock(side_effect=ValueError('secret-bearing native failure')), private_failures=private)
            self.assertNotIn('secret-bearing', str(result))
            self.assertEqual(result['rows'][0]['error_type'], 'ValueError')
            self.assertEqual(private, [{'id': 'one', 'error_type': 'ValueError', 'reason': 'secret-bearing native failure'}])
            error=ValueError('masked');error.private_replay_diagnostics=[{'reason':'private first mismatch'}]
            private=[]
            result=replay({'version':1,'entries':[entry]},root,root/'out',0,8,
                          Mock(side_effect=error),private_failures=private)
            self.assertNotIn('private first mismatch',str(result))
            self.assertEqual(private[0]['first_tape_errors'][0]['reason'],'private first mismatch')
            private = []
            result = replay({'version': 1, 'entries': [entry]}, root, root / 'out', 0, 8,
                            Mock(return_value={'matched': False, 'detail': 'private mismatch body'}), private_failures=private)
            self.assertNotIn('private mismatch body', str(result))
            self.assertEqual(private[0]['result']['detail'], 'private mismatch body')


if __name__ == '__main__': unittest.main()
