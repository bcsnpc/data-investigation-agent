import copy
import sqlite3
import unittest
from unittest.mock import Mock

from cloud_value_verifier import Refused, compile_layer, declared_producers, execute, measure_program


def fixture(expression='SUM(Facts[amount])'):
    members = []
    for table, fields in {'Facts': ['amount','dim_id','status'], 'Dimension': ['id','name','price']}.items():
        members.append({'id': table, 'kind': 'SemanticTable', 'name': table})
        members += [{'id': table+'.'+field, 'kind':'SemanticColumn', 'name':field, 'parent_id':table, 'metadata':{'dataType':'string' if field in ('name','status') else 'int64'}} for field in fields]
    members += [{'id':'measure','kind':'Measure','name':'Result','parent_id':'Facts','metadata':{'expression':expression}},
        {'id':'relationship','kind':'SemanticRelationship','name':'r','metadata':{'fromTable':'Facts','fromColumn':'dim_id','toTable':'Dimension','toColumn':'id'}}]
    model = {'context':{'model_assets':members}}
    mapping = {'layer_id':'GOLD','endpoint':{'surface':'FABRIC_SQL','object':'catalog'},
        'objects':{'fact':{'schema':'main','table':'facts','columns':['amount','dim_id','status']},
                   'dim':{'schema':'main','table':'dimension','columns':['id','name','price']}},
        'columns':{a['id']:{'object_id':'fact' if a['parent_id']=='Facts' else 'dim','column':a['name']} for a in members if a['kind']=='SemanticColumn'},
        'relationships':['relationship']}
    return model,mapping


def restriction(field, values): return {'field_id':field,'operator':'IN','values':values}


class CompilerTests(unittest.TestCase):
    def test_overlap_intersects_one_predicate_per_column(self):
        model,mapping=fixture(); program=measure_program(model,'measure')
        compiled=compile_layer(model,program,[restriction('Facts.status',['A','B']),restriction('Facts.status',['B'])],mapping)
        self.assertIn("[status] IN (N'B')",compiled['statement'])
        self.assertEqual(compiled['statement'].count('[status] IN'),1)

    def test_empty_intersection_is_explicit_filter(self):
        model,mapping=fixture()
        compiled=compile_layer(model,measure_program(model,'measure'),[restriction('Facts.status',['A']),restriction('Facts.status',['B'])],mapping)
        self.assertIn('WHERE 1=0',compiled['statement'])

    def test_dimension_predicate_maps_declared_relationship_not_guessed_id(self):
        model,mapping=fixture()
        compiled=compile_layer(model,measure_program(model,'measure'),[restriction('Dimension.name',["O'North"])],mapping)
        self.assertIn('EXISTS (SELECT 1 FROM [main].[dimension] d WHERE d.[id]=f.[dim_id]',compiled['statement'])
        self.assertIn("N'O''North'",compiled['statement'])
        self.assertNotIn('dim_id IN',compiled['statement'])

    def test_dimension_map_missing_or_ambiguous_refuses(self):
        model,mapping=fixture();mapping['relationships']=[]
        with self.assertRaisesRegex(Refused,'FILTER_RELATIONSHIP_UNRESOLVED'):
            compile_layer(model,measure_program(model,'measure'),[restriction('Dimension.name',['North'])],mapping)

    def test_unmapped_column_refuses_no_dropped_scope(self):
        model,mapping=fixture();del mapping['columns']['Facts.status']
        with self.assertRaisesRegex(Refused,'UNMAPPED_SCOPE_COLUMN'):
            compile_layer(model,measure_program(model,'measure'),[restriction('Facts.status',['A'])],mapping)

    def test_unknown_measure_refuses(self):
        model,_=fixture('CALCULATE(SUM(Facts[amount]),ALL(Facts))')
        with self.assertRaisesRegex(Refused,'UNSUPPORTED_MEASURE_SEMANTICS'): measure_program(model,'measure')

    def test_mrr_removefilters_not_carried_and_duplicate_guard_retained(self):
        expression='CALCULATE(SUMX(FILTER(Facts, Facts[status] = "ACTIVE"), RELATED(Dimension[price])), REMOVEFILTERS(Dimension))'
        model,mapping=fixture(expression);program=measure_program(model,'measure')
        compiled=compile_layer(model,program,[restriction('Dimension.name',['Selected plan'])],mapping)
        self.assertNotIn('Selected plan',compiled['statement'])
        self.assertEqual(compiled['translations'][0]['operation'],'REMOVED_BY_MEASURE_REMOVEFILTERS')
        self.assertIn('HAVING COUNT_BIG(*)>1',compiled['statement'])
        self.assertIn('LEFT JOIN',compiled['statement'])
        self.assertIn("f.[status]=N'ACTIVE'",compiled['statement'])
        self.assertIn('SUM(p.[price])',compiled['statement'])

    def test_additive_query_preserves_multiplicity_and_blank(self):
        model,mapping=fixture();db=sqlite3.connect(':memory:');self.addCleanup(db.close)
        db.executescript('CREATE TABLE facts(amount,dim_id,status); CREATE TABLE dimension(id,name,price); INSERT INTO facts VALUES(3,1,"A"),(3,1,"A"); INSERT INTO dimension VALUES(1,"North",10),(1,"North",10);')
        query=compile_layer(model,measure_program(model,'measure'),[restriction('Dimension.name',['North'])],mapping)['statement'].replace("N'","'")
        self.assertEqual(db.execute(query).fetchone()[0],6)
        query=compile_layer(model,measure_program(model,'measure'),[restriction('Facts.status',[])],mapping)['statement']
        self.assertIsNone(db.execute(query).fetchone()[0])

    def test_native_date_text_only_for_declared_string_column(self):
        from investigator.adapters.report_predicates import quantity_query, Refusal
        model,_=fixture()
        field=next(a for a in model['context']['model_assets'] if a['id']=='Facts.status')
        query=quantity_query(model,'measure',[restriction('Facts.status',['2026-09-15'])])
        self.assertIn('"2026-09-15"',query)
        field['metadata']['dataType']='dateTime'
        with self.assertRaisesRegex(Refusal,'RENDER_VALUE_TYPE_dateTime'):
            quantity_query(model,'measure',[restriction('Facts.status',['2026-09-15'])])

    def test_producer_alternatives_do_not_invent_last_execution(self):
        graph={'nodes':[{'id':'table','kind':'TABLE','properties':{'asset_id':'physical'}},
            *[{'id':str(i),'kind':'QUERY_STEP','owner':'pipeline'+str(i),'properties':{'expression':'CREATE TABLE x AS SELECT a FROM y','language':'TSQL','execution_established':False},'provenance':{'definition_hash':str(i)}} for i in range(2)]],
            'edges':[{'source':'table','target':str(i),'kind':'DERIVED_IN_STEP'} for i in range(2)]}
        result=declared_producers(graph,['table'])[0]
        self.assertEqual(len(result['writers']),2);self.assertFalse(result['last_writer_established'])
        self.assertTrue(all(not w['execution_established'] for w in result['writers']))


