import io,json,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from investigator.process_tape import Tape,active,bytes_of,TapeError
from investigator.physical_reads import scope
from gateway_test_support import allow_sql
from fabric_sql_surface import read
from test_managed_sql_worker import AUTH


class Tests(unittest.TestCase):
    def test_managed_surface_worker_payload_is_identical_live_and_offline(self):
        reader={**AUTH,'server':'synthetic.database.windows.net','account':'reader'}
        config={'fabric':{'sql_reader':reader,'auth':{'tenant_id':AUTH['tenant_id']}}}
        request={'query':'SELECT value FROM dbo.synthetic','read_only_objects':['dbo.synthetic'],
                 'result_columns':['value'],'max_rows':2}
        result={'rows':[{'value':7}]}
        child=SimpleNamespace(stdin=io.StringIO(),stdout=io.StringIO(json.dumps(result)+'\n'),
            wait=lambda timeout=None:0,poll=lambda:0,kill=lambda:None)
        bootstrap={'entry_point':'synthetic','context_identity':'retained','config':{},
                   'profile':{},'usage_policy':{},'engine_hash':'test','state':{}}
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'tape.json';recorded=Tape(path,bootstrap)
            with active(recorded),scope(lambda k,f:f()),allow_sql(reader['server'],'db',['dbo.synthetic']), \
                 patch('subprocess.Popen',return_value=child):
                self.assertEqual(read(config,'db',request),result)
                recorded.finish(result)
            original=path.read_bytes()
            replayed=Tape(path)
            with active(replayed),scope(lambda k,f:f()), \
                 patch('investigator.live_gateway.current',side_effect=AssertionError('live gateway queried')), \
                 patch('subprocess.Popen',side_effect=AssertionError('live worker launched')):
                actual=read(config,'db',request)
                replayed.finish(actual)
            self.assertEqual(actual,result);self.assertEqual(path.read_bytes(),original)

    def test_original_worker_payload_mismatch_survives_cleanup_and_settlement(self):
        bootstrap={'entry_point':'synthetic','context_identity':'retained','config':{},
                   'profile':{},'usage_policy':{},'engine_hash':'test','state':{}}
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'tape.json';t=Tape(path,bootstrap)
            t.event('WORKER_START',bytes_of({'command':['worker'],'mode':'STREAM'}))
            t.event('WORKER_SEND',bytes_of({'require_read_only':True}))
            t.event('WORKER_READ',b'{}\n');t.event('WORKER_END',bytes_of({'returncode':0}));t.finish({})
            replay=Tape(path);replay.take('WORKER_START')
            with self.assertRaisesRegex(TapeError,'TAPE_REQUEST_BYTES_DIFFER') as first:
                replay.event('WORKER_SEND',bytes_of({}))
            for cleanup in ('WORKER_END','BUDGET_INPUT','FINAL'):
                with self.assertRaises(TapeError) as later:replay.take(cleanup)
                self.assertIs(later.exception,first.exception)


if __name__=='__main__':unittest.main()
