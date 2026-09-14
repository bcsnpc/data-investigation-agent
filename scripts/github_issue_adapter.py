"""GitHub issue adapter with injected transport. Not wired to automatic delivery."""
from contextlib import closing
import json
import re
from routing_drafts import digest, prepare
from ticket_workflow import Conflict


class GithubIssueAdapter:
    def __init__(self, review, transport):
        """transport(method, relative_path, payload) returns (HTTP status, decoded JSON).

        Caller owns scoped credentials, fixed api.github.com origin, timeouts and no
        automatic POST retries. No network transport is installed by this module.
        """
        self.review, self.transport = review, transport
        with closing(review.store.connect()) as db:
            db.execute('''CREATE TABLE IF NOT EXISTS github_issue_attempts(
                draft_id TEXT PRIMARY KEY, operation_key TEXT UNIQUE NOT NULL, approved_hash TEXT NOT NULL,
                state TEXT NOT NULL, receipt TEXT)'''); db.commit()

    def _request(self, identity, authorized_hash):
        detail = self.review.detail(identity)
        if detail['draft_hash'] != authorized_hash or not detail['approval'] or detail['approval']['draft_hash'] != authorized_hash:
            raise Conflict('Exact approved draft and explicit delivery authorization required')
        record = detail['record']
        item = self.review.evidence.get(record['investigation_id'])
        if item is None or dict(prepare(item, self.review.policy_loader()), id=None) != dict(record, id=None):
            raise Conflict('Evidence, ownership or proposed content changed')
        issue = record.get('draft', {}).get('destination_preview', {}).get('issue')
        if not issue or issue.get('provider') != 'github' or not re.search(r'<!-- investigator-operation:[a-f0-9]{64} -->$', issue['body']):
            raise Conflict('Reviewed GitHub destination and operation marker required')
        return issue

    @staticmethod
    def _receipt(data, issue):
        if not isinstance(data, dict) or 'pull_request' in data or data.get('title') != issue['title'] or data.get('body') != issue['body']:
            raise Conflict('Provider content does not match approved issue')
        number = data.get('number')
        if type(number) is not int or number <= 0 or data.get('html_url') != 'https://github.com/' + issue['repository'] + '/issues/' + str(number):
            raise Conflict('Invalid provider issue reference')
        return {'provider': 'github', 'repository': issue['repository'], 'number': number, 'url': data['html_url']}

    def _call(self, method, path, payload=None):
        try:
            return self.transport(method, path, payload)
        except Exception:
            raise Conflict('Provider outcome unavailable; attempt remains held') from None

    def create_issue(self, identity, *, authorized_hash):
        """Caller must independently authorize external delivery of this exact hash."""
        issue = self._request(identity, authorized_hash)
        with closing(self.review.store.connect()) as db:
            db.execute('BEGIN IMMEDIATE')
            old = db.execute('SELECT approved_hash,state,receipt FROM github_issue_attempts WHERE draft_id=? OR operation_key=?', (identity, digest(issue))).fetchone()
            if old:
                if old[0] == authorized_hash and old[1] == 'SUCCEEDED':
                    return json.loads(old[2])
                raise Conflict('Prior attempt held; reconcile instead of creating again')
            db.execute('INSERT INTO github_issue_attempts VALUES(?,?,?,?,NULL)', (identity, digest(issue), authorized_hash, 'UNCERTAIN')); db.commit()
        status, data = self._call('POST', '/repos/' + issue['repository'] + '/issues', {k: issue[k] for k in ('title', 'body')})
        if status != 201:
            raise Conflict('Creation not confirmed; attempt remains held')
        receipt = self._receipt(data, issue)
        self._finish(identity, authorized_hash, receipt)
        return receipt

    def _finish(self, identity, authorized_hash, receipt):
        self._request(identity, authorized_hash)
        with closing(self.review.store.connect()) as db:
            db.execute('UPDATE github_issue_attempts SET state=?,receipt=? WHERE draft_id=? AND approved_hash=?',
                       ('SUCCEEDED', json.dumps(receipt), identity, authorized_hash)); db.commit()

    def reconcile(self, identity, *, authorized_hash):
        issue = self._request(identity, authorized_hash)
        with closing(self.review.store.connect()) as db:
            old = db.execute('SELECT approved_hash,state,receipt FROM github_issue_attempts WHERE draft_id=?', (identity,)).fetchone()
        if not old or old[0] != authorized_hash:
            raise Conflict('Matching attempt required')
        if old[1] == 'SUCCEEDED': return json.loads(old[2])
        marker = re.search(r'<!-- investigator-operation:[a-f0-9]{64} -->$', issue['body']).group()
        matches = {}
        for page in range(1, 6):
            status, data = self._call('GET', '/repos/' + issue['repository'] + '/issues?state=all&sort=created&direction=desc&per_page=100&page=' + str(page))
            if status != 200 or not isinstance(data, list) or len(data) > 100:
                raise Conflict('Receipt lookup incomplete; attempt remains held')
            for row in data:
                if not isinstance(row, dict): raise Conflict('Malformed receipt page')
                if 'pull_request' not in row and marker in (row.get('body') or ''):
                    receipt = self._receipt(row, issue)
                    matches[receipt['number']] = receipt
            if len(data) < 100:
                if len(matches) != 1: raise Conflict('Unique matching receipt unavailable; attempt remains held')
                receipt = next(iter(matches.values()))
                self._finish(identity, authorized_hash, receipt)
                return receipt
        raise Conflict('Receipt scan limit reached; attempt remains held')
