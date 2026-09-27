import json
from pathlib import Path
import sys
import tempfile
from threading import Thread
import unittest

from read_budget import Catalog
from investigator.usage_governance import UsageGovernor,UsageHold
from investigator.physical_reads import run,scope


class ReadBudgetTests(unittest.TestCase):
    def setUp(self):
        folder=tempfile.TemporaryDirectory();self.addCleanup(folder.cleanup)
        self.folder=Path(folder.name);self.now=172799.0
        self.runtime=Catalog(self.folder/'catalog.sqlite','estate')
        self.policy={'environment':'estate','daily_limits':{'planner_calls':20,'cloud_calls':2,
                     'input_characters':100000,'output_tokens':30000},'max_inflight_planners':1,'no_progress_limit':2}
        self.g=UsageGovernor(self.runtime,self.policy,lambda:self.now)

    def reserve(self,session,key='one',purpose='INVESTIGATION'):
        with self.runtime.db() as db:
            db.execute('BEGIN IMMEDIATE');self.g.reserve(db,session,key,'cloud',purpose=purpose)

    def approval(self):
        return {'environment':'estate','batch_id':'approved-batch','approved_by':'operator',
                'approval_reference':'human-request-123','expires_at':self.now+600,
                'runs':[{'session_id':'trial','purpose':'INVESTIGATION','reads':2},
                        {'session_id':'restore','purpose':'RESTORATION','reads':1}]}

    def test_midnight_does_not_reset_and_exact_24_hour_expiry(self):
        self.reserve('one');self.reserve('two');self.now+=2
        with self.assertRaises(UsageHold):self.reserve('three')
        self.now=172799+86400
        self.reserve('three')
        self.assertEqual(self.g.snapshot()['read_allowance']['ordinary_charged'],1)
        with self.runtime.db() as db:self.assertEqual(db.execute('SELECT count(*) FROM adaptive_usage').fetchone()[0],3)

    def test_legacy_rows_count_without_rewriting(self):
        self.reserve('old')
        with self.runtime.db() as db:
            db.execute('DELETE FROM read_allocations') # model a pre-migration record
            before=tuple(db.execute('SELECT * FROM adaptive_usage').fetchone())
        self.assertEqual(self.g.snapshot()['read_allowance']['ordinary_charged'],1)
        with self.runtime.db() as db:self.assertEqual(tuple(db.execute('SELECT * FROM adaptive_usage').fetchone()),before)

    def test_atomic_competing_requests_cannot_overrun(self):
        errors=[]
        def attempt(i):
            try:self.reserve(str(i))
            except UsageHold:errors.append(i)
        threads=[Thread(target=attempt,args=(i,)) for i in range(8)]
        for t in threads:t.start()
        for t in threads:t.join()
        self.assertEqual(len(errors),6)
        self.assertEqual(self.g.snapshot()['read_allowance']['ordinary_charged'],2)

    def test_batch_is_separate_scoped_expiring_and_earmarked(self):
        self.reserve('one');self.reserve('two')
        before=self.g.hash;self.g.grant_batch(self.approval())
        self.reserve('trial','1');self.reserve('trial','2')
        with self.assertRaises(UsageHold):self.reserve('trial','3')
        with self.assertRaises(UsageHold):self.reserve('unrelated')
        with self.assertRaises(UsageHold):self.reserve('restore')
        self.assertEqual(self.g.restoration_read('restore','one',lambda:'verified'),'verified')
        with self.assertRaises(UsageHold):self.g.restoration_read('restore','one',lambda:self.fail('replayed'))
        self.assertEqual(self.g.hash,before)
        self.assertEqual(self.g.snapshot()['read_allowance']['ordinary_charged'],2)

    def test_expired_batch_never_falls_back_to_ordinary(self):
        approval=self.approval();self.g.grant_batch(approval);self.now=approval['expires_at']
        with self.assertRaises(UsageHold):self.reserve('trial')
        self.assertEqual(self.g.snapshot()['read_allowance']['batches'][0]['runs'][0]['available'],0)
        self.reserve('ordinary')

    def test_no_midrun_credit_or_redefinition(self):
        self.reserve('trial')
        with self.assertRaises(ValueError):self.g.grant_batch(self.approval())
        approval=self.approval();approval['runs'][0]['session_id']='new'
        self.g.grant_batch(approval)
        with self.assertRaises(ValueError):self.g.grant_batch(approval)

    def test_uncertain_is_charged_no_refund(self):
        self.reserve('one')
        with self.runtime.db() as db:self.g.settle(db,'one','one',uncertain=True)
        self.reserve('two')
        with self.assertRaises(UsageHold):self.reserve('three')

    def test_same_key_cannot_change_purpose(self):
        self.g.grant_batch(self.approval());self.reserve('restore',purpose='RESTORATION')
        with self.assertRaises(UsageHold):self.reserve('restore')

    def test_exhausted_read_pool_does_not_block_synthesis_planner(self):
        self.reserve('one');self.reserve('two')
        with self.runtime.db() as db:
            db.execute('BEGIN IMMEDIATE');self.g.reserve(db,'synthesis','planner','planner',100)

    def child(self,count=2,fail_after=None):
        path=self.folder/'fake_transport.py'
        # This is a real pipe protocol test, with no sockets or data services.
        path.write_text('''import json,sys
json.loads(sys.stdin.readline())
for index in range(COUNT):
    print(json.dumps({'physical_read':'REQUEST','kind':'onelake_commit'}),flush=True)
    if sys.stdin.readline().strip()!='ALLOW':sys.exit(2)
    with open(MARKER,'a') as f:f.write('read\\n')
    if index==FAIL:sys.exit(3)
    print(json.dumps({'physical_read':'DONE','kind':'onelake_commit','status':'AVAILABLE'}),flush=True)
print(json.dumps({'status':'AVAILABLE'}),flush=True)
'''.replace('COUNT',str(count)).replace('MARKER',repr(str(self.folder/'sent.txt'))).replace('FAIL',repr(fail_after)))
        return [sys.executable,str(path)]

    def test_each_physical_request_is_charged_and_held_before_send(self):
        self.g.grant_batch(self.approval())
        command=self.child(3)
        with self.assertRaises(UsageHold):
            self.g.restoration_read('restore','op',lambda:run(command,input='{}',timeout=5))
        self.assertEqual((self.folder/'sent.txt').read_text().splitlines(),['read'])
        self.assertEqual(next(r for r in self.g.snapshot()['read_allowance']['batches'][0]['runs'] if r['session_id']=='restore')['charged'],1)

    def test_two_requests_have_two_reservations(self):
        approval=self.approval();approval['runs'][1]['reads']=2;self.g.grant_batch(approval)
        result=self.g.restoration_read('restore','op',lambda:run(self.child(),input='{}',timeout=5))
        self.assertEqual(json.loads(result.stdout)['status'],'AVAILABLE')
        self.assertEqual(len((self.folder/'sent.txt').read_text().splitlines()),2)
        self.assertEqual(next(r for r in self.g.snapshot()['read_allowance']['batches'][0]['runs'] if r['session_id']=='restore')['charged'],2)

    def test_first_request_failure_never_sends_second(self):
        self.g.grant_batch(self.approval())
        with self.assertRaises(RuntimeError):
            self.g.restoration_read('restore','op',lambda:run(self.child(fail_after=0),input='{}',timeout=5))
        self.assertEqual(len((self.folder/'sent.txt').read_text().splitlines()),1)
        self.assertEqual(self.g.snapshot()['reservation_states']['UNCERTAIN'],1)

    def test_process_counts_physical_requests_even_if_later_validation_fails(self):
        import test_flexible_investigation as fixture
        from investigator.adaptive_runtime import AdaptiveRuntime
        from investigator.process_debugging import VERSION
        from investigator.process_read_receipts import accounting
        from unittest.mock import patch
        import copy
        h=fixture.DynamicTests();h.setUp();self.addCleanup(h.doCleanups)
        envelope=copy.deepcopy(h.envelope);envelope['strategy']=VERSION
        agent=AdaptiveRuntime(h.runtime,lambda _:self.fail('not a planning test'))
        command=self.child(2)
        original=h.runtime.native_transport
        def transport(request):
            run(command,input='{}',timeout=5)
            return original(request)
        h.runtime.native_transport=transport
        identity=agent.create(envelope,'physical-reads')['id']
        with patch('investigator.assessment_support.validate',side_effect=ValueError('later failure')):
            state=agent.run(identity)
        self.assertEqual(state['status'],'HELD')
        self.assertEqual(state['cloud_calls'],2)
        self.assertEqual(accounting(state)['reads_total'],2)
        self.assertEqual(accounting(state)['reads_completed'],2)
        self.assertEqual(accounting(agent.get(identity)),accounting(state))
        primary=next(e for e in state['process_read_receipts'] if e.get('logical_tool')=='bounded_dax')
        self.assertTrue(primary.get('logical_receipt',{}).get('receipt_id'))

    def test_existing_run_limit_still_binds_physical_reads(self):
        import test_adaptive_investigation as fixture
        from investigator.adaptive_runtime import AdaptiveRuntime
        h=fixture.AdaptiveTests();h.setUp();self.addCleanup(h.doCleanups)
        h.envelope['limits']['cloud_calls']=1
        h.planner.side_effect=lambda p:(fixture.decision(h.choose(p)),{})
        agent=AdaptiveRuntime(h.runtime,h.planner,h.clock)
        command=self.child(2)
        original=h.native.return_value
        def transport(_):
            run(command,input='{}',timeout=5)
            return original
        h.native.side_effect=transport
        state=agent.run(agent.create(h.envelope,'limited')['id'])
        self.assertEqual(state['cloud_calls'],1)
        from investigator.process_read_receipts import accounting
        self.assertEqual(accounting(state)['reads_total'],1)
        self.assertEqual(state['status'],'HELD')
        self.assertEqual(len((self.folder/'sent.txt').read_text().splitlines()),1)

    def test_sql_requests_have_mandatory_admission_before_each_execute(self):
        root=Path(__file__).resolve().parents[1]
        for name in ('Read-CatalogAggregate.ps1','Read-FabricSqlAggregate.ps1'):
            source=(root/'infra/scripts'/name).read_text()
            lines=source.splitlines()
            executions=[i for i,l in enumerate(lines) if '.ExecuteReader()' in l or '.ExecuteScalar()' in l]
            self.assertGreater(len(executions),2)
            for i in executions:self.assertIn('Begin-PhysicalRead',lines[i-1],(name,lines[i]))

    def test_allowance_reporting_does_not_change_planner_directory_or_payload(self):
        import test_flexible_investigation as fixture
        from investigator.adaptive_runtime import AdaptiveRuntime
        from investigator.adaptive_candidates import catalog
        from investigator.onboarding import encoded
        h=fixture.DynamicTests();h.setUp();self.addCleanup(h.doCleanups)
        agent=AdaptiveRuntime(h.runtime,lambda _:None)
        state=agent.get(agent.create(h.envelope,'context')['id'])
        choices,_=catalog(h.store,h.config,h.envelope)
        before=agent.payload(state,choices)
        # Budget reports live in recording/control plane, never the model directory.
        agent.governor=self.g
        self.g.grant_batch(self.approval())
        self.g.snapshot()
        after=agent.payload(state,choices)
        self.assertEqual(encoded(before),encoded(after))
        self.assertTrue(before['context_entry_points'])
        self.assertTrue(any(a['kind']=='SqlObject' for a in before['context_entry_points']))


if __name__=='__main__':unittest.main()
