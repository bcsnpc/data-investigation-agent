import copy,sqlite3,unittest
from unittest.mock import patch
from contextlib import redirect_stderr
from io import StringIO
import duckdb
from sqlglot import parse_one
import dia
import test_translation_native as native
import test_translation_proposer as witnesses
from investigator import translation_proposer as t,query_dax
from investigator.adapters.translation_ranking import compile_ranked_sql
from investigator.adapters.translation_native import FilterRoute
from investigator.adapters.translation_filter_definition import compile_native
from investigator.transformation_sql import compile_quantity
from investigator.verification_budget import VerificationBudget
from investigator.key_profile import quantities
from investigator.binding_sample import verify as binding_verify
from investigator.process_debugging import attest_surface
from test_lineage_binding import proposal

NORM={'encoding':'typed-json-utf8','case_fold':False,'trim':False}

class TranslatorGapTests(unittest.TestCase):
 def test_missing_token_prints_storage_identity_command_and_exits_before_installation(self):
  out=StringIO()
  with patch.dict('os.environ',{},clear=True),patch('investigator.estate_installation.build') as build,redirect_stderr(out):
   self.assertEqual(dia.main(['demo','--manifest','m','--case','c']),2)
   build.assert_not_called()
  text=out.getvalue()
  for token in ('local Windows operator','not an Entra','ConvertFrom-SecureString','workspace-access.dpapi','INVESTIGATOR_WORKSPACE_TOKEN'):
   self.assertIn(token,text)
  self.assertNotIn('Traceback',text)
 def test_distinct_keeps_the_inner_projected_columns(self):
  f=native.NativeTranslationTests();f.setUp();self.addCleanup(f.doCleanups)
  request,candidate,route=f.route_case(['North'])
  query='EVALUATE DISTINCT('+candidate['expression'].removeprefix('EVALUATE ')+')'
  self.assertEqual(query_dax.compile_query(query,f.model['context']['model_assets'])['result_columns'],['translation_key_0'])
 def test_predicate_is_wrapped_by_adapter_before_parser_and_dispatch(self):
  f=native.NativeTranslationTests();f.setUp();self.addCleanup(f.doCleanups)
  request,candidate,route=f.route_case(['North'])
  candidate['expression']='Customers[Region]="North"'
  plan=route.compile(candidate,'PROPOSED',request,{'kind':'TRANSLATION','proposal_hash':t.seal(candidate),'cell':None,'evaluation_timestamp':None})
  self.assertIn('FILTER',plan['plan']['query']);self.assertIn('translation_key_0',plan['plan']['query'])
  self.assertEqual(f.requests,[])
 def test_sql_top_n_renders_row_number_over_the_declared_grouped_scope(self):
  catalog=[{'id':'items','metadata':{'schema_name':'dbo','name':'Items','type_desc':'USER_TABLE','columns':[
   {'name':'key','data_type':'int'},{'name':'value','data_type':'bigint'},{'name':'scope','data_type':'int'}]}}]
  query=compile_ranked_sql('SELECT [key],SUM([value]) AS score FROM dbo.Items WHERE [scope]=1 GROUP BY [key]',keys=['key'],ordering=[('score','DESC'),('key','ASC')],limit=2,catalog=catalog)
  self.assertIn('ROW_NUMBER()',query);self.assertIn('WHERE',query)
  db=sqlite3.connect(':memory:');self.addCleanup(db.close);db.execute('CREATE TABLE Items(key int,value int,scope int)');db.executemany('INSERT INTO Items VALUES(?,?,?)',[(1,10,1),(2,20,1),(3,100,0),(4,5,1)])
  sql=parse_one(query,read='tsql');
  for table in sql.find_all(__import__('sqlglot').exp.Table):table.set('db',None)
  self.assertEqual(db.execute(sql.sql(dialect='sqlite')).fetchall(),[(2,),(1,)])
 def test_tied_and_untied_native_key_sets_are_retained(self):
  f=native.NativeTranslationTests();f.setUp();self.addCleanup(f.doCleanups)
  request,candidate,route=f.route_case(['a','b','c'])
  original=route.compile
  def compiler(*args):
   plan=original(*args);plan['top_n']=2;return plan
  result=t.verify(candidate,request,cells=[None],compiler=compiler,execute=route.execute,budget=VerificationBudget({},1,record=lambda _:None))
  self.assertEqual(result['status'],'FALSIFIED');self.assertEqual(result['reason'],'TIE_AT_BOUNDARY')
  self.assertEqual(result['failure']['row_count'],1);self.assertEqual(len(result['observations']),2)
  self.assertEqual(result['observations'][0]['keys'],[['a'],['b'],['c']])
  self.assertEqual(t.revalidate(result),result)
  f2=native.NativeTranslationTests();f2.setUp();self.addCleanup(f2.doCleanups)
  req,cand,r=f2.route_case(['a','b'])
  compile2=r.compile
  def no_tie(*args):
   p=compile2(*args);p['top_n']=2;return p
  self.assertEqual(t.verify(cand,req,cells=[None],compiler=no_tie,execute=r.execute,budget=VerificationBudget({},1,record=lambda _:None))['status'],'VERIFIED')
 def test_text_to_date_and_int_casts_record_invalid_rows(self):
  relation={'kind':'SCAN','table':'input','columns':['key','amount']}
  catalog={'input':{'id':'input','metadata':{'schema_name':'dbo','name':'Input','type_desc':'USER_TABLE','columns':[{'name':'key','data_type':'int'},{'name':'amount','data_type':'varchar'}]}}}
  sample={'kind':'KEY_RANGE','column':'key','lower':1,'upper':9,'provenance':'synthetic'}
  db=duckdb.connect();self.addCleanup(db.close);db.execute('CREATE SCHEMA dbo');db.execute('CREATE TABLE dbo.Input(key INTEGER,amount VARCHAR)')
  for dtype,profile,values in [('date','TEMPORAL',['2026-01-01','bad']),('int','NUMERIC',['12','bad'])]:
   db.execute('DELETE FROM dbo.Input');db.executemany('INSERT INTO dbo.Input VALUES(?,?)',[(i+1,v) for i,v in enumerate(values)])
   text=compile_quantity(relation,'amount',catalog,profile=profile,sample=sample,comparison_type=dtype)
   self.assertIn('TRY_CAST',text);self.assertIn('cast_failure_count',text)
   row=db.execute(parse_one(text,read='tsql').sql(dialect='duckdb')).fetchone()
   self.assertEqual(row[-1],1)
   db.execute("DELETE FROM dbo.Input WHERE amount='bad'")
   valid=db.execute(parse_one(text,read='tsql').sql(dialect='duckdb')).fetchone()
   self.assertEqual(valid[-1],0)
   self.assertEqual(str(valid[0]),values[0] if dtype=='date' else '12')
 def test_failed_cast_is_falsified_with_the_actual_failure_count(self):
  p=proposal();context='synthetic';sample={'kind':'KEY_RANGE','column':'key','lower':1,'upper':9,'provenance':'test'}
  def compiler(p,side,context,address):return {'type_cast':{'operation':'TRY_CAST','target_observed_type':'int'} if side=='SOURCE' else None}
  def execute(side,plan):
   from investigator.binding_sample import sample_address
   address=sample_address(p,sample,'NUMERIC');surface={'engine':'sql','connection':'c','object':side,'identity':'reader'}
   rows=[{'sum':12,'count':2,**({'cast_failure_count':1} if side=='SOURCE' else {})}]
   evidence={'id':side,'context_id':context,'read_address':address,'values':rows,'completeness':'COMPLETE_RESPONSE','execution_surface':surface,'surface_report':surface,'surface_report_binding':'VALUE_QUERY','surface_report_receipt_id':side,'surface_report_types':{'object':'DATABASE_CATALOG_NAME'},'surface_attestation':attest_surface(surface,surface,tuple(surface))}
   return {'status':'COMPLETED','context':context,'address':address,'quantities':{'sum':12,'count':2},'evidence':evidence}
  result=binding_verify(p,context=context,sample=sample,profile='NUMERIC',compiler=compiler,execute=execute)
  self.assertEqual(result['status'],'FALSIFIED');self.assertEqual(result['reason'],'TYPE_CAST_FAILED');self.assertEqual(result['failed_row_count'],1)
 def test_key_content_hash_is_full_order_independent_and_type_sensitive(self):
  one=quantities([{'key_value':1},{'key_value':2}],NORM,'COMPLETE_RESPONSE')
  self.assertEqual(one,quantities([{'key_value':2},{'key_value':1}],NORM,'COMPLETE_RESPONSE'))
  self.assertNotEqual(one,quantities([{'key_value':'1'},{'key_value':'2'}],NORM,'COMPLETE_RESPONSE'))
  self.assertEqual(len(one['binary_hash']),64)
  with self.assertRaisesRegex(ValueError,'Complete'):quantities([{'key_value':1}],NORM,'TRUNCATED')
 def test_key_binding_filter_uses_complete_original_witness_or_names_missing_columns(self):
  f=witnesses.TranslationTests();request,candidate=witnesses.case();proof=f.binding(request)
  self.assertEqual(proof['kind'],'KEY')
  f.run_case(cross=True)
  proof=f.binding(f.request)
  f.request['metadata'].update(key_binding=proof,key_definition_hashes=proof['declaration']['definition_hashes'])
  result=t.verify(f.proposal,f.request,cells=[None],compiler=f.compiler,execute=f.execute,budget=f.budget,cross_boundary=True)
  self.assertEqual(result['status'],'VERIFIED')
  request['metadata']['native_key_columns']=['native.k']
  with self.assertRaisesRegex(ValueError,'NO_KEY_BINDING.*native.k'):t._binding_for(request)
 def test_per_binding_key_profile_is_consumable_without_relabelling_receipts(self):
  from investigator.binding_sample import sample_address
  from investigator.binding_keys import certify
  p=proposal();p['binding_kind']='KEY';context='synthetic';sample={'kind':'KEY_RANGE','column':'key','lower':1,'upper':20,'provenance':'test'}
  def compiler(*args):return {'key_normalization':NORM}
  def execute(side,plan):
   address=sample_address(p,sample,'KEY');surface={'engine':'sqlite','connection':'test','object':'NATIVE' if side=='TARGET' else 'PROPOSED','identity':'synthetic-reader'}
   rows=[{'key_value':i} for i in range(1,5)]
   evidence={'id':'binding-'+side,'context_id':context,'read_address':address,'values':rows,'completeness':'COMPLETE_RESPONSE','execution_surface':surface,'surface_report':surface,'surface_report_binding':'VALUE_QUERY','surface_report_receipt_id':'binding-'+side,'surface_report_types':{'engine':'ENGINE_PRODUCT','object':'DATABASE'},'surface_attestation':attest_surface(surface,surface,tuple(surface))}
   return {'status':'COMPLETED','context':context,'address':address,'evidence':evidence,'quantities':quantities(rows,NORM,'COMPLETE_RESPONSE')}
  verified=binding_verify(p,context=context,sample=sample,profile='KEY',compiler=compiler,execute=execute)
  self.assertEqual(verified['status'],'VERIFIED',verified['reason'])
  f=witnesses.TranslationTests();f.run_case(cross=True);decl=f.binding(f.request)['declaration']
  columns={'native':{'id':'native.k',**p['target']},'proposed':{'id':'proposed.k','table':p['sources'][0]['table'],'column':p['expression']['column']}}
  proof=certify(decl,verified,columns)
  self.assertEqual(proof['observations'][0]['evidence']['read_address']['kind'],'BINDING_SAMPLE')
  f.request['metadata'].update(key_binding=proof,key_definition_hashes=decl['definition_hashes'])
  result=t.verify(f.proposal,f.request,cells=[None],compiler=f.compiler,execute=f.execute,budget=f.budget,cross_boundary=True)
  self.assertEqual(result['status'],'VERIFIED',result['reason'])
  self.assertEqual(t.revalidate(result),result)
 def test_static_join_keys_are_key_bindings_and_not_quantity_proofs(self):
  from investigator.code_sources import normalize
  from investigator.transformation_reader import propose
  unit=normalize('join.py',b"a=spark.table('left')\nb=spark.table('right')\nc=a.join(b,['key'],'left')\nc.write.format('delta').mode('overwrite').save('out')\n")
  result=propose(unit,schemas={'left':{'key':'int','amount':'int'},'right':{'key':'int','rate':'int'}},boundary={'from_layer':'left','to_layer':'out'},item='code',target_table='out',layers=[])
  keys=[p for p in result['proposals'] if p.get('binding_kind')=='KEY']
  self.assertEqual([p['target']['column'] for p in keys],['key'])

if __name__=='__main__':unittest.main()
