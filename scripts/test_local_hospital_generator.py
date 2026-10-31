"""Source-generator checks, run by the existing Validation checkout job."""
from contextlib import closing
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT)=='/app'and not(ROOT/'fixtures/hospital').exists():
    raise unittest.SkipTest('Hospital builder intentionally excluded from DIA image; tested by checkout Validation')
sys.path.insert(0,str(ROOT))
from fixtures.hospital.generate import generate,Settings
from fixtures.hospital.schema import ddl
from fixtures.hospital.verify import verify
from fixtures.hospital.marts import build_local,warehouse_sql,projection_columns
from fixtures.hospital.models import model
from fixtures.hospital.artifacts import pipeline,notebook,nightly_pipeline,reference_dataflow,warehouse_item_binding
from fixtures.hospital.models import build as build_models
from fixtures.hospital.reports import build as build_reports
from fixtures.hospital.validate_assets import validate as validate_assets
from fixtures.hospital.owner_sql import bulk_metadata
from fixtures.hospital.reconcile_sources import hash_rows
from fixtures.hospital.owner_warehouse import routed_address,named_instance_routing
from fixtures.hospital.publish import definition_parts,update
from fixtures.hospital.owner_fabric import OwnerFabric
from fixtures.hospital.profile import profile


class HospitalGeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        cls.path=Path(cls.temp.name)
        cls.a=generate(cls.path/'a',Settings(patients=100,encounters=600,orders=3600))
        cls.b=generate(cls.path/'b',Settings(patients=100,encounters=600,orders=3600))
        cls.marts=build_local(cls.path/'a')

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def test_deterministic_all_source_hashes(self):self.assertEqual(self.a,self.b)

    def test_population_profile_uses_actual_rows_and_separates_denominators(self):
        measured=profile(self.path/'a',self.path/'a')
        self.assertEqual(sum(r[1]for r in measured['order_type_mix']),3600)
        self.assertEqual(sum(r[1]for r in measured['original_payer_mix_encounters']),600)
        self.assertAlmostEqual(sum(r[2]for r in measured['original_payer_mix_encounters']),1)
        self.assertTrue(all(0<=r[1]<=1 for r in measured['occupancy_fraction_by_facility']))
        self.assertGreater(measured['ed_door_provider_median_minutes'],0)

    def test_lakehouse_sink_uses_native_overwrite_and_upsert_properties(self):
        copies=[a for a in pipeline('clinical','ws','lh','source','warehouse')['properties']['activities']if a['type']=='Copy']
        reference=next(a for a in copies if a['name']=='copy_facility')['typeProperties']['sink']
        incremental=next(a for a in copies if a['name']=='copy_order_line')['typeProperties']['sink']
        self.assertEqual(reference['tableActionOption'],'OverwriteSchema')
        self.assertEqual(incremental['tableActionOption'],'Upsert')
        self.assertEqual(incremental['upsertSettings']['keys'],['id'])

    def test_audit_commit_is_retryable_without_cross_pipeline_watermark_deletes(self):
        activities=pipeline('clinical','ws','lh','source','warehouse')['properties']['activities']
        commit=next(a for a in activities if a['name']=='commit_encounter')
        sql=commit['typeProperties']['scripts'][0]['text']
        self.assertEqual(commit['policy']['retry'],3)
        self.assertIn('IF NOT EXISTS',sql)
        self.assertNotIn('XACT_ABORT',sql)
        self.assertNotIn('DELETE FROM dbo.load_watermark',sql)
        self.assertIn('INSERT INTO dbo.load_watermark',sql)

    def test_native_update_preserves_before_and_requires_matching_readback(self):
        import base64,json
        folder=self.path/'publish-update';folder.mkdir(exist_ok=True)
        (folder/'pipeline-content.json').write_text('{"properties":{"activities":[]}}')
        class FakeOwner:
            state={'workspace':{'id':'d237966c-b0b6-4123-bc89-e69643f4bf1f'},'published':{'pl_clinical':{'item':{'id':'item'},'definition_sha256':'old'}}}
            def call(self,path,body=None):
                if path.endswith('/updateDefinition'):self.parts=body['definition']['parts'];return {}
                return {'definition':{'parts':getattr(self,'parts',[])}}
            def save(self):pass
        owner=FakeOwner()
        result=update(owner,'pl_clinical',folder,['pipeline-content.json'],'native key fix')
        self.assertEqual(owner.state['definition_updates'][0]['before'],{'definition':{'parts':[]}})
        self.assertEqual(result,owner.state['definition_updates'][0]['after'])
        with self.assertRaisesRegex(ValueError,'reason required'):update(owner,'pl_clinical',folder,['pipeline-content.json'],'')

    def test_native_visual_queries_cover_bookmarks_and_bound_patient_windows(self):
        from fixtures.hospital.visual_queries import report_queries
        root=self.path/'query-reports';build_reports(root=root)
        queries=report_queries(root/'HealthNetOperations.Report')
        self.assertTrue(any(r['context']=='North ED only' and 'TREATAS' in (r['query']or'') for r in queries))
        self.assertTrue(any('masked_mrn' in (r['query']or'') for r in queries))
        self.assertTrue(all('TOPN(100,T' in r['query'] and '__baseline_total_rows' in r['query'] for r in queries if r['query']))
        self.assertEqual(len({r['visual_id']for r in queries}),len(queries)//2)

    def test_warehouse_timestamp_types_and_empty_schema_column_derivation(self):
        names=projection_columns()
        with closing(sqlite3.connect(self.path/'a/hn_dw.sqlite'))as db:
            for table,actual in names.items():
                self.assertEqual(actual,[r[1]for r in db.execute('PRAGMA table_info(['+table+'])')])
        sql=warehouse_sql()
        self.assertIn('CONVERT(DATETIME2(6),src.[admit_utc]) [admit_utc]',sql)
        self.assertIn('CONVERT(DATETIME2(6),src.[submitted_at]) [submitted_at]',sql)
        self.assertNotIn('TRY_CONVERT',sql)

    def test_async_definition_update_has_no_result_resource(self):
        import json
        from unittest.mock import patch
        owner=object.__new__(OwnerFabric);owner.token='test-only'
        owner.path=self.path/'owner-update-fake.json';owner.state={'receipts':[]}
        class Response:
            def __init__(self,status,body,headers=None):self.status=status;self.body=body;self.headers=headers or{}
            def read(self):return json.dumps(self.body).encode()
            def __enter__(self):return self
            def __exit__(self,*args):pass
        replies=[Response(202,{}, {'Location':'https://api.fabric.microsoft.com/v1/operations/op'}),Response(200,{'status':'Succeeded'})]
        with patch('urllib.request.urlopen',side_effect=replies)as request,patch('time.sleep'):
            result=owner.call('workspaces/ws/items/item/updateDefinition',{'definition':{'parts':[]}})
        self.assertEqual(result,{})
        self.assertEqual(request.call_count,2)
        self.assertNotIn('pending_operation',owner.state)

    def test_job_admission_does_not_poll_item_operation_protocol(self):
        from unittest.mock import patch
        owner=object.__new__(OwnerFabric);owner.token='test-only'
        owner.path=self.path/'owner-fake.json';owner.state={'receipts':[]}
        class Response:
            status=202
            headers={'Location':'https://api.fabric.microsoft.com/v1/workspaces/ws/items/item/jobs/instances/run'}
            def read(self):return b''
            def __enter__(self):return self
            def __exit__(self,*args):pass
        with patch('urllib.request.urlopen',return_value=Response())as request:
            result=owner.call('workspaces/ws/items/item/jobs/instances?jobType=Pipeline',{})
        self.assertEqual(result['status'],'ACCEPTED');self.assertEqual(request.call_count,1)
        self.assertNotIn('pending_operation',owner.state)

    def test_warehouse_credential_also_has_exact_native_item_address(self):
        value=warehouse_item_binding(pipeline('billing','workspace','lakehouse','source','owner-warehouse'),
                                     'workspace','native-warehouse','native-endpoint')
        first=value['properties']['activities'][0]['typeProperties']['datasetSettings']
        self.assertEqual(first['connectionSettings']['properties']['typeProperties'],
                         {'endpoint':'native-endpoint','artifactId':'native-warehouse','workspaceId':'workspace'})
        script=next(a for a in value['properties']['activities']if a['type']=='Script')
        self.assertEqual(script['connectionSettings']['properties']['externalReferences']['connection'],'owner-warehouse')
        self.assertEqual(script['typeProperties']['database'],'hn_dw')

    def test_owner_publisher_refuses_unbound_assets_and_preserves_bytes(self):
        import base64
        folder=self.path/'publish-test';folder.mkdir()
        (folder/'pipeline-content.json').write_bytes(b'{"connection":"REQUIRES_OWNER_CONNECTION"}')
        with self.assertRaises(ValueError):definition_parts(folder,['pipeline-content.json'])
        original=b'{"connection":"verified-owner"}\n'
        (folder/'pipeline-content.json').write_bytes(original)
        self.assertEqual(base64.b64decode(definition_parts(folder,['pipeline-content.json'])[0]['payload']),original)

    def test_dataflow_destination_uses_bound_warehouse_connector(self):
        pq,metadata=reference_dataflow('workspace','lakehouse','server','warehouse',{
            'warehouse':{'id':'owner-warehouse','cluster_id':'cluster'}})
        self.assertIn('Fabric.Warehouse(',pq)
        self.assertIn('warehouseId="warehouse"',pq)
        self.assertIn('?[Data]?',pq)
        binding=metadata['connections'][0]
        self.assertEqual((binding['kind'],binding['path']),('Warehouse','Warehouse'))
        self.assertEqual(__import__('json').loads(binding['connectionId']),{'ClusterId':'cluster','DatasourceId':'owner-warehouse'})
        self.assertTrue(all(not m['loadEnabled']for n,m in metadata['queriesMetadata'].items()if n.endswith('_DataDestination')))

    def test_nightly_requires_native_mpi_and_reference_success(self):
        activities=nightly_pipeline('workspace','notebook','dataflow','owner-warehouse')['properties']['activities']
        self.assertEqual([a['type']for a in activities],['RefreshDataFlow','TridentNotebook','Script'])
        self.assertEqual({d['activity']for d in activities[-1]['dependsOn']},{'patient_mpi','reference_mapping'})
        self.assertTrue(all(d['dependencyConditions']==['Succeeded']for d in activities[-1]['dependsOn']))
        self.assertEqual(activities[-1]['externalReferences']['connection'],'owner-warehouse')

    def test_native_tds_redirect_retains_instance_without_dns_backslash(self):
        host='pbipcus2-centralus.pbidedicated.windows.net'
        self.assertEqual(routed_address(host+'\\HEALTHNET-dw',''),(host,'HEALTHNET-dw'))
        with self.assertRaises(ValueError):routed_address('unexpected.example\\instance','')
        from types import SimpleNamespace
        calls=[]
        def original(**kwargs):calls.append(kwargs);return 'connected'
        driver=SimpleNamespace(_connect=original)
        with named_instance_routing(driver):
            self.assertEqual(driver._connect(host=host+'\\HEALTHNET-dw',instance='',port=1433),'connected')
        self.assertIs(driver._connect,original)
        self.assertEqual(calls,[{'host':host,'instance':'HEALTHNET-dw','port':1433}])

    def test_native_reconciliation_restores_utc_datetime_bytes(self):
        from datetime import datetime
        from fixtures.hospital.generate import canonical_hash
        with closing(sqlite3.connect(self.path/'a/hn_clinical.sqlite'))as db:
            rows=db.execute('SELECT * FROM facility ORDER BY id').fetchall()
            # SQL DATETIME2 returns datetime objects where SQLite retains ISO.
            native=[tuple(datetime.fromisoformat(v).replace(tzinfo=None)
                          if isinstance(v,str)and v.endswith('+00:00')else v for v in row)for row in rows]
            self.assertEqual(hash_rows(native),(len(rows),canonical_hash(db,'facility')))
            changed=[tuple([-1,*native[0][1:]]),*native[1:]]
            self.assertNotEqual(hash_rows(changed)[1],hash_rows(native)[1])
        with closing(sqlite3.connect(self.path/'a/hn_billing.sqlite'))as db:
            rows=db.execute('SELECT * FROM charge ORDER BY id').fetchall()
            native=[tuple(datetime.fromisoformat(v).replace(tzinfo=None)
                          if i>=len(row)-4 and isinstance(v,str)and v[:4].isdigit()else v
                          for i,v in enumerate(row))for row in rows]
            self.assertEqual(hash_rows(native,rows),(len(rows),canonical_hash(db,'charge')))
        self.assertNotEqual(hash_rows([(datetime(2026,1,1,0,0,0,1),)])[1],
                            hash_rows([(datetime(2026,1,1),)])[1])

    def test_relational_and_financial_invariants(self):
        report=verify(self.path/'a')
        self.assertTrue(report['all_passed'],report['checks'])
        for name in('duplicate_mrns','merged_mrns','reentered_orders','misposts_moved','cross_month_late_charges','bad_debt_writeoffs','billing_only_accounts','clinical_only_encounters'):
            self.assertGreater(report['messiness'][name],0,name)

    def test_rebuild_refuses_overwrite(self):
        with self.assertRaises(FileExistsError):generate(self.path/'a',Settings(1,20,20,20))

    def test_different_seed_changes_patient_data(self):
        other=generate(self.path/'other',Settings(20261031,100,600,3600))
        self.assertNotEqual(other['tables']['clinical']['patient']['canonical_sha256'],self.a['tables']['clinical']['patient']['canonical_sha256'])

    def test_temporal_ddl_only_intended_tables(self):
        for system,tables in [('clinical',['patient','encounter','order_line']),('billing',['charge','claim'])]:
            sql=ddl(system,'azure')
            self.assertEqual(sql.count('SYSTEM_VERSIONING=ON'),len(tables))
            for table in tables:self.assertIn('[app].['+table+'_history]',sql)
        self.assertIn('HISTORY_RETENTION_PERIOD = 30 DAYS',ddl('clinical','azure'))

    def test_child_foreign_keys_are_indexed_for_reentry(self):
        sql=ddl('clinical')
        self.assertIn('ix_result_order_line_id',sql)
        self.assertIn('ix_medication_admin_order_line_id',sql)

    def test_native_bulk_metadata_never_defaults_numeric_columns_to_text(self):
        from types import SimpleNamespace
        class Column:
            fNullable=1
            def __init__(self,**kwargs):self.__dict__.update(kwargs)
        types=SimpleNamespace(BigIntType=lambda:'BIGINT',FloatType=lambda:'FLOAT',NVarCharType=lambda size:('NVARCHAR',size),DateTime2Type=lambda precision:('DATETIME2',precision))
        metadata=bulk_metadata('id:int value:real label:text when_utc:text optional:int?',SimpleNamespace(Column=Column),types)
        typed={c.name:c.type for c in metadata}
        self.assertEqual(typed['id'],'BIGINT')
        self.assertEqual(typed['value'],'FLOAT')
        self.assertEqual(typed['label'],('NVARCHAR',240))
        self.assertEqual(typed['when_utc'],('DATETIME2',6))
        self.assertEqual(next(c.flags for c in metadata if c.name=='optional'),1)

    def test_actual_warehouse_consumes_dataflow_and_notebook_outputs(self):
        sql=warehouse_sql()
        self.assertIn('FROM ref_department_mapping',sql)
        self.assertIn('FROM ref_payer_group_history',sql)
        self.assertIn('FROM [hn_raw].[dbo].[stg_patient]',sql)
        self.assertNotIn('{mpi}',sql)
        self.assertIn("CONCAT('SYN-***-',RIGHT(p.mrn,4))",sql)

    def test_mart_money_reconciles_and_masks_patient_rows(self):
        with closing(sqlite3.connect(self.path/'a/hn_dw.sqlite'))as db:
            self.assertEqual(db.execute("SELECT COUNT(*)FROM mart_encounter WHERE masked_mrn NOT LIKE 'SYN-***-%'OR masked_given_name NOT LIKE '_***'").fetchone()[0],0)
            money=db.execute('SELECT SUM(amount_cents)FROM mart_charge').fetchone()[0]
        with closing(sqlite3.connect(self.path/'a/hn_billing.sqlite'))as db:
            self.assertEqual(money,db.execute('SELECT SUM(amount_cents)FROM charge WHERE is_deleted=0').fetchone()[0])
        self.assertIn('mart_census_daily',self.marts['marts'])
        self.assertIn('mart_provider_productivity_daily',self.marts['marts'])

    def test_pipeline_counts_are_native_and_watermark_follows_copy(self):
        doc=pipeline('clinical','workspace','lakehouse','source','warehouse')
        activities={a['name']:a for a in doc['properties']['activities']}
        commit=activities['commit_order_line']
        self.assertEqual(commit['dependsOn'],[{'activity':'copy_order_line','dependencyConditions':['Succeeded']}])
        script=commit['typeProperties']['scripts'][0]['text']
        self.assertIn('output.rowsRead',script)
        self.assertIn('output.rowsCopied',script)
        self.assertNotIn('COUNT(*)',script)
        self.assertEqual(activities['copy_order_line']['typeProperties']['sink']['upsertSettings']['keys'],['id'])

    def test_import_parameters_directlake_and_doctor_ols(self):
        with closing(sqlite3.connect(self.path/'a/hn_dw.sqlite'))as db:
            operations=model('HealthNet Operations',db,'server','database')
            revenue=model('HealthNet Revenue',db,'server','database')
            productivity=model('HealthNet Productivity',db,'server','database')
        self.assertEqual(operations['model']['tables'][0]['partitions'][0]['mode'],'directLake')
        expression=revenue['model']['tables'][0]['partitions'][0]['source']['expression']
        self.assertIn('Sql.Database(ServerName,DatabaseName)',expression)
        doctor=next(r for r in productivity['model']['roles']if r['name']=='Doctor')
        columns=next(p['columnPermissions']for p in doctor['tablePermissions']if 'columnPermissions'in p)
        self.assertEqual({c['name']for c in columns},{'synthetic_cost_cents','synthetic_margin_cents'})
        self.assertTrue(all(c['metadataPermission']=='none'for c in columns))
        roles=json_text=__import__('json').dumps(productivity['model']['roles'])
        self.assertIn('USERPRINCIPALNAME()',roles)
        self.assertNotIn('investigator-reader',__import__('json').dumps(productivity))
        census=next(m for t in operations['model']['tables']for m in t.get('measures',[])if m['name']=='Midnight Census')
        self.assertIn('MAX(mart_census_daily[calendar_date])',census['expression'])

    def test_notebook_never_guesses_patient_identity(self):
        source=''.join(notebook('workspace','lakehouse')['cells'][0]['source'])
        self.assertIn('raw_clinical_patient_merge',source)
        self.assertIn('did not converge',source)
        self.assertNotIn('given_name',source)

    def test_bookmarks_bind_filters_by_expression_like_native_editor(self):
        import json
        root=self.path/'native-bookmark-reports';build_reports(root=root)
        for path in root.rglob('*.bookmark.json'):
            b=json.loads(path.read_text());state=b['explorationState']['filters']
            self.assertNotIn('byName',state)
            self.assertTrue(state['byExpr'])
            for f in state['byExpr']:
                self.assertEqual(f['howCreated'],1)
                self.assertIn('Column',f['expression'])
                self.assertTrue(f['filter']['Where'])
        from fixtures.hospital.visual_queries import report_queries
        q=report_queries(root/'HealthNetRevenue.Report')
        self.assertTrue(any(r['context']=='Commercial payers'and 'Commercial' in (r['query']or'')for r in q))

    def test_patient_detail_exposes_only_masked_patient_identifiers(self):
        import json
        root=self.path/'masked-detail-reports';build_reports(root=root)
        fields=[]
        for path in root.rglob('visual.json'):
            visual=json.loads(path.read_text())['visual']
            for role in visual.get('query',{}).get('queryState',{}).values():
                for p in role['projections']:
                    c=p['field'].get('Column',{})
                    if c.get('Expression',{}).get('SourceRef',{}).get('Entity')=='mart_encounter':fields.append(c['Property'])
        for field in ['masked_mrn','masked_given_name','masked_family_name']:self.assertIn(field,fields)
        for raw in ['given_name','family_name','mrn']:self.assertNotIn(raw,fields)

    def test_visual_native_references_are_unique_across_tables(self):
        import json
        root=self.path/'unique-reference-reports';build_reports(root=root)
        for path in root.rglob('visual.json'):
            visual=json.loads(path.read_text())['visual']
            projections=[p for role in visual.get('query',{}).get('queryState',{}).values()for p in role['projections']]
            refs=[p['nativeQueryRef']for p in projections]
            self.assertEqual(len(refs),len(set(refs)),str(path))

    def test_three_reports_bind_every_field_and_keep_real_filtered_bookmarks(self):
        root=self.path/'assets'
        build_models(self.path/'a',root/'models','server','database')
        build_reports(root=root/'reports')
        check=validate_assets(root)
        self.assertEqual(check['models'],3)
        self.assertEqual(check['filtered_bookmarks'],2)
        self.assertEqual(check['drillthrough_pages'],1)
        self.assertTrue(check['all_fields_bound'])
        self.assertFalse(check['native_rendering_verified'])
        report_text='\n'.join(p.read_text()for p in(root/'reports').rglob('visual.json'))
        for required in('Admissions','Discharges','Order Turnaround (minutes)','Payer mix by service-date charges'):
            self.assertIn(required,report_text)

    def test_declared_money_is_integer_and_dates_are_offset_aware(self):
        db=sqlite3.connect(self.path/'a/hn_billing.sqlite')
        self.assertEqual(db.execute("SELECT COUNT(*)FROM charge WHERE typeof(amount_cents)<>'integer'").fetchone()[0],0)
        db.close()
        db=sqlite3.connect(self.path/'a/hn_clinical.sqlite')
        self.assertEqual(db.execute("SELECT COUNT(*)FROM encounter WHERE arrival_utc NOT LIKE '%+00:00'").fetchone()[0],0)
        self.assertGreater(db.execute('SELECT COUNT(DISTINCT utc_offset_minutes)FROM ed_visit_detail').fetchone()[0],1)
        db.close()


if __name__=='__main__':unittest.main()
