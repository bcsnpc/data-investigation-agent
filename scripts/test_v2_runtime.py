import unittest
from unittest.mock import MagicMock, patch

import test_source_diagnostics as source_fixture
from test_native_diagnostics import fixture, response
from investigator.runtime import Runtime
from investigator.onboarding import Conflict
from investigator.runtime import read_run
from threading import Thread, Event


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        helper = source_fixture.SourceTests(); helper.setUp(); self.addCleanup(helper.doCleanups)
        self.store = helper.store; self.config = helper.config; self.model = helper.model
        self.native = MagicMock(return_value=response([{'[m0]':5}]))
        self.source = MagicMock(return_value={'value':'5','row_count':'5','nonblank_count':'5'})
        self.runtime = Runtime(self.store,self.config,self.native,self.source)
        self.request = {'native_plan':fixture()[1], 'source_plan':helper.plan, 'measure_id':'Unseen ratio',
                        'mapping_id':None,'call_budget':2}

    def create(self):return self.runtime.create(self.request,'case-1')['id']

    def test_full_run_has_pinned_receipts_budget_and_insufficient_outcome(self):
        identity = self.create(); result = self.runtime.execute(identity)
        self.assertEqual(result['status'],'COMPLETED');self.assertEqual(result['calls_reserved'],2)
        self.assertEqual(result['outcome']['outcome'],'INSUFFICIENT_EVIDENCE')
        self.assertFalse(result['outcome']['comparable'])
        self.assertEqual([s['status'] for s in result['steps']],['COMPLETED']*3)
        self.assertNotIn('lease_token',result)
        self.native.assert_called_once();self.source.assert_called_once()

    def test_completed_run_and_idempotent_creation_do_not_repeat_queries(self):
        identity = self.create();self.runtime.execute(identity)
        self.assertEqual(self.create(),identity)
        self.runtime.execute(identity)
        self.native.assert_called_once();self.source.assert_called_once()
        self.request['call_budget']=3
        with self.assertRaises(Conflict):self.create()

    def test_invalid_budget_and_mixed_model_rejected_before_dispatch(self):
        for budget in [True,1,11]:
            self.request['call_budget']=budget
            with self.assertRaises(ValueError):self.create()
        self.native.assert_not_called();self.source.assert_not_called()

    def test_disable_before_dispatch_holds_without_query(self):
        identity=self.create();self.model['enabled']=False
        with self.assertRaises(Conflict):self.runtime.execute(identity)
        self.native.assert_not_called()

    def test_engine_change_requires_new_admission(self):
        identity=self.create()
        with patch('investigator.runtime.fingerprint',return_value='different'):
            with self.assertRaises(Conflict):self.runtime.execute(identity)
        self.native.assert_not_called()

    def test_crash_before_dispatch_can_reconcile_and_fences_old_worker(self):
        identity=self.create();token=self.runtime.claim(identity)
        self.assertEqual(self.runtime.reconcile(identity)['status'],'READY')
        with self.assertRaises(Conflict):self.runtime.commit(identity,0,token,{'id':'fake','status':'COMPLETED'})
        self.assertEqual(self.runtime.execute(identity)['status'],'COMPLETED')

    def test_crash_after_each_receipt_adopts_without_resending(self):
        for ordinal in range(3):
            with self.subTest(ordinal=ordinal):
                identity=self.runtime.create(self.request,'crash-'+str(ordinal))['id']
                original=self.runtime.commit
                def crash(run_id,index,token,result):
                    if index==ordinal:raise SystemExit('simulated crash')
                    return original(run_id,index,token,result)
                with patch.object(self.runtime,'commit',side_effect=crash):
                    with self.assertRaises(SystemExit):self.runtime.execute(identity)
                n=self.native.call_count;s=self.source.call_count
                recovered=self.runtime.reconcile(identity)
                if recovered['status']!='COMPLETED':self.runtime.execute(identity)
                self.assertEqual(self.native.call_count,n)
                self.assertEqual(self.source.call_count,s+(1 if ordinal==0 else 0))
                self.assertEqual(self.runtime.get(identity)['calls_reserved'],2)

    def test_unknown_remote_completion_blocks_all_new_dispatch(self):
        identity=self.create();self.native.side_effect=KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt):self.runtime.execute(identity)
        with self.assertRaises(Conflict):self.runtime.reconcile(identity)
        other=self.runtime.create(self.request,'other')['id']
        with self.assertRaises(Conflict):self.runtime.execute(other)
        self.assertEqual(self.runtime.get(identity)['calls_reserved'],1)
        self.source.assert_not_called()

    def test_timeout_preserves_uncertain_reservation(self):
        identity=self.create();self.native.side_effect=TimeoutError()
        result=self.runtime.execute(identity)
        self.assertEqual(result['status'],'HELD');self.assertEqual(result['steps'][0]['status'],'DISPATCHED')
        with self.assertRaises(Conflict):self.runtime.reconcile(identity)
        self.native.assert_called_once();self.source.assert_not_called()

    def test_failure_stops_pipeline_and_no_automatic_retry(self):
        identity=self.create();self.native.side_effect=RuntimeError('secret')
        result=self.runtime.execute(identity)
        self.assertEqual(result['status'],'HELD');self.assertEqual(result['steps'][0]['status'],'FAILED')
        self.assertNotIn('secret',str(result));self.source.assert_not_called()
        with self.assertRaises(Conflict):self.runtime.execute(identity)

    def test_reserved_budget_cannot_be_reset_by_resume(self):
        identity=self.create()
        with self.runtime.db() as db:db.execute('UPDATE v2_runs SET calls_reserved=2 WHERE id=?',(identity,))
        result=self.runtime.execute(identity)
        self.assertEqual(result['status'],'HELD');self.native.assert_not_called()

    def test_changed_connection_and_scope_integrity_rejected(self):
        identity=self.create();self.config['sql']['database']='other'
        with self.assertRaises(Conflict):self.runtime.execute(identity)
        self.config['sql']['database']='db'
        with self.runtime.db() as db:db.execute("UPDATE v2_runs SET request_hash='bad' WHERE id=?",(identity,))
        with self.assertRaises(ValueError):self.runtime.execute(identity)

    def test_concurrent_worker_cannot_duplicate_dispatch(self):
        identity=self.create();entered=Event();release=Event()
        def slow(req):
            entered.set();release.wait(5)
            return response([{'[m0]':5}])
        self.native.side_effect=slow
        worker=Thread(target=lambda:self.runtime.execute(identity));worker.start()
        try:
            self.assertTrue(entered.wait(3))
            with self.assertRaises(Conflict):self.runtime.execute(identity)
            with self.assertRaises(Conflict):self.runtime.reconcile(identity)
        finally:release.set();worker.join(8)
        self.assertFalse(worker.is_alive());self.native.assert_called_once()

    def test_midflight_disable_reconciles_terminal_receipt_without_resuming(self):
        identity=self.create()
        def disable(req):
            self.model['enabled']=False
            return response([{'[m0]':5}])
        self.native.side_effect=disable
        self.assertEqual(self.runtime.execute(identity)['status'],'HELD')
        result=self.runtime.reconcile(identity)
        self.assertEqual(result['status'],'HELD');self.assertEqual(result['steps'][0]['status'],'FAILED')
        self.source.assert_not_called()

    def test_tampered_orphan_receipt_not_adopted(self):
        identity=self.create()
        with patch.object(self.runtime,'commit',side_effect=SystemExit()):
            with self.assertRaises(SystemExit):self.runtime.execute(identity)
        with self.runtime.db() as db:
            db.execute("UPDATE native_diagnostics SET request='{}'")
        with self.assertRaises((Conflict,KeyError)):self.runtime.reconcile(identity)
        self.native.assert_called_once();self.source.assert_not_called()

    def test_read_projection_is_scoped_and_contains_no_worker_token(self):
        identity=self.create();self.runtime.execute(identity)
        result=read_run(self.store,'model',identity)
        self.assertEqual(result,self.runtime.get(identity));self.assertNotIn('lease_token',str(result))
        with self.assertRaises(KeyError):read_run(self.store,'other',identity)

    def test_source_first_plan_uses_registry_not_fixed_layer_order(self):
        order=[]
        self.source.side_effect=lambda req:(order.append('source') or {'value':'5','row_count':'5','nonblank_count':'5'})
        self.native.side_effect=lambda req:(order.append('native') or response([{'[m0]':5}]))
        plan={'model_id':'model','call_budget':2,'actions':[
            {'tool':'source','input':self.request['source_plan']},
            {'tool':'native','input':self.request['native_plan']},
            {'tool':'compare','input':{'native_step':1,'source_step':0,'measure_id':'Unseen ratio','mapping_id':None}}]}
        identity=self.runtime.create(plan,'source-first')['id']
        self.assertEqual(self.runtime.execute(identity)['status'],'COMPLETED')
        self.assertEqual(order,['source','native'])

    def test_multiple_native_observations_use_explicit_dependency_reference(self):
        self.native.side_effect=[response([{'[m0]':3}]),response([{'[m0]':5}])]
        plan={'model_id':'model','call_budget':3,'actions':[
            {'tool':'native','input':self.request['native_plan']},
            {'tool':'native','input':self.request['native_plan']},
            {'tool':'source','input':self.request['source_plan']},
            {'tool':'compare','input':{'native_step':1,'source_step':2,'measure_id':'Unseen ratio','mapping_id':None}}]}
        result=self.runtime.execute(self.runtime.create(plan,'multi-read')['id'])
        self.assertEqual(result['calls_reserved'],3)
        self.assertEqual(result['outcome']['observations']['native']['value'],'5')

    def test_single_observation_finishes_without_inventing_comparison(self):
        plan={'model_id':'model','call_budget':1,'actions':[{'tool':'source','input':self.request['source_plan']}]}
        result=self.runtime.execute(self.runtime.create(plan,'single')['id'])
        self.assertEqual(result['status'],'COMPLETED');self.assertEqual(result['calls_reserved'],1)
        self.assertEqual(result['outcome']['outcome'],'INSUFFICIENT_EVIDENCE');self.native.assert_not_called()

    def test_unknown_tools_and_forward_dependencies_are_rejected(self):
        for action in [{'tool':'arbitrary_sql','input':{}},
                       {'tool':'compare','input':{'native_step':1,'source_step':2,'measure_id':'Unseen ratio','mapping_id':None}}]:
            with self.assertRaises(ValueError):self.runtime.create({'model_id':'model','call_budget':2,'actions':[action]},'invalid')

    def test_crash_before_local_assessment_replays_no_cloud_calls(self):
        identity=self.create()
        with patch('investigator.runtime.comparisons.assess',side_effect=SystemExit()):
            with self.assertRaises(SystemExit):self.runtime.execute(identity)
        self.assertEqual(self.runtime.reconcile(identity)['status'],'READY')
        result=self.runtime.execute(identity)
        self.assertEqual(result['status'],'COMPLETED');self.assertEqual(result['calls_reserved'],2)
        self.native.assert_called_once();self.source.assert_called_once()


if __name__=='__main__':unittest.main()
