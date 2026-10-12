import unittest
from unittest.mock import Mock
from investigator.adapters.warehouse_catalog import read, inventory


class WarehouseCatalogTests(unittest.TestCase):
    def test_inventory_is_visible_scope_and_refuses_truncation_or_wrong_reader(self):
        config={'fabric':{'sql_reader':{'server':'approved','account':'reader'}}}
        warehouse={'displayName':'ops','properties':{'connectionString':'approved'}}
        row={'schema_name':'a','table_name':'events','column_name':'id','data_type':'int','column_id':1,
             'max_length':4,'precision':10,'scale':0,'is_nullable':False,'can_view_definition':0}
        execute=Mock(return_value={'read_only_verified':True,'surface_report':{'identity':'reader','object':'ops','engine':'Microsoft Azure SQL Data Warehouse'},'rows':[row]})
        result=inventory(config,warehouse,execute=execute)
        self.assertFalse(result['complete_schema'])
        self.assertEqual(result['scope'],'VISIBLE_OBJECTS_ONLY')
        self.assertFalse(result['tables'][0]['definition_visible'])
        self.assertEqual(result['tables'][0]['columns'][0]['name'],'id')
        from investigator.control_contract import bounds
        maximum = bounds('FABRIC_SQL')['maximum_rows']
        request=execute.call_args.args[2]
        self.assertEqual(request['max_rows'],maximum)
        self.assertIn('TOP '+str(maximum-1),request['query'])
        execute.return_value['rows']=[row]*(maximum-1)
        with self.assertRaises(ValueError):inventory(config,warehouse,execute=execute)
        execute.return_value['rows']=[row];execute.return_value['surface_report']['identity']='owner'
        with self.assertRaises(ValueError):inventory(config,warehouse,execute=execute)

    def test_scoped_reader_schema_and_own_surface(self):
        config={'fabric':{'sql_reader':{'server':'approved','account':'reader'}}}
        warehouse={'displayName':'ops','properties':{'connectionString':'approved'}}
        execute=Mock(return_value={'read_only_verified':True,'surface_report':{'identity':'reader','object':'ops','engine':'Microsoft Azure SQL Data Warehouse'},
                                   'rows':[{'column_name':'run_id','data_type':'varchar'}]})
        self.assertEqual(read(config,warehouse,'dbo.audit',execute=execute),[{'name':'run_id','data_type':'varchar'}])
        request=execute.call_args.args[2]
        self.assertEqual(request['read_only_objects'],['[dbo].[audit]'])
        self.assertEqual(request['parameters'],[{'name':'@schema','value':'dbo'},{'name':'@table','value':'audit'}])
        for changed in ({'surface_report':{'identity':'publisher','object':'ops'}},
                        {'surface_report':{'identity':'reader','object':'other'}},
                        {'read_only_verified':False},{'rows':[]}):
            execute.return_value.update(changed)
            with self.assertRaises(ValueError):read(config,warehouse,'dbo.audit',execute=execute)

    def test_no_implicit_connection_or_unbounded_object_scope(self):
        execute=Mock()
        for name,server in [('dbo.audit','other'),('audit','approved'),('dbo.audit;DROP TABLE x','approved')]:
            with self.assertRaises(ValueError):
                read({'fabric':{'sql_reader':{'server':'approved','account':'reader'}}},
                     {'displayName':'ops','properties':{'connectionString':server}},name,execute=execute)
        execute.assert_not_called()


if __name__=='__main__':unittest.main()
