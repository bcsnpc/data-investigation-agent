"""Source-generator checks, run by the existing Validation checkout job."""
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


class HospitalGeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        cls.path=Path(cls.temp.name)
        cls.a=generate(cls.path/'a',Settings(patients=100,encounters=600,orders=3600))
        cls.b=generate(cls.path/'b',Settings(patients=100,encounters=600,orders=3600))

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

    def test_declared_money_is_integer_and_dates_are_offset_aware(self):
        db=sqlite3.connect(self.path/'a/hn_billing.sqlite')
        self.assertEqual(db.execute("SELECT COUNT(*)FROM charge WHERE typeof(amount_cents)<>'integer'").fetchone()[0],0)
        db.close()
        db=sqlite3.connect(self.path/'a/hn_clinical.sqlite')
        self.assertEqual(db.execute("SELECT COUNT(*)FROM encounter WHERE arrival_utc NOT LIKE '%+00:00'").fetchone()[0],0)
        self.assertGreater(db.execute('SELECT COUNT(DISTINCT utc_offset_minutes)FROM ed_visit_detail').fetchone()[0],1)
        db.close()


if __name__=='__main__':unittest.main()
