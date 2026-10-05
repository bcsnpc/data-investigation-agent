import unittest
from investigator.adapters.binding_catalog import read


class BindingCatalogTests(unittest.TestCase):
    def test_exact_target_schema_as_reader_not_code_derived_placeholder(self):
        config={'fabric':{'sql_reader':{'server':'declared-endpoint','account':'reader'}}}
        obj={'connection':'declared-endpoint','database':'db','asset_id':'exact-target',
             'catalog':{'metadata':{'schema_name':'dbo','name':'items'}}}
        seen=[]
        def execute(database,request):
            seen.append((database,request))
            return {'surface_report':{'identity':'reader','object':'db','engine':'Microsoft Azure SQL Data Warehouse'},
                    'read_only_verified':True,'rows':[{'column_name':'value','data_type':'bigint','collation_name':None}]}
        columns,proof=read(config,obj,execute=execute)
        self.assertEqual(columns[0]['data_type'],'bigint')
        self.assertEqual(proof['asset_id'],'exact-target')
        self.assertEqual(seen[0][1]['read_only_objects'],['[dbo].[items]'])
        obj['connection']='elsewhere'
        with self.assertRaisesRegex(ValueError,'approved'):
            read(config,obj,execute=lambda *args:self.fail('must not run'))

    def test_refuses_unattested_or_empty_catalog(self):
        config={'fabric':{'sql_reader':{'server':'endpoint','account':'reader'}}}
        obj={'connection':'endpoint','database':'db','asset_id':'target',
             'catalog':{'metadata':{'schema_name':'dbo','name':'items'}}}
        with self.assertRaisesRegex(ValueError,'evidence'):
            read(config,obj,execute=lambda *args:{'rows':[]})


if __name__=='__main__':unittest.main()
