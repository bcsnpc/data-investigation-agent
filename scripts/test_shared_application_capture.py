"""Exact shared table baselines/deltas, with old tape grammar untouched."""
import base64,copy,json,sqlite3,tempfile,unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import Mock,patch
from investigator.process_tape import Tape,active,TapeError
from investigator.shared_application_capture import VERSION,read,build,apply
from investigator.shared_state import sha,StateConflict
from investigator import shared_application as app
from test_process_tape import bootstrap
import test_shared_application as fixtures
from test_shared_application import store


class ApplicationDeltaCaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
    def payload(self,rows=100):
        return {'revision':1,'body':{'schema':'CREATE TABLE flexible_diagnostics(id TEXT,result TEXT)','columns':['id','result'],
            'rows':[[i+1,str(i),'public fixture '*40] for i in range(rows)]}}
    def header(self,enabled=True):
        b=bootstrap();b['state']['shared_application']=app.VERSION
        if enabled:b['state']['shared_application_capture']=VERSION
        return b
    def test_once_baseline_then_exact_small_deltas_replay_without_authority(self):
        a=self.payload();b=copy.deepcopy(a);b['revision']=2;b['body']['rows'][17][-1]='{ "amount": 12.125, "note": null }'
        c=copy.deepcopy(b);c['revision']=3;c['body']['rows'].pop(5);c['body']['rows'].append([101,'new','new observation'])
        producer=Mock(side_effect=[a,b,c]);tape=Tape(self.root/'tape.json',self.header())
        with active(tape):
            observed=[read('flexible_diagnostics',producer) for _ in range(3)];tape.finish(observed)
        self.assertEqual([a,b,c],observed);self.assertEqual(3,producer.call_count)
        cfg=[e for e in tape.events if e['kind']=='CONFIGURATION']
        self.assertLess(len(cfg[1]['body']),len(cfg[0]['body'])//10)
        self.assertLess(len(cfg[2]['body']),len(cfg[0]['body'])//10)
        self.assertEqual(['BASELINE','DELTA','DELTA'],[json.loads(base64.b64decode(e['body']))['value']['mode'] for e in cfg])
        replay=Tape(tape.path);no_authority=Mock(side_effect=AssertionError('no replay authority'))
        with active(replay):replay.finish([read('flexible_diagnostics',no_authority) for _ in range(3)])
        no_authority.assert_not_called()
    def test_legacy_tapes_still_emit_full_snapshots_each_time_and_replay(self):
        saved=self.payload();tape=Tape(self.root/'old.json',self.header(False))
        with active(tape):
            values=[read('flexible_diagnostics',lambda:saved) for _ in range(2)];tape.finish(values)
        cfg=[json.loads(base64.b64decode(e['body'])) for e in tape.events if e['kind']=='CONFIGURATION']
        self.assertEqual([{'name':'shared_application:flexible_diagnostics','value':saved}]*2,cfg)
        replay=Tape(tape.path)
        with active(replay):replay.finish([read('flexible_diagnostics',lambda:self.fail('authority')) for _ in range(2)])
    def test_bad_parent_before_image_after_hash_and_duplicate_changes_refuse(self):
        a=self.payload(2);b=copy.deepcopy(a);b['revision']=2;b['body']['rows'][0][-1]='changed'
        prior=(a,sha(a));delta=build(prior,b)
        mutations=[]
        for field in ('before_sha256','after_sha256'):
            v=copy.deepcopy(delta);v[field]='0'*64;mutations.append(v)
        v=copy.deepcopy(delta);v['changes'][0]['before'][-1]='wrong before';mutations.append(v)
        v=copy.deepcopy(delta);v['changes']*=2;mutations.append(v)
        for v in mutations:
            with self.subTest(),self.assertRaises(TapeError):apply('flexible_diagnostics',prior,v)
        self.assertEqual(b,apply('flexible_diagnostics',prior,delta))
    def test_schema_change_or_absent_table_is_explicit_replacement(self):
        a=self.payload(1);b={'revision':None,'body':None};prior=(a,sha(a))
        delta=build(prior,b);self.assertEqual('REPLACE',delta['mode']);self.assertEqual(b,apply('flexible_diagnostics',prior,delta))
    def test_unregistered_version_and_invalid_table_payload_refuse(self):
        header=self.header();header['state']['shared_application_capture']='unknown'
        with active(Tape(self.root/'bad.json',header)),self.assertRaisesRegex(TapeError,'CAPTURE_VERSION'):
            read('flexible_diagnostics',lambda:self.payload())
        payload=self.payload(1);payload['body']['rows'][0][-1]=b'opaque'
        with active(Tape(self.root/'shape.json',self.header())),self.assertRaises(StateConflict):
            read('flexible_diagnostics',lambda:payload)


class ApplicationDeltaAuthorityTests(unittest.TestCase):
    def test_real_connections_keep_authoritative_writes_and_concurrency_fence(self):
        fixture=fixtures.SharedApplicationTests();fixture.setUp();self.addCleanup(fixture.doCleanups)
        controller,claim=fixture.claim();before=fixture.root/'baseline.sqlite'
        with closing(sqlite3.connect(fixture.store.database)) as src,closing(sqlite3.connect(before)) as dst:src.backup(dst)
        header=bootstrap();header['state'].update(shared_application=app.VERSION,shared_application_capture=VERSION)
        def operation(s):
            results=[]
            for _ in range(2):
                with s.connect() as db:results.append(list(db.execute('SELECT id,revision FROM claim_intakes').fetchone()))
            with s.connect() as db:
                db.execute('UPDATE claim_intakes SET revision=revision+1')
            with s.connect() as db:results.append(list(db.execute('SELECT id,revision FROM claim_intakes').fetchone()))
            return results
        tape=Tape(fixture.root/'delta.json',header)
        with active(tape):tape.finish(operation(fixture.store))
        saved=app.source(fixture.store.database,'synthetic')
        replay=Tape(tape.path)
        with patch.object(fixture.authority,'transaction',side_effect=AssertionError('replay authority')):
            with active(replay):replay.finish(operation(store(before,None)))
        self.assertEqual(saved,app.source(before,'synthetic'))
        with self.assertRaisesRegex(StateConflict,'REVISION_CHANGED'):
            with fixture.store.connect() as db:
                db.execute('SELECT id FROM claim_intakes')
                old=fixture.authority.get(app.NAMESPACE,app.key('synthetic','claim_intakes'))
                fixture.authority.put(app.NAMESPACE,app.key('synthetic','claim_intakes'),old['body'],revision=old['revision'])
                db.execute('UPDATE claim_intakes SET revision=99')


if __name__=='__main__':unittest.main()
