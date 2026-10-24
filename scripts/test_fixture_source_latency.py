import copy
from pathlib import Path
import tempfile
import unittest
from fixture.apply import LatencySourceScenario
from fixture.source_latency import InvalidLatencyFixture
from fixture.pipeline_schedule import PipelineScheduleScenario
from investigator.investigator_harness import RunHarness, CaseLog
from investigator.live_gateway import validate_sql, _object
import test_fixture_failure_scenarios as fixtures


class LiveLatencyAdmission(unittest.TestCase):
    def setUp(self):
        self.scenario = LatencySourceScenario(fixtures.SourceHistoryPlans().baseline())
        self.value = fixtures.SourceHistoryPlans().added()
        self.source = {'read_only_verified': True, 'surface_report_binding': 'VALUE_QUERY',
                       'rows': [self.value]}
        self.bronze = {'read_only_verified': True, 'surface_report_binding': 'VALUE_QUERY',
                       'rows': [{'matched_rows': '0', 'units': None}]}
        expected = PipelineScheduleScenario.plan(start='2026-10-25T00:00:00Z', now='2026-10-24T00:00:00Z')
        self.owned = {'id': 'owned', 'expected': expected}
        self.schedules = [{'id': 'owned', **copy.deepcopy(expected)}]
        self.calls = []

    def admit(self, ticket=None):
        def source(request):
            self.calls.append('source')
            validate_sql(request['query'], {_object(x) for x in request['read_only_objects']})
            return copy.deepcopy(self.source)
        def bronze(request):
            self.calls.append('bronze')
            validate_sql(request['query'], {_object(x) for x in request['read_only_objects']})
            self.assertEqual(request['max_rows'], 2)
            self.assertNotIn('COALESCE', request['query'])
            return copy.deepcopy(self.bronze)
        def schedule():
            self.calls.append('schedule')
            return copy.deepcopy(self.schedules)
        return self.scenario.admit(source, bronze, schedule, [self.value],
                                   owned_schedule=self.owned, clock=lambda: '2026-10-24T00:00:00Z')

    def test_every_ticket_rechecks_both_sides_and_native_future_schedule(self):
        self.admit(); result = self.admit()
        self.assertEqual(self.calls, ['source', 'bronze', 'schedule'] * 2)
        self.assertEqual(result['observations'][0]['bronze_native']['rows'][0]['units'], None)
        self.assertIn('Fixture admission only', result['scope'])

    def test_loaded_or_changed_data_and_collapsed_blank_invalidate_fixture(self):
        for side, changed in [('source', []), ('source', [{**self.value, 'units': 8}]),
                              ('bronze', [{'matched_rows': '1', 'units': 7}]),
                              ('bronze', [{'matched_rows': '0', 'units': 0}])]:
            with self.subTest(side=side, changed=changed):
                old = copy.deepcopy(getattr(self, side))
                getattr(self, side)['rows'] = changed
                with self.assertRaises(InvalidLatencyFixture): self.admit()
                setattr(self, side, old)

    def test_removed_disabled_changed_or_due_schedule_is_invalid(self):
        original = copy.deepcopy(self.schedules)
        for schedules in [[], [{**original[0], 'enabled': False}],
                          [{**original[0], 'configuration': {**original[0]['configuration'],
                                                           'startDateTime': '2026-10-23T00:00:00Z'}}]]:
            self.schedules = schedules
            with self.assertRaisesRegex(InvalidLatencyFixture, 'SCHEDULE'): self.admit()
        self.schedules = original
        self.owned['expected']['configuration']['startDateTime'] = '2026-10-23T00:00:00Z'
        self.schedules[0]['configuration']['startDateTime'] = '2026-10-23T00:00:00Z'
        with self.assertRaisesRegex(InvalidLatencyFixture, 'NOT_IN_FUTURE'): self.admit()

    def test_unattested_read_is_invalid(self):
        self.bronze['surface_report_binding'] = 'METADATA'
        with self.assertRaisesRegex(InvalidLatencyFixture, 'NOT_ATTESTED'): self.admit()

    def test_invalid_fixture_blocks_before_submit_and_is_not_engine_failure(self):
        calls = self.calls
        class User:
            def submit(self, ticket): calls.append('submit'); return {'run_id': 'one'}
            def poll(self, run): return {'status': 'Succeeded'}
            def outcome(self, run, state): return {'verdict': 'latency'}
        with tempfile.TemporaryDirectory() as directory:
            valid = CaseLog(Path(directory) / 'valid')
            RunHarness(User(), valid, admit=self.admit).run({'id': 'valid'})
            self.assertEqual(calls, ['source', 'bronze', 'schedule', 'submit'])
            events = [x['event'] for x in valid.events]
            self.assertLess(events.index('ADMISSION'), events.index('SUBMIT_ATTEMPT'))
            self.bronze['rows'][0] = {'matched_rows': '1', 'units': 7}
            invalid = CaseLog(Path(directory) / 'invalid')
            with self.assertRaises(InvalidLatencyFixture):
                RunHarness(User(), invalid, admit=self.admit).run({'id': 'invalid'})
            self.assertEqual(calls.count('submit'), 1)
            self.assertEqual(invalid.events[-1]['value']['fixture_status'], 'INVALID_NOT_AN_ENGINE_RESULT')
            self.assertNotIn('SUBMIT_ATTEMPT', [x['event'] for x in invalid.events])
            self.assertNotIn('OUTCOME', [x['event'] for x in invalid.events])


if __name__ == '__main__': unittest.main()
