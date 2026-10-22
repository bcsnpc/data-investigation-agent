"""Monthly authority replaces run ceilings without changing legacy replay."""
import copy
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from investigator.build_phase import operating_mode, PHYSICAL_REQUESTS
from investigator import process_budget, candidate_read_budget
from investigator.form_candidates import NotMeasurable
from investigator.verification_budget import VerificationBudget
from investigator.usage_governance import UsageHold


class RunCounters(unittest.TestCase):
    def test_diagnostic_phase_counts_continue_past_twelve_only_in_build_mode(self):
        state={'envelope':{'limits':{'cloud_calls':12}},'cloud_calls':12,
               'diagnostic_phase_counts':{'WALK':12,'REPRODUCTION':0}}
        with self.assertRaises(UsageHold):process_budget.admit(state,'next')
        with operating_mode():
            for _ in range(45):
                process_budget.admit(state,'next');process_budget.charge(state);state['cloud_calls']+=1
            self.assertEqual(process_budget.remaining(state),PHYSICAL_REQUESTS)
        self.assertEqual(state['cloud_calls'],57)
        self.assertEqual(state['diagnostic_phase_counts']['WALK'],57)
        with self.assertRaises(UsageHold):process_budget.admit(state,'next')

    def test_explicit_config_activates_the_same_diagnostic_behavior(self):
        state={'envelope':{'limits':{'cloud_calls':12}},'cloud_calls':40}
        process_budget.admit(state,'next',{'_estate':{'operating_mode':'BUILD_PHASE'}})
        with self.assertRaises(UsageHold):process_budget.admit(state,'next')

    def test_candidate_scope_and_legacy_form_counters_are_informational(self):
        workspace=SimpleNamespace(_form_candidate_count=12,dynamic_read_limit=12,_form_candidate_session='legacy')
        with self.assertRaises(NotMeasurable):candidate_read_budget.consume(workspace)
        with operating_mode():
            with candidate_read_budget.scope('form',12,12) as state:
                for ordinal in range(12,43):self.assertEqual(candidate_read_budget.consume(None),('form',ordinal))
                self.assertEqual(state['used'],43)
            self.assertEqual(candidate_read_budget.consume(workspace),('legacy',12))
        self.assertEqual(workspace._form_candidate_count,13)
        with self.assertRaises(NotMeasurable):candidate_read_budget.consume(workspace)
        with self.assertRaises(ValueError):
            with candidate_read_budget.scope('form',13,12):pass

    def test_verification_passes_forty_without_changing_old_cap_or_events(self):
        events=[];budget=VerificationBudget({'binding_verification':{'session_cap':40}},20,record=events.append)
        for _ in range(40):budget.read('SOURCE',lambda:None)
        with self.assertRaises(UsageHold):budget.read('TARGET',lambda:self.fail('legacy dispatch'))
        with operating_mode():
            self.assertEqual(budget.read('TARGET',lambda:17),17)
        self.assertEqual(budget.cap,40);self.assertEqual(budget.count,41)
        self.assertEqual(events[-1],{'event':'VERIFICATION_CAP','decision':'ADMITTED','count':41,'cap':40,'kind':'TARGET'})
        with operating_mode(),self.assertRaisesRegex(ValueError,'Unknown verification'):
            budget.read('WRITE',lambda:self.fail('unknown kind'))


class AdaptiveCounters(unittest.TestCase):
    def setUp(self):
        from test_adaptive_investigation import AdaptiveTests
        self.fixture=AdaptiveTests();self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)

    def exhausted(self):
        f=self.fixture;identity=f.create()
        with f.runtime.db() as db:
            state=f.agent.load(db,identity)
            state.update(planner_calls=40,cloud_calls=40,input_characters=2_000_000)
            f.agent.save(db,state,'TEST_OLD_RUN_COUNTERS')
        return identity

    def test_planner_runs_after_old_cumulative_limits_but_legacy_stops(self):
        from test_adaptive_investigation import decision
        f=self.fixture;identity=self.exhausted();f.planner.return_value=(decision(),{})
        with operating_mode():result=f.agent.step(identity)
        self.assertEqual(result['status'],'COMPLETED');self.assertEqual(result['planner_calls'],41)
        f.planner.assert_called_once();self.assertEqual(result['cloud_calls'],40)

    def test_legacy_still_stops_before_model_after_old_cumulative_limits(self):
        f=self.fixture;identity=self.exhausted();result=f.agent.step(identity)
        self.assertEqual(result['stop_reason'],'BUDGET_LIMIT');f.planner.assert_not_called()

    def test_build_mode_keeps_single_request_payload_bound(self):
        f=self.fixture;identity=self.exhausted()
        with operating_mode(),patch.object(f.agent,'payload',return_value={'oversized':'x'*100_000}):
            result=f.agent.step(identity)
        self.assertEqual(result['stop_reason'],'BUDGET_LIMIT');f.planner.assert_not_called()

    def test_build_mode_keeps_deadline(self):
        f=self.fixture;identity=self.exhausted();f.clock.return_value=10_000
        with operating_mode():result=f.agent.step(identity)
        self.assertEqual(result['stop_reason'],'DEADLINE');f.planner.assert_not_called()


