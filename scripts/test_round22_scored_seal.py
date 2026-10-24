"""The scored questions and independent expectations cannot drift silently."""
import hashlib
import json
from pathlib import Path
import unittest


class ScoredSeal(unittest.TestCase):
    def test_both_splits_and_every_evidence_reference_match_the_pre_run_seal(self):
        root = Path(__file__).resolve().parents[1]
        path = root / 'docs/runs/round-twenty-two-scored-set-seal.json'
        record = json.loads(path.read_bytes())
        from investigator.process_tape import bytes_of
        body = {k: v for k, v in record.items() if k != 'seal'}
        self.assertEqual(hashlib.sha256(bytes_of(body)).hexdigest(), record['seal'])
        self.assertFalse(record['engine_scores_available_at_seal'])
        verdicts = {'as designed', 'not found', 'failed job', 'access difference',
                    'different question', 'latency', 'source changed history',
                    'refresh stale', 'waiting on job'}
        for split, count in [('dev', 40), ('heldout', 20)]:
            files = []
            for suffix in ('', '-expected'):
                relative = 'tests/tickets/scored-set-v1-' + split + suffix + '.json'
                pin = record['outputs'][relative.replace('/', '\\')]
                raw = (root / relative).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), pin['sha256'])
                files.append(json.loads(raw))
            tickets, expected = files[0]['tickets'], files[1]['records']
            self.assertEqual(len(tickets), count)
            self.assertEqual([t['id'] for t in tickets], [e['id'] for e in expected])
            self.assertEqual({e['expected']['verdict'] for e in expected}, verdicts)
            for ticket, expectation in zip(tickets, expected):
                self.assertNotIn('expected', ticket)
                self.assertNotIn('request', ticket)  # Runtime resolves the original raw text.
                self.assertEqual(hashlib.sha256(ticket['text'].encode()).hexdigest(), ticket['text_sha256'])
                self.assertEqual(ticket['text_sha256'], expectation['text_sha256'])
                if expectation['expected']['verdict'] == 'latency':
                    self.assertEqual(expectation['fixture_admission'], 'LIVE_LATENCY')
                for ref in expectation['evidence']:
                    self.assertEqual(hashlib.sha256((root / ref['path']).read_bytes()).hexdigest(), ref['sha256'])


if __name__ == '__main__': unittest.main()
