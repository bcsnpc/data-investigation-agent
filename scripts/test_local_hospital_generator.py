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
from fixtures.hospital.marts import build_local,warehouse_sql
from fixtures.hospital.models import model
from fixtures.hospital.artifacts import pipeline,notebook
from fixtures.hospital.models import build as build_models
from fixtures.hospital.reports import build as build_reports
from fixtures.hospital.validate_assets import validate as validate_assets
from fixtures.hospital.owner_sql import bulk_metadata


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

    def test_notebook_never_guesses_patient_identity(self):
        source=''.join(notebook('workspace','lakehouse')['cells'][0]['source'])
        self.assertIn('raw_clinical_patient_merge',source)
        self.assertIn('did not converge',source)
        self.assertNotIn('given_name',source)

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

    def test_declared_money_is_integer_and_dates_are_offset_aware(self):
        db=sqlite3.connect(self.path/'a/hn_billing.sqlite')
        self.assertEqual(db.execute("SELECT COUNT(*)FROM charge WHERE typeof(amount_cents)<>'integer'").fetchone()[0],0)
        db.close()
        db=sqlite3.connect(self.path/'a/hn_clinical.sqlite')
        self.assertEqual(db.execute("SELECT COUNT(*)FROM encounter WHERE arrival_utc NOT LIKE '%+00:00'").fetchone()[0],0)
        self.assertGreater(db.execute('SELECT COUNT(DISTINCT utc_offset_minutes)FROM ed_visit_detail').fetchone()[0],1)
        db.close()


if __name__=='__main__':unittest.main()
