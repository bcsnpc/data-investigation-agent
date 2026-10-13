"""Concurrency uses the existing shared SQLite admission, not local totals."""
import concurrent.futures
import unittest
from threading import Barrier
import test_adaptive_investigation as fixture
from investigator.usage_governance import UsageGovernor


class ParallelReservationsTests(unittest.TestCase):
    def test_many_fake_calls_commit_exact_totals_without_leaked_reservations(self):
        helper = fixture.AdaptiveTests()
        helper.setUp()
        self.addCleanup(helper.doCleanups)
        helper.store.environment = 'development'
        policy = {'environment':'development','daily_limits':{
            'planner_calls':100,'cloud_calls':100,'input_characters':100000,'output_tokens':100000},
            'max_inflight_planners':4,'no_progress_limit':2}
        governor = UsageGovernor(helper.runtime, policy, helper.clock)
        active_per_wave=[]
        rendezvous=Barrier(4,action=lambda:active_per_wave.append(
            governor.snapshot()['active_reservations']['planner_calls']),timeout=10)
        def fake_call(number):
            identity = 'parallel-' + str(number)
            with helper.runtime.db() as db:
                db.execute('BEGIN IMMEDIATE')
                governor.reserve(db, identity, 'model', 'planner', 100, output_tokens=500)
            # Wait outside every DB transaction: all four reservations must be
            # active before any settles. A fast worker cannot reacquire this
            # legacy SQLite file through 80 calls and starve its peers.
            rendezvous.wait()
            with helper.runtime.db() as db:
                db.execute('BEGIN IMMEDIATE')
                governor.settle(db, identity, 'model', {'input_tokens':25,'output_tokens':10})
            return governor.metered_read(identity, 'read', lambda: number)
        results=[]
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            for start in range(0,80,4):
                results.extend(pool.map(fake_call,range(start,start+4)))
        self.assertEqual(results,list(range(80)))
        self.assertEqual(active_per_wave,[4]*20)
        actual = governor.snapshot()
        self.assertEqual(actual['reserved_today'], {'planner_calls':80,'cloud_calls':80,
                                                  'input_characters':8000,'output_tokens':40000})
        self.assertEqual(actual['charged_today']['output_tokens'], 800)
        self.assertTrue(all(value == 0 for value in actual['active_reservations'].values()))
        self.assertEqual(actual['reservation_states'], {'SETTLED':160})


if __name__ == '__main__': unittest.main()

