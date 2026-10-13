import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from cloud_verification_capture import Capture, replay
from investigator.runtime import fingerprint
from investigator.shared_state import SharedState
from investigator.shared_usage import export_usage, import_usage
from investigator.usage_governance import UsageGovernor
from read_budget import Catalog


PROGRAM = '''from read_budget import Catalog
from investigator.usage_governance import UsageGovernor, UsageHold
from investigator.process_tape import clock
def perform(b,work,catalog,live):
 runtime=Catalog(catalog,b['state']['environment'])
 g=UsageGovernor(runtime,b['usage_policy'],lambda:clock('verification-budget',lambda:172799.0))
 def read():
  if b['state']['inputs']['fail']:raise ValueError('SYNTHETIC_READ_FAILURE')
  return {'count':7}
 first=g.metered_read(b['state']['inputs']['session_id'],'one',read)
 try:g.metered_read(b['state']['inputs']['session_id'],'two',read)
 except UsageHold as exc:return {'first':first,'refusal':str(exc)}
 raise AssertionError('cap bypassed')
'''


class SharedUsageReplayTests(unittest.TestCase):
    def test_cloud_single_clock_algorithm_replays_success_failure_and_cap(self):
        for fail in (False, True):
            with self.subTest(fail=fail), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                catalog = root / 'catalog.sqlite'
                runtime = Catalog(catalog, 'estate')
                policy = {'environment': 'estate', 'daily_limits': {
                    'planner_calls': 20, 'cloud_calls': 1,
                    'input_characters': 100000, 'output_tokens': 30000},
                    'max_inflight_planners': 1, 'no_progress_limit': 2}
                UsageGovernor(runtime, policy, lambda: 172799.0)
                state = SharedState.offline(root / 'shared.sqlite')
                state.migrate()
                with runtime.db() as db:
                    import_usage(state, 'initial', export_usage(db, 'estate', policy, None))
                program = root / 'program.py'
                program.write_text(PROGRAM)
                capture = Capture(root / 'capture', inputs={'session_id': 'fresh',
                    'fail': fail, 'verification_cap': 40}, config={}, policy=policy,
                    engine_hash=fingerprint(), program=program, files={},
                    databases={'catalog.sqlite': catalog}, environment='estate',
                    context_identity='fixture', shared_usage=True)
                with patch('investigator.shared_state.configured_state', return_value=state), \
                     patch.dict('os.environ', {'INVESTIGATOR_WORKER_ID': 'live-worker'}):
                    final = capture.execute()
                self.assertEqual(final['accounting']['physical_requests'], 1)
                self.assertEqual(final['accounting']['pending_reservations'], 0)
                self.assertEqual(final['status'], 'FAILED' if fail else 'COMPLETED')
                with patch('investigator.shared_state.configured_state',
                           side_effect=AssertionError('offline replay contacted live state')):
                    result = replay(root / 'capture', root / 'replay')
                self.assertTrue(result['matched'])
                self.assertEqual(result['status'], final['status'])
                if not fail:
                    self.assertEqual(result['result']['refusal'], 'Rolling read allowance exhausted')

    def test_replay_marker_cannot_claim_an_existing_session(self):
        from investigator.shared_usage_replay import declaration
        self.assertEqual(declaration('fresh')['version'], 'FRESH_SHARED_USAGE_V1')
        with self.assertRaises(ValueError):
            declaration('')


if __name__ == '__main__':
    unittest.main()
