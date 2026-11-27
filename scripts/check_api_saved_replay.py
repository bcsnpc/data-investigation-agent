"""Exercise the loopback API using an explicitly supplied saved delivery; no live fallback."""
import argparse
import hashlib
import json
from pathlib import Path
import secrets
from threading import Thread
from urllib.request import Request, urlopen
from wsgiref.simple_server import make_server, WSGIRequestHandler
from investigator.estate_config import load
from investigator.investigation_api import ReplayEngine, Service, TokenAuth, create_app


class Quiet(WSGIRequestHandler):
    def log_message(self, *args): pass


def check(estate, saved_outcome, private_root):
    config = load(estate)
    raw = Path(saved_outcome).read_bytes()
    saved = json.loads(raw)
    saved = saved['result'] if 'result' in saved else saved
    ticket = saved['ticket']
    submitted = {'text': ticket['description'], 'estate_id': config['id'], 'requester': 'offline-reviewer'}
    for key in ('report', 'page', 'visual'):
        if ticket.get(key): submitted[key] = ticket[key]
    # Retain delivered fields exactly. Do not expose the model's private transcript.
    delivery = {'status': saved['status'], 'verdict': saved.get('conclusion'),
        'explanation': saved.get('business', saved.get('outputs', {}).get('business', '')),
        'evidence_summary': [{'id': row['id'], 'layer': row.get('layer'), 'status': row.get('status')}
                             for row in saved.get('case', {}).get('queries', [])],
        'handoff': saved.get('technical', saved.get('outputs', {}).get('technical', ''))}
    engine = ReplayEngine([{'request': submitted, 'result': delivery}])
    service = Service(root=private_root, engine=engine, estates={config['id']: config})
    token = secrets.token_urlsafe(48)
    auth = TokenAuth(token, principal='offline-reviewer', estates=[config['id']])
    server = make_server('127.0.0.1', 0, lambda *a: [], handler_class=Quiet)
    server.set_app(create_app(service, auth, port=server.server_port))
    thread = Thread(target=server.serve_forever, daemon=True); thread.start()
    try:
        base = 'http://127.0.0.1:' + str(server.server_port)
        headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
        def call(path, data=None):
            with urlopen(Request(base + path, headers=headers, data=data), timeout=10) as response:
                return response.status, json.load(response)
        assert call('/v1/health')[1]['live_enabled'] is False
        status, admitted = call('/v1/investigations', json.dumps(submitted).encode())
        assert status == 202
        assert call(admitted['status_url'])[1]['status'] == 'COMPLETED'
        actual = call(admitted['status_url'] + '/result')[1]
        assert actual == delivery
        events = [json.loads(line) for line in (Path(private_root)/'audit.jsonl').read_text().splitlines()]
        assert len(events) == 4
        assert all(token not in path.read_text() for path in Path(private_root).glob('*') if path.is_file())
        return {'scope': 'LOCAL_HTTP_SAVED_DELIVERY_REPLAY', 'status': 'PASS', 'http_requests': 4,
            'saved_outcome_sha256': hashlib.sha256(raw).hexdigest(), 'estate_id': config['id'],
            'delivery_sha256': hashlib.sha256(json.dumps(delivery, sort_keys=True).encode()).hexdigest(),
            'returned_saved_delivery_unchanged': True, 'case_status': 'COMPLETED',
            'requester_passed_through': True, 'audit_events': len(events), 'estate_reads': 0, 'model_calls': 0}
    finally:
        server.shutdown(); server.server_close(); thread.join(10)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--estate', required=True, type=Path)
    parser.add_argument('--saved-outcome', required=True, type=Path)
    parser.add_argument('--private-root', required=True, type=Path)
    parser.add_argument('--report', required=True, type=Path)
    args = parser.parse_args()
    if args.private_root.exists(): raise ValueError('USE_A_NEW_PRIVATE_REPLAY_DIRECTORY')
    result = check(args.estate, args.saved_outcome, args.private_root)
    args.report.write_text(json.dumps(result, indent=2)+'\n', encoding='utf8')
    print(json.dumps(result))


if __name__ == '__main__': main()
