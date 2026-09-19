import copy
import json
from io import BytesIO
from threading import Thread,Event
import unittest
from unittest.mock import patch

import test_adaptive_investigation as fixture
from test_native_diagnostics import response
from investigator.adaptive_runtime import AdaptiveRuntime
from investigator.onboarding import Conflict
from investigator.usage_governance import UsageGovernor,UsageHold


class GovernanceTests(unittest.TestCase):
    def setUp(self):
        h=fixture.AdaptiveTests();h.setUp();self.addCleanup(h.doCleanups)
        self.helper=h
        for name in ('store','config','model','native','source','runtime','planner','clock','envelope'):setattr(self,name,getattr(h,name))
        self.store.environment='development'
        self.policy={'environment':'development','daily_limits':{'planner_calls':12,'cloud_calls':6,'input_characters':150000,'output_tokens':18000},'max_inflight_planners':1,'no_progress_limit':2}
        self.reset_agent()

    def reset_agent(self):self.agent=AdaptiveRuntime(self.runtime,self.planner,self.clock,usage_policy=self.policy)
    def create(self,key='case'):return self.agent.create(self.envelope,key)['id']
    def read_first(self,p):return fixture.decision(self.helper.choose(p)),{'usage':{'input_tokens':25,'output_tokens':10}}

    def test_cloud_limit_shared_across_sessions(self):
        self.policy['daily_limits']['cloud_calls']=1;self.reset_agent();self.planner.side_effect=self.read_first
        self.agent.step(self.create('first'));second=self.agent.step(self.create('second'))
        self.assertEqual(second['stop_reason'],'USAGE_LIMIT');self.native.assert_called_once()
        self.assertEqual(self.agent.governor.snapshot()['reserved_today']['cloud_calls'],1)

    def test_daily_planner_limit_survives_restart(self):
        self.policy['daily_limits']['planner_calls']=1;self.reset_agent();self.planner.return_value=(fixture.decision(),{})
        self.agent.run(self.create('first'));self.reset_agent();result=self.agent.run(self.create('second'))
        self.assertEqual(result['stop_reason'],'USAGE_LIMIT');self.planner.assert_called_once()

    def test_output_allowance_reserved_before_call(self):
        self.policy['daily_limits']['output_tokens']=1499;self.reset_agent()
        self.assertEqual(self.agent.run(self.create())['stop_reason'],'USAGE_LIMIT');self.planner.assert_not_called()

    def test_payload_character_limit_shared(self):
        self.policy['daily_limits']['input_characters']=1;self.reset_agent()
        self.assertEqual(self.agent.run(self.create())['stop_reason'],'USAGE_LIMIT');self.planner.assert_not_called()

    def test_configured_output_is_reserved_and_provider_settings_are_fenced(self):
        profile={'adapter':'azure','generation_options':{'max_output_tokens':4000,'timeout_seconds':120,'reasoning_effort':'medium'}}
        self.agent=AdaptiveRuntime(self.runtime,self.planner,self.clock,planner_profile=profile,usage_policy=self.policy)
        self.planner.return_value=(fixture.decision(),{'usage':{'output_tokens':2500}})
        self.agent.run(self.create())
        self.assertEqual(self.agent.governor.snapshot()['reserved_today']['output_tokens'],4000)
        self.assertEqual(self.planner.call_args.args[0]['generation_options']['reasoning_effort'],'medium')
        identity=self.create('changed');profile['generation_options']['reasoning_effort']='low'
        self.assertEqual(self.agent.run(identity)['stop_reason'],'ADMISSION_CHANGED')

    def test_payload_allowance_is_opt_in_and_cumulative_limit_still_applies(self):
        self.planner.return_value=(fixture.decision(),{})
        with patch.object(self.agent,'payload',return_value={'padding':'x'*34000}):
            self.assertEqual(self.agent.run(self.create('default'))['stop_reason'],'BUDGET_LIMIT')
        self.agent=AdaptiveRuntime(self.runtime,self.planner,self.clock,
            planner_profile={'generation_options':{'max_payload_characters':48000}},usage_policy=self.policy)
        original=self.agent.payload
        def larger(state,candidates):return {**original(state,candidates),'padding':'x'*34000}
        with patch.object(self.agent,'payload',side_effect=larger):
            self.assertEqual(self.agent.run(self.create('larger'))['stop_reason'],'NO_USEFUL_TEST')
            self.envelope['limits']['input_characters']=30000
            self.assertEqual(self.agent.run(self.create('cumulative'))['stop_reason'],'BUDGET_LIMIT')
        self.assertEqual(self.planner.call_count,1)

    def test_timeout_reserve_prevents_late_provider_dispatch(self):
        self.agent=AdaptiveRuntime(self.runtime,self.planner,self.clock,
            planner_profile={'adapter':'azure','generation_options':{'timeout_seconds':120}},usage_policy=self.policy)
        identity=self.create();self.clock.return_value+=800
        self.assertEqual(self.agent.run(identity)['stop_reason'],'DEADLINE');self.planner.assert_not_called()

    def test_provider_error_records_classes_without_messages(self):
        from investigator.generation_policy import error_summary
        inner=TimeoutError('secret request body');outer=RuntimeError('secret API key');outer.__cause__=inner
        self.assertEqual(error_summary(outer),{'error_type':'RuntimeError','cause_types':['TimeoutError']})
        inner.__cause__=outer
        self.assertEqual(len(error_summary(outer)['cause_types']),1)

    def test_explicit_planner_recovery_reserves_again_without_data_execution(self):
        class APITimeoutError(Exception):pass
        self.agent=AdaptiveRuntime(self.runtime,self.planner,self.clock,
            planner_profile={'adapter':'azure','max_planner_recoveries':1},usage_policy=self.policy)
        self.planner.side_effect=[APITimeoutError(),(fixture.decision(),{})]
        result=self.agent.run(self.create())
        self.assertEqual(result['status'],'COMPLETED');self.assertEqual(self.planner.call_count,2)
        states=self.agent.governor.snapshot()
        self.assertEqual(states['reserved_today']['output_tokens'],3000)
        self.assertEqual(states['reservation_states'],{'UNCERTAIN':1,'SETTLED':1})
        self.native.assert_not_called();self.source.assert_not_called()

    def test_repeated_timeout_stops_after_one_recovery(self):
        class APITimeoutError(Exception):pass
        self.agent=AdaptiveRuntime(self.runtime,self.planner,self.clock,
            planner_profile={'adapter':'azure','max_planner_recoveries':1},usage_policy=self.policy)
        self.planner.side_effect=APITimeoutError()
        self.assertEqual(self.agent.run(self.create())['stop_reason'],'PLANNER_FAILED')
        self.assertEqual(self.planner.call_count,2)

    def test_recovery_cannot_bypass_daily_budget(self):
        class APITimeoutError(Exception):pass
        self.policy['daily_limits']['planner_calls']=1
        self.agent=AdaptiveRuntime(self.runtime,self.planner,self.clock,
            planner_profile={'adapter':'azure','max_planner_recoveries':1},usage_policy=self.policy)
        self.planner.side_effect=APITimeoutError()
        self.assertEqual(self.agent.run(self.create())['stop_reason'],'USAGE_LIMIT')
        self.planner.assert_called_once()

    def test_incomplete_response_usage_is_settled_without_retry_or_execution(self):
        from investigator.generation_policy import ProviderResponseError
        self.agent=AdaptiveRuntime(self.runtime,self.planner,self.clock,
            planner_profile={'adapter':'azure','max_planner_recoveries':1},usage_policy=self.policy)
        self.planner.side_effect=ProviderResponseError('OUTPUT_TOKEN_LIMIT',{'output_tokens':1500,'input_tokens':20})
        identity=self.create();result=self.agent.run(identity)
        self.assertEqual(result['stop_reason'],'PLANNER_FAILED');self.planner.assert_called_once()
        self.native.assert_not_called();self.source.assert_not_called()
        snapshot=self.agent.governor.snapshot()
        self.assertEqual(snapshot['reservation_states'],{'SETTLED':1})
        self.assertEqual(snapshot['reserved_today']['output_tokens'],1500)
        with self.runtime.db() as db:
            event=json.loads(db.execute("SELECT detail FROM adaptive_events WHERE session_id=? AND kind='PLANNER_ERROR'",(identity,)).fetchone()[0])
        self.assertEqual(event['response_failure'],'OUTPUT_TOKEN_LIMIT')
        self.assertFalse(event['recovery_scheduled'])

    def test_actual_usage_does_not_refund_reservation(self):
        self.planner.return_value=(fixture.decision(),{'usage':{'output_tokens':10,'input_tokens':20}})
        self.agent.run(self.create())
        self.assertEqual(self.agent.governor.snapshot()['reserved_today']['output_tokens'],1500)
        with self.runtime.db() as db:r=db.execute('SELECT actual,status FROM adaptive_usage').fetchone()
        self.assertEqual(json.loads(r['actual'])['output_tokens'],10);self.assertEqual(r['status'],'SETTLED')

    def test_provider_overrun_blocks_later_reads(self):
        self.planner.side_effect=lambda p:(fixture.decision(self.helper.choose(p)),{'usage':{'output_tokens':2000}})
        result=self.agent.run(self.create());self.assertEqual(result['stop_reason'],'USAGE_LIMIT');self.native.assert_not_called()
        self.assertEqual(self.agent.governor.snapshot()['reservation_states']['VIOLATION'],1)

    def test_new_utc_day_has_new_reservations_without_erasing_history(self):
        self.policy['daily_limits']['planner_calls']=1;self.reset_agent();self.planner.return_value=(fixture.decision(),{})
        self.agent.run(self.create('day1'));self.clock.return_value+=86400
        result=self.agent.run(self.create('day2'));self.assertEqual(result['status'],'COMPLETED')
        with self.runtime.db() as db:self.assertEqual(db.execute('SELECT count(DISTINCT day) FROM adaptive_usage').fetchone()[0],2)

    def test_changed_policy_invalidates_admission(self):
        identity=self.create();self.policy['daily_limits']['cloud_calls']=5;self.reset_agent()
        self.assertEqual(self.agent.run(identity)['stop_reason'],'ADMISSION_CHANGED');self.planner.assert_not_called()

    def test_environment_mismatch_rejected(self):
        self.policy['environment']='other'
        with self.assertRaises(ValueError):self.reset_agent()

    def test_live_profile_requires_explicit_policy(self):
        agent=AdaptiveRuntime(self.runtime,self.planner,self.clock,planner_profile={'adapter':'azure'})
        with self.assertRaises(ValueError):agent.create(self.envelope,'unsafe')
        self.planner.assert_not_called()

    def test_failed_planner_keeps_reserved_budget(self):
        self.planner.side_effect=TimeoutError();result=self.agent.run(self.create())
        self.assertEqual(result['status'],'HELD');snapshot=self.agent.governor.snapshot()
        self.assertEqual(snapshot['reserved_today']['planner_calls'],1);self.assertEqual(snapshot['reservation_states']['UNCERTAIN'],1)

    def test_concurrent_sessions_obey_planner_limit(self):
        entered=Event();release=Event();errors=[]
        def planner(p):entered.set();release.wait(5);return fixture.decision(),{}
        self.planner.side_effect=planner;first=self.create('one');second=self.create('two')
        def worker():
            try:self.agent.run(first)
            except Exception as e:errors.append(type(e).__name__)
        thread=Thread(target=worker);thread.start();self.assertTrue(entered.wait(5))
        result=self.agent.run(second);self.assertEqual(result['stop_reason'],'USAGE_LIMIT')
        release.set();thread.join(5);self.assertFalse(errors);self.planner.assert_called_once()

    def test_reservation_and_session_transition_rollback_together(self):
        identity=self.create()
        with patch.object(self.agent,'save',side_effect=RuntimeError('disk failure')):
            with self.assertRaises(RuntimeError):self.agent.step(identity)
        self.assertEqual(self.agent.governor.snapshot()['reserved_today']['planner_calls'],0)
        self.assertEqual(self.agent.get(identity)['status'],'READY');self.planner.assert_not_called()

    def test_reservation_key_is_idempotent_and_cannot_change_cost(self):
        with self.runtime.db() as db:
            db.execute('BEGIN IMMEDIATE')
            for _ in range(2):self.agent.governor.reserve(db,'s','r','planner',10)
        self.assertEqual(self.agent.governor.snapshot()['reserved_today']['planner_calls'],1)
        with self.runtime.db() as db,self.assertRaises(UsageHold):self.agent.governor.reserve(db,'s','r','planner',20)

    def test_cancel_ready_is_idempotent_and_does_not_plan(self):
        identity=self.create();self.agent.cancel(identity);before=self.agent.get(identity)
        self.assertEqual(self.agent.cancel(identity),before);self.assertEqual(self.agent.run(identity)['status'],'CANCELLED')
        self.planner.assert_not_called()

    def test_cancel_active_planner_fences_late_action(self):
        entered=Event();release=Event();errors=[]
        def planner(p):entered.set();release.wait(5);return self.read_first(p)
        self.planner.side_effect=planner;identity=self.create()
        def worker():
            try:self.agent.step(identity)
            except Conflict:errors.append('fenced')
        thread=Thread(target=worker);thread.start();self.assertTrue(entered.wait(5))
        self.agent.cancel(identity);release.set();thread.join(5)
        self.assertEqual(errors,['fenced']);self.native.assert_not_called()
        self.assertEqual(self.agent.governor.snapshot()['reservation_states']['UNCERTAIN'],1)

    def test_cancel_between_child_creation_and_link_prevents_dispatch(self):
        identity=self.create();self.planner.side_effect=self.read_first;original=self.runtime.create
        def create(*args,**kwargs):
            self.agent.cancel(identity);return original(*args,**kwargs)
        with patch.object(self.runtime,'create',side_effect=create):result=self.agent.step(identity)
        self.assertEqual(result['status'],'CANCELLED');self.native.assert_not_called()
        with self.runtime.db() as db:self.assertEqual(db.execute('SELECT status FROM v2_runs').fetchone()[0],'CANCELLED')

    def test_cancel_remote_read_then_adopt_receipt_without_resume(self):
        entered=Event();release=Event();errors=[]
        def native(p):entered.set();release.wait(5);return response([{'[m0]':5}])
        self.native.side_effect=native;self.planner.side_effect=self.read_first;identity=self.create()
        def worker():
            try:self.agent.step(identity)
            except Exception as e:errors.append(type(e).__name__)
        thread=Thread(target=worker);thread.start();self.assertTrue(entered.wait(5));self.agent.cancel(identity)
        release.set();thread.join(5);self.assertFalse(errors)
        result=self.agent.reconcile_cancelled(identity)
        self.assertEqual(result['status'],'CANCELLED');self.assertEqual(len(result['observations']),1);self.native.assert_called_once()
        self.assertEqual(self.agent.reconcile_cancelled(identity),result)

    def test_unknown_remote_completion_stays_cancelled_and_blocked(self):
        self.native.side_effect=TimeoutError();self.planner.side_effect=self.read_first;identity=self.create()
        self.agent.step(identity);self.agent.cancel(identity)
        with self.assertRaises(Conflict):self.agent.reconcile_cancelled(identity)
        self.assertEqual(self.agent.get(identity)['status'],'CANCELLED');self.native.assert_called_once()

    def test_cancel_without_policy_can_settle_outstanding_local_usage(self):
        identity=self.create()
        with self.runtime.db() as db:
            db.execute('BEGIN IMMEDIATE');self.agent.governor.reserve(db,identity,'planner:1','planner',10)
        unconfigured=AdaptiveRuntime(self.runtime,None,self.clock)
        unconfigured.cancel(identity)
        self.assertEqual(self.agent.governor.snapshot()['reservation_states']['UNCERTAIN'],1)

    def test_repeated_blank_reads_stop_for_no_progress(self):
        self.native.return_value=response([{'[m0]':None}])
        self.planner.side_effect=lambda p:(fixture.decision(next(c['id'] for c in p['candidates'] if c['tool']=='native' and c['dimension_id'] is None)),{})
        result=self.agent.run(self.create());self.assertEqual(result['stop_reason'],'NO_PROGRESS');self.assertEqual(result['cloud_calls'],2)

    def test_zero_is_information_not_no_progress(self):
        from investigator.progress_policy import informative
        self.assertTrue(informative({'status':'COMPLETED','values':[{'[m0]':{'type':'decimal','value':'0'}}]}))
        self.assertFalse(informative({'status':'COMPLETED','values':[{'[dimension]':{'type':'string','value':'USD'},'[m0]':{'type':'blank','value':None}}]}))

    def test_admin_cancel_is_scoped_and_reader_cannot_use_it(self):
        from investigator.admin_api import create_app
        app=create_app(self.store,'a'*32,'r'*32,investigations=self.agent);identity=self.create()
        def call(token,path,method='POST'):
            statuses=[];body=app({'PATH_INFO':path,'REQUEST_METHOD':method,'HTTP_AUTHORIZATION':'Bearer '+token,
                'CONTENT_TYPE':'application/json','CONTENT_LENGTH':'2','wsgi.input':BytesIO(b'{}')},lambda s,h:statuses.append(s))
            return statuses[0],json.loads(b''.join(body))
        path='/api/v2/admin/models/model/adaptive-sessions/'+identity+'/cancel'
        self.assertEqual(call('r'*32,path)[0],'403 Forbidden');self.assertEqual(call('a'*32,path.replace('/model/','/other/'))[0],'404 Not Found')
        self.assertEqual(call('a'*32,path)[1]['status'],'CANCELLED')
        self.assertEqual(call('a'*32,'/api/v2/admin/usage','GET')[0],'200 OK')
