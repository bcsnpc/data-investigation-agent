"""Retention only touches an explicit temporary root; historical fixture default keeps all."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from investigator import retention


class RetentionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name); self.tapes = self.root / 'tapes'; self.tapes.mkdir()
        self.ledger = self.root / 'ledger.jsonl'; self.audit = self.root / 'retention.jsonl'
        self.lines = b'{"at":"2020-01-01T00:00:00Z","status":"FAILED"}\n{"status":"UNDATED"}\n'
        self.ledger.write_bytes(self.lines)

    def plan(self, policy):
        return retention.plan(policy, root=self.root, tapes=self.tapes,
                              ledger=self.ledger, now=1800000000)

    def test_default_keeps_failed_and_undated_evidence(self):
        p = self.plan(retention.DEFAULT)
        self.assertEqual(p['delete_files'], []); self.assertEqual(p['expired_ledger_rows'], [])
        self.assertEqual(b''.join(p['keep_ledger_lines']), self.lines)
        self.assertFalse(self.audit.exists())

    def test_explicit_ledger_expiry_records_original_hash(self):
        p = self.plan({'tape_days': 'indefinite', 'ledger_days': 30})
        retention.apply(p, root=self.root, audit=self.audit)
        self.assertEqual(self.ledger.read_bytes(), self.lines.splitlines(keepends=True)[1])
        rows = [json.loads(x) for x in self.audit.read_text().splitlines()]
        self.assertEqual(rows[1]['status'], 'LEDGER_EXPIRED')
        self.assertEqual(rows[1]['rows'][0]['sha256'], hashlib.sha256(self.lines.splitlines(keepends=True)[0]).hexdigest())

    def test_changed_ledger_refuses_before_deletion_audit(self):
        p = self.plan({'tape_days': 'indefinite', 'ledger_days': 30})
        self.ledger.write_bytes(self.lines + b'{}\n')
        with self.assertRaisesRegex(ValueError, 'Ledger changed'): retention.apply(p, root=self.root, audit=self.audit)
        self.assertFalse(self.audit.exists())

    def test_outside_root_and_bad_period_refuse(self):
        with self.assertRaisesRegex(ValueError, 'strictly inside'): retention.owned(self.root.parent / 'other', self.root)
        with self.assertRaises(Exception): self.plan({'tape_days': 0, 'ledger_days': 'indefinite'})

    def test_expired_tape_and_sidecars_deleted_with_individual_audit(self):
        folder = self.tapes / 'run'; folder.mkdir()
        files = [folder / name for name in ('tape.json', 'tape.events.jsonl', 'catalog.sqlite')]
        for file in files: file.write_bytes(b'fixture')
        fake = SimpleNamespace(events=[{'kind':'FINAL', 'at':1}])
        with patch('investigator.process_tape.Tape', return_value=fake):
            p = self.plan({'tape_days':30, 'ledger_days':'indefinite'})
        self.assertEqual(len(p['delete_files']), 3)
        retention.apply(p, root=self.root, audit=self.audit)
        self.assertTrue(all(not file.exists() for file in files))
        self.assertEqual(self.ledger.read_bytes(), self.lines)
        rows = [json.loads(x) for x in self.audit.read_text().splitlines()]
        self.assertEqual(sum(r['status']=='DELETED' for r in rows), 3)

    def test_unknown_sidecar_keeps_entire_tape(self):
        folder = self.tapes / 'run'; folder.mkdir()
        (folder / 'tape.json').write_bytes(b'fixture')
        (folder / 'unfamiliar').write_bytes(b'keep')
        fake = SimpleNamespace(events=[{'kind':'FINAL', 'at':1}])
        with patch('investigator.process_tape.Tape', return_value=fake):
            p = self.plan({'tape_days':30, 'ledger_days':'indefinite'})
        self.assertEqual(p['delete_files'], [])
        self.assertIn('Unfamiliar', p['kept'][0]['reason'])

    def test_manifest_accepts_closed_retention_without_mutating_legacy(self):
        from investigator.estate_manifest import validate
        fixture = Path(__file__).resolve().parents[1] / 'infra/estates/fixture.json'
        old = json.loads(fixture.read_text()); self.assertNotIn('retention', old)
        current = dict(old, retention={'tape_days':'indefinite', 'ledger_days':'indefinite'})
        validate(current)
        current['retention']['unexpected'] = 1
        with self.assertRaisesRegex(ValueError, 'retention'): validate(current)


if __name__ == '__main__': unittest.main()
