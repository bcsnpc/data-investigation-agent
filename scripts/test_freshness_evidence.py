import copy
import hashlib
from io import BytesIO
import json
import unittest
from unittest.mock import MagicMock

import test_source_diagnostics as fixture
import test_adaptive_investigation as adaptive_fixture
from investigator import freshness, source_diagnostics
from investigator.adaptive_candidates import observation, diagnostic_pairs
from investigator.admin_api import create_app
from investigator.onboarding import Conflict
from investigator.runtime import Runtime


def timestamp_column(store, identity):
    with fixture.database(store.inventory) as db:
        raw = db.execute('SELECT metadata FROM assets WHERE id=?', (identity,)).fetchone()[0]
        metadata = dict(json.loads(raw), data_type='datetime2', scale=7)
        raw = json.dumps(metadata, sort_keys=True, ensure_ascii=False)
        db.execute('UPDATE assets SET metadata=?,content_hash=? WHERE id=?',
                   (raw, hashlib.sha256(raw.encode()).hexdigest(), identity))


class FreshnessTests(unittest.TestCase):
    def setUp(self):
        helper = fixture.SourceTests(); helper.setUp(); self.addCleanup(helper.doCleanups)
        for name in ('store', 'model', 'config', 'plan', 'obj'):
            setattr(self, name, getattr(helper, name))
        timestamp_column(self.store, self.obj + '/amount')
        self.plan.update(operation='watermark_age_microseconds', column_id=self.obj + '/amount')
        self.body = {'plan': copy.deepcopy(self.plan), 'max_age_seconds': 60,
                     'timestamp_meaning': 'Lab committed UTC heartbeat timestamp', 'timezone': 'UTC',
                     'authority_reference': 'Test fixture policy; not a production SLA'}

    def reviewed(self):
        policy = freshness.register(self.store, 'model', self.body, 'test-reviewer', self.config)
        return dict(self.plan, freshness_policy_id=policy['id'])

    def run_read(self, value='60000001', count='2', nonblank='2', plan=None):
        return source_diagnostics.run(self.store, plan or self.plan, self.config,
                                      lambda req: {'value': value, 'row_count': count, 'nonblank_count': nonblank})

    def test_query_is_parameterized_catalog_watermark_not_metric_sum(self):
        request = source_diagnostics.build(self.store, self.plan, self.config)
        self.assertIn('DATEDIFF_BIG(microsecond,MAX([amount]),SYSUTCDATETIME())', request['query'])
        self.assertIn('COUNT_BIG([amount]) AS nonblank_count', request['query'])
        self.assertNotIn('USD', request['query'])
        self.assertIsNone(request['freshness_policy'])

    def test_no_policy_is_a_gap_even_for_old_timestamp(self):
        result = self.run_read()['result']['freshness']
        self.assertEqual(result['classification'], 'INSUFFICIENT_EVIDENCE')
        self.assertFalse(result['condition_verified'])

    def test_threshold_is_strict_and_microsecond_boundary_preserved(self):
        plan = self.reviewed()
        for value, expected in [('59999999', 'WATERMARK_WITHIN_POLICY'), ('60000000', 'WATERMARK_WITHIN_POLICY'),
                                ('60000001', 'WATERMARK_AGE_EXCEEDED'), ('0', 'WATERMARK_WITHIN_POLICY')]:
            with self.subTest(value=value):
                receipt = self.run_read(value, plan=plan)
                self.assertEqual(receipt['status'], 'COMPLETED')
                result = receipt['result']['freshness']
                self.assertEqual(result['classification'], expected)
                self.assertTrue(result['condition_verified'])
                self.assertFalse(result['root_cause_verified'])
                self.assertFalse(result['delivery_eligible'])

    def test_empty_null_partial_null_and_future_are_gaps(self):
        plan = self.reviewed()
        for value, count, nonblank in [(None,'0','0'), (None,'2','0'), ('90000000','2','1'), ('-1','2','2')]:
            with self.subTest(value=value, count=count, nonblank=nonblank):
                receipt = self.run_read(value, count, nonblank, plan)
                self.assertEqual(receipt['status'], 'COMPLETED')
                self.assertFalse(receipt['result']['freshness']['condition_verified'])

    def test_invalid_age_and_nullability_fail_closed(self):
        for value, nonblank in [('1.5','2'), ('315537897600000001','2'), ('NaN','2'), (None,'2'), ('0','0')]:
            with self.subTest(value=value, nonblank=nonblank):
                self.assertEqual(self.run_read(value, nonblank=nonblank)['status'], 'FAILED')

    def test_unknown_timezone_and_unreviewed_meaning_rejected(self):
        for change in [{'timezone':'local'}, {'max_age_seconds':True}, {'max_age_seconds':0},
                       {'max_age_seconds':31536001}, {'authority_reference':''}, {'timestamp_meaning':''}]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                freshness.register(self.store, 'model', dict(self.body, **change), 'reviewer', self.config)

    def test_type_and_column_gates(self):
        for change in [{'column_id':self.obj+'/currency'}, {'column_id':'unknown'}, {'filters':[]}]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                source_diagnostics.build(self.store, dict(self.plan, **change), self.config)

    def test_exact_scope_and_revision_binding(self):
        plan = self.reviewed()
        for change in [{'filters':[{'column_id':self.obj+'/currency','values':['EUR']}]},
                       {'freshness_policy_id':None}, {'revision':4}]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                source_diagnostics.build(self.store, dict(plan, **change), self.config)

    def test_cross_model_policy_access_rejected(self):
        plan = self.reviewed()
        with self.assertRaises(KeyError):freshness.read(self.store, 'other', plan['freshness_policy_id'])

    def test_changed_connection_invalidates_policy(self):
        plan = self.reviewed()
        self.config['sql']['auth']['changed'] = True
        with self.assertRaises(Conflict):source_diagnostics.build(self.store, plan, self.config)

    def test_policy_tamper_rejected(self):
        plan = self.reviewed()
        with self.store.connect() as db:db.execute("UPDATE freshness_policies SET body_hash='bad'")
        with self.assertRaises(Conflict):source_diagnostics.build(self.store, plan, self.config)

    def test_revocation_preserves_history_and_blocks_new_read(self):
        plan = self.reviewed(); receipt = self.run_read(plan=plan)
        freshness.revoke(self.store, 'model', plan['freshness_policy_id'], 'Meaning no longer valid', 'reviewer')
        with self.assertRaises(Conflict):source_diagnostics.build(self.store, plan, self.config)
        historical = source_diagnostics.evidence(self.store, 'model', receipt['id'])
        self.assertTrue(historical['result']['freshness']['condition_verified'])
        self.assertFalse(historical['freshness_policy_current'])
        self.assertEqual(historical['result']['freshness']['evaluated_at'], 'SQL_OBSERVATION_TIME')

    def test_revocation_during_read_holds_result(self):
        plan = self.reviewed()
        def execute(req):
            freshness.revoke(self.store, 'model', plan['freshness_policy_id'], 'Withdrawn', 'reviewer')
            return {'value':'1', 'row_count':'2', 'nonblank_count':'2'}
        receipt = source_diagnostics.run(self.store, plan, self.config, execute)
        self.assertEqual(receipt['status'], 'HELD')
        self.assertNotIn('freshness', receipt['result'])

    def test_timeout_keeps_uncertain_receipt_and_no_finding(self):
        receipt = source_diagnostics.run(self.store, self.reviewed(), self.config, MagicMock(side_effect=TimeoutError()))
        self.assertEqual(receipt['status'], 'INTERRUPTED')
        self.assertNotIn('freshness', receipt['result'])

    def test_policy_cannot_attach_to_other_aggregate(self):
        plan = dict(self.reviewed(), operation='count_rows', column_id=None)
        with self.assertRaises(ValueError):source_diagnostics.build(self.store, plan, self.config)

    def test_observation_keeps_condition_and_never_compares_age_to_metric(self):
        plan = self.reviewed(); receipt = self.run_read(plan=plan)
        candidate = {'id':'candidate', 'tool':'source', 'plan':plan, 'measure_id':'m', 'dimension_id':None}
        source = observation(candidate, {'id':'run', 'steps':[{'result':receipt}]})
        native = dict(source, tool='native', values=[{'[m0]':{'type':'decimal', 'value':'100'}}])
        self.assertEqual(diagnostic_pairs([native, source]), [])
        self.assertTrue(source['freshness']['condition_verified'])

    def test_durable_runtime_replay_reuses_receipt(self):
        transport = MagicMock(return_value={'value':'60000001', 'row_count':'2', 'nonblank_count':'2'})
        runtime = Runtime(self.store, self.config, None, transport)
        request = {'model_id':'model', 'actions':[{'tool':'source','input':self.reviewed()}], 'call_budget':1}
        identity = runtime.create(request, 'watermark')['id']
        result = runtime.execute(identity)
        self.assertEqual(result['status'], 'COMPLETED')
        self.assertTrue(result['steps'][0]['result']['result']['freshness']['condition_verified'])
        runtime.execute(identity); transport.assert_called_once()

    def test_admin_policy_api_requires_role_and_connection(self):
        app = create_app(self.store, 'a'*32, 'r'*32)
        for token, expected in [('r'*32,'403 Forbidden'), ('a'*32,'503 Service Unavailable')]:
            statuses = []; raw = json.dumps(self.body).encode()
            list(app({'PATH_INFO':'/api/v2/admin/models/model/freshness-policies', 'REQUEST_METHOD':'POST',
                      'HTTP_AUTHORIZATION':'Bearer '+token, 'CONTENT_TYPE':'application/json',
                      'CONTENT_LENGTH':str(len(raw)), 'wsgi.input':BytesIO(raw)}, lambda s,h:statuses.append(s)))
            self.assertEqual(statuses, [expected])

    def test_admin_register_read_and_revoke(self):
        controller = MagicMock(); controller.runtime.config = self.config
        app = create_app(self.store, 'a'*32, 'r'*32, investigations=controller)
        def request(path, body=None):
            statuses=[]; raw=json.dumps(body).encode() if body is not None else b''
            result=b''.join(app({'PATH_INFO':'/api/v2/admin/models/model/freshness-policies'+path,
                                'REQUEST_METHOD':'POST' if body is not None else 'GET',
                                'HTTP_AUTHORIZATION':'Bearer '+'a'*32, 'CONTENT_TYPE':'application/json',
                                'CONTENT_LENGTH':str(len(raw)), 'wsgi.input':BytesIO(raw)}, lambda s,h:statuses.append(s)))
            self.assertEqual(statuses,['200 OK'])
            return json.loads(result)
        created=request('',self.body)
        self.assertEqual(request('/'+created['id'])['body_hash'],created['body_hash'])
        self.assertIsNotNone(request('/'+created['id']+'/revoke',{'reason':'Retired'})['revocation'])

    def test_adaptive_watermark_flow_preserves_finding_without_cause_claim(self):
        helper=adaptive_fixture.AdaptiveTests(); helper.setUp(); self.addCleanup(helper.doCleanups)
        plan=helper.envelope['source_tests'][0]['plan']
        column=plan['object_id']+'/amount'; timestamp_column(helper.store,column)
        plan.update(operation='watermark_age_microseconds',column_id=column)
        policy=freshness.register(helper.store,'model',dict(self.body,plan=copy.deepcopy(plan)),'reviewer',helper.config)
        plan['freshness_policy_id']=policy['id']
        helper.source.return_value={'value':'60000001','row_count':'3','nonblank_count':'3'}
        helper.planner.side_effect=lambda p:(adaptive_fixture.decision(helper.choose(p,tool='source')) if not p['observations'] else adaptive_fixture.decision(),{})
        result=helper.agent.run(helper.create())
        self.assertEqual(result['status'],'COMPLETED')
        self.assertEqual(result['outcome']['scoped_conditions'][0]['classification'],'WATERMARK_AGE_EXCEEDED')
        self.assertFalse(result['outcome']['cause_verified'])
        self.assertEqual(result['outcome']['diagnostic_pairs'],[])
        helper.source.assert_called_once(); helper.native.assert_not_called()
        helper.agent.run(result['id']); helper.source.assert_called_once()


if __name__ == '__main__':unittest.main()
