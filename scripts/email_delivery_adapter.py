"""SMTP-injected notification adapter; no live connection or automatic invocation."""
from contextlib import closing
from email.message import EmailMessage
import json
from github_issue_adapter import GithubIssueAdapter
from routing_destination import validate_destination
from routing_drafts import digest
from ticket_workflow import Conflict


class EmailAdapter:
    def __init__(self, review, smtp):
        self.review, self.smtp = review, smtp
        self.github = GithubIssueAdapter(review, None)
        with closing(review.store.connect()) as db:
            db.execute('''CREATE TABLE IF NOT EXISTS email_delivery_attempts(
                draft_id TEXT PRIMARY KEY, envelope_hash TEXT UNIQUE NOT NULL,
                state TEXT NOT NULL, receipt TEXT)'''); db.commit()

    def preview(self, identity, *, authorized_hash, sender):
        issue = self.github._request(identity, authorized_hash)
        detail = self.review.detail(identity)
        notification = detail['record']['draft']['destination_preview']['notification']
        validation = {'issue': {'provider': 'github', 'repository': issue['repository']},
                      'notification': {'provider': 'email', 'recipients': [sender]}}
        validate_destination(validation)
        with closing(self.review.store.connect()) as db:
            row = db.execute('SELECT approved_hash,state,receipt FROM github_issue_attempts WHERE draft_id=?', (identity,)).fetchone()
        if not row or row[0] != authorized_hash or row[1] != 'SUCCEEDED':
            raise Conflict('Confirmed issue receipt required before email')
        receipt = json.loads(row[2])
        if receipt.get('repository') != issue['repository']:
            raise Conflict('Issue receipt destination mismatch')
        envelope = {'sender': sender, 'recipients': list(notification['recipients']),
                    'subject': notification['subject'], 'body': notification['body'],
                    'draft_hash': authorized_hash, 'issue_receipt': receipt}
        key = digest(envelope)
        envelope['message_id'] = '<investigator-' + key + '@' + sender.split('@')[1] + '>'
        return {'envelope': envelope, 'envelope_hash': digest(envelope), 'delivery_confirmed': False}

    def send(self, identity, *, authorized_hash, sender, authorized_envelope_hash):
        preview = self.preview(identity, authorized_hash=authorized_hash, sender=sender)
        if preview['envelope_hash'] != authorized_envelope_hash:
            raise Conflict('Explicit authorization for this exact sender and envelope required')
        envelope = preview['envelope']
        message = EmailMessage()
        message['From'] = sender; message['To'] = ', '.join(envelope['recipients'])
        message['Subject'] = envelope['subject']; message['Message-ID'] = envelope['message_id']
        message.set_content(envelope['body'])
        with closing(self.review.store.connect()) as db:
            db.execute('BEGIN IMMEDIATE')
            old = db.execute('SELECT envelope_hash,state,receipt FROM email_delivery_attempts WHERE draft_id=? OR envelope_hash=?', (identity, authorized_envelope_hash)).fetchone()
            if old:
                if old[0] == authorized_envelope_hash and old[1] == 'ACCEPTED': return json.loads(old[2])
                raise Conflict('Prior email attempt held; no automatic resend')
            db.execute('INSERT INTO email_delivery_attempts VALUES(?,?,?,NULL)', (identity, authorized_envelope_hash, 'UNCERTAIN')); db.commit()
        try:
            refused = self.smtp.send_message(message, from_addr=sender, to_addrs=list(envelope['recipients']))
        except Exception:
            raise Conflict('SMTP outcome unavailable; attempt remains held') from None
        if not isinstance(refused, dict) or any(address not in envelope['recipients'] for address in refused):
            raise Conflict('Invalid SMTP result; attempt remains held')
        accepted = [address for address in envelope['recipients'] if address not in refused]
        state = 'ACCEPTED' if not refused else 'PARTIAL' if accepted else 'REFUSED'
        receipt = {'state': state, 'message_id': envelope['message_id'], 'accepted_recipients': accepted,
                   'refused_recipients': list(refused), 'delivery_confirmed': False}
        with closing(self.review.store.connect()) as db:
            db.execute('UPDATE email_delivery_attempts SET state=?,receipt=? WHERE draft_id=?', (state, json.dumps(receipt), identity)); db.commit()
        return receipt
