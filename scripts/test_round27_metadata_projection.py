import unittest
from investigator.investigative_queries import validate
from investigator.live_gateway import validate_dax, GatewayDenied
from test_round23_intake_queries import sql_objects,dax_objects
from managed_sql_worker import metadata_columns_from_cursor


class MetadataProjectionTests(unittest.TestCase):
    def test_saved_partition_projection_passes_both_read_boundaries(self):
        query='EVALUATE SELECTCOLUMNS(INFO.PARTITIONS(), "Name", [Name], "Mode", [Mode], "State", [State], "RefreshedTime", [RefreshedTime], "ModifiedTime", [ModifiedTime])'
        compiled=validate(query,{'dialect':'DAX','objects':dax_objects()})
        self.assertIn('TOPN(251,SELECTCOLUMNS(INFO.PARTITIONS()',compiled['query'])
        self.assertEqual(validate_dax(compiled['query']),compiled['query'])

    def test_metadata_projection_never_opens_business_measure_or_second_statement(self):
        for query in ['EVALUATE SELECTCOLUMNS(INFO.PARTITIONS(), "x", [SecretMeasure])',
                      'EVALUATE UNION(INFO.PARTITIONS(), ROW("x",[SecretMeasure]))',
                      'EVALUATE TOPN([SecretMeasure],INFO.PARTITIONS())',
                      'EVALUATE SELECTCOLUMNS(PrivateTable,"x",[Name])+INFO.PARTITIONS()',
                      'EVALUATE INFO.PARTITIONS(); EVALUATE ROW("x",1)',
                      'EVALUATE INFO.PARTITIONS("Name",)']:
            with self.subTest(query=query), self.assertRaises((ValueError,GatewayDenied)):
                validate_dax(query)

    def test_sql_projection_names_cross_native_transport(self):
        compiled=validate('SELECT name, create_date, modify_date, temporal_type_desc FROM sys.tables',
                          {'dialect':'T-SQL','objects':sql_objects()})
        self.assertEqual(compiled['result_columns'],['name','create_date','modify_date','temporal_type_desc'])

    def test_star_metadata_schema_is_native_and_cannot_enable_unbound_business_read(self):
        compiled=validate('SELECT * FROM sys.dm_db_log_stats(DB_ID())',
                          {'dialect':'T-SQL','objects':sql_objects()})
        self.assertEqual(compiled['result_columns'],[])
        self.assertTrue(metadata_columns_from_cursor(compiled))
        with self.assertRaises(ValueError):
            metadata_columns_from_cursor({'query':'SELECT * FROM dbo.Secret','result_columns':[]})


if __name__=='__main__':unittest.main()
