"""Saved sorted-read regression shapes, synthetic catalogs, no estate/model calls."""
import unittest
from investigator.investigative_queries import validate
from investigator.query_dax import compile_query
from investigator.regression_features import configured
from investigator.live_gateway import validate_dax
from test_round23_intake_queries import dax_objects


class DaxOrderingTests(unittest.TestCase):
    def setUp(self):
        self.objects=dax_objects()+[
            {'id':'key','kind':'SemanticColumn','name':'id','parent_id':'t'},
            {'id':'status','kind':'SemanticColumn','name':'status','parent_id':'t'},
            {'id':'plans','kind':'SemanticTable','name':'Plans','parent_id':'model'},
            {'id':'price','kind':'SemanticColumn','name':'price','parent_id':'plans'}]
        self.layer={'dialect':'DAX','objects':self.objects}

    def test_sorted_projection_with_related_column_and_grouped_result(self):
        # Both forms occurred in the saved MRR repair trace. Names are synthetic.
        queries=[
            ('EVALUATE SELECTCOLUMNS(FILTER(Activity, Activity[status] = "ACTIVE"), '
             '"item_id", Activity[id], "price", RELATED(Plans[price])) ORDER BY [item_id]'),
            ('EVALUATE SUMMARIZECOLUMNS(Activity[status], "rows", COUNTROWS(Activity), '
             '"total", [Quantity]) ORDER BY [status] DESC, [total]')]
        for text in queries:
            with self.subTest(text=text):
                bound=validate(text,self.layer)
                self.assertIn('EVALUATE TOPN(251,',bound['query'])
                self.assertIn(') ORDER BY ',bound['query'])
                self.assertEqual(bound['max_rows'],251)
                self.assertEqual(bound['validator_version'],'bounded-dax-v3-order')
                validate_dax(bound['query'])

    def test_sort_columns_are_bound_and_sort_stays_after_existing_topn(self):
        bound=validate('EVALUATE TOPN(10,Activity,Activity[units],DESC) '
                       'ORDER BY Activity[id] DESC, Activity[units]',self.layer)
        self.assertEqual(bound['query'],
            'EVALUATE TOPN(251,TOPN(10,Activity,Activity[units],DESC)) '
            'ORDER BY Activity[id] DESC,Activity[units] ASC')
        self.assertEqual(set(bound['asset_ids']),{'t','c','key'})

    def test_row_alias_identity_and_escaped_projection_names(self):
        query='EVALUATE ROW("sort]key",[Quantity]) ORDER BY [sort]]key]'
        bound=validate(query,self.layer)
        self.assertIn('ORDER BY [sort]]key] ASC',bound['query'])
        self.assertEqual(bound['asset_ids'],['m'])
        first=validate('EVALUATE ROW("n",[Quantity]) ORDER BY [n]',self.layer)
        explicit=validate('EVALUATE ROW("n",[Quantity]) ORDER BY [n] ASC',self.layer)
        reverse=validate('EVALUATE ROW("n",[Quantity]) ORDER BY [n] DESC',self.layer)
        unsorted=validate('EVALUATE ROW("n",[Quantity])',self.layer)
        self.assertEqual(first['compiled_read'],explicit['compiled_read'])
        self.assertNotEqual(first['compiled_read'],reverse['compiled_read'])
        self.assertNotEqual(first['compiled_read'],unsorted['compiled_read'])

    def test_query_local_definitions_and_gateway_keep_single_read_boundary(self):
        for text in (
            'DEFINE VAR x = SELECTCOLUMNS(Activity,"key",Activity[id]) '
            'EVALUATE x ORDER BY [key]',
            'DEFINE MEASURE Activity[Scoped] = SUM(Activity[units]) '
            'EVALUATE ROW("value",[Scoped]) ORDER BY [value]'):
            with self.subTest(text=text):
                bound=validate(text,self.layer)
                self.assertTrue(bound['query'].startswith('DEFINE '))
                validate_dax(bound['query'],allow_define=True)

    def test_unknown_members_and_writes_never_become_ordering_aliases(self):
        for text in (
            'EVALUATE Activity ORDER BY [unknown]',
            'EVALUATE Activity ORDER BY Outside[id]',
            'EVALUATE ROW("invented",[invented]) ORDER BY [invented]',
            'EVALUATE Activity ORDER BY Activity[id]; DELETE FROM Activity',
            'EVALUATE Activity ORDER BY Activity[id] EVALUATE Activity',
            'EVALUATE Activity ORDER BY Activity[id] START AT 1',
            'EVALUATE Activity ORDER BY VALUES(Activity[id])',
            'EVALUATE Activity ORDER BY DESC',
            'EVALUATE Activity ORDER BY Activity[id],',
            'EVALUATE Activity ORDER BY '+','.join(['Activity[id]']*17)):
            with self.subTest(text=text),self.assertRaises(ValueError):
                validate(text,self.layer)

    def test_ambiguous_unqualified_column_is_not_guessed(self):
        objects=self.objects+[
            {'id':'other','kind':'SemanticTable','name':'Other','parent_id':'model'},
            {'id':'other-key','kind':'SemanticColumn','name':'id','parent_id':'other'}]
        with self.assertRaisesRegex(ValueError,'Ambiguous'):
            validate('EVALUATE SUMMARIZECOLUMNS(Activity[id], Other[id]) ORDER BY [id]',
                     {'dialect':'DAX','objects':objects})

    def test_old_unsorted_identity_and_explicit_legacy_refusal_stay_unchanged(self):
        left=compile_query('EVALUATE ROW("left",[Quantity])',self.objects)
        right=compile_query('EVALUATE ROW("right",[Quantity])',self.objects)
        self.assertEqual(left['compiled_read'],right['compiled_read'])
        self.assertEqual(left['result_columns'],['left'])
        self.assertEqual(left['validator_version'],'bounded-dax-v1')
        ordered='EVALUATE ROW("value",[Quantity]) ORDER BY [value]'
        with self.assertRaises(ValueError):compile_query(ordered,self.objects)
        with configured({'r27_dax_query_ordering':False}),self.assertRaises(ValueError):
            validate(ordered,self.layer)


if __name__=='__main__':unittest.main()
