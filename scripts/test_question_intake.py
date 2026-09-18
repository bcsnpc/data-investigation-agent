import copy
import json
from threading import Event, Thread
import unittest
from unittest.mock import MagicMock, patch

from investigator.question_intake import Intake, validate, snapshot, azure_resolve, wire_contract
from investigator.onboarding import Conflict
from investigator.usage_governance import UsageHold
from investigator.workspace import Workspace
import test_investigator_workspace as workspace_fixture


def proposal():
    return {'action': 'PROPOSE', 'model_id': 'model', 'measure_id': 'Unseen ratio', 'metric_quote': 'ratio',
            'question': None, 'filters': [{'column_id': 'c', 'operator': 'in', 'values': ['USD']}],
            'dimension_ids': [], 'scope_quotes': [{'column_id': 'c', 'quote': 'USD'}]}


def ask():
    return {'action': 'ASK', 'model_id': None, 'measure_id': None, 'metric_quote': None,
            'question': 'Which metric and exact filters should be checked?', 'filters': [], 'dimension_ids': [], 'scope_quotes': []}


class WireContractTests(unittest.TestCase):
    def payload(self):
        return {'text':'Compare an unfamiliar value for North.', 'models':[{
            'id':'model-id','measures':[{'id':'fabric://a/measure/Unfamiliar%20value','name':'Unfamiliar value'}],
            'columns':[{'column_id':'fabric://a/column/Region%20name','name':'Region name'}]}]}

    def test_opaque_handles_roundtrip_and_filter_quotes_stay_attached(self):
        payload=self.payload();original=copy.deepcopy(payload)
        proposed={'action':'PROPOSE','model_id':'m0','measure_id':'m0v0','metric_quote':'unfamiliar value','question':None,
                  'filters':[{'column_id':'m0c0','operator':'in','values':['North'],'quote':'North'}],
                  'dimension_ids':['m0c0']}
        with patch('ticket_planner.azure_generate',return_value=(proposed,{})) as generate:
            result,_=azure_resolve(payload)
        self.assertEqual(result['measure_id'],'fabric://a/measure/Unfamiliar%20value')
        self.assertEqual(result['scope_quotes'],[{'column_id':'fabric://a/column/Region%20name','quote':'North'}])
        self.assertNotIn('quote',result['filters'][0]);self.assertEqual(payload,original)
        schema=generate.call_args.kwargs['schema']
        self.assertEqual(schema['properties']['measure_id']['enum'],['m0v0',None])
        self.assertNotIn('scope_quotes',schema['properties'])
        self.assertEqual(schema['properties']['dimension_ids']['maxItems'],1)

    def test_global_proposal_cannot_add_detached_scope_quotes(self):
        proposed={'action':'PROPOSE','model_id':'m0','measure_id':'m0v0','metric_quote':'unfamiliar value',
                  'question':None,'filters':[],'dimension_ids':[]}
        with patch('ticket_planner.azure_generate',return_value=(proposed,{})):
            result,_=azure_resolve(self.payload())
        self.assertEqual(result['scope_quotes'],[])
        proposed['measure_id']='fabric://a/measure/Unfamiliar value'
        with patch('ticket_planner.azure_generate',return_value=(proposed,{})):
            with self.assertRaises(ValueError):azure_resolve(self.payload())


