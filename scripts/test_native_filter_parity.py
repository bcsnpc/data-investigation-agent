import unittest
from native_filter_parity import query, assess


def response(**changes):
    row = {'[native_orders]': '1', '[adapter_orders]': '1', '[native_cash]': '99.0000', '[adapter_cash]': '99.0000'}
    row.update(changes)
    return {'results': [{'tables': [{'rows': [row]}]}]}


class ParityTests(unittest.TestCase):
    def test_bounded_scope(self):
        for currency, order in [('USD', None), ('USD', 'ORD-000001"'), ('usd', 'ORD-000001')]:
            with self.assertRaises(ValueError): query(currency, order)
        dax = query('USD', 'ORD-000001')
        self.assertIn('FactOrder[currency]', dax)
        self.assertIn('FactOrderLine[currency]', dax)

    def test_match_is_not_proof(self):
        result = assess(response())
        self.assertEqual(result['status'], 'OBSERVED_MATCH')
        self.assertFalse(result['snapshot_comparable'])
        self.assertFalse(result['runtime_filter_verified'])

    def test_mismatch_and_empty(self):
        self.assertEqual(assess(response(**{'[adapter_cash]': '0'}))['status'], 'OBSERVED_MISMATCH')
        self.assertEqual(assess(response(**{'[native_orders]': '0', '[adapter_orders]': '0', '[native_cash]': '0', '[adapter_cash]': '0'}))['status'], 'NO_MATCHING_ORDERS')
        self.assertEqual(assess(response(**{'[native_orders]': '0', '[adapter_orders]': '0', '[adapter_cash]': '0'}))['status'], 'OBSERVED_MISMATCH')

    def test_incomplete_and_invalid(self):
        for raw in ({}, {'error': {} , 'results': []}, response(**{'[native_cash]': None}), response(**{'[native_cash]': 'NaN'}), response(**{'[native_orders]': '1.5'})):
            with self.assertRaises(ValueError): assess(raw)


if __name__ == '__main__': unittest.main()
