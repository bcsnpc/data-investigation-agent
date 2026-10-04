import unittest
from unittest.mock import Mock
from investigator.adapters.warehouse_catalog import read


class WarehouseCatalogTests(unittest.TestCase):
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
