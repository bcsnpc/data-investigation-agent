from unittest.mock import Mock
import hashlib
import unittest
from investigator.guided_runtime_reads import SubjectHistory
from investigator.grounded_answers import finding
from test_round23_answers_native import case


class StaleSettingTests(unittest.TestCase):
    def test_schedule_disabled_does_not_report_automatic_updates_off(self):
        def http(path, **kwargs):
            if path.endswith('refreshSchedule'):
                return {'status_code': 200, 'text': {'enabled': False, 'days': [], 'times': [], 'localTimeZoneId': 'UTC'}}
            return {'status_code': 200, 'text': {'value': [{'requestId': 'run', 'status': 'Completed',
                    'startTime': '2026-11-01T00:00:00Z', 'endTime': '2026-11-01T00:01:00Z'}]}}
        reader = SubjectHistory(subjects={'model': {'kind': 'MODEL', 'workspace': '11111111-1111-1111-1111-111111111111',
                    'item': '22222222-2222-2222-2222-222222222222'}}, allowed=['model'], http=http,
                    retain=lambda b: {'sha256': hashlib.sha256(b).hexdigest()}, now=lambda: '2026-11-01T01:00:00Z')
        result = reader('model', {'REFRESH_RUN', 'SCHEDULE'})
        self.assertEqual(result['automatic_updates']['status'], 'UNAVAILABLE_FROM_THIS_SURFACE')
        self.assertNotIn('enabled', result['automatic_updates'])

    def test_unreadable_setting_cannot_be_invented_as_cause(self):
        value = case()
        args = {'verdict': 'refresh stale', 'cause': 'Automatic updates are disabled.',
                'numbers': [7], 'checked': ['gold'], 'evidence_ids': ['q']}
        with self.assertRaisesRegex(ValueError, 'SETTING_UNREADABLE'):
            finding(args, value)
        args['cause'] = 'The retained refresh is older than the newer data observation.'
        result = finding(args, value)
        self.assertIn('ON/OFF state is unestablished', result['business'])
