"""Durable local envelope review and opt-in adapter coordination."""
from contextlib import closing
import json
import time
from routing_drafts import digest
from ticket_workflow import Conflict


class EnvelopeWorkflow:
    def __init__(self, email, *, delivery_enabled=False):
        self.email = email
        self.store = email.review.store
        self.delivery_enabled = delivery_enabled is True
        with closing(self.store.connect()) as db:
            db.execute('''CREATE TABLE IF NOT EXISTS reviewed_envelopes(
                envelope_hash TEXT PRIMARY KEY, draft_id TEXT NOT NULL,
                preview TEXT NOT NULL, approved_at REAL, reviewer TEXT)'''); db.commit()

    def prepare(self, identity, *, authorized_hash, sender):
        preview = self.email.preview(identity, authorized_hash=authorized_hash, sender=sender)
        with closing(self.store.connect()) as db:
            db.execute('INSERT OR IGNORE INTO reviewed_envelopes VALUES(?,?,?,NULL,NULL)',
                       (preview['envelope_hash'], identity, json.dumps(preview))); db.commit()
        return self.detail(preview['envelope_hash'])

    def detail(self, envelope_hash):
        with closing(self.store.connect()) as db:
            row = db.execute('SELECT draft_id,preview,approved_at,reviewer FROM reviewed_envelopes WHERE envelope_hash=?', (envelope_hash,)).fetchone()
            if row is None: raise KeyError('Unknown envelope')
            attempt = db.execute('SELECT envelope_hash,state,receipt FROM email_delivery_attempts WHERE draft_id=?', (row[0],)).fetchone()
        preview = json.loads(row[1])
        if preview['envelope_hash'] != envelope_hash or digest(preview['envelope']) != envelope_hash:
            raise Conflict('Stored envelope changed')
        return {'draft_id': row[0], 'preview': preview,
                'approval': None if row[2] is None else {'at': row[2], 'reviewer': row[3]},
                'attempt': None if not attempt else {'envelope_hash': attempt[0], 'state': attempt[1],
                            'receipt': None if attempt[2] is None else json.loads(attempt[2])},
                'delivery_enabled': self.delivery_enabled, 'delivery_confirmed': False}

    def _current(self, envelope_hash):
        detail = self.detail(envelope_hash)
        envelope = detail['preview']['envelope']
        current = self.email.preview(detail['draft_id'], authorized_hash=envelope['draft_hash'], sender=envelope['sender'])
        if current != detail['preview']: raise Conflict('Envelope or issue receipt changed; prepare a new review')
        return detail

    def approve(self, envelope_hash, *, confirm=False):
        if confirm is not True: raise Conflict('Explicit envelope review confirmation required')
        self._current(envelope_hash)
        with closing(self.store.connect()) as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT preview FROM reviewed_envelopes WHERE envelope_hash=?', (envelope_hash,)).fetchone()
            if row is None or digest(json.loads(row[0])['envelope']) != envelope_hash:
                raise Conflict('Stored envelope changed')
            db.execute('UPDATE reviewed_envelopes SET approved_at=?,reviewer=? WHERE envelope_hash=? AND approved_at IS NULL',
                       (time.time(), 'local-envelope-operator', envelope_hash)); db.commit()
        return self.detail(envelope_hash)

    def execute(self, envelope_hash):
        if not self.delivery_enabled: raise Conflict('Delivery disabled')
        detail = self._current(envelope_hash)
        if not detail['approval']: raise Conflict('Saved envelope approval required')
        envelope = detail['preview']['envelope']
        self.email.send(detail['draft_id'], authorized_hash=envelope['draft_hash'], sender=envelope['sender'],
                        authorized_envelope_hash=envelope_hash)
        return self.detail(envelope_hash)


if __name__ == '__main__':
    import argparse
    from pathlib import Path
    from email_delivery_adapter import EmailAdapter
    from routing_review import RoutingReview
    from investigation_evidence_api import EvidenceStore
    from ticket_workflow import TicketStore
    parser = argparse.ArgumentParser(description='Local envelope preview/approval only; no send command')
    parser.add_argument('action', choices=('prepare', 'approve', 'status'))
    parser.add_argument('--workflow', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--ownership', type=Path, required=True)
    parser.add_argument('--draft-id'); parser.add_argument('--draft-hash'); parser.add_argument('--sender')
    parser.add_argument('--envelope-hash'); parser.add_argument('--confirm', action='store_true')
    args = parser.parse_args()
    if not all(p.is_file() for p in (args.workflow, args.evidence, args.ownership)):
        parser.error('Existing workflow, evidence and ownership files required')
    if args.action == 'prepare' and not all((args.draft_id, args.draft_hash, args.sender)):
        parser.error('prepare requires draft-id, draft-hash and sender')
    if args.action != 'prepare' and not args.envelope_hash: parser.error('envelope-hash required')
    review = RoutingReview(TicketStore(args.workflow), EvidenceStore(args.evidence), lambda: json.loads(args.ownership.read_text()))
    workflow = EnvelopeWorkflow(EmailAdapter(review, None))
    try:
        if args.action == 'prepare': result = workflow.prepare(args.draft_id, authorized_hash=args.draft_hash, sender=args.sender)
        elif args.action == 'approve': result = workflow.approve(args.envelope_hash, confirm=args.confirm)
        else: result = workflow.detail(args.envelope_hash)
        print(json.dumps(result, indent=2))
    except (Conflict, KeyError, ValueError) as error:
        parser.exit(1, str(error) + '\n')