class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.h = workspace_fixture.WorkspaceTests(); self.h.setUp(); self.addCleanup(self.h.doCleanups)
        self.workspace = self.h.workspace
        self.resolver = MagicMock(return_value=(proposal(), {'usage': {'output_tokens': 80}}))
        self.workspace.intake = Intake(self.workspace, self.resolver)
        self.request = {'text': 'The ratio looks low for USD.', 'request_key': 'question-1', 'parent_id': None}

    def resolve(self): return self.workspace.intake.resolve(copy.deepcopy(self.request))

    def review(self, saved):
        return self.workspace.preview(dict(self.h.request, symptom=saved['text'], intake_id=saved['id']))

    def test_proposal_review_start_preserves_origin_and_uses_real_runtime(self):
        saved = self.resolve(); self.assertEqual(saved['status'], 'PROPOSED')
        self.h.native.assert_not_called(); self.h.planner.assert_not_called(); self.h.source.assert_not_called()
        p = self.review(saved); self.assertEqual(p['intake']['metric_quote'], 'ratio')
        run = self.workspace.start(p['id']); self.workspace.run_once(); result = self.workspace.session(run['id'])
        self.assertEqual(result['intake']['id'], saved['id']); self.assertFalse(result['cause_verified'])
        self.assertEqual(result['facts'][0]['values'][0]['[m0]']['value'], '7')

    def test_duplicate_request_and_history_make_no_calls(self):
        first = self.resolve(); self.assertEqual(first, self.resolve())
        self.assertEqual(first, self.workspace.intake.get(first['id']))
        self.resolver.assert_called_once()
        usage = self.h.agent.governor.snapshot()['reserved_today']
        self.assertEqual(usage['planner_calls'], 1); self.assertEqual(usage['cloud_calls'], 0)

    def test_changed_request_key_cannot_replace_question(self):
        self.resolve(); self.request['text'] = 'Different question'
        with self.assertRaises(Conflict): self.resolve()
        self.resolver.assert_called_once()

    def test_clarification_is_saved_and_answer_is_combined_without_queries(self):
        self.resolver.return_value = ask(), {}; parent = self.resolve()
        self.assertEqual(parent['status'], 'NEEDS_INPUT')
        with self.assertRaises(Conflict): self.review(parent)
        self.resolver.return_value = proposal(), {}
        self.request.update(text='Use the ratio for USD.', request_key='answer', parent_id=parent['id'])
        saved = self.resolve(); self.assertEqual(saved['turn'], 2)
        self.assertIn('Clarification: Use the ratio', self.resolver.call_args.args[0]['text'])
        self.h.native.assert_not_called()

    def test_clarification_requires_waiting_parent_and_has_turn_limit(self):
        saved = self.resolve(); self.request.update(request_key='answer', parent_id=saved['id'])
        with self.assertRaises(Conflict): self.resolve()
        self.resolver.return_value = ask(), {}; self.request.update(request_key='ask', parent_id=None)
        for i in range(4):
            saved = self.resolve(); self.request.update(request_key='turn-' + str(i), parent_id=saved['id'])
        with self.assertRaises(Conflict): self.resolve()

    def test_timeout_is_held_redacted_and_not_retried(self):
        self.resolver.side_effect = TimeoutError('secret provider response')
        saved = self.resolve(); self.assertEqual(saved['error'], 'RESOLUTION_UNCERTAIN')
        self.assertEqual(saved, self.resolve()); self.resolver.assert_called_once()
        self.assertNotIn('secret', json.dumps(saved))
        self.assertEqual(self.h.agent.governor.snapshot()['reservation_states'], {'UNCERTAIN': 1})

    def test_crash_reservation_survives_restart_without_reissue(self):
        self.resolver.side_effect = KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt): self.resolve()
        self.workspace.intake = Intake(self.workspace, self.resolver)
        saved = self.resolve(); self.assertEqual(saved['status'], 'RESOLVING'); self.resolver.assert_called_once()
        with self.assertRaises(Conflict): self.review(saved)

    def test_hold_releases_inflight_slot_without_refund_or_requery(self):
        self.resolver.side_effect = KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt): self.resolve()
        identity = self.workspace.intake.list()['questions'][0]['id']
        held = self.workspace.intake.hold(identity)
        self.assertEqual(held['status'], 'HELD')
        self.assertEqual(self.resolve(), held); self.resolver.assert_called_once()
        self.assertEqual(self.h.agent.governor.snapshot()['reservation_states'], {'UNCERTAIN': 1})
        self.resolver.side_effect = None; self.request['request_key'] = 'new-explicit-request'
        self.assertEqual(self.resolve()['status'], 'PROPOSED')
        self.assertEqual(self.h.agent.governor.snapshot()['reserved_today']['planner_calls'], 2)

    def test_hold_fences_late_provider_result(self):
        entered, release = Event(), Event(); results = []
        def resolve(_): entered.set(); release.wait(5); return proposal(), {}
        self.resolver.side_effect = resolve
        worker = Thread(target=lambda: results.append(self.resolve())); worker.start()
        self.assertTrue(entered.wait(5))
        try:
            identity = self.workspace.intake.list()['questions'][0]['id']
            self.workspace.intake.hold(identity)
        finally: release.set(); worker.join(5)
        self.assertFalse(worker.is_alive()); self.assertEqual(results[0]['status'], 'HELD')
        self.assertIsNone(results[0]['proposal'])

    def test_concurrent_duplicate_does_not_dispatch_twice(self):
        entered, release = Event(), Event(); results = []
        def resolve(_): entered.set(); release.wait(5); return proposal(), {}
        self.resolver.side_effect = resolve
        worker = Thread(target=lambda: results.append(self.resolve())); worker.start()
        self.assertTrue(entered.wait(5))
        try: self.assertEqual(self.resolve()['status'], 'RESOLVING')
        finally: release.set(); worker.join(5)
        self.resolver.assert_called_once(); self.assertEqual(results[0]['status'], 'PROPOSED')

    def test_shared_daily_budget_blocks_second_question_before_provider(self):
        self.h.agent.governor.policy['daily_limits']['planner_calls'] = 1
        self.resolve(); self.request['request_key'] = 'another'
        with self.assertRaises(UsageHold): self.resolve()
        self.resolver.assert_called_once()

    def test_provider_usage_violation_holds_proposal(self):
        self.resolver.return_value = proposal(), {'usage': {'output_tokens': 1501}}
        saved = self.resolve(); self.assertEqual(saved['error'], 'PROVIDER_USAGE_LIMIT')
        self.assertIsNone(saved['proposal'])
        with self.assertRaises(Conflict): self.review(saved)

    def test_usage_counts_are_recorded_without_provider_metadata(self):
        self.resolver.return_value = proposal(), {'usage': {'input_tokens': 50, 'output_tokens': 10}, 'response_id': 'private'}
        self.resolve()
        with self.h.store.connect() as db:
            row = db.execute('SELECT actual FROM adaptive_usage').fetchone()[0]
        self.assertEqual(json.loads(row), {'input_tokens': 50, 'output_tokens': 10})

    def test_catalog_change_during_preview_cannot_adopt_old_proposal(self):
        saved = self.resolve()
        from investigator.adaptive_candidates import catalog
        def changing(*args):
            result = catalog(*args); self.h.model['revision'] += 1; return result
        with patch('investigator.workspace.catalog', side_effect=changing):
            with self.assertRaises(Conflict): self.review(saved)

    def test_invalid_output_cannot_be_reviewed(self):
        for change in ({'measure_id': 'invented'}, {'model_id': 'foreign'}, {'filters': []}, {'metric_quote': 'absent'},
                       {'dimension_ids': ['foreign']}, {'scope_quotes': []}, {'query': 'SELECT 1'}):
            with self.subTest(change=change):
                self.request['request_key'] = str(change)
                self.resolver.return_value = dict(proposal(), **change), {}
                saved = self.resolve(); self.assertEqual(saved['status'], 'HELD')
                with self.assertRaises(Conflict): self.review(saved)
        self.h.native.assert_not_called()

    def test_model_change_during_provider_holds_proposal(self):
        def resolve(_): self.h.model['revision'] += 1; return proposal(), {}
        self.resolver.side_effect = resolve
        self.assertEqual(self.resolve()['error'], 'INVALID_OR_STALE_PROPOSAL')

    def test_stale_disabled_expired_config_and_engine_proposals_cannot_review(self):
        saved = self.resolve()
        original = copy.deepcopy(self.h.model)
        for mutate in [lambda: self.h.model.update(enabled=False), lambda: self.h.model.update(revision=99),
                       lambda: self.h.model['context'].update(changed=True)]:
            mutate()
            with self.assertRaises(Conflict): self.review(saved)
            self.h.model.clear(); self.h.model.update(copy.deepcopy(original))
        self.h.clock.return_value = saved['expires'] + 1
        with self.assertRaises(Conflict): self.review(saved)
        self.h.clock.return_value = 1000
        with patch('investigator.question_intake.fingerprint', return_value='other'):
            with self.assertRaises(Conflict): self.review(saved)
        self.h.config['changed'] = True
        with self.assertRaises(Conflict): self.review(saved)

    def test_manual_edits_must_not_claim_original_ai_provenance(self):
        saved = self.resolve(); self.h.request['filters'][0]['values'] = ['EUR']
        with self.assertRaises(Conflict): self.review(saved)
        manual = self.workspace.preview(self.h.request); self.assertIsNone(manual['intake'])

    def test_tampered_saved_question_fails_integrity(self):
        saved = self.resolve()
        with self.h.store.connect() as db: db.execute("UPDATE workspace_intakes SET body='{}'")
        with self.assertRaises(Conflict): self.workspace.intake.get(saved['id'])

    def test_history_only_does_not_resolve(self):
        self.workspace.execution_enabled = False
        with self.assertRaises(Conflict): self.resolve()
        self.resolver.assert_not_called()

    def test_catalog_excludes_disabled_and_sensitive_config_expressions(self):
        self.h.config['credential'] = 'should-not-leak'
        self.resolve(); payload = self.resolver.call_args.args[0]
        serialized = json.dumps(payload)
        self.assertNotIn('credential', serialized); self.assertNotIn('expression', serialized)
        self.assertNotIn('should-not-leak', serialized)
        self.h.model['enabled'] = False; self.request['request_key'] = 'disabled'
        with self.assertRaises(Conflict): self.resolve()

    def test_catalog_size_fails_without_silent_truncation(self):
        self.h.model['context']['measures'] *= 201
        with self.assertRaises(Conflict): self.resolve()
        self.resolver.assert_not_called()

    def test_scope_types_quotes_and_duplicate_filters(self):
        payload = {'text': self.request['text'], 'models': snapshot(self.workspace)['models']}
        for filt in [{'column_id': 'c', 'operator': 'in', 'values': [True]},
                     {'column_id': 'foreign', 'operator': 'in', 'values': ['USD']},
                     {'column_id': 'c', 'operator': 'range', 'values': ['A', 'Z']}]:
            with self.assertRaises(ValueError): validate(dict(proposal(), filters=[filt]), payload)
        with self.assertRaises(ValueError): validate(dict(proposal(), filters=proposal()['filters'] * 2), payload)
        with self.assertRaises(ValueError): validate(dict(proposal(), scope_quotes=[{'column_id': 'c', 'quote': 'EUR'}]), payload)

    def test_exact_date_boolean_and_decimal_scopes(self):
        payload = {'text': 'ratio for exact selection', 'models': snapshot(self.workspace)['models']}
        for kind, operator, values in [('boolean', 'in', [False]), ('decimal', 'range', ['0.25', '1.50']),
                                      ('dateTime', 'range', ['2026-09-01', '2026-09-08'])]:
            payload['models'][0]['columns'][0]['data_type'] = kind
            p = proposal(); p['filters'][0].update(operator=operator, values=values)
            p['scope_quotes'][0]['quote'] = 'exact selection'
            self.assertEqual(validate(p, payload), p)

    def test_empty_and_oversize_questions_never_call_provider(self):
        for content in ['', 'x' * 2001]:
            self.request['text'] = content
            with self.assertRaises(ValueError): self.resolve()
        self.resolver.assert_not_called()

    def test_ask_cannot_smuggle_selected_scope(self):
        with self.assertRaises(ValueError): validate(dict(ask(), measure_id='Unseen ratio'), {'text': '', 'models': []})

    def test_authenticated_api_resolve_read_and_review(self):
        url = '/api/workspace/questions'
        self.assertEqual(self.h.http(url, self.request, token='bad')['status'], '401 Unauthorized')
        self.resolver.assert_not_called()
        result = self.h.http(url, self.request); self.assertEqual(result['status'], '200 OK')
        identity = result['body']['id']
        self.assertEqual(self.h.http(url + '/' + identity)['body'], result['body'])
        self.assertEqual(self.h.http(url)['body']['questions'][0]['id'], identity)
        self.assertEqual(self.h.http(url, dict(self.request, sql='SELECT 1'))['status'], '400 Bad Request')
        self.resolver.assert_called_once()


if __name__ == '__main__': unittest.main()
