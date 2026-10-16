"""Independent tickets and unplanned rendering cases retain separate contracts."""
import hashlib,json,unittest
from pathlib import Path

class BillingSealTests(unittest.TestCase):
    def test_sealed_nine_answers_still_bind_unchanged_independent_ticket_bytes(self):
        root=Path(__file__).resolve().parents[1]
        base=root/'acceptance/billing'
        seal=json.loads((base/'independent-expectations-seal.json').read_text())
        raw=(base/seal['file']).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),seal['sha256'])
        cases=json.loads(raw)['cases']
        self.assertEqual({c['ticket'] for c in cases},{f'ticket-{n:02}.txt' for n in [1,2,3,4,5,6,13,14,15]})
        self.assertFalse(set(seal['excluded_tickets']) & {c['ticket'] for c in cases})
        for case in cases:
            ticket=root/'acceptance/tickets/billing/tester'/case['ticket']
            self.assertEqual(hashlib.sha256(ticket.read_bytes()).hexdigest(),case['ticket_sha256'])

if __name__=='__main__':unittest.main()
