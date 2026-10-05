"""Reader verification replays original observations and budget decisions offline."""
import copy,sqlite3,tempfile,unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import Mock
import test_flexible_investigation as runtime_fixture
import test_lineage_binding as proof_fixture
from investigator import process_tape as journal
from investigator.transformation_service import run
from investigator.lineage_binding import Ledger
from investigator.usage_governance import UsageGovernor


class ReaderTapeTests(unittest.TestCase):
    def test_reader_replays_code_proposals_probes_and_charged_budget_without_io(self):
        h=runtime_fixture.DynamicTests();h.setUp();self.addCleanup(h.doCleanups)
        policy={'environment':h.store.environment,'daily_limits':{'planner_calls':50,'cloud_calls':50,
            'input_characters':1000000,'output_tokens':100000},'max_inflight_planners':1,'no_progress_limit':3}
        gov=UsageGovernor(h.runtime,policy,lambda:1000)
        proof,_=proof_fixture.BindingTests().verification(('7','14'))
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d);(folder/'unit.py').write_text(
                "a=spark.table('input-table')\na.write.format('delta').mode('overwrite').save('output-table')\n",encoding='utf8')
            initial=folder/'initial.sqlite'
            with h.runtime.db() as db,closing(sqlite3.connect(initial)) as saved:db.backup(saved)
            def perform(ledger,live):
                number=0
                def meter(fn):
                    nonlocal number
                    number+=1
                    return gov.metered_read('reader','physical-'+str(number),fn)
                def execute(side,plan):
                    return meter(lambda:journal.bounded_call('code_verification_probe',{'side':side},
                        lambda:live(side)))
                result=run(source={'id':'source','kind':'LOCAL_PATH','identity':'export-reader','path':'.'},
                    path='unit.py',meter=meter,root=folder,schemas={'input-table':{'amount':'int'}},
                    boundary={'from_layer':'input','to_layer':'output'},item='source',target_table='output-table',
                    layers=[],context=proof['context'],cell=proof['cell'],precision=proof['precision'],
                    compiler=lambda *args:None,execute=execute,ledger=ledger)
                return {'result':result,'charged':gov.snapshot()['read_allowance']['ordinary_charged']}
            bootstrap={'entry_point':'code_verifier','context_identity':'offline','config':{},'profile':{},
                       'usage_policy':policy,'engine_hash':'synthetic-reader','state':{}}
            tape=journal.Tape(folder/'tape.json',bootstrap=bootstrap)
            live=Mock(side_effect=lambda side:copy.deepcopy(proof['observations'][0 if side=='TARGET' else 1]))
            with journal.active(tape):
                expected=perform(Ledger(folder/'original.jsonl'),live);tape.finish(expected)
            self.assertEqual(expected['charged'],3)
            self.assertEqual(expected['result']['verifications'][0]['status'],'FALSIFIED')
            self.assertEqual(live.call_count,2)
            with closing(sqlite3.connect(initial)) as saved,h.runtime.db() as db:saved.backup(db)
            (folder/'unit.py').unlink()
            forbidden=Mock(side_effect=AssertionError('Live probe forbidden'))
            replay=journal.Tape(tape.path)
            with journal.active(replay):
                actual=perform(Ledger(folder/'replayed.jsonl'),forbidden);replay.finish(actual)
            forbidden.assert_not_called();self.assertEqual(expected,actual)
            self.assertEqual((folder/'original.jsonl').read_bytes(),(folder/'replayed.jsonl').read_bytes())

if __name__=='__main__':unittest.main()
