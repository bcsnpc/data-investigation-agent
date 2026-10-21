"""Snapshot the audited SQLite read transaction without a full in-memory DB."""
from contextlib import closing
import hashlib,json,sqlite3,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from cloud_verification_capture import snapshot
from investigator.planner_recording import _safe,RecordingError


class StreamingSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
    def database(self,mode='DELETE'):
        path=self.root/'source.sqlite'
        with closing(sqlite3.connect(path)) as db:
            db.execute('PRAGMA journal_mode='+mode)
            db.execute('CREATE TABLE fixture(value)');db.execute('INSERT INTO fixture VALUES(?)',('audited prior value',));db.commit()
        return path
    def test_concurrent_wal_change_cannot_enter_already_audited_snapshot(self):
        source=self.database('WAL');writer=sqlite3.connect(source);self.addCleanup(writer.close)
        target=self.root/'snapshot.sqlite';changed=[]
        def audit(raw):
            _safe(raw)
            if not changed and b'audited prior value' in raw:
                writer.execute('UPDATE fixture SET value=?',('password=unexamined_secret_123',));writer.commit();changed.append(True)
        with patch('cloud_verification_capture._safe',side_effect=audit):snapshot(source,target)
        self.assertTrue(changed)
        with closing(sqlite3.connect(target)) as db:
            self.assertEqual([('audited prior value',)],db.execute('SELECT value FROM fixture').fetchall())
        self.assertEqual([('password=unexamined_secret_123',)],writer.execute('SELECT value FROM fixture').fetchall())
    def test_readonly_transaction_preserves_source_and_repeated_backups_exact(self):
        source=self.database();before=hashlib.sha256(source.read_bytes()).hexdigest()
        first=self.root/'first.sqlite';second=self.root/'second.sqlite'
        a=snapshot(source,first);b=snapshot(source,second)
        self.assertEqual(a,b);self.assertEqual(first.read_bytes(),second.read_bytes())
        self.assertEqual(before,hashlib.sha256(source.read_bytes()).hexdigest())
    def test_unsafe_value_refuses_before_any_destination_write(self):
        source=self.database()
        with closing(sqlite3.connect(source)) as db:
            db.execute('UPDATE fixture SET value=?',(b'{"note":"synthetic_\\u0073ecret_123"}',));db.commit()
        before=hashlib.sha256(source.read_bytes()).hexdigest();target=self.root/'refused.sqlite'
        with patch.dict('os.environ',{'TEST_API_KEY':'synthetic_secret_123'}):
            with self.assertRaises(RecordingError):snapshot(source,target)
        self.assertFalse(target.exists());self.assertEqual(before,hashlib.sha256(source.read_bytes()).hexdigest())
    @unittest.skipUnless(sys.platform.startswith('linux'),'Linux ru_maxrss reports KiB; Windows lacks resource')
    def test_linux_child_peak_growth_stays_below_full_128m_database(self):
        code=r'''
from contextlib import closing
import json,resource,sqlite3,sys
from pathlib import Path
from cloud_verification_capture import snapshot
root=Path(sys.argv[1]);source=root/'large.sqlite'
with closing(sqlite3.connect(source)) as db:
 db.execute('CREATE TABLE fixture(value BLOB)')
 db.executemany('INSERT INTO fixture VALUES(zeroblob(2097152))',[() for _ in range(64)]);db.commit()
baseline=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
snapshot(source,root/'snapshot.sqlite')
print(json.dumps({'bytes':source.stat().st_size,'peak_growth_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss-baseline}))
'''
        result=subprocess.run([sys.executable,'-c',code,str(self.root)],cwd=Path(__file__).parent,check=True,capture_output=True,text=True,timeout=180)
        receipt=json.loads(result.stdout);self.assertGreater(receipt['bytes'],128*1024*1024)
        self.assertLess(receipt['peak_growth_kib'],96*1024)


if __name__=='__main__':unittest.main()
