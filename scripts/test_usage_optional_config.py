"""Planner-only runtime protocol does not require estate configuration."""
import unittest
from unittest.mock import patch
import test_model_transport_retry as fixture
from investigator.build_phase import operating_mode


class OptionalRuntimeConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.fixture=fixture.RetryTests();self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
        self.governor=self.fixture.governor
        del self.fixture.runtime.config
    def test_legacy_planner_reservation_and_snapshot_need_only_budget_runtime(self):
        with patch('investigator.build_phase.active',return_value=False):
            with self.fixture.runtime.db() as db:
                db.execute('BEGIN IMMEDIATE')
                self.governor.reserve(db,'planner-only','request','planner',100,output_tokens=8000)
            snapshot=self.governor.snapshot()
        self.assertEqual(snapshot['active_reservations']['planner_calls'],2)
        self.assertNotIn('monthly',snapshot)
    def test_explicit_build_mode_can_select_monthly_path_without_estate_config(self):
        with operating_mode():
            with self.fixture.runtime.db() as db:
                db.execute('BEGIN IMMEDIATE')
                self.governor.reserve(db,'planner-only','request','planner',100,output_tokens=8000)
            snapshot=self.governor.snapshot()
        self.assertTrue(snapshot['legacy_limits_informational'])
        self.assertEqual(snapshot['monthly']['total_limit'],6000)

    def test_legacy_replay_without_build_declaration_never_inherits_live_build_mode(self):
        from types import SimpleNamespace
        from investigator import process_tape,build_phase
        token=process_tape.ACTIVE.set(SimpleNamespace(replaying=True,version='bounded-worker-tape-v6'))
        try:
            with operating_mode():
                self.assertFalse(build_phase.active())
        finally:
            process_tape.ACTIVE.reset(token)