class ScannerMeter(unittest.TestCase):
    def test_real_meter_uses_monthly_authority_with_historical_round_pin(self):
        from investigator.shared_state import SharedState
        from scan_estate_graph import Meter
        from tempfile import TemporaryDirectory
        from pathlib import Path
        with TemporaryDirectory() as folder:
            state=SharedState.offline(Path(folder)/'state.sqlite');state.migrate()
            retained={'policy':{'environment':'test','daily_limits':{'cloud_calls':1,'planner_calls':1,'input_characters':1,'output_tokens':8000},'max_inflight_planners':1,'no_progress_limit':2},'round_policy':{'id':'historical'}}
            state.put('usage_policy','test',retained)
            with operating_mode(category='INVESTIGATION'):
                meter=Meter(state,{'environment':'test'},1)
                try:
                    self.assertEqual(meter(lambda:7),7)
                    self.assertEqual(meter(lambda:8),8)
                    self.assertEqual(meter.used,2)
                    self.assertEqual(meter.usage.snapshot()['monthly']['used']['INVESTIGATION'],2)
                finally:meter.close()
            self.assertEqual(state.get('usage_policy','test')['body'],retained)

    def test_observer_publishes_each_result_after_settlement_and_sanitizes_failure(self):
        from scan_estate_graph import Meter, READ_OBSERVER
        state=Mock();state.get.return_value={'body':{'policy':{},'round_policy':{}}}
        events=[]
        with operating_mode(category='SCAN'),patch('investigator.shared_usage.SharedUsage') as authority:
            meter=Meter(state,{'environment':'test'},1);self.addCleanup(meter.close)
            def observe(label,body):
                self.assertEqual(authority.return_value.settle.call_count,body['ordinal'])
                events.append((label,body))
            token=READ_OBSERVER.set(observe)
            try:
                self.assertEqual(meter(lambda:{'count':3}),{'count':3})
                with self.assertRaisesRegex(RuntimeError,'secret-like provider text'):
                    meter(lambda:(_ for _ in ()).throw(RuntimeError('secret-like provider text')))
            finally:READ_OBSERVER.reset(token)
        self.assertEqual(events,[('physical_read:1',{'status':'COMPLETED','category':'SCAN','ordinal':1,'result':{'count':3}}),
                                 ('physical_read:2',{'status':'FAILED','category':'SCAN','ordinal':2,'error_type':'RuntimeError'})])

    def test_build_meter_ignores_old_pin_and_cap_and_preserves_category(self):
        from scan_estate_graph import Meter
        retained={'policy':{'daily_limits':{'cloud_calls':1}},'round_policy':{'id':'old'}}
        state=Mock();state.get.return_value={'body':retained}
        with patch('investigator.shared_usage.SharedUsage') as authority:
            with operating_mode(category='SCAN'):
                meter=Meter(state,{'environment':'test','policy_sha256':'stale','round_id':'stale','rolling_limit':1},1)
                self.addCleanup(meter.close)
                for _ in range(41):self.assertEqual(meter(lambda:7),7)
                self.assertEqual(meter.used,41)
                self.assertTrue(all(call.kwargs['purpose']=='SCAN' for call in authority.return_value.reserve.call_args_list))
            with operating_mode(category='INVESTIGATION'):
                probe=Meter(state,{'environment':'test'},1);self.addCleanup(probe.close);probe(lambda:8)
                self.assertEqual(authority.return_value.reserve.call_args.kwargs['purpose'],'INVESTIGATION')

    def test_monthly_authority_refusal_still_precedes_dispatch(self):
        from scan_estate_graph import Meter
        state=Mock();state.get.return_value={'body':{'policy':{},'round_policy':{}}};operation=Mock()
        with operating_mode(category='SCAN'),patch('investigator.shared_usage.SharedUsage') as authority:
            authority.return_value.reserve.side_effect=UsageHold('MONTHLY_PHYSICAL_SCAN_EXHAUSTED')
            meter=Meter(state,{'environment':'test'},1);self.addCleanup(meter.close)
            with self.assertRaises(UsageHold):meter(operation)
        operation.assert_not_called();self.assertEqual(meter.used,0)


if __name__=='__main__':unittest.main()
