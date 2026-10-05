"""Declared copy through inferred compilation, against sealed fixture evidence."""
import copy,json,unittest
from pathlib import Path
from types import SimpleNamespace
from investigator.lineage_binding import verify
from investigator.transformation_service import select
from investigator.adapters.code_verification import VerificationRoute
from investigator.query_sql import compile_query


class RoundTripTests(unittest.TestCase):
    def test_synthetic_declared_relations_round_trip_and_wrong_expression_falsifies(self):
        import sqlite3
        from contextlib import closing
        from investigator.transformation_sql import compile_quantity
        from investigator.process_debugging import attest_surface
        from test_lineage_binding import proposal
        for operation,outputs in (('SCAN',[3,3,4]),('DEDUPE',[3,4]),('MULTIPLY',[6,6,8]),('FILTER',[4])):
            with self.subTest(operation=operation),closing(sqlite3.connect(':memory:')) as db:
                db.executescript("ATTACH DATABASE ':memory:' AS lower_data; ATTACH DATABASE ':memory:' AS upper_data; CREATE TABLE lower_data.items(amount INT); CREATE TABLE upper_data.items(amount INT); INSERT INTO lower_data.items VALUES (3),(3),(4);")
                db.executemany('INSERT INTO upper_data.items VALUES (?)',[(x,) for x in outputs])
                p=proposal();scan=p['expression']['relation']
                if operation=='DEDUPE':p['expression']['relation']={'kind':'DEDUPE','input':scan,'keys':['amount']}
                if operation=='MULTIPLY':p['expression']['relation']={'kind':'PROJECT','input':scan,'columns':[{'name':'amount','expression':{'kind':'MULTIPLY','left':{'kind':'COLUMN','name':'amount'},'right':{'kind':'LITERAL','value':2}}}]}
                if operation=='FILTER':p['expression']['relation']={'kind':'FILTER','input':scan,'predicate':{'kind':'GT','left':{'kind':'COLUMN','name':'amount'},'right':{'kind':'LITERAL','value':3}}}
                catalog={name:{'id':name,'metadata':{'schema_name':schema,'name':'items','type_desc':'USER_TABLE','columns':[{'name':'amount','data_type':'int'}]}}
                    for name,schema in [('input-table','lower_data'),('output-table','upper_data')]}
                def compiler(binding,side,*args):
                    relation=binding['expression']['relation'] if side=='SOURCE' else {'kind':'SCAN','table':'output-table','columns':['amount']}
                    return compile_quantity(relation,'amount',catalog)
                def execute(side,query):
                    surface={'engine':'sqlite','connection':'memory-session','object':'upper_data' if side=='TARGET' else 'lower_data','identity':'synthetic-reader'}
                    evidence={'id':side,'execution_surface':surface,'surface_report':surface,'surface_report_binding':'VALUE_QUERY','surface_report_receipt_id':side,'surface_report_types':{'engine':'ENGINE_PRODUCT','object':'DATABASE'}}
                    evidence['surface_attestation']=attest_surface(surface,surface,tuple(surface))
                    return {'status':'COMPLETED','context':'synthetic','cell':{'id':'sample'},'precision':{'state':'EXACT'},'evidence':evidence,'quantity':{'state':'NUMBER','value':str(db.execute(query).fetchone()[0])}}
                options={'context':'synthetic','cell':{'id':'sample'},'precision':{'state':'EXACT'},'compiler':compiler,'execute':execute}
                declared=verify(p,**options)
                p.update(extractor='MODEL',confidence=0.1)
                inferred=verify(p,**options)
                self.assertEqual(declared['status'],'VERIFIED');self.assertEqual(inferred['status'],'VERIFIED')
                self.assertEqual([o['quantity'] for o in declared['observations']],[o['quantity'] for o in inferred['observations']])
                if operation=='SCAN':
                    p['expression']['relation']={'kind':'PROJECT','input':scan,'columns':[{'name':'amount','expression':{'kind':'MULTIPLY','left':{'kind':'COLUMN','name':'amount'},'right':{'kind':'LITERAL','value':2}}}]}
                    self.assertEqual(verify(p,**options)['status'],'FALSIFIED')

    def test_declared_fixture_binding_round_trips_through_inferred_route(self):
        record=json.loads((Path(__file__).parent/'fixtures/round-six-declared-copy-verification.json').read_text(encoding='utf-8'))
        original=record['verification'];p=copy.deepcopy(original['proposal'])
        p.update(extractor='MODEL',confidence=0.5)
        objects={}
        for side,table in (('TARGET',p['target']['table']),('SOURCE',p['sources'][0]['table'])):
            source=side=='SOURCE';request=record['requests'][1 if source else 0]
            objects[table]={'asset_id':table,'connection':'application-server' if source else 'fabric-server',
                'database':request['database'],'surface':'APPLICATION_SQL' if source else 'FABRIC_SQL',
                'catalog':{'id':table,'metadata':{'name':'stock_movements_round_two_20261003',
                    'schema_name':'app' if source else 'dbo','type_desc':'USER_TABLE',
                    'columns':[{'name':'units','data_type':'bigint'}]}}}
        process=SimpleNamespace(model={'context_id':original['context']},config={
            'sql':{'server':'application-server'},'fabric':{'sql_reader':{'server':'fabric-server'}}})
        route=VerificationRoute(process,objects=objects,context=original['context'],
            measure_id=original['cell']['measure_id'],quantity_column='units',restrictions=[])
        seen=[]
        def execute(side,plan):
            # No values can be replayed unless the inferred compiler produces
            # the same governed statement the recorded physical request used.
            query=compile_query(plan['compiled']['query'],plan['compiled']['catalog'],max_rows=20)['query']
            index=0 if side=='TARGET' else 1
            if side=='SOURCE':
                query="SELECT q.*, CURRENT_USER AS [__application_identity], CAST(SERVERPROPERTY('EngineEdition') AS int) AS [__application_engine], DB_NAME() AS [__application_object] FROM ("+query+") AS q"
            self.assertEqual(query,record['requests'][index]['query'])
            seen.append(side);return copy.deepcopy(original['observations'][index])
        result=verify(p,context=original['context'],cell=original['cell'],precision=original['precision'],
            compiler=route.compile,execute=execute)
        self.assertEqual(seen,['TARGET','SOURCE']);self.assertEqual(result['status'],'VERIFIED')
        self.assertEqual([o['quantity'] for o in result['observations']],[o['quantity'] for o in original['observations']])
        loc=p['location']
        selected=select(declared=[],inferred=[result],current_hashes={(loc['item'],loc['path']):loc['content_hash']},
            boundary=p['boundary'],target_column=p['target']['column'],
            context=result['context'],cell=result['cell'],precision=result['precision'])
        self.assertEqual(selected['status'],'RESOLVED')
        self.assertEqual(selected['provenance'],'INFERRED_FROM_CODE')

if __name__=='__main__':unittest.main()
