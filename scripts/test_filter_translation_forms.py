import unittest,copy,sqlite3
from unittest.mock import Mock
from sqlglot import parse_one,exp
from investigator.adapters.translation_filter_forms import dax_form,dax_quantity,sql_filter
from investigator import translation_proposer as t
from investigator.verification_budget import VerificationBudget
import test_translation_native as fixture


class FilterFormTests(unittest.TestCase):
 def setUp(self):
  self.f=fixture.NativeTranslationTests();self.f.setUp();self.addCleanup(self.f.doCleanups)
  self.request,self.proposal,self.route=self.f.route_case(['North'])
  self.catalog=self.f.model['context']['model_assets']
 def test_mislabelled_table_is_refused_before_budget_or_read(self):
  self.proposal.update(expression='KEEPFILTERS(VALUES(Customers[Region]))',form='PREDICATE')
  budget=Mock()
  result=t.verify(self.proposal,self.request,cells=[None],compiler=self.route.compile,execute=self.route.execute,budget=budget)
  self.assertEqual(result['status'],'UNVERIFIED');self.assertIn('FILTER_FORM_MISMATCH',result['reason'])
  budget.read.assert_not_called();self.assertEqual(self.f.requests,[])
 def test_predicate_and_table_forms_are_wrapped_and_attested(self):
  for form,expression in [('PREDICATE','Customers[Region]="North"'),('TABLE_FILTER','KEEPFILTERS(FILTER(Customers,Customers[Region]="North"))')]:
   with self.subTest(form=form):
    p={**self.proposal,'expression':expression,'form':form}
    result=t.verify(p,self.request,cells=[None],compiler=self.route.compile,execute=self.route.execute,budget=VerificationBudget({},1,record=lambda _:None))
    self.assertEqual(result['status'],'VERIFIED',result['reason']);self.assertEqual(t.revalidate(result),result)
    query=self.f.requests[-1]['query'];self.assertIn('SELECTCOLUMNS',query)
    if form=='TABLE_FILTER':self.assertIn('CALCULATETABLE',query);self.assertNotIn('FILTER(\'Customers\',KEEPFILTERS',query)
 def test_unknown_form_and_scalar_nonpredicate_are_refused(self):
  for expression,form in [('VALUES(Customers[Region])','UNKNOWN'),('1','PREDICATE'),('Customers[Region]="North"','TABLE_FILTER')]:
   with self.assertRaises(ValueError):dax_form(expression,form,self.catalog)
  with self.assertRaises(ValueError):dax_form('VALUES(Customers[Region])=1','PREDICATE',self.catalog)
 def test_fresh_producer_cannot_omit_form_but_old_sealed_proposal_is_readable(self):
  t.validate(self.proposal,self.request)
  proposer=Mock();proposer.propose.return_value=self.proposal
  with self.assertRaises(Exception):t.propose(self.request,proposer,lambda _,fn:fn())
 def test_form_schema_does_not_reduce_the_retained_object_directory(self):
  from investigator.adapters.translation_model import Provider
  from investigator.onboarding import encoded
  generate=Mock(return_value=({**self.proposal,'form':'PREDICATE'},None))
  provider=Provider(options={},generate=generate)
  before=provider.input(self.request);provider.propose(self.request,t.SCHEMA)
  after=generate.call_args.args[0]
  self.assertEqual(encoded(before),encoded(after))
  self.assertEqual(before['metadata']['objects'],after['metadata']['objects'])
  self.assertEqual(len(after['metadata']['objects']),2)
 def test_sql_predicate_where_and_table_filter_join_preserve_scope_and_multiplicity(self):
  catalog=[{'id':'items','metadata':{'schema_name':'dbo','name':'Items','type_desc':'USER_TABLE','columns':[{'name':'key','data_type':'int'},{'name':'value','data_type':'int'},{'name':'scope','data_type':'int'}]}}]
  base='SELECT dbo.Items.[key],dbo.Items.[value] FROM dbo.Items WHERE scope=1'
  db=sqlite3.connect(':memory:');self.addCleanup(db.close);db.execute('CREATE TABLE Items(key int,value int,scope int)');db.executemany('INSERT INTO Items VALUES(?,?,?)',[(1,12,1),(2,20,1),(3,30,0),(2,20,0)])
  for form,expression in [('PREDICATE','[value]>=20'),('TABLE_FILTER','SELECT [key] AS selected_key FROM dbo.Items WHERE [value]>=20')]:
   text=sql_filter(base,expression,form,key_pairs=[('key','selected_key')],catalog=catalog)
   tree=parse_one(text,read='tsql')
   for table in tree.find_all(exp.Table):table.set('db',None)
   # Qualifiers emitted by base schema are removed only for SQLite execution.
   for col in tree.find_all(exp.Column):col.set('db',None)
   self.assertEqual(db.execute(tree.sql(dialect='sqlite')).fetchall(),[(2,20)])
  for form,expression in [('PREDICATE','SELECT [key] FROM dbo.Items'),('TABLE_FILTER','[value]>=20')]:
   with self.assertRaisesRegex(ValueError,'FILTER_FORM_MISMATCH'):sql_filter(base,expression,form,key_pairs=[('key','key')],catalog=catalog)


if __name__=='__main__':unittest.main()
