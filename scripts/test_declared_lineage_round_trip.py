"""Declared copy through inferred compilation, against sealed fixture evidence."""
import copy,json,unittest
from pathlib import Path
from types import SimpleNamespace
from investigator.lineage_binding import verify
from investigator.transformation_service import select
from investigator.adapters.code_verification import VerificationRoute
from investigator.query_sql import compile_query


class RoundTripTests(unittest.TestCase):
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
