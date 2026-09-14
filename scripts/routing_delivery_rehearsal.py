"""Local-only delivery rehearsal. No network adapters or external delivery entry point."""
from contextlib import closing
import json
from routing_drafts import digest, prepare
from ticket_workflow import Conflict


class DeliveryRehearsal:
    def __init__(self, review):
        self.review = review
        self.store = review.store
        with closing(self.store.connect()) as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS routing_rehearsals(
                    draft_id TEXT PRIMARY KEY, draft_hash TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS routing_rehearsal_steps(
                    draft_id TEXT, stage TEXT, state TEXT NOT NULL,
                    operation_key TEXT UNIQUE NOT NULL, payload TEXT NOT NULL,
                    PRIMARY KEY(draft_id, stage));
                CREATE TABLE IF NOT EXISTS routing_rehearsal_receipts(
                    operation_key TEXT PRIMARY KEY, payload_hash TEXT NOT NULL,
                    receipt TEXT NOT NULL);
            ''')

    def _validated(self, identity):
        detail = self.review.detail(identity)
        approval = detail['approval']
        if not approval or approval['draft_hash'] != detail['draft_hash']:
            raise Conflict('Current draft approval required')
        item = self.review.evidence.get(detail['record']['investigation_id'])
        if item is None:
            raise Conflict('Evidence missing')
        current = prepare(item, self.review.policy_loader())
        if current['status'] != 'DRAFT_REQUIRES_REVIEW' or dict(current, id=None) != dict(detail['record'], id=None):
            raise Conflict('Evidence or ownership changed')
        return detail

    def enqueue(self, identity):
        detail = self._validated(identity)
        with closing(self.store.connect()) as db:
            db.execute('BEGIN IMMEDIATE')
            db.execute('INSERT OR IGNORE INTO routing_rehearsals VALUES(?,?)', (identity, detail['draft_hash']))
            for stage in ('issue', 'notification'):
                key = digest(['local-rehearsal-v1', identity, detail['draft_hash'], stage])
                payload = {'mode': 'LOCAL_REHEARSAL', 'draft': detail['record']['draft'], 'stage': stage}
                db.execute('INSERT OR IGNORE INTO routing_rehearsal_steps VALUES(?,?,?,?,?)',
                           (identity, stage, 'PENDING', key, json.dumps(payload, sort_keys=True)))
            db.commit()
        return self.status(identity)

    def status(self, identity):
        with closing(self.store.connect()) as db:
            rows = db.execute('SELECT stage,state,operation_key FROM routing_rehearsal_steps WHERE draft_id=? ORDER BY stage', (identity,)).fetchall()
        if not rows:
            raise KeyError('Unknown rehearsal')
        return {'mode': 'LOCAL_REHEARSAL', 'external_delivery': False,
                'complete': all(row[1] == 'SUCCEEDED' for row in rows),
                'steps': [dict(zip(('stage', 'state', 'operation_key'), row)) for row in rows]}

    def advance(self, identity, *, interrupt_after_receipt=False):
        """Run at most one local stage. An interrupted stage is held for reconciliation."""
        detail = self._validated(identity)
        with closing(self.store.connect()) as db:
            db.execute('BEGIN IMMEDIATE')
            run = db.execute('SELECT draft_hash FROM routing_rehearsals WHERE draft_id=?', (identity,)).fetchone()
            if run is None or run[0] != detail['draft_hash']:
                raise Conflict('Approved rehearsal missing or changed')
            rows = db.execute('SELECT stage,state,operation_key,payload FROM routing_rehearsal_steps WHERE draft_id=? ORDER BY stage', (identity,)).fetchall()
            pending = next((row for row in rows if row[1] != 'SUCCEEDED'), None)
            if pending is None:
                return self.status(identity)
            stage, state, key, raw = pending
            if state != 'PENDING':
                raise Conflict('Uncertain operation requires receipt reconciliation; no automatic replay')
            payload = json.loads(raw)
            if stage == 'notification':
                issue_key = rows[0][2]
                receipt = db.execute('SELECT receipt FROM routing_rehearsal_receipts WHERE operation_key=?', (issue_key,)).fetchone()
                if receipt is None:
                    raise Conflict('Issue receipt missing')
                payload['issue_reference'] = json.loads(receipt[0])
                raw = json.dumps(payload, sort_keys=True)
            db.execute('UPDATE routing_rehearsal_steps SET state=?,payload=? WHERE draft_id=? AND stage=?', ('UNCERTAIN', raw, identity, stage))
            db.commit()
        # Separate commit models a provider accepting an operation before the worker saves success.
        receipt = {'mode': 'LOCAL_REHEARSAL', 'reference': 'local-rehearsal:' + key, 'stage': stage}
        with closing(self.store.connect()) as db:
            db.execute('INSERT INTO routing_rehearsal_receipts VALUES(?,?,?)', (key, digest(payload), json.dumps(receipt)))
            db.commit()
        if interrupt_after_receipt:
            return self.status(identity)
        return self.reconcile(identity)

    def reconcile(self, identity):
        """Resolve only a matching durable local receipt. Never retry an absent receipt."""
        self._validated(identity)
        with closing(self.store.connect()) as db:
            db.execute('BEGIN IMMEDIATE')
            rows = db.execute('SELECT stage,operation_key,payload FROM routing_rehearsal_steps WHERE draft_id=? AND state=?', (identity, 'UNCERTAIN')).fetchall()
            for stage, key, raw in rows:
                receipt = db.execute('SELECT payload_hash FROM routing_rehearsal_receipts WHERE operation_key=?', (key,)).fetchone()
                if receipt is None or receipt[0] != digest(json.loads(raw)):
                    raise Conflict('Matching receipt unavailable; operation remains held')
                db.execute('UPDATE routing_rehearsal_steps SET state=? WHERE draft_id=? AND stage=?', ('SUCCEEDED', identity, stage))
            db.commit()
        return self.status(identity)

if __name__ == '__main__':
    import argparse
    from pathlib import Path
    from investigation_evidence_api import EvidenceStore
    from routing_review import RoutingReview
    from ticket_workflow import TicketStore
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('enqueue', 'advance', 'status', 'reconcile'))
    parser.add_argument('--draft-id', required=True)
    parser.add_argument('--workflow', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--ownership', type=Path, required=True)
    parser.add_argument('--interrupt-after-receipt', action='store_true')
    args = parser.parse_args()
    if args.interrupt_after_receipt and args.action != 'advance':
        parser.error('Interruption simulation applies only to advance')
    if not all(path.is_file() for path in (args.workflow, args.evidence, args.ownership)):
        parser.error('Existing workflow, evidence and ownership files are required')
    review = RoutingReview(TicketStore(args.workflow), EvidenceStore(args.evidence),
                           lambda: json.loads(args.ownership.read_text()))
    rehearsal = DeliveryRehearsal(review)
    try:
        if args.action == 'advance':
            result = rehearsal.advance(args.draft_id, interrupt_after_receipt=args.interrupt_after_receipt)
        else:
            result = getattr(rehearsal, args.action)(args.draft_id)
        print(json.dumps(result, indent=2))
    except (Conflict, KeyError, ValueError) as error:
        parser.exit(1, str(error) + '\n')
