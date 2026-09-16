"""Create-only isolated fixture publisher with durable, non-retrying mutations."""
import argparse
import json
from pathlib import Path
import sqlite3
import subprocess
import tempfile
import time
from uuid import UUID

from import_fixture import digest, encoded, query, validate, verify_table


def transport(endpoint, method, body, audience):
    """Private request file and bounded CLI process; never print token/error bodies."""
    root = Path(__file__).resolve().parents[1]
    command = [str(root / '.local/fabric-cli-env/Scripts/fab.exe'), 'api', endpoint,
               '-X', method, '-A', audience, '--show_headers']
    with tempfile.TemporaryDirectory(dir=root / '.local') as folder:
        if body is not None:
            path = Path(folder) / 'request.json'
            path.write_bytes(encoded(body))
            command += ['-i', str(path)]
        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', timeout=105)
    if result.returncode or len(result.stdout) > 4_000_000:
        raise RuntimeError('Fixture transport failed or exceeded response budget')
    return json.loads(result.stdout)


def uid(value):
    return str(UUID(value))


class Journal:
    def __init__(self, path):
        self.db = sqlite3.connect(path, timeout=10)
        self.db.execute('CREATE TABLE IF NOT EXISTS operations (key TEXT PRIMARY KEY, request_hash TEXT NOT NULL, state TEXT NOT NULL, response TEXT)')
        self.db.execute('CREATE TABLE IF NOT EXISTS resolutions (key TEXT PRIMARY KEY, body TEXT NOT NULL, hash TEXT NOT NULL)')
        self.db.commit()

    def mutation(self, key, request, send):
        request_hash = digest(request)
        with self.db:
            existing = self.db.execute('SELECT request_hash,state,response FROM operations WHERE key=?', (key,)).fetchone()
            if existing:
                if existing[0] != request_hash:
                    raise ValueError('Publication request changed')
                if existing[1] != 'RECEIVED':
                    raise RuntimeError('Uncertain publication: inspect remote state; automatic retry disabled')
                return json.loads(existing[2])
            self.db.execute('INSERT INTO operations VALUES (?,?,?,NULL)', (key, request_hash, 'DISPATCHED'))
        # Reservation is committed before network I/O. Exceptions leave DISPATCHED.
        response = send()
        with self.db:
            self.db.execute('UPDATE operations SET state=?,response=? WHERE key=?', ('RECEIVED', encoded(response).decode(), key))
        return response


