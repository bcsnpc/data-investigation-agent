import unittest
from investigator.history_comparison import disposition


class HistoryComparisonTests(unittest.TestCase):
    def test_native_normalized_job_end_is_an_anchor(self):
        case = self.case()
        native = case['triage']['facts'][0]['value']
        native['end'] = native.pop('end_time')
        self.assertTrue(disposition(case, ['now', 'then'])['ruled_out'])

    def case(self):
        return {'triage': {'facts': [{'kind': 'JOB_RUN', 'state': 'OBSERVED',
                                     'value': {'status': 'Succeeded', 'end_time': '2026-10-01T00:00:00Z'}}]},
                'context': {'system_of_record': {'layer': 'source', 'asset_id': 'table'},
                            'layers': {'source': {'dialect': 'T-SQL'}}}, 'queries': [
            {'id': 'now', 'layer': 'source', 'status': 'SUCCEEDED', 'asset_ids': ['table'],
             'text': 'SELECT SUM(quantity) AS n FROM dbo.Items', 'result': {'rows': [{'n': 10}]}},
            {'id': 'then', 'layer': 'source', 'status': 'SUCCEEDED', 'asset_ids': ['table'],
             'text': "SELECT SUM(quantity) AS n FROM dbo.Items FOR SYSTEM_TIME AS OF '2026-10-01'",
             'result': {'rows': [{'n': 10}]}}]}

    def test_current_and_history_must_be_same_calculation(self):
        case = self.case()
        self.assertTrue(disposition(case, ['now', 'then'])['ruled_out'])
        case['queries'][1]['text'] = "SELECT COUNT(*) AS n FROM dbo.Items FOR SYSTEM_TIME AS OF '2026-10-01'"
        self.assertFalse(disposition(case, ['now', 'then'])['ruled_out'])

    def test_unrelated_snapshot_or_missing_native_load_is_not_exclusion(self):
        case = self.case()
        case['queries'][1]['text'] = "SELECT SUM(quantity) AS n FROM dbo.Items FOR SYSTEM_TIME AS OF '2026-09-01'"
        self.assertFalse(disposition(case, ['now', 'then'])['ruled_out'])
        case['triage'] = {}
        self.assertFalse(disposition(case, ['now', 'then'])['ruled_out'])

    def test_changed_history_missing_history_or_uncited_history_cannot_be_latency(self):
        case = self.case()
        self.assertFalse(disposition(case, ['now'])['ruled_out'])
        case['queries'][1]['result']['rows'][0]['n'] = 9
        self.assertFalse(disposition(case, ['now', 'then'])['ruled_out'])
        case['queries'][1]['text'] = 'SELECT SUM(quantity) AS n FROM dbo.Items'
        self.assertFalse(disposition(case, ['now', 'then'])['ruled_out'])
