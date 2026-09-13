"""Contract tests for live metadata pagination, async definitions and snapshots."""
import base64
import json
import tempfile
import unittest
from pathlib import Path
from metadata_inventory import Inventory, pages, definition, expand_definition, attempt


class MetadataTests(unittest.TestCase):
    def test_onelake_schema_discovery_and_column_details(self):
        from onelake_metadata import collect
        calls = []
        def get(path):
            calls.append(path)
            if path.startswith('schemas?'):
                return {'schemas': [{'name': 'app'}]}
            if path.startswith('tables?'):
                return {'tables': [{'name': 'orders'}]}
            return {'name': 'orders', 'columns': [{'name': 'order_id', 'type_name': 'string'}]}
        result = collect('ws', 'lh', 'bronze.Lakehouse', get)
        self.assertEqual(result['tables'][0]['schema_name'], 'app')
        self.assertEqual(result['tables'][0]['columns'][0]['name'], 'order_id')
        self.assertEqual(calls[-1], 'tables/bronze.Lakehouse.app.orders')

    def test_failed_extraction_rolls_back_partial_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Inventory(Path(tmp)/'inventory.sqlite')
            def fail():
                store.asset('partial', 'ReportVisual', 'broken', 'live', {})
                raise ValueError('bad payload')
            attempt(store, 'report', 'definition', 'live', fail)
            self.assertEqual(store.db.execute('SELECT count(*) FROM assets').fetchone()[0], 0)
            self.assertEqual(store.finish()['status'], 'PARTIAL')
            store.db.close()

    def test_pagination_and_origin_guard(self):
        calls = []
        def call(endpoint, **kw):
            calls.append(endpoint)
            return {'text': {'value': [len(calls)], **({'continuationToken': 'a/b+='} if len(calls)==1 else {})}}
        self.assertEqual(pages('items', call), [1, 2])
        self.assertEqual(calls[1], 'items?continuationToken=a%2Fb%2B%3D')
        with self.assertRaises(ValueError):
            pages('items', lambda *a, **k: {'text': {'value': [], 'continuationUri': 'https://evil.example/v1/items'}})

    def test_repeated_pagination_rejected(self):
        with self.assertRaises(ValueError):
            pages('items', lambda *a, **k: {'text': {'value': [], 'continuationToken': 'same'}})

    def test_async_definition_result_is_fetched(self):
        responses = iter([
            {'status_code': 202, 'headers': {'X-MS-Operation-ID': 'op'}},
            {'text': {'status': 'Running'}}, {'text': {'status': 'Succeeded'}},
            {'text': {'definition': {'parts': [{'path': 'model.bim', 'payloadType': 'InlineBase64', 'payload': base64.b64encode(b'{}').decode()}]}}},
        ])
        calls = []
        def call(endpoint, *args):
            calls.append(endpoint)
            return next(responses)
        self.assertEqual(definition('item/getDefinition', call, lambda _: None), {'model.bim': '{}'})
        self.assertEqual(calls[-1], 'operations/op/result')

    def test_failed_async_definition_is_not_success(self):
        responses = iter([{'status_code': 202, 'headers': {'x-ms-operation-id': 'op'}}, {'text': {'status': 'Failed'}}])
        with self.assertRaises(RuntimeError):
            definition('definition', lambda *a: next(responses))

    def test_snapshots_preserve_changes_and_gaps(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'inventory.sqlite'
            first = Inventory(path)
            first.asset('asset', 'Measure', 'Revenue', 'live', {'expression': 'SUM(a)'})
            first.finish(); first.db.close()
            second = Inventory(path)
            second.asset('asset', 'Measure', 'Revenue', 'live', {'expression': 'SUM(b)'})
            def fail():
                raise RuntimeError('secret must not be stored')
            attempt(second, 'asset', 'definition', 'live', fail)
            result = second.finish()
            self.assertEqual(result['status'], 'PARTIAL')
            self.assertEqual(second.db.execute('SELECT count(DISTINCT content_hash) FROM assets').fetchone()[0], 2)
            self.assertNotIn('secret', str(second.db.execute('SELECT detail FROM observations').fetchall()))
            second.db.close()

    def test_model_and_visual_context_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Inventory(Path(tmp)/'inventory.sqlite')
            model = {'model': {'tables': [{'name': 'Sales', 'columns': [{'name': 'amount'}], 'measures': [{'name': 'Net', 'expression': 'SUM(Sales[amount])'}]}], 'relationships': []}}
            expand_definition(store, 'model', 'SemanticModel', {'model.bim': json.dumps(model)}, 'live')
            visual = {'name': 'v', 'filterConfig': {'filters': [{'name': 'region'}]}}
            expand_definition(store, 'report', 'Report', {'definition/pages/p/page.json': '{"name":"p"}', 'definition/pages/p/visuals/v/visual.json': json.dumps(visual)}, 'live')
            row = store.db.execute("SELECT parent_id,metadata FROM assets WHERE kind='ReportVisual'").fetchone()
            self.assertEqual(row[0], 'report/page/p')
            self.assertEqual(json.loads(row[1])['filterConfig'], visual['filterConfig'])
            self.assertEqual(store.db.execute("SELECT count(*) FROM assets WHERE kind='Measure'").fetchone()[0], 1)
            store.db.close()


if __name__ == '__main__':
    unittest.main()
