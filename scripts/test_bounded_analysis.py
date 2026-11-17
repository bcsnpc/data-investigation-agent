import unittest
from investigator.bounded_analysis import contribution, row_diff


def result(identity, rows, **extra):
    return dict(id=identity, status='SUCCEEDED', result={'rows': rows}, **extra)


class AnalysisTests(unittest.TestCase):
    def test_contributions_rank_and_reconcile_without_float_loss(self):
        left=result('q1',[{'region':'A','amount':'100.10'},{'region':'B','amount':'50'}])
        right=result('q2',[{'region':'A','amount':'10.10'},{'region':'B','amount':'40'}])
        value=contribution(left,right,dimensions=['region'],value_field='amount')
        self.assertEqual(value['net_difference'],'-100.00')
        self.assertEqual(value['ranked_slices'][0]['slice'],{'region':'A'})
        self.assertEqual(value['ranked_slices'][0]['share_of_net_difference'],'0.9')
        self.assertEqual(value['query_ids'],['q1','q2'])

    def test_zero_net_is_not_a_fake_percentage(self):
        a=result('a',[{'key':1,'value':5},{'key':2,'value':5}])
        b=result('b',[{'key':1,'value':10},{'key':2,'value':0}])
        value=contribution(a,b,dimensions=['key'],value_field='value')
        self.assertIsNone(value['ranked_slices'][0]['share_of_net_difference'])

    def test_sql_decimal_precision_is_not_lost_to_default_context(self):
        a=result('a',[{'key':1,'value':'999999999999999999999999999999999999.01'}])
        b=result('b',[{'key':1,'value':'999999999999999999999999999999999999.02'}])
        self.assertEqual(contribution(a,b,dimensions=['key'],value_field='value')['net_difference'],'0.01')

    def test_diff_missing_extra_and_changed(self):
        a=result('a',[{'id':1,'value':None},{'id':2,'value':5}])
        b=result('b',[{'id':1,'value':0},{'id':3,'value':5}])
        value=row_diff(a,b,keys=['id'],compare_fields=['value'])
        self.assertEqual((value['missing_count'],value['extra_count'],value['changed_count']),(1,1,1))
        self.assertEqual(value['changed_sample'][0]['fields']['value'],{'before':None,'after':0})

    def test_truncation_never_proves_missing_rows(self):
        a=result('a',[{'id':1,'value':2}],truncated=True)
        b=result('b',[])
        value=row_diff(a,b,keys=['id'],compare_fields=['value'])
        self.assertIsNone(value['missing_count']); self.assertIsNone(value['extra_count'])
        self.assertFalse(value['complete_returned_scopes'])

    def test_duplicate_keys_and_errors_are_not_silently_aggregated(self):
        a=result('a',[{'id':1,'value':2},{'id':1,'value':3}])
        b=result('b',[])
        with self.assertRaisesRegex(ValueError,'NOT_UNIQUE'):
            row_diff(a,b,keys=['id'],compare_fields=['value'])
        a['status']='ERROR'
        with self.assertRaisesRegex(ValueError,'SUCCESSFUL'):
            contribution(a,b,dimensions=['id'],value_field='value')


if __name__=='__main__': unittest.main()
