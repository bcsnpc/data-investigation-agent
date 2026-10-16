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


class BatchCatalogTests(unittest.TestCase):
    def setUp(self):
        self.config={'fabric':{'sql_reader':{'server':'endpoint','account':'reader'}}}
        self.objects=[{'connection':'endpoint','database':'db','asset_id':name,
            'catalog':{'metadata':{'schema_name':'dbo','name':name}}} for name in ('movements','rates')]
        self.answer={'surface_report':{'identity':'reader','object':'db','engine':'Microsoft Azure SQL Data Warehouse'},
            'read_only_verified':True,'rows':[{'schema_name':'dbo','table_name':name,
                'column_name':'value','data_type':'bigint','collation_name':None} for name in ('movements','rates')]}

    def test_same_metadata_one_request_both_objects_guarded(self):
        from investigator.adapters.binding_catalog import read_many
        seen=[]
        def execute(database,request):seen.append(request);return self.answer
        result=read_many(self.config,self.objects,execute=execute)
        self.assertEqual(len(seen),1)
        self.assertEqual(seen[0]['read_only_objects'],['[dbo].[movements]','[dbo].[rates]'])
        for obj in self.objects:
            _,old=read(self.config,obj,execute=lambda *args:{**self.answer,'rows':[{
                'column_name':'value','data_type':'bigint','collation_name':None}]})
            columns,proof=result[obj['asset_id']]
            self.assertEqual(columns,old['columns'])
            self.assertEqual({key:proof[key] for key in old},old)
        self.assertEqual(result['movements'][1]['catalog_batch_request_hash'],result['rates'][1]['catalog_batch_request_hash'])

    def test_absent_unexpected_duplicate_or_unattested_rows_refuse(self):
        import copy
        from investigator.adapters.binding_catalog import read_many
        changes=[lambda a:a['rows'].pop(),lambda a:a['rows'].append(dict(a['rows'][0])),
            lambda a:a['rows'][0].update(table_name='undeclared'),
            lambda a:a['surface_report'].update(identity='writer')]
        for change in changes:
            answer=copy.deepcopy(self.answer);change(answer)
            with self.assertRaises(ValueError):read_many(self.config,self.objects,execute=lambda *args:answer)

    def test_cross_database_or_object_injection_never_executes(self):
        from investigator.adapters.binding_catalog import read_many
        self.objects[1]['database']='other'
        with self.assertRaisesRegex(ValueError,'crosses'):read_many(self.config,self.objects,execute=lambda *args:self.fail())
        self.objects[1]['database']='db';self.objects[1]['catalog']['metadata']['name']='x]; DROP TABLE x'
        with self.assertRaises(ValueError):read_many(self.config,self.objects,execute=lambda *args:self.fail())

if __name__=='__main__':unittest.main()
