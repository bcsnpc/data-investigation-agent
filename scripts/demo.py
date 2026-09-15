"""Repeatable isolated investigator demo using the existing review API and worker."""
import argparse
from io import BytesIO
import json
import os
from pathlib import Path
from uuid import uuid4
from wsgiref.simple_server import make_server

from defect_lab import initialize, mutate, validate
from serve_lab_review import components
from serve_investigations import QuietHandler

POLICY = {'version': 1, 'owners': [{'kind': 'lab_record_reconciliation',
          'upstream': 'silver', 'downstream': 'gold', 'team': 'Demo Data Team (simulated)'}]}


def prepare(folder):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=False)
    initialize(folder / 'lab.duckdb')
    (folder / 'demo.json').write_text(json.dumps({'mode': 'isolated_demo', 'version': 1}))
    return folder


def require_demo(folder):
    folder = Path(folder)
    if json.loads((folder / 'demo.json').read_text()) != {'mode': 'isolated_demo', 'version': 1}:
        raise ValueError('Not a demo folder')
    return folder


def rehearsal(folder):
    folder = prepare(folder)
    token = 'local-rehearsal-only-' + str(uuid4())
    app, worker, store = components(folder / 'review', folder / 'lab.duckdb', token, lambda: POLICY)

    def call(path, body=None):
        raw = json.dumps(body).encode() if body is not None else b''
        statuses = []
        result = b''.join(app({'REQUEST_METHOD': 'GET' if body is None else 'POST',
            'PATH_INFO': path, 'QUERY_STRING': '', 'HTTP_AUTHORIZATION': 'Bearer ' + token,
            'HTTP_IDEMPOTENCY_KEY': str(uuid4()), 'CONTENT_TYPE': 'application/json',
            'CONTENT_LENGTH': str(len(raw)), 'wsgi.input': BytesIO(raw)},
            lambda status, headers: statuses.append(status)))
        if not statuses[0].startswith(('200', '201')):
            raise RuntimeError('Demo API failed: ' + statuses[0])
        return json.loads(result)

    report = {'mode': 'ISOLATED_DEMO', 'external_delivery': False, 'llm_used': False}
    try:
        report['baseline'] = validate(folder / 'lab.duckdb')
        mutate(folder / 'lab.duckdb', 'inject-double-refund')
        parent = call('/api/tickets', {'title': 'Net cash is USD 99 too low', 'report': 'Lab Net Cash',
            'description': 'Compare Silver and Gold net cash in USD. Investigate the discrepancy and explain affected orders.'})['ticket_id']
        draft = call('/api/tickets/' + parent + '/plan', {'confirm': True})['plan_id']
        detail = call('/api/plans/' + draft)
        child = call('/api/plans/' + draft + '/approve', {'confirm': True, 'plan_hash': detail['plan_hash']})['ticket_id']
        worker.start()
        worker.thread.join(30)
        if worker.thread.is_alive():
            raise RuntimeError('Demo worker did not finish')
        ticket = call('/api/tickets/' + child)['ticket']
        if ticket['status'] != 'COMPLETED':
            raise RuntimeError('Demo investigation incomplete')
        run = ticket['investigation_run_id']
        finding = call('/api/investigations/' + run)['investigation']['result']
        if finding['classification'] != 'TECHNICAL_DEFECT' or not finding['root_cause_verified']:
            raise RuntimeError('Expected verified local cause')
        if finding['impact_by_currency']['USD']['downstream_minus_upstream'] != '-99.0000':
            raise RuntimeError('Unexpected demo impact')
        routing = call('/api/investigations/' + run + '/routing', {'confirm': True})
        if routing['record']['status'] != 'DRAFT_REQUIRES_REVIEW':
            raise RuntimeError('Routing draft unavailable')
        report.update(status='PASSED', ticket_id=parent, approved_ticket_id=child,
                      plan_id=draft, investigation_id=run, finding=finding, routing=routing)
    finally:
        worker.stop()
        report['reset'] = mutate(folder / 'lab.duckdb', 'reset')
        (folder / 'rehearsal.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare', 'rehearse', 'inject', 'reset', 'serve'])
    parser.add_argument('--folder', type=Path, required=True)
    parser.add_argument('--port', type=int, default=8772)
    args = parser.parse_args()
    if args.action == 'prepare':
        prepare(args.folder)
        print('READY: isolated baseline created')
    elif args.action == 'rehearse':
        result = rehearsal(args.folder)
        print(result['status'] + ': ticket -> review -> worker -> verified cause -> defect draft -> reset')
    else:
        folder = require_demo(args.folder)
        if args.action in ('inject', 'reset'):
            print(json.dumps(mutate(folder / 'lab.duckdb', 'inject-double-refund' if args.action == 'inject' else 'reset'), default=str))
            return
        if not 1 <= args.port <= 65535:
            parser.error('Invalid port')
        token = os.environ.get('INVESTIGATOR_API_TOKEN', '')
        app, worker, _ = components(folder / 'review', folder / 'lab.duckdb', token, lambda: POLICY)
        with make_server('127.0.0.1', args.port, app, handler_class=QuietHandler) as server:
            worker.start()
            print(f'Isolated demo: http://127.0.0.1:{args.port}; one approved job per server session', flush=True)
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass
            finally:
                worker.stop()


if __name__ == '__main__':
    main()
