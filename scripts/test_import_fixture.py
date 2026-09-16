import copy
import json
from pathlib import Path
import tempfile
import unittest

from import_fixture import build, m_literal, query, validate, verify_table
from publish_import_fixture import Journal, Publisher


def spec():
    return {'tables': [{'name': 'Events', 'columns': [{'name': 'Id', 'type': 'int64'}, {'name': 'Flag', 'type': 'boolean'}],
                        'rows': [[1, True], [2, False], [2, False], [3, None]],
                        'measures': [{'name': 'Event Count', 'expression': 'COUNTROWS(Events)'}]}], 'relationships': []}


def response(rows):
    return {'results': [{'tables': [{'rows': rows}]}]}


class CompilerTests(unittest.TestCase):
    def test_deterministic_and_tamper_rejected(self):
        a = build(spec())
        self.assertEqual(a, validate(a))
        a['inputs'][0]['rows'][0][0] = 99
        with self.assertRaises(ValueError): validate(a)

    def test_measure_and_input_change_generation(self):
        s = spec(); a = build(s)['bundle_hash']
        s['tables'][0]['measures'][0]['expression'] = 'SUM(Events[Id])'
        self.assertNotEqual(a, build(s)['bundle_hash'])
        s['tables'][0]['rows'].pop()
        self.assertNotEqual(a, build(s)['bundle_hash'])

    def test_typed_values(self):
        for value in (True, 1.5, 2**53, '1'):
            s = spec(); s['tables'][0]['rows'][0][0] = value
            with self.subTest(value=value), self.assertRaises(ValueError): build(s)

    def test_names_and_columns(self):
        for value in ('Bad]Name', 'Bad\nName', '', 'x' * 81):
            s = spec(); s['tables'][0]['name'] = value
            with self.subTest(value=value), self.assertRaises(ValueError): build(s)

    def test_case_insensitive_duplicates(self):
        s = spec(); t = copy.deepcopy(s['tables'][0]); t['name'] = 'events'; s['tables'].append(t)
        with self.assertRaises(ValueError): build(s)

    def test_budget(self):
        s = spec(); s['tables'][0]['rows'] = [[1, True]] * 1001
        with self.assertRaises(ValueError): build(s)

    def test_no_external_m_source(self):
        s = spec(); s['tables'][0]['source'] = 'Web.Contents("https://example.com")'
        with self.assertRaises(ValueError): build(s)

    def test_m_escaping(self):
        self.assertEqual(m_literal('a"#(lf)\n'), '"a""#(#)(lf)#(lf)"')

    def test_relationship_keys(self):
        s = spec()
        s['tables'].append({'name': 'Parent', 'columns': [{'name': 'Id', 'type': 'int64'}], 'rows': [[1], [2], [3]], 'measures': []})
        s['relationships'] = [{'fromTable': 'Events', 'fromColumn': 'Id', 'toTable': 'Parent', 'toColumn': 'Id'}]
        build(s)
        s['tables'][1]['rows'].pop()
        with self.assertRaises(ValueError): build(s)

    def test_duplicate_parent(self):
        s = spec(); s['relationships'] = [{'fromTable': 'Events', 'fromColumn': 'Id', 'toTable': 'Events', 'toColumn': 'Id'}]
        with self.assertRaises(ValueError): build(s)

    def test_complete_multiset(self):
        table = build(spec())['inputs'][0]
        rows = [{'[c0]': r[0], '[c1]': r[1]} for r in reversed(table['rows'])]
        self.assertTrue(verify_table(table, response(rows))['matches'])
        self.assertFalse(verify_table(table, response(rows[:-1]))['matches'])
        rows[0] = rows[1]
        self.assertFalse(verify_table(table, response(rows))['matches'])

    def test_partial_success_errors(self):
        table = build(spec())['inputs'][0]
        for r in ({'error': {}}, {'results': []}, {'results': [{'error': {'message': 'partial'}, 'tables': [{'rows': []}]}]},
                  response([{'[c0]': 1}]), response([{'[c0]': 1, '[c1]': True}] * 1001)):
            with self.subTest(r=str(r)[:60]), self.assertRaises(ValueError): verify_table(table, r)

    def test_query_sentinel(self):
        self.assertIn('TOPN(1001', query(build(spec())['inputs'][0]))


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.journal = Journal(Path(self.tmp.name) / 'journal.sqlite')

    def tearDown(self):
        self.journal.db.close(); self.tmp.cleanup()

    def test_mutation_replay_and_changed_body(self):
        calls = []
        def send(): calls.append(1); return {'status_code': 201, 'text': {'id': 'abc'}}
        a = self.journal.mutation('create', {'x': 1}, send)
        self.assertEqual(a, self.journal.mutation('create', {'x': 1}, send))
        self.assertEqual(len(calls), 1)
        with self.assertRaises(ValueError): self.journal.mutation('create', {'x': 2}, send)

    def test_uncertain_never_reissued(self):
        def fail(): raise TimeoutError()
        with self.assertRaises(TimeoutError): self.journal.mutation('create', {}, fail)
        with self.assertRaises(RuntimeError): self.journal.mutation('create', {}, lambda: self.fail('reissued'))

    def test_reservation_visible_before_dispatch(self):
        def send():
            with self.assertRaises(RuntimeError): self.journal.mutation('create', {}, lambda: self.fail('reissued'))
            return {}
        self.journal.mutation('create', {}, send)

    def test_lro_bounded_and_no_external_url(self):
        calls = []
        def call(path, *args): calls.append(path); return {'status_code': 200, 'text': {'status': 'Running'}}
        p = Publisher(self.journal, call, sleep=lambda _: None)
        with self.assertRaises(RuntimeError):
            p.item({'status_code': 202, 'headers': {'x-ms-operation-id': '11111111-1111-1111-1111-111111111111', 'location': 'https://evil.test/'}})
        self.assertEqual(len(calls), 8)
        self.assertTrue(all(x.startswith('operations/') for x in calls))

    def test_global_call_budget(self):
        p = Publisher(self.journal, lambda *args: {'status_code': 200})
        p.calls = 40
        with self.assertRaises(RuntimeError): p.call('workspaces')

    def test_completed_lro_resolution_survives_operation_expiry(self):
        calls = []
        def call(path, *args):
            calls.append(path)
            return {'status_code': 200, 'text': {'id': 'created'} if path.endswith('/result') else {'status': 'Succeeded'}}
        p = Publisher(self.journal, call)
        r = {'status_code': 202, 'headers': {'x-ms-operation-id': '11111111-1111-1111-1111-111111111111'}}
        self.assertEqual(p.item(r), p.item(r))
        self.assertEqual(len(calls), 2)
        with self.journal.db: self.journal.db.execute("UPDATE resolutions SET body='{}'")
        with self.assertRaises(ValueError): p.item(r)

    def test_wrong_bundle_before_readback(self):
        p = Publisher(self.journal, lambda *args: self.fail('query dispatched'))
        with self.assertRaises(ValueError): p.verify(build(spec()), {'bundle_hash': 'wrong', 'refresh_status': 'Completed'})

    def test_request_id_refresh_correlation_ignores_other_completed(self):
        w = '11111111-1111-1111-1111-111111111111'; r = '44444444-4444-4444-4444-444444444444'
        calls = []
        def call(path, method, body, audience):
            calls.append(path)
            if method == 'post': return {'status_code': 202, 'headers': {'RequestId': r}}
            return {'status_code': 200, 'text': {'value': [{'requestId': w, 'status': 'Completed'}]}}
        p = Publisher(self.journal, call, sleep=lambda _: None)
        with self.assertRaises(RuntimeError): p.refresh({'workspace_id': w, 'semantic_model_id': w})
        self.assertEqual(len(calls), 9)

    def test_malicious_refresh_location_rejected(self):
        w = '11111111-1111-1111-1111-111111111111'
        p = Publisher(self.journal, lambda *args: {'status_code': 202, 'headers': {'Location': 'https://evil.test/'}})
        with self.assertRaises(RuntimeError): p.refresh({'workspace_id': w, 'semantic_model_id': w})
        self.assertEqual(p.calls, 1)

    def test_http_failure_stays_uncertain(self):
        p = Publisher(self.journal, lambda *args: {'status_code': 500})
        with self.assertRaises(RuntimeError): p.post('model', 'workspaces', {})
        with self.assertRaises(RuntimeError): p.post('model', 'workspaces', {})
        self.assertEqual(p.calls, 1)

    def test_end_to_end_create_refresh_verify_and_replay(self):
        w = '11111111-1111-1111-1111-111111111111'; m = '22222222-2222-2222-2222-222222222222'
        c = '33333333-3333-3333-3333-333333333333'; r = '44444444-4444-4444-4444-444444444444'
        posts = []
        def call(path, method, body, audience):
            if method == 'post' and not path.endswith('executeQueries'): posts.append(path)
            if path == 'workspaces': return {'status_code': 201, 'text': {'id': w, 'displayName': body['displayName']}}
            if path == 'workspaces/' + w: return {'status_code': 200, 'text': {'id': w, 'capacityId': c, 'displayName': 'investigator-fixture-' + build(spec())['bundle_hash'][:16]}}
            if path.endswith('semanticModels'): return {'status_code': 201, 'text': {'id': m, 'workspaceId': w}}
            if path.endswith('/semanticModels/' + m): return {'status_code': 200, 'text': {'id': m, 'displayName': 'Fixture ' + build(spec())['bundle_hash'][:16]}}
            if path.endswith('/refreshes'): return {'status_code': 202, 'headers': {'Location': f'https://api.powerbi.com/v1.0/myorg/groups/{w}/datasets/{m}/refreshes/{r}'}}
            if path.endswith('/refreshes?$top=5'): return {'status_code': 200, 'text': {'value': [{'requestId': r, 'status': 'Completed'}]}}
            if path.endswith('executeQueries'): return {'status_code': 200, 'text': response([{'[c0]': a, '[c1]': b} for a, b in spec()['tables'][0]['rows']])}
            self.fail(path)
        for _ in range(2):
            p = Publisher(self.journal, call, sleep=lambda _: None)
            result = p.verify(build(spec()), p.refresh(p.publish(build(spec()), c)))
            self.assertTrue(result['contents_match']); self.assertFalse(result['generation_proven']); self.assertFalse(result['live_acceptance_ready'])
        self.assertEqual(len(posts), 3)


if __name__ == '__main__': unittest.main()
