import unittest
from fixture.source_scopes import grouped_quantity
from investigator.live_gateway import validate_sql,_object


class SourceScopeControls(unittest.TestCase):
    def test_both_export_groups_are_native_with_bound_values_and_one_overflow_row(self):
        for column,values in [('warehouse_id',[1,2]),('product_id',[7,8]),('event_day',['2026-09-14','2026-09-15'])]:
            request=grouped_quantity(column,values)
            self.assertEqual(request['max_rows'],3)
            self.assertEqual([p['value']for p in request['parameters']],values)
            self.assertIn('GROUP BY ['+column+']',request['query'])
            self.assertIn('SUM(CONVERT(bigint,[units]))',request['query'])
            from sqlglot import parse_one,exp
            self.assertEqual(list(parse_one(request['query'],read='tsql').args['where'].find_all(exp.Literal)),[])
            validate_sql(request['query'],{_object(v)for v in request['read_only_objects']})

    def test_unknown_columns_duplicate_scopes_and_literal_injection_refuse(self):
        for column,values in [('units',[1,2]),('warehouse_id',[True,2]),('warehouse_id',[1,1]),('warehouse_id',[1,2,3]),('event_day',["2026-09-14');DROP TABLE x;--",'2026-09-15']),('event_day',['2026-09-14','2026-09-14'])]:
            with self.subTest(column=column,values=values),self.assertRaises(ValueError):grouped_quantity(column,values)


if __name__=='__main__':unittest.main()
