import unittest,copy,json
from test_graph_code_columns import CodeColumnsTests

CREATE='CREATE PROCEDURE app.build AS BEGIN DELETE FROM app.result; INSERT INTO app.result(amount) SELECT amount FROM app.source; END;'
class Procedures(unittest.TestCase):
 def build(self,scripts):
  h=CodeColumnsTests();return h.build(h.scripts(['CREATE TABLE app.result(amount int);',*scripts]))
 def test_called_native_procedure_carries_exact_table_and_column_producer(self):
  g=self.build([CREATE,'EXEC app.build;']);nodes={n['id']:n for n in g['nodes']};root=next(n['id']for n in nodes.values()if n['kind']=='TABLE'and n['label']=='app.result')
  steps=[e['target']for e in g['edges']if e['source']==root and e['kind']=='DERIVED_IN_STEP'];self.assertEqual(len(steps),1)
  upstream=[nodes[e['target']]['label']for e in g['edges']if e['source']==steps[0]and e['kind']=='COMPUTED_FROM'];self.assertEqual(upstream,['app.source'])
  p=next(n for n in nodes.values()if n['kind']=='PROCEDURE');self.assertFalse(p['properties']['execution_established']);self.assertEqual(p['provenance']['span']['path'],'/properties/activities/0/typeProperties/scripts/1/text')
  self.assertTrue(any(e['kind']=='COMPUTED_FROM'and nodes[e['source']]['label']=='amount'and nodes[e['target']]['label']=='amount'for e in g['edges']))
 def test_no_call_ambiguous_body_parameters_early_call_or_dynamic_call_never_select(self):
  for scripts in ([CREATE],[CREATE,CREATE,'EXEC app.build;'],['EXEC app.build;',CREATE],[CREATE,'EXEC app.build @x=1;'],[CREATE,"EXEC(N'app.build');"],[CREATE.replace('DELETE FROM app.result;','DELETE FROM app.source;'),'EXEC app.build;'],[CREATE.replace('DELETE FROM app.result;','DELETE FROM app.result WHERE amount>0;'),'EXEC app.build;']):
   with self.subTest(scripts=scripts):
    g=self.build(scripts);self.assertFalse(any(n['properties'].get('basis')=='EXACT_SAME_ACTIVITY_CREATE_AND_EXECUTE'for n in g['nodes']))
 def test_same_names_in_another_warehouse_do_not_bind(self):
  h=CodeColumnsTests();a=h.scripts(['CREATE TABLE app.result(amount int);',CREATE,'EXEC app.build;']);a[0]['metadata']['id']='different';g=h.build(a)
  self.assertFalse(any(n['kind']=='PROCEDURE'for n in g['nodes']))
  mismatch=h.scripts(['CREATE TABLE app.result(amount int);',CREATE,'EXEC app.build;']);part=next(a for a in mismatch if a['kind']=='DefinitionPart');doc=json.loads(part['metadata']['content']);doc['properties']['activities'][0]['typeProperties']['database']='Some other database';part['metadata']['content']=json.dumps(doc);g=h.build(mismatch)
  self.assertFalse(any(n['kind']=='PROCEDURE'for n in g['nodes']))
 def test_native_batch_of_two_explicit_executes_keeps_both_calls(self):
  g=self.build([CREATE,'CREATE PROCEDURE app.second AS BEGIN DELETE FROM app.result; INSERT INTO app.result(amount) SELECT amount FROM app.source; END;','EXEC app.build; EXEC app.second;'])
  self.assertEqual({n['label']for n in g['nodes']if n['kind']=='PROCEDURE'},{'app.build','app.second'})
 def test_missing_connection_and_duplicate_native_object_addresses_never_choose_one(self):
  from test_estate_graph_static import asset
  h=CodeColumnsTests();base=h.scripts(['CREATE TABLE app.result(amount int);',CREATE,'EXEC app.build;'])
  ambiguous=copy.deepcopy(base);ambiguous.extend([asset('other','WarehouseTable','app.source','w'),asset('other/c','WarehouseColumn','amount','other')]);g=h.build(ambiguous)
  self.assertFalse(any(n['label']=='Declared procedure INSERT SELECT'for n in g['nodes']))
  missing=copy.deepcopy(base);missing[0]['metadata']={};part=next(a for a in missing if a['kind']=='DefinitionPart');import json
  doc=json.loads(part['metadata']['content']);doc['properties']['activities'][0]['linkedService']={};part['metadata']['content']=json.dumps(doc);g=h.build(missing)
  self.assertFalse(any(n['kind']=='PROCEDURE'for n in g['nodes']))
if __name__=='__main__':unittest.main()
