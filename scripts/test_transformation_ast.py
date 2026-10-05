import json,sqlite3,unittest
from investigator.transformation_ast import Reader
from investigator.transformation_sql import extract_statement,compile_quantity
from investigator.code_static import Unsupported

class StaticReaderTests(unittest.TestCase):
    schemas={'input':{'id':'int','amount':'int','kind':'int'},'other':{'id':'int','kind':'int','rate':'int'}}
    catalog={k:{'id':k,'metadata':{'schema_name':'main','name':k,'type_desc':'USER_TABLE',
                'columns':[{'name':c,'data_type':t} for c,t in fields.items()]}} for k,fields in schemas.items()}
    def reader(self,body):
        return Reader('from pyspark.sql import functions as F\n'+body,self.schemas)
    def query(self,plan,col):return compile_quantity(plan,col,self.catalog)
    def test_plain_selection_rename_arithmetic_and_filter(self):
        examples=[
            ("a=spark.table('input')\na.select('id','amount').write.format('delta').mode('overwrite').save('out')",'amount','PROJECT'),
            ("a=spark.table('input')\na.withColumnRenamed('amount','value').write.format('delta').mode('overwrite').save('out')",'value','PROJECT'),
            ("a=spark.table('input')\na.withColumn('value',F.col('amount')*F.lit(2)).write.format('delta').mode('overwrite').save('out')",'value','PROJECT'),
            ("a=spark.table('input')\na.filter(F.col('amount')>10).write.format('delta').mode('overwrite').save('out')",'amount','FILTER')]
        for code,col,kind in examples:
            with self.subTest(kind=kind):
                reader=self.reader(code);frame=reader.writes['out'];self.assertEqual(frame.plan['kind'],kind)
                self.assertIn('SUM',self.query(frame.plan,col));self.assertEqual(reader.write_locations['out'][0],3)
    def test_two_key_join_and_grouped_aggregation(self):
        joined=self.reader("a=spark.table('input')\nb=spark.table('other')\na.join(b,['id','kind'],'left').write.format('delta').mode('overwrite').save('out')")
        plan=joined.writes['out'].plan;self.assertEqual(plan['keys'],['id','kind']);self.assertIn('LEFT JOIN',self.query(plan,'amount'))
        grouped=self.reader("a=spark.table('input')\na.groupBy('kind').agg(F.sum('amount').alias('value')).write.format('delta').mode('overwrite').save('out')")
        self.assertIn('GROUP BY',self.query(grouped.writes['out'].plan,'value'))
    def test_whole_row_dedupe_is_explicit_partial_key_survivor_is_refused(self):
        r=self.reader("a=spark.table('input')\na.dropDuplicates().write.format('delta').mode('overwrite').save('out')")
        self.assertIn('DISTINCT',self.query(r.writes['out'].plan,'amount'))
        with self.assertRaises(Unsupported):self.reader("a=spark.table('input')\na.dropDuplicates(['id']).write.format('delta').mode('overwrite').save('out')")
    def test_dynamic_table_requires_model_proposal_never_static_guess(self):
        with self.assertRaises((Unsupported,TypeError)):self.reader("a=spark.table(resolve_name())\na.write.format('delta').mode('overwrite').save('out')")
    def test_sql_filter_select_aggregate_and_arithmetic_compile(self):
        for query in ('SELECT id, amount FROM input','SELECT kind, SUM(amount) AS value FROM input GROUP BY kind',
                      'SELECT amount * 2 AS value FROM input WHERE amount > 10'):
            frame=extract_statement('CREATE TABLE out AS '+query,self.schemas)['out']
            name='value' if 'value' in frame.columns else 'amount'
            self.assertIn('SUM',self.query(frame.plan,name))

    def test_append_and_conditional_sql_writes_cannot_claim_whole_target_equivalence(self):
        for statement in ('INSERT INTO out SELECT amount FROM input',
                          'CREATE TABLE IF NOT EXISTS out AS SELECT amount FROM input'):
            with self.assertRaises(Unsupported):extract_statement(statement,self.schemas)
        self.assertIn('out',extract_statement('INSERT OVERWRITE TABLE out SELECT amount FROM input',self.schemas))
    def test_exported_command_marker_notebook_uses_core_without_platform_adapter(self):
        from investigator.code_sources import normalize
        unit=normalize('unit.py',b"# Databricks notebook source\n# COMMAND ----------\na=spark.table('input')\na.write.format('delta').mode('overwrite').save('out')\n")
        text='\n'.join(c['source'] for c in unit['cells'])
        reader=Reader(text,self.schemas);self.assertEqual(reader.writes['out'].plan['kind'],'SCAN')
    def test_static_seed_is_not_proposed_as_an_observed_source(self):
        r=Reader("a=spark.createDataFrame([[1]],'amount int')\na.write.format('delta').mode('overwrite').save('seed')\nb=spark.read.format('delta').load('seed')\nb.write.format('delta').mode('overwrite').save('out')",{})
        self.assertIsNone(r.writes['seed'].plan);self.assertEqual(r.writes['out'].plan['table'],'seed')
    def test_division_without_declared_type_and_zero_semantics_refuses_compilation(self):
        frame=extract_statement('CREATE TABLE out AS SELECT amount / 2 AS value FROM input',self.schemas)['out']
        with self.assertRaisesRegex(Unsupported,'Division result type and zero semantics'):
            self.query(frame.plan,'value')

    def test_string_deduplication_cannot_assume_execution_collation_and_padding(self):
        catalog={**self.catalog,'input':{'id':'input','metadata':{'schema_name':'main','name':'input',
            'columns':[{'name':'id','data_type':'int'},{'name':'amount','data_type':'int'},
                       {'name':'kind','data_type':'nvarchar'}]}}}
        relation={'kind':'DEDUPE','keys':['id','amount','kind'],'input':
            {'kind':'SCAN','table':'input','columns':['id','amount','kind']}}
        with self.assertRaisesRegex(Unsupported,'no assumed string collation or padding'):
            compile_quantity(relation,'amount',catalog)

    def test_sql_alias_or_outer_join_null_difference_cannot_be_erased(self):
        for query in ('SELECT missing.amount FROM input a',
                      'SELECT b.id FROM input a LEFT JOIN other b ON a.id=b.id AND a.kind=b.kind',
                      'SELECT a.amount FROM input a LEFT JOIN other b ON a.id=b.id AND a.kind=b.kind WHERE b.id > 0'):
            with self.assertRaises(Unsupported):extract_statement('CREATE TABLE out AS '+query,self.schemas)

if __name__=='__main__':unittest.main()
