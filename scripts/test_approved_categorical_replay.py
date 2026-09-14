from contextlib import closing
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from defect_lab import initialize,mutate
from approved_categorical_replay import ReplayReview
from ticket_workflow import Conflict
from test_categorical_filter_replay import definitions,choices,PAGE

class ApprovedReplayTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        root=Path(self.temp.name);self.lab=root/'lab.duckdb';initialize(self.lab)
        self.service=ReplayReview(root/'review.sqlite')
        self.draft=self.service.prepare(self.lab,definitions(),PAGE,choices(order_id=['ORD-000001']))
    def approve(self):return self.service.approve(self.draft['id'],self.draft['scope_hash'],'fixture-reviewer')
    def run_review(self):return self.service.run(self.draft['id'],self.draft['scope_hash'])
    def test_unapproved_run_is_blocked(self):
        with self.assertRaises(Conflict):self.run_review()
        self.assertEqual(self.service.get(self.draft['id'])['status'],'DRAFT_REQUIRES_REVIEW')
    def test_approved_replay_persists_once(self):
        self.approve();first=self.run_review();second=self.run_review()
        self.assertEqual(first,second)
        self.assertEqual(first['selected_records'],1)
        with closing(self.service.connect()) as db:self.assertEqual(db.execute('SELECT count(*) FROM investigation_runs').fetchone()[0],1)
    def test_wrong_hash_does_not_approve(self):
        with self.assertRaises(Conflict):self.service.approve(self.draft['id'],'wrong','reviewer')
    def test_source_change_blocks_capture_and_retry(self):
        self.approve();mutate(self.lab,'inject-double-refund')
        with self.assertRaises(ValueError):self.run_review()
        self.assertEqual(self.service.get(self.draft['id'])['status'],'UNCERTAIN')
        with self.assertRaises(Conflict):self.run_review()
    def test_stored_scope_change_is_rejected(self):
        with closing(self.service.connect()) as db:
            db.execute("UPDATE categorical_reviews SET scope='{}'");db.commit()
        with self.assertRaises(Conflict):self.approve()
    def test_execution_exception_never_retries(self):
        self.approve()
        with patch('approved_categorical_replay.execute',side_effect=RuntimeError('fixture failure')) as mocked:
            with self.assertRaises(RuntimeError):self.run_review()
            with self.assertRaises(Conflict):self.run_review()
            self.assertEqual(mocked.call_count,1)
