import unittest
from unittest.mock import patch
from investigator import context_search


class ResolverBudgetTests(unittest.TestCase):
    def resolve(self, length):
        measure = {'id':'measure', 'kind':'Measure', 'name':'Quantity',
                   'availability':'CURRENT', 'metadata':{'expression':'x' * length}}
        model = {'context':{'semantic_graph':{'measures':{'measure':{'references':[]}}}}}
        with patch('investigator.model_context.assets', return_value=[measure]), \
             patch.object(context_search, 'latest', return_value=None):
            return context_search.measure_path(None, model, 'measure')

    def test_shared_resolver_retains_path_between_old_and_new_owner_bounds(self):
        self.assertEqual(context_search.MEASURE_PATH_LIMIT, 24000)
        result = self.resolve(18000)
        self.assertEqual(result['measure']['metadata']['expression'], 'x' * 18000)
        self.assertFalse(result['truncated'])

    def test_shared_resolver_still_refuses_above_new_bound(self):
        with self.assertRaises(context_search.MeasurePathLimit) as caught:
            self.resolve(26000)
        self.assertEqual(caught.exception.limit, 24000)
        self.assertGreater(caught.exception.characters, 24000)
