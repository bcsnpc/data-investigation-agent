import copy
import unittest
from unittest.mock import Mock, patch
from investigator.question_intake import snapshot
from investigator.onboarding import digest


class SnapshotReadsTests(unittest.TestCase):
    def test_one_context_lookup_and_no_duplicate_full_model_fetch(self):
        rows = [{'id': name, 'enabled': True, 'context': {'reports': []},
                 'context_id': 'context', 'revision': 1, 'business': {}}
                for name in ('a', 'b')]
        workspace = Mock(intake_configuration=None)
        workspace.store.list.return_value = rows
        workspace.agent.config = {'layer_roles': [{'asset_id': 'asset'}]}
        workspace.model.side_effect = lambda name: {'id': name, 'name': name,
            'columns': [], 'measures': [], 'dynamic_investigation': True}
        with patch('investigator.context_search.latest', return_value={
                'assets': [{'id': 'asset', 'name': 'Declared role'}]}) as latest, \
                patch('investigator.adapters.report_cells.catalog', return_value=[]), \
                patch('investigator.adapters.report_cells.declared_scopes', return_value=[]), \
                patch('investigator.adapters.report_cells.declared_aliases', return_value={}):
            first = snapshot(workspace)
            latest.assert_called_once_with(workspace.store)
            workspace.store.get.assert_not_called()
            self.assertEqual(first['versions'], {r['id']: digest({
                'context': r['context'], 'revision': r['revision'],
                'business': r['business'], 'enabled': r['enabled']}) for r in rows})
            expected = [{'id': 'asset', 'name': 'Declared role'}]
            self.assertEqual([m['declared_layers'] for m in first['models']], [expected, expected])
            first['models'][0]['declared_layers'][0]['name'] = 'changed'
            self.assertEqual(first['models'][1]['declared_layers'], expected)
            rows[0]['context']['new_definition'] = 'changed'
            second = snapshot(workspace)
            self.assertNotEqual(first['versions'], second['versions'])


if __name__ == '__main__':
    unittest.main()
