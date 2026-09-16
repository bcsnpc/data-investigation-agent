import copy
from decimal import Decimal
import unittest
from unittest.mock import MagicMock
import test_record_discovery as fixture
from test_native_diagnostics import response
from test_adaptive_investigation import decision
from investigator import record_readback, record_bindings
from investigator.adaptive_candidates import catalog
from investigator.runtime import Runtime
from investigator.adaptive_runtime import AdaptiveRuntime


class JointCaptureTests(unittest.TestCase):
    def setUp(self):
        self.h=fixture.DiscoveryTests();self.h.setUp();self.addCleanup(self.h.doCleanups)
        self.store,self.model,self.config=self.h.store,self.h.model,self.h.config
        self.measure=self.h.envelope['measure_id']
        self.asset=next(a for a in self.model['context']['reports'][0]['model_assets'] if a['id']==self.measure)
        self.asset['metadata']={'expression':"SUM('O''Brien'[amount])"}
        self.model['context']['semantic_graph']['measures'][self.measure].update(operations=['AGGREGATE'],dependencies=[])
        self.plan=dict(self.h.h.nplan,aggregate_measure_id=self.measure)

    def build(self):return record_readback.build(self.store,self.plan,self.config,'native_records')
    def rows(self,total=Decimal('30'),rows=None):
        rows=[('A','10',1),('B','20',1)] if rows is None else rows
        result=[{'[c0]':k,'[c1]':Decimal(v) if v is not None else None,'[multiplicity]':m,'[__aggregate]':total} for k,v,m in rows]
        if not result:result.append({'[c0]':None,'[c1]':None,'[multiplicity]':None,'[__aggregate]':total})
        return response(result)

    def test_query_combines_one_scalar_and_bounded_groups(self):
        r=self.build();self.assertEqual(r['query'].count('EVALUATE'),1)
        self.assertIn('GENERATEALL(',r['query']);self.assertIn('TOPN(4,',r['query'])
        self.assertEqual(r['joint_aggregate']['measure_id'],self.measure)
        self.assertEqual(r['query'].count('USD'),2)

    def test_exact_total_reconciles_without_cause_or_generation_claim(self):
        r=record_readback.extract(self.rows(),self.build());a=r['joint_aggregate']
        self.assertEqual(a['status'],'CAPTURE_RECONCILES');self.assertEqual(a['observed']['value'],'30')
        self.assertEqual(a['reconstructed']['row_count'],'2')
        self.assertFalse(a['root_cause_verified']);self.assertFalse(a['shared_generation_verified'])
        self.assertFalse(r['snapshot_comparable'])

    def test_mismatch_remains_diagnostic(self):
        a=record_readback.extract(self.rows(Decimal('31')),self.build())['joint_aggregate']
        self.assertEqual(a['status'],'CAPTURE_INCONSISTENCY');self.assertFalse(a['root_cause_verified'])

    def test_multiplicity_and_blank_values(self):
        a=record_readback.extract(self.rows(Decimal('20'),[('A','10',2),('B',None,3)]),self.build())['joint_aggregate']
        self.assertEqual(a['status'],'CAPTURE_RECONCILES');self.assertEqual(a['reconstructed']['row_count'],'5')

    def test_empty_and_all_blank_sum(self):
        for rows in ([],[('A',None,2)]):
            a=record_readback.extract(self.rows(None,rows),self.build())['joint_aggregate']
            self.assertEqual(a['status'],'CAPTURE_RECONCILES');self.assertEqual(a['observed']['type'],'blank')

    def test_count_uses_multiplicity_and_empty_native_blank(self):
        self.asset['metadata']['expression']="COUNTROWS('O''Brien')"
        for rows,total in [([('A','10',2)],2),([],None)]:
            self.assertEqual(record_readback.extract(self.rows(total,rows),self.build())['joint_aggregate']['status'],'CAPTURE_RECONCILES')

    def test_partial_groups_do_not_reconcile_even_if_total_matches_prefix(self):
        self.plan['limit']=1
        r=record_readback.extract(self.rows(),self.build())
        self.assertEqual(r['completeness'],'PARTIAL');self.assertEqual(r['joint_aggregate']['status'],'NOT_ASSESSED')

    def test_missing_duplicate_or_malformed_aggregate_rejected(self):
        original=self.rows()['results'][0]['tables'][0]['rows']
        cases=[original+[original[-1]],[],[{'[c0]':None,'[c1]':None,'[multiplicity]':None}],
               [dict(original[-1],**{'[__kind]':'other'})], [dict(original[-1],**{'[__aggregate]':'30'})],
               [dict(original[-1],**{'[__aggregate]':True})]]
        for rows in cases:
            with self.subTest(rows=rows),self.assertRaises(ValueError):record_readback.extract(response(rows),self.build())

    def test_changed_totals_and_malformed_empty_placeholder_rejected(self):
        for extra in ({'[__aggregate]':1},{'unexpected':1},{'[multiplicity]':None}):
            rows=self.rows()['results'][0]['tables'][0]['rows'];rows[0].update(extra)
            with self.assertRaises(ValueError):record_readback.extract(response(rows),self.build())

    def test_unsupported_expression_and_missing_sum_projection_rejected(self):
        for expr in ["SUM('O''Brien'[amount])+1","DIVIDE(1,2)"]:
            self.asset['metadata']['expression']=expr
            with self.assertRaises(ValueError):self.build()
        self.asset['metadata']['expression']="SUM('O''Brien'[amount])";self.plan['column_ids']=['key']
        with self.assertRaises(ValueError):self.build()

    def test_source_cannot_request_joint_aggregate(self):
        with self.assertRaises(ValueError):record_readback.build(self.store,dict(self.h.h.splan,aggregate_measure_id=self.measure),self.config,'source_records')

    def test_receipt_is_sealed_and_replay_dispatches_once(self):
        native=MagicMock(return_value=self.rows());runtime=Runtime(self.store,self.config,native,None)
        req={'model_id':'model','call_budget':1,'actions':[{'tool':'native_records','input':self.plan}]}
        created=runtime.create(req,'joint');run=runtime.execute(created['id'])
        self.assertEqual(run['status'],'COMPLETED');runtime.execute(created['id']);native.assert_called_once()
        rid=run['steps'][0]['result']['id'];saved=record_readback.read(self.store,'model',rid)
        self.assertEqual(saved['result']['joint_aggregate']['status'],'CAPTURE_RECONCILES')
        with self.store.connect() as db:db.execute("UPDATE record_readbacks SET result='{}' WHERE id=?",(rid,))
        with self.assertRaises(ValueError):record_readback.read(self.store,'model',rid)

    def test_discovery_joint_capture_is_explicit_and_review_pinned(self):
        review=self.h.register();legacy=self.h.selected()
        self.assertNotIn('aggregate_measure_id',legacy[0]['plan'])
        self.h.envelope['joint_native_records']=True
        joint=next(c for c in self.h.selected() if c['tool']=='native_records')
        self.assertEqual(joint['plan']['aggregate_measure_id'],self.measure)
        self.assertEqual(joint['record_mapping']['hash'],review['hash'])

    def test_unsupported_discovery_retains_legacy_read_with_gap(self):
        self.h.register();self.h.envelope['joint_native_records']=True
        self.asset['metadata']['expression']='DIVIDE(1,2)'
        candidates,gaps=self.h.candidates()
        self.assertTrue(any(g['reason']=='JOINT_NATIVE_CAPTURE_UNSUPPORTED' for g in gaps))
        self.assertTrue(any(c['tool']=='native_records' and 'aggregate_measure_id' not in c['plan'] for c in candidates))

    def test_adaptive_observation_contains_saved_joint_evidence(self):
        self.h.register();self.h.envelope['joint_native_records']=True
        native=MagicMock(side_effect=lambda r:self.rows() if 'joint_aggregate' in r else response([{'[m0]':Decimal('30')}]))
        def choose(p):
            tool='native' if not p['observations'] else 'native_records'
            return (decision(next(c['id'] for c in p['candidates'] if c['tool']==tool)) if len(p['observations'])<2 else decision()),{}
        planner=MagicMock(side_effect=choose)
        agent=AdaptiveRuntime(Runtime(self.store,self.config,native,None),planner)
        state=agent.run(agent.create(self.h.envelope,'adaptive-joint')['id'])
        self.assertEqual(state['status'],'COMPLETED')
        self.assertEqual(state['observations'][1]['joint_aggregate']['status'],'CAPTURE_RECONCILES')
        self.assertIn('joint_aggregate',planner.call_args.args[0]['observations'][1]);self.assertEqual(native.call_count,2)

    def test_reader_verifier_one_call_and_sealed_replay(self):
        import test_reader_runtime as reader_fixture
        from investigator.native_identity import KEY,make
        from test_reader_execution import READER
        h=reader_fixture.ReaderRuntimeTests();h.setUp();self.addCleanup(h.doCleanups)
        def execute(cfg,request):
            raw=h.response(cfg,request);raw.pop(KEY)
            for row in raw['results'][0]['tables'][0]['rows']:row['[__aggregate]']=2
            return dict(raw,**{KEY:make(raw,request,READER)})
        h.transport.side_effect=execute
        r=h.execute(joint_measure='New Metric')
        self.assertTrue(r['summary']['runtime_verification_passed']);self.assertEqual(r['summary']['calls_reserved'],1)
        self.assertEqual(h.execute(joint_measure='New Metric',status_only=True)['summary'],r['summary'])
        h.transport.assert_called_once()


if __name__=='__main__':unittest.main()