class NativeFirstTests(unittest.TestCase):
    def plan(self):
        return {'native_statement':'EVALUATE ROW("quantity",[Result])','layers':[{'layer_id':'GOLD','statement':'SELECT SUM(amount) quantity FROM x'}],
            'tolerance':{'kind':'ABSOLUTE','value':'0','source':'authored exact'},'qualifications':['SNAPSHOT_UNVERIFIED']}

    def test_dax_401_retained_exact_before_any_lower_read(self):
        original={'status':'FAILED','http_status':401,'error':{'type':'HTTPError','message':'Unauthorized'},'provider_body':'{"error":"unauthorized"}'}
        lower=Mock();records=[]
        result=execute(self.plan(),lambda q:original,lower,records.append)
        self.assertEqual(result['reason'],'NATIVE_VISUAL_READ_FAILED');self.assertEqual(result['layer'],'SEMANTIC')
        lower.assert_not_called();self.assertEqual(records[0]['receipt'],original)

    def test_missing_value_is_not_blank(self):
        lower=Mock();result=execute(self.plan(),lambda q:{'status':'SUCCEEDED'},lower,lambda r:None)
        self.assertEqual(result['reason'],'NATIVE_VALUE_NOT_OBTAINED');lower.assert_not_called()

    def test_measured_blank_compares_as_result(self):
        result=execute(self.plan(),lambda q:{'status':'SUCCEEDED','value':None},lambda q:{'status':'SUCCEEDED','value':None},lambda r:None)
        self.assertEqual(result['status'],'VALUES_AGREE_UNDER_MAPPING');self.assertFalse(result['confidence_awarded'])
        result=execute(self.plan(),lambda q:{'status':'SUCCEEDED','value':None},lambda q:{'status':'SUCCEEDED','value':0},lambda r:None)
        self.assertEqual(result['reason'],'UNEXPLAINED_VALUE_DIFFERENCE')

    def test_duplicate_lookup_refuses_even_matching_value(self):
        result=execute(self.plan(),lambda q:{'status':'SUCCEEDED','value':5},lambda q:{'status':'SUCCEEDED','value':5,'duplicate_lookup_keys':1},lambda r:None)
        self.assertEqual(result['reason'],'RELATED_LOOKUP_KEYS_NOT_UNIQUE')

    def test_mrr_guard_absence_is_not_unique(self):
        plan=self.plan();plan['layers'][0]['requires_lookup_guard']=True
        result=execute(plan,lambda q:{'status':'SUCCEEDED','value':5},lambda q:{'status':'SUCCEEDED','value':5},lambda r:None)
        self.assertEqual(result['reason'],'RELATED_LOOKUP_GUARD_NOT_OBTAINED')

    def test_unexplained_difference_refuses_never_qualitative_story(self):
        result=execute(self.plan(),lambda q:{'status':'SUCCEEDED','value':16},lambda q:{'status':'SUCCEEDED','value':8},lambda r:None)
        self.assertEqual(result['reason'],'UNEXPLAINED_VALUE_DIFFERENCE')
        self.assertEqual(result['comparisons'],[{'layer':'GOLD','previous':16,'value':8,'equal':False}])

    def test_no_lower_layers_never_awards_vacuous_success(self):
        plan=self.plan();plan['layers']=[]
        self.assertEqual(execute(plan,lambda q:{'status':'SUCCEEDED','value':5},Mock(),lambda r:None)['reason'],'NO_DECLARED_LOWER_MAPPING')

    def test_compile_refusal_occurs_after_native_probe(self):
        plan=self.plan();plan['layers']=[{'layer_id':'SILVER','compilation_error':'UNMAPPED_SCOPE_COLUMN:opaque'}]
        native=Mock(return_value={'status':'SUCCEEDED','value':5});lower=Mock()
        result=execute(plan,native,lower,lambda r:None)
        native.assert_called_once();lower.assert_not_called();self.assertEqual(result['layer'],'SILVER')


if __name__=='__main__':unittest.main()
