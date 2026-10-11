from contextlib import closing
import hashlib,importlib.util,json,re,shutil,sqlite3,sys,tempfile,threading,time,types,unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import Mock,patch
HERE=Path(__file__).parent;ROOT=Path.cwd();sys.path[:0]=[str(HERE),str(ROOT/'scripts')]
from investigator.artifact_identity_cache import ArtifactChanged,IdentityCache,file_sha,scan
PATTERN=re.compile(r'(?i)\b[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\b')
ONE='12345678-1234-1234-1234-123456789abc';TWO='22345678-1234-1234-1234-123456789abc'
def db(path,text):
    with closing(sqlite3.connect(path)) as c:c.execute('CREATE TABLE contents(text TEXT)');c.execute('INSERT INTO contents VALUES(?)',(text,));c.commit()
class Tests(unittest.TestCase):
    def test_same_main_hash_wal_overlay_never_expands_cached_identity(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'a.sqlite';db(p,ONE)
            with closing(sqlite3.connect(p)) as writer:
                writer.execute('PRAGMA journal_mode=WAL');writer.execute('PRAGMA wal_checkpoint(TRUNCATE)')
                expected=file_sha(p);scanner=Mock(wraps=scan);c=IdentityCache(PATTERN,scanner=scanner)
                self.assertEqual(c.get(p,expected),frozenset([ONE]))
                writer.execute('UPDATE contents SET text=?',(TWO,));writer.commit()
                self.assertEqual(file_sha(p),expected)
                self.assertGreater(Path(str(p)+'-wal').stat().st_size,0)
                with self.assertRaisesRegex(ArtifactChanged,'unsealed SQLite overlay'):c.get(p,expected)
                self.assertEqual(scanner.call_count,1)
                self.assertEqual(c.stats()['identities'],1)
    def test_journal_overlay_is_refused_even_with_matching_main_hash(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'a.sqlite';db(p,ONE);expected=file_sha(p);c=IdentityCache(PATTERN)
            self.assertEqual(c.get(p,expected),frozenset([ONE]));Path(str(p)+'-journal').write_bytes(b'not sealed')
            with self.assertRaises(ArtifactChanged):c.get(p,expected)
    def test_warm_cache_still_hashes_changed_actual_file(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'a.sqlite';db(p,ONE);expected=file_sha(p);c=IdentityCache(PATTERN)
            self.assertEqual(c.get(p,expected),frozenset([ONE]))
            with closing(sqlite3.connect(p)) as connection:connection.execute('UPDATE contents SET text=?',(TWO,));connection.commit()
            with self.assertRaises(ArtifactChanged):c.get(p,expected)
            self.assertEqual(c.get(p,file_sha(p)),frozenset([TWO]))
    def test_four_copies_singleflight_scan_once(self):
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder)/'a.sqlite';db(base,ONE);expected=file_sha(base);paths=[Path(folder)/(str(i)+'.sqlite') for i in range(4)]
            for p in paths:shutil.copyfile(base,p)
            count=0;lock=threading.Lock();barrier=threading.Barrier(4)
            def scanner(path,pattern):
                nonlocal count
                with lock:count+=1
                time.sleep(.1);return scan(path,pattern)
            c=IdentityCache(PATTERN,scanner=scanner)
            def call(path):barrier.wait();return c.get(path,expected)
            with ThreadPoolExecutor(4) as pool:results=list(pool.map(call,paths))
            self.assertEqual(count,1);self.assertEqual(results,[frozenset([ONE])]*4);self.assertEqual(c.stats()['flights'],0)
    def test_failures_never_cached(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'a.sqlite';db(p,ONE);scanner=Mock(side_effect=[sqlite3.DatabaseError('synthetic'),frozenset([ONE])]);c=IdentityCache(PATTERN,scanner=scanner)
            with self.assertRaises(sqlite3.DatabaseError):c.get(p,file_sha(p))
            self.assertEqual(c.stats()['entries'],0);self.assertEqual(c.get(p,file_sha(p)),frozenset([ONE]));self.assertEqual(scanner.call_count,2)
    def test_eviction_limits_both_entry_and_identity_counts(self):
        with tempfile.TemporaryDirectory() as folder:
            paths=[]
            for i,text in enumerate([ONE,TWO,ONE+' '+TWO]):
                p=Path(folder)/(str(i)+'.sqlite');db(p,text);paths.append(p)
            scanner=Mock(wraps=scan);c=IdentityCache(PATTERN,max_entries=1,max_identities=1,scanner=scanner)
            for p in paths:c.get(p,file_sha(p))
            self.assertEqual(c.stats(),{'entries':1,'identities':1,'flights':0})
            c.get(paths[0],file_sha(paths[0]));self.assertEqual(scanner.call_count,4)
    def test_changed_during_scan_refuses_and_is_not_cached(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'a.sqlite';db(p,ONE)
            def scanner(path,pattern):
                result=scan(path,pattern)
                with closing(sqlite3.connect(path)) as c:c.execute('UPDATE contents SET text=?',(TWO,));c.commit()
                return result
            c=IdentityCache(PATTERN,scanner=scanner)
            with self.assertRaises(ArtifactChanged):c.get(p,file_sha(p))
            self.assertEqual(c.stats()['entries'],0)
    def test_real_tape_introduced_uuid_refusal_unchanged_on_warm_cache(self):
        cache=IdentityCache(PATTERN)
        from investigator import process_tape as m
        with patch.object(m,'_ARTIFACT_IDENTITIES',cache), tempfile.TemporaryDirectory() as folder:
            folder=Path(folder);hashes={}
            for name in ('catalog.sqlite','inventory.sqlite'):
                path=folder/name;db(path,ONE);hashes[name]=file_sha(path)
            bootstrap={'entry_point':'workspace','context_identity':'retained-context','config':{},'profile':{},'usage_policy':{},'engine_hash':'synthetic-engine','state':{'environment':'synthetic','workspace_owner':None,'artifacts':hashes,'dynamic_read_limit':12,'dynamic_input_limit':10000}}
            tape=m.Tape(folder/'tape.json',bootstrap)
            tape.finish({'operation':'run','error':None,'status':'HELD','outputs':None,'result':{'identity':ONE}})
            before=(folder/'tape.json').read_bytes();m.Tape(folder/'tape.json')
            self.assertEqual((folder/'tape.json').read_bytes(),before)
            bad=m.Tape(folder/'wrong.json',bootstrap)
            with self.assertRaisesRegex(m.TapeError,'TAPE_UNRECORDED_IDENTITY'):
                bad.finish({'operation':'run','error':None,'status':'HELD','outputs':None,'result':{'identity':TWO}})
            with closing(sqlite3.connect(folder/'catalog.sqlite')) as c:c.execute('UPDATE contents SET text=?',(TWO,));c.commit()
            with self.assertRaisesRegex(m.TapeError,'TAPE_BOOTSTRAP_ARTIFACT_CHANGED'):m.Tape(folder/'tape.json')
if __name__=='__main__':unittest.main()
