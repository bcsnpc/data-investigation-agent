import copy
import os
import unittest
from unittest.mock import Mock,patch
from investigator.adapters.graph_sql_changes import FabricSqlChanges,request,compiled_control_objects
from investigator.live_gateway import configured,authorize_sql_payload,GatewayDenied

OBJ={'asset_id':'sql://server/db/object/1','connection':'server','database':'db',
    'catalog':{'metadata':{'schema_name':'dbo','name':'Revenue'}}}
CONFIG={'fabric':{'sql_reader':{'server':'server','account':'reader'}}}
POLICY={'version':1,'live_enabled':True,'identities':{'reader':{'sql':[{'server':'server','database':'db',
    'objects':['dbo.Revenue'],'read_only':True,'row_cap':251,'timeout_seconds':30,'controls':['CATALOG']}]}}}


class SqlChangeTests(unittest.TestCase):
    def fingerprint(self):
        return [{'object_type':'V','modified_at':'2026-10-13T00:00:00','column_id':1,'column_name':'amount','data_type':'decimal','collation_name':None}]
    def answer(self,rows):return {'read_only_verified':True,'surface_report':{'identity':'reader','object':'db','engine':'Microsoft Azure SQL Data Warehouse'},'rows':rows}
    def test_only_changed_owner_fetches_definition_and_schema_date_not_freshness(self):
        import tempfile
        from pathlib import Path
        from investigator.shared_state import SharedState,sha
        from investigator.estate_graph_repository import GraphRepository
        from investigator.estate_graph_incremental import IncrementalScanner
        from investigator.adapters.estate_graph_static import extract
        def execute(database,req):
            return self.answer(self.fingerprint() if 'column_id' in req['result_columns'] else [{'object_type':'V','modified_at':'2026-10-13T00:00:00','definition_bytes':len('SELECT 1 AS amount'.encode('utf-16-le')),'definition':'SELECT 1 AS amount'}])
        transport=Mock(side_effect=execute);source=FabricSqlChanges('sql',CONFIG,{'owner':OBJ},transport)
        sink=lambda raw:{'sha256':__import__('hashlib').sha256(raw).hexdigest(),'bytes':len(raw),'uri':'blob:definition'}
        with tempfile.TemporaryDirectory()as folder:
            repo=GraphRepository(SharedState.offline(Path(folder)/'state.db'));repo.migrate()
            scanner=IncrementalScanner(repo,source,lambda estate,owner,at,payload:extract(estate,payload['assets'],sink,owner=owner,observed_at=at))
            scanner.run('estate','2026-10-13T00:00:00Z');self.assertEqual(transport.call_count,2)
            transport.reset_mock();scanner.run('estate','2026-10-13T01:00:00Z')
            self.assertEqual(transport.call_count,1)
            self.assertIn('column_id',transport.call_args.args[1]['result_columns'])
            self.assertTrue(all('timing'not in n['properties']for n in repo.records('estate')['nodes']))
    def test_surface_identity_and_visibility_fail_closed(self):
        for answer in [self.answer([]),{**self.answer(self.fingerprint()),'read_only_verified':False},
            {**self.answer(self.fingerprint()),'surface_report':{'identity':'admin','object':'db','engine':'Microsoft Azure SQL Data Warehouse'}}]:
            with self.subTest(answer=answer),self.assertRaises(RuntimeError):
                FabricSqlChanges('sql',CONFIG,{'owner':OBJ},Mock(return_value=answer)).list_changes()
    def test_changed_version_between_schema_and_definition_refused(self):
        response=self.answer([{'object_type':'V','modified_at':'changed','definition_bytes':1,'definition':'x'}])
        source=FabricSqlChanges('sql',CONFIG,{'owner':OBJ},Mock(side_effect=[self.answer(self.fingerprint()),response]))
        source.list_changes()
        with self.assertRaisesRegex(RuntimeError,'CHANGED_DURING'):source.fetch('owner')
    def test_truncated_definition_and_duplicate_columns_refuse(self):
        response=self.answer([{'object_type':'V','modified_at':'2026-10-13T00:00:00','definition_bytes':90,'definition':'SELECT 1'}])
        source=FabricSqlChanges('sql',CONFIG,{'owner':OBJ},Mock(side_effect=[self.answer(self.fingerprint()),response]))
        source.list_changes()
        with self.assertRaisesRegex(RuntimeError,'BYTES_DIFFER'):source.fetch('owner')
        source=FabricSqlChanges('sql',CONFIG,{'owner':OBJ},Mock(return_value=self.answer(self.fingerprint()*2)))
        with self.assertRaisesRegex(ValueError,'DUPLICATE_COLUMN'):source.list_changes()
    def test_definition_permission_denied_or_oversized_is_not_empty_logic(self):
        for size in (None,262145):
            response=self.answer([{'object_type':'V','modified_at':'2026-10-13T00:00:00','definition_bytes':size,'definition':None}])
            source=FabricSqlChanges('sql',CONFIG,{'owner':OBJ},Mock(side_effect=[self.answer(self.fingerprint()),response]))
            source.list_changes()
            with self.assertRaisesRegex(RuntimeError,'PERMISSION_OR_SIZE'):source.fetch('owner')
    def test_exact_compiler_gateway_keeps_object_scope_and_rejects_query_changes(self):
        with patch.dict(os.environ,{'DIA_GATEWAY_SQL_IDENTITY':'reader','DIA_LIVE_ACCESS_DISABLED':'0'}),configured(POLICY):
            for kind in ('fingerprint','definition'):
                payload={**request(OBJ,kind),'server':'server','database':'db'}
                self.assertTrue(authorize_sql_payload(payload)['require_read_only'])
                changed={**payload,'query':payload['query']+'; SELECT 1'}
                self.assertIsNone(compiled_control_objects(changed))
                with self.assertRaises(GatewayDenied):authorize_sql_payload(changed)
                other=copy.deepcopy(OBJ);other['catalog']['metadata']['name']='Other'
                with self.assertRaises(GatewayDenied):authorize_sql_payload({**request(other,kind),'server':'server','database':'db'})
    def test_missing_catalog_control_still_refuses_and_never_grants_sys_views(self):
        policy=copy.deepcopy(POLICY);policy['identities']['reader']['sql'][0]['controls']=[]
        with patch.dict(os.environ,{'DIA_GATEWAY_SQL_IDENTITY':'reader','DIA_LIVE_ACCESS_DISABLED':'0'}),configured(policy):
            with self.assertRaises(GatewayDenied):authorize_sql_payload({**request(OBJ,'definition'),'server':'server','database':'db'})


if __name__=='__main__':unittest.main()