class Publisher:
    def __init__(self, journal, transport, sleep=time.sleep):
        self.journal, self.transport, self.sleep = journal, transport, sleep
        self.calls = 0

    def call(self, endpoint, method='get', body=None, audience='fabric'):
        if self.calls >= 40:
            raise RuntimeError('Publication invocation call budget exhausted')
        self.calls += 1
        response = self.transport(endpoint, method, body, audience)
        if response.get('status_code') not in (200, 201, 202):
            raise RuntimeError('Publication HTTP request failed')
        return response

    def post(self, key, endpoint, body, audience='fabric'):
        request = {'endpoint': endpoint, 'body': body, 'audience': audience}
        return self.journal.mutation(key, request, lambda: self.call(endpoint, 'post', body, audience))

    def item(self, response):
        if response['status_code'] == 201:
            return response['text']
        key = digest(response)
        saved = self.journal.db.execute('SELECT body,hash FROM resolutions WHERE key=?', (key,)).fetchone()
        if saved:
            body = json.loads(saved[0])
            if digest(body) != saved[1]:
                raise ValueError('Publication resolution integrity mismatch')
            return body
        headers = {k.lower(): v for k, v in response.get('headers', {}).items()}
        operation = uid(headers['x-ms-operation-id'])
        for _ in range(8):
            status = self.call('operations/' + operation)['text']
            if status.get('status') == 'Succeeded':
                body = self.call('operations/' + operation + '/result')['text']
                with self.journal.db:
                    self.journal.db.execute('INSERT OR IGNORE INTO resolutions VALUES (?,?,?)', (key, encoded(body).decode(), digest(body)))
                return body
            if status.get('status') in ('Failed', 'Cancelled'):
                raise RuntimeError('Remote publication failed; inspect operation ' + operation)
            self.sleep(5)
        raise RuntimeError('Publication still pending; rerun resumes polling without another create')

    def publish(self, bundle, capacity):
        bundle = validate(bundle)
        capacity = uid(capacity)
        generation = bundle['bundle_hash']
        # Journal key locks the workspace to one exact bundle/capacity. A new
        # generation uses a new journal and a new workspace, never updates by name.
        ws = self.item(self.post('workspace', 'workspaces', {
            'displayName': 'investigator-fixture-' + generation[:16], 'capacityId': capacity,
            'description': 'Isolated Import fixture ' + generation}))
        workspace = uid(ws['id'])
        observed = self.call('workspaces/' + workspace)['text']
        if observed.get('capacityId', '').lower() != capacity or observed.get('displayName') != ws.get('displayName'):
            raise RuntimeError('Workspace identity or capacity does not match publication')
        model = self.item(self.post('model', 'workspaces/' + workspace + '/semanticModels', {
            'displayName': 'Fixture ' + generation[:16], 'definition': bundle['definition']}))
        model_id = uid(model['id'])
        if model.get('workspaceId', workspace).lower() != workspace:
            raise RuntimeError('Created model belongs to unexpected workspace')
        observed_model = self.call(f'workspaces/{workspace}/semanticModels/{model_id}')['text']
        if observed_model.get('id', '').lower() != model_id or observed_model.get('displayName') != 'Fixture ' + generation[:16]:
            raise RuntimeError('Published model identity no longer matches')
        return {'bundle_hash': generation, 'input_hash': bundle['input_hash'], 'model_hash': bundle['model_hash'],
                'workspace_id': workspace, 'semantic_model_id': model_id,
                'generation_proven': False, 'live_acceptance_ready': False}

    def refresh(self, publication):
        workspace, model = uid(publication['workspace_id']), uid(publication['semantic_model_id'])
        response = self.post('refresh', f'groups/{workspace}/datasets/{model}/refreshes', {'notifyOption': 'NoNotification'}, 'powerbi')
        headers = {k.lower(): v for k, v in response.get('headers', {}).items()}
        location = headers.get('location', '')
        # Never follow a service-provided URL. Extract a UUID from the expected path.
        prefix = f'https://api.powerbi.com/v1.0/myorg/groups/{workspace}/datasets/{model}/refreshes/'
        if location:
            if not location.startswith(prefix):
                raise RuntimeError('Unexpected refresh receipt location')
            refresh_id = uid(location[len(prefix):])
        else:
            refresh_id = uid(headers.get('requestid', ''))
        for _ in range(8):
            history = self.call(f'groups/{workspace}/datasets/{model}/refreshes?$top=5', audience='powerbi')['text']
            matches = [r for r in history.get('value', []) if r.get('requestId') == refresh_id]
            if len(matches) > 1:
                raise RuntimeError('Ambiguous refresh history')
            status = matches[0] if matches else {}
            if status.get('status') == 'Completed':
                return dict(publication, refresh_id=refresh_id, refresh_status='Completed')
            if status.get('status') in ('Failed', 'Cancelled', 'Disabled'):
                raise RuntimeError('Fixture refresh failed')
            self.sleep(5)
        raise RuntimeError('Refresh pending; rerun polls the same refresh')

    def verify(self, bundle, publication):
        bundle = validate(bundle)
        if publication['bundle_hash'] != bundle['bundle_hash'] or publication.get('refresh_status') != 'Completed':
            raise ValueError('Completed publication for this bundle required')
        workspace, model = uid(publication['workspace_id']), uid(publication['semantic_model_id'])
        results = []
        for table in bundle['inputs']:
            response = self.call(f'groups/{workspace}/datasets/{model}/executeQueries', 'post',
                {'queries': [{'query': query(table)}], 'serializerSettings': {'includeNulls': True}}, 'powerbi')
            results.append(verify_table(table, response['text']))
        return dict(publication, tables=results, contents_match=all(r['matches'] for r in results),
                    generation_proven=False, live_acceptance_ready=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', required=True, type=Path)
    parser.add_argument('--journal', required=True, type=Path)
    parser.add_argument('--capacity', required=True)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    publisher = Publisher(Journal(args.journal), transport)
    bundle = json.loads(args.bundle.read_text(encoding='utf-8'))
    result = publisher.publish(bundle, args.capacity)
    args.output.write_bytes(encoded(result))
    if args.verify:
        result = publisher.refresh(result)
        args.output.write_bytes(encoded(result))
        result = publisher.verify(bundle, result)
        args.output.write_bytes(encoded(result))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
