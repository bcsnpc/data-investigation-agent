import copy
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from investigator.claim_intake import ClaimIntake
from investigator.claim_investigations import ClaimInvestigations
from investigator.onboarding import Conflict, digest, encoded
from test_claim_intake import Store, CAT
import test_claim_projection as projection_fixture


class Agent:
    def __init__(self):
        self.config = {}
        self.planner_profile = {'adapter': 'injected'}
        self.begun = []
        self.finalized = []
        self.receipts = []
    def begin_claim_process(self, envelope, key, **hashes):
        self.begun.append((envelope, key, hashes))
        return {'id': 'session'}
    def process_adapter(self, identity):
        return SimpleNamespace(model={'id': 'model'})
    def finalize_claim_process(self, identity, result, **hashes):
        self.finalized.append(copy.deepcopy(result))
        return self.get(identity)
    def get(self, identity):
        return {'cloud_calls': len(self.receipts), 'physical_calls': len(self.receipts),
                'process_read_receipts': copy.deepcopy(self.receipts)}


class ClaimsExecutionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = Store(Path(self.tmp.name) / 'catalog.sqlite')
        self.agent = Agent()
        self.workspace = SimpleNamespace(store=self.store, agent=self.agent, execution_enabled=True,
                                          owner='test-operator', dynamic_read_limit=12)
        self.workspace.claims = ClaimIntake(self.workspace)
        self.controller = ClaimInvestigations(self.workspace)
        patcher = patch.object(self.workspace.claims, '_catalog', return_value=copy.deepcopy(CAT))
        patcher.start(); self.addCleanup(patcher.stop)
        self.model = {'id':'model', 'revision':1, 'context_id':'context'}
        self.store.get = lambda identity: copy.deepcopy(self.model)

    def confirmed(self, **changes):
        submitted = {'metric_phrase': 'Quantity', 'direction': 'LESS', 'comparator': 'OWN_COUNT',
                     'scope': {'kind': 'RECORDS'}, 'examples': ['22']}
        submitted.update(changes)
        claim = self.workspace.claims.submit({'request_key': 'submit', 'claim': submitted})
        self.assertEqual(claim['status'], 'AWAITING_CONFIRMATION')
        saved = self.workspace.claims.confirm({'id': claim['id'], 'revision': claim['revision'],
                                               'request_key': 'confirm', 'accepted': True})
        return {'id': saved['id'], 'revision': saved['revision'], 'request_key': 'run'}

    def planned(self, execute=None):
        return patch.object(self.controller, '_prepare', return_value=(
            {'status':'PLANNED', 'model_id':'model', 'measure_ids':['quantity'], 'limitations':[]},
            execute or (lambda adapter: {'status':'OBSERVED', 'summary':'The requested records agree.',
                                         'limitations':['SNAPSHOT_UNVERIFIED']})))

    def test_actual_submit_confirm_execute_is_once_only_and_preserves_pins(self):
        request = self.confirmed()
        with self.store.connect() as db:
            before = db.execute('SELECT body FROM claim_intakes').fetchone()[0]
        with self.planned():
            result = self.controller.run(request)
            self.assertEqual(result, self.controller.run(request))
        self.assertEqual(len(self.agent.begun),1)
        self.assertEqual(self.agent.begun[0][0]['limits']['cloud_calls'],12)
        self.assertEqual(result['status'],'COMPLETED')
        self.assertIn('timing',result['outputs']['business_explanation'])
        self.assertIn('served versions',result['outputs']['technical_narrative'])
        with self.store.connect() as db:
            self.assertEqual(before, db.execute('SELECT body FROM claim_intakes').fetchone()[0])
        with self.assertRaises(Conflict):
            self.controller.run(dict(request, request_key='second-run'))

    def test_no_execution_before_confirmation_or_when_disabled(self):
        raw = self.workspace.claims.submit({'request_key':'new','claim':{'direction':'STALE','scope':{'kind':'PAGE','report_id':'report','page_id':'page'}}})
        with self.assertRaises(Conflict):
            self.controller.run({'id':raw['id'],'revision':0,'request_key':'run'})
        request = self.confirmed()
        self.workspace.execution_enabled = False
        with self.assertRaises(Conflict): self.controller.run(request)
        self.assertEqual(self.agent.begun,[])

    def test_runtime_client_cannot_override_scope_route_or_keys(self):
        request = self.confirmed()
        for field in ('scope','route','keys','query','field_id'):
            with self.assertRaises(ValueError):
                self.controller.run(dict(request, **{field:'forged'}))
        self.assertEqual(self.agent.begun,[])

    def test_screenshot_without_compiled_context_holds_before_session(self):
        request = self.confirmed()
        with self.store.connect() as db:
            _, body = self.workspace.claims._load(db, request['id'])
            body['captured_context']={'visible_filter_scope':{'status':'NOT_COMPILED'}}
            db.execute('UPDATE claim_intakes SET body=?,body_hash=? WHERE id=?',
                       (encoded(body),digest(body),request['id']))
        result=self.controller.run(request)
        self.assertEqual(result['reason'],'SCREENSHOT_SCOPE_NOT_COMPILED')
        self.assertEqual(self.agent.begun,[])
        self.assertIn('security scope',result['outputs']['business_explanation'])

    def test_exception_keeps_read_receipt_and_once_only_terminal_result(self):
        request=self.confirmed()
        def execute(adapter):
            self.agent.receipts.append({'id':'retained-receipt','status':'COMPLETED'})
            raise RuntimeError('downstream consumer failure')
        with self.planned(execute):
            result=self.controller.run(request)
            again=self.controller.run(request)
        self.assertEqual(result,again)
        self.assertEqual(result['status'],'HELD')
        self.assertEqual(result['reads']['diagnostic'],1)
        self.assertEqual(result['reads']['receipts'][0]['id'],'retained-receipt')
        self.assertEqual(len(self.agent.begun),1)
        with self.store.connect()as db:
            failure=json.loads(db.execute('SELECT body FROM claim_execution_failures WHERE claim_id=? AND phase=?',
                (request['id'],'EXECUTION')).fetchone()[0])
        self.assertEqual(failure['message'],'downstream consumer failure')
        self.assertFalse(failure['message_redacted'])
        self.assertNotIn('downstream consumer failure',result['outputs']['business_explanation'])

    def test_changed_visible_definition_requires_reconfirmation(self):
        request=self.confirmed()
        changed=copy.deepcopy(CAT)
        changed['models'][0]['measures'][0]['name']='New Quantity'
        with patch.object(self.workspace.claims,'_catalog',return_value=changed):
            result=self.controller.run(request)
        self.assertEqual(result['reason'],'INTERPRETATION_RECONFIRMATION_REQUIRED')
        self.assertEqual(self.agent.begun,[])

    def test_same_stable_referent_revalidates_new_catalog_pin(self):
        request=self.confirmed()
        changed=copy.deepcopy(CAT);changed['models'][0]['revision']=2
        with patch.object(self.workspace.claims,'_catalog',return_value=changed),self.planned():
            result=self.controller.run(request)
        self.assertNotEqual(result['catalog_revalidation']['recorded_catalog_hash'],
                            result['catalog_revalidation']['current_catalog_hash'])
        self.assertEqual(result['status'],'COMPLETED')

    def test_unknown_target_is_not_replaced_by_another_card(self):
        request=self.confirmed()
        changed=copy.deepcopy(CAT);changed['models'][0]['visuals']=[]
        with patch.object(self.workspace.claims,'_catalog',return_value=changed):
            result=self.controller.run(request)
        self.assertEqual(result['reason'],'CONFIRMED_TARGET_UNAVAILABLE')
        self.assertEqual(self.agent.begun,[])

    def test_model_asset_guid_cannot_become_explanation(self):
        request=self.confirmed()
        bad={'status':'OBSERVED','summary':'Read asset 12345678-1234-1234-1234-123456789abc.'}
        with self.planned(lambda adapter:bad):result=self.controller.run(request)
        self.assertEqual(result['reason'],'CLAIM_OUTPUT_VALIDATION_FAILED')
        self.assertNotIn('12345678',result['outputs']['business_explanation'])

    def test_conservative_legacy_hold_does_not_run_an_unrelated_total(self):
        request=self.confirmed(direction='DEFINITION')
        result=self.controller.run(request)
        self.assertEqual(result['reason'],'LEGACY_ROUTE_ADMISSION_UNAVAILABLE')
        self.assertEqual(self.agent.begun,[])

    def test_page_definition_question_is_not_routed_to_value_comparison(self):
        request=self.confirmed(direction='DEFINITION',scope={'kind':'PAGE','report_id':'report','page_id':'page'})
        result=self.controller.run(request)
        self.assertEqual(result['reason'],'LEGACY_ROUTE_ADMISSION_UNAVAILABLE')
        self.assertEqual(self.agent.begun,[])

    def test_filter_question_is_not_routed_to_page_consistency(self):
        request=self.confirmed(direction='CONTEXT',scope={'kind':'PAGE','report_id':'report','page_id':'page'})
        result=self.controller.run(request)
        self.assertEqual(result['reason'],'UNIMPLEMENTED_CLAIM_ROUTE')
        self.assertEqual(self.agent.begun,[])

    def test_output_header_retains_confirmed_request_and_conservative_ending(self):
        request=self.confirmed()
        with self.planned():result=self.controller.run(request)
        for output in result['outputs'].values():
            self.assertTrue(output.startswith('Confirmed request:'))
            self.assertIn('Quantity',output)
            self.assertIn('The bounded checks completed',output)
            self.assertNotIn('Is this interpretation correct?',output)

    def test_serialized_checker_body_cannot_become_prose(self):
        request=self.confirmed()
        with self.planned(lambda adapter:{'status':'OBSERVED','summary':'{"rows": 123}'}):
            result=self.controller.run(request)
        self.assertEqual(result['reason'],'CLAIM_OUTPUT_VALIDATION_FAILED')
        self.assertNotIn('"rows"',result['outputs']['business_explanation'])

    def test_malformed_prose_evidence_still_retains_terminal_result(self):
        request=self.confirmed()
        with self.planned(lambda adapter:{'status':'OBSERVED','summary':'Checked.', 'evidence':[{'id':12}]}):
            result=self.controller.run(request)
        self.assertEqual(result['reason'],'CLAIM_OUTPUT_VALIDATION_FAILED')
        self.assertEqual(result,self.controller.get(request['id']))

    def test_submitted_example_list_normalizes_only_explicit_exact_keys(self):
        request=self.confirmed(examples=[900099, '22'])
        with self.store.connect()as db:_,body=self.workspace.claims._load(db,request['id'])
        prepared,execute=self.controller._prepare(body)
        self.assertEqual(prepared['status'],'PLANNED')
        self.assertEqual(prepared['request'],{'kind':'SET_RECONCILIATION','keys':['900099','22']})
        self.assertEqual(prepared['measure_ids'],['quantity'])
        # Actual confirm/run, not a hand-built claim body.
        observed={}
        def projection(adapter,projection,measure):
            observed.update(request=projection,measure=measure)
            return {'status':'OBSERVED','summary':'The bounded keys were checked.','limits':[]}
        with patch.object(self.controller,'_projection',side_effect=projection):result=self.controller.run(request)
        self.assertEqual(result['status'],'COMPLETED')
        self.assertEqual(observed['request']['keys'],['900099','22'])
        self.assertEqual(observed['measure'],'quantity')

    def test_example_prose_cannot_be_guessed_into_a_key(self):
        request=self.confirmed(examples=['Record 900099 may be the one'])
        result=self.controller.run(request)
        self.assertEqual(result['reason'],'CLAIM_PROJECTION_REQUEST_UNRESOLVED')
        self.assertEqual(self.agent.begun,[])

    def test_textual_filter_is_not_dropped_for_record_projection(self):
        request=self.confirmed(filters=['North'])
        result=self.controller.run(request)
        self.assertEqual(result['reason'],'CLAIM_SCOPE_NOT_COMPILED')
        self.assertEqual(self.agent.begun,[])

    def test_visual_field_projection_cannot_erase_visual_restrictions(self):
        request=self.confirmed(direction='FIELD_WRONG',scope={'kind':'VISUALS','report_id':'report',
            'page_id':'page','visual_ids':['card']})
        result=self.controller.run(request)
        self.assertEqual(result['reason'],'VISUAL_PROJECTION_SCOPE_UNSUPPORTED')
        self.assertEqual(self.agent.begun,[])

    def test_unknown_producer_status_cannot_default_to_completed(self):
        request=self.confirmed()
        with self.planned(lambda adapter:{'status':'MAYBE_GREEN'}):result=self.controller.run(request)
        self.assertEqual(result['status'],'HELD')
        self.assertEqual(result['reason'],'CLAIM_EXECUTION_FAILED')

    def test_missing_producer_status_cannot_default_to_completed(self):
        request=self.confirmed()
        with self.planned(lambda adapter:{}):result=self.controller.run(request)
        self.assertEqual(result['status'],'HELD')

    def test_dollar_or_provider_auth_stop_is_retained_then_propagated(self):
        from investigator.model_spend import SpendHold
        request=self.confirmed()
        with self.planned(lambda adapter:(_ for _ in ()).throw(SpendHold('stop'))):
            with self.assertRaises(SpendHold):self.controller.run(request)
        result=self.controller.get(request['id'])
        self.assertEqual(result['status'],'HELD')
        self.assertEqual(result['failure']['type'],'SpendHold')
        self.assertEqual(len(self.agent.begun),1)

    def test_bare_check_cannot_promote_causal_or_defect_claim(self):
        request=self.confirmed()
        with self.planned(lambda adapter:{'status':'OBSERVED_DIFFERENCE','cause_verified':True}):
            result=self.controller.run(request)
        self.assertEqual(result['status'],'HELD')
        self.assertEqual(result['reason'],'CLAIM_EXECUTION_FAILED')

    def test_finalization_failure_still_seals_once_only_controller_result(self):
        request=self.confirmed()
        with self.planned(),patch.object(self.agent,'finalize_claim_process',side_effect=RuntimeError('failed')):
            result=self.controller.run(request)
        self.assertEqual(result['reason'],'CLAIM_FINALIZATION_FAILED')
        self.assertEqual(result['status'],'HELD')
        self.assertIn('persistence failed',result['outputs']['business_explanation'])
        self.assertEqual(result,self.controller.run(request))

    def test_business_attestation_limit_does_not_display_receipt_id(self):
        result=self.controller._prose({'summary':'The example key was checked.'},'PARTIAL',None,
            ['Surface fields not self-reported for receipt private-receipt: connection.',
             'SNAPSHOT_UNVERIFIED: timing was not excluded.'])
        self.assertNotIn('private-receipt',result['business_explanation'])
        self.assertNotIn('SNAPSHOT_UNVERIFIED',result['business_explanation'])
        self.assertIn('private-receipt',result['technical_narrative'])

    def test_page_attestation_gaps_are_rendered_per_receipt_without_mutation(self):
        checks={'kind':'PAGE_CONSISTENCY','status':'NOT_COMPARABLE','summary':'The values use different restrictions.',
            'evidence':[{'id':'receipt-a','attestation':{'unattested_fields':['connection']}},
                        {'id':'receipt-b','attestation':{'unattested_fields':['connection']}}],
            'comparisons':[{'outcome':'NOT_COMPARABLE','reason':'DIFFERENT_DECLARED_RESTRICTIONS'}]}
        before=copy.deepcopy(checks)
        limits=self.controller._limits(checks,['SNAPSHOT_UNVERIFIED'])
        self.assertEqual(limits,self.controller._limits(checks,limits))
        reason=self.controller._held_reason(checks)
        self.assertEqual(reason,'DIFFERENT_DECLARED_RESTRICTIONS')
        result=self.controller._prose(checks,'HELD',reason,limits)
        self.assertIn('receipt receipt-a: connection',result['technical_narrative'])
        self.assertIn('receipt receipt-b: connection',result['technical_narrative'])
        self.assertNotIn('receipt-a',result['business_explanation'])
        for output in result.values():
            self.assertIn('Recommended action: Ask the report owner',output)
            self.assertIn('compare matching declared scope',output)
        self.assertEqual(checks,before)

    def test_actual_run_retains_evidenced_hold_reason_and_attestation_limits(self):
        request=self.confirmed()
        checks={'status':'NOT_COMPARABLE','kind':'PAGE_CONSISTENCY','summary':'92 versus16 use different restrictions.',
            'evidence':[{'id':'page-receipt','attestation':{'unattested_fields':['connection']}}],
            'comparisons':[{'outcome':'NOT_COMPARABLE','reason':'DIFFERENT_DECLARED_RESTRICTIONS'}]}
        with self.planned(lambda adapter:checks):result=self.controller.run(request)
        self.assertEqual(result['status'],'HELD')
        self.assertEqual(result['reason'],'DIFFERENT_DECLARED_RESTRICTIONS')
        self.assertIn('Surface fields not self-reported for receipt page-receipt: connection.',result['limits'])
        self.assertEqual(result['outputs']['technical_narrative'].count('receipt page-receipt: connection'),1)

    def test_generic_held_and_freshness_actions_do_not_invent_a_cause(self):
        for checks in ({'status':'HELD'}, {'status':'UNAVAILABLE','kind':'PAGE_FRESHNESS'}):
            reason=self.controller._held_reason(checks)
            self.assertTrue(reason)
            result=self.controller._prose(checks,'HELD',reason,[])
            for output in result.values():
                self.assertIn('Recommended action:',output)
                self.assertNotIn('fix the defect',output)

    def test_multiple_evidenced_gaps_are_not_collapsed_to_one_invented_reason(self):
        checks={'status':'NOT_COMPARABLE','comparisons':[
            {'outcome':'NOT_COMPARABLE','reason':'DIFFERENT_DECLARED_RESTRICTIONS'},
            {'outcome':'NOT_COMPARABLE','reason':'DIFFERENT_METRICS'}]}
        self.assertEqual(self.controller._held_reason(checks),'MULTIPLE_COMPARISON_GAPS')


class NativeClaimExecutionTests(unittest.TestCase):
    def setUp(self):
        self.fixture=projection_fixture.ProjectionTests()
        self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
        self.agent=Agent();self.agent.config=self.fixture.config
        self.agent.config['_estate']={'layers':[
            {'asset_id':'app','role':'APPLICATION','business_name':'application'},
            {'asset_id':'landing','role':'LANDING','business_name':'loaded data'},
            {'asset_id':'semantic','role':'SEMANTIC','business_name':'report calculation'}]}
        self.workspace=SimpleNamespace(store=self.fixture.store,agent=self.agent,execution_enabled=True,
            owner='test-operator',dynamic_read_limit=12)
        self.workspace.claims=ClaimIntake(self.workspace)
        self.controller=ClaimInvestigations(self.workspace)
        catalog=copy.deepcopy(CAT)
        catalog['models'][0]['columns']=[{'column_id':'memo','name':'Memo'},
                                       {'column_id':'category','name':'Category'}]
        patcher=patch.object(self.workspace.claims,'_catalog',return_value=catalog)
        patcher.start();self.addCleanup(patcher.stop)
        self.fixture.adapter.resolve_path=lambda measure:self.fixture.path
        self.agent.process_adapter=lambda identity:self.fixture.adapter
        original_meter=self.fixture.adapter.meter_read
        def meter(tool,execute):
            result=original_meter(tool,execute)
            self.agent.receipts.append({'logical_tool':tool,'status':'COMPLETED'})
            return result
        self.fixture.adapter.meter_read=meter

    def run_claim(self,direction,scope=None,examples=None):
        claim={'metric_phrase':'Quantity','direction':direction,'comparator':'APPLICATION',
               'scope':scope or {'kind':'RECORDS'},'examples':examples if examples is not None else ['22']}
        first=self.workspace.claims.submit({'request_key':'submit','claim':claim})
        self.assertEqual(first['status'],'AWAITING_CONFIRMATION')
        confirmed=self.workspace.claims.confirm({'id':first['id'],'revision':first['revision'],
            'request_key':'confirm','accepted':True})
        request={'id':confirmed['id'],'revision':confirmed['revision'],'request_key':'run'}
        result=self.controller.run(request)
        self.assertEqual(result,self.controller.run(request))
        self.assertEqual(len(self.agent.begun),1)
        return result

    def test_set_reconciliation_actual_receipts_and_first_drop_are_rendered(self):
        self.fixture.rows={'app':[{'count_0':1}],'landing':[{'count_0':0}],'semantic':[{'count_0':0}]}
        result=self.run_claim('LESS')
        self.assertEqual(result['status'],'COMPLETED')
        self.assertEqual(result['reads']['diagnostic'],3)
        self.assertEqual(result['checks']['status'],'OBSERVED_DIFFERENCE')
        self.assertIn('Record 22 has 0 rows in loaded data',result['outputs']['business_explanation'])
        self.assertIn('first observed disappearance',result['outputs']['business_explanation'])
        self.assertIn('APPLICATION to LANDING',result['outputs']['technical_narrative'])
        self.assertFalse(result['checks']['defect_established'])

    def test_multiplicity_global_counts_are_not_a_business_correctness_claim(self):
        self.fixture.rows={layer:[{'all_rows':4,'distinct_keys':2,'null_keys':1,'count_0':2}]
                           for layer in ('app','landing','semantic')}
        result=self.run_claim('MORE')
        self.assertEqual(result['status'],'COMPLETED')
        self.assertIn('4 rows and 2 distinct',result['outputs']['business_explanation'])
        self.assertIn('1 rows repeat',result['outputs']['business_explanation'])
        self.assertIn('Business-key intent',result['outputs']['business_explanation'])
        self.assertFalse(result['checks']['cause_verified'])

    def test_duplicate_record_field_is_incomparable_not_wrong_value(self):
        self.fixture.rows={layer:[{'count_0':2,'value_0':'UNSAFE_MAX_RESULT'}]for layer in ('app','landing','semantic')}
        result=self.run_claim('FIELD_WRONG',{'kind':'RECORDS','field_id':'memo'})
        self.assertEqual(result['status'],'HELD')
        self.assertEqual(result['checks']['status'],'NOT_COMPARABLE')
        self.assertIn('not comparable',result['outputs']['business_explanation'])
        self.assertNotIn('UNSAFE_MAX_RESULT',result['outputs']['business_explanation'])
        self.assertNotIn('results differ',result['outputs']['business_explanation'])

    def test_field_change_uses_exact_typed_field_and_names(self):
        self.fixture.rows={layer:[{'count_0':1,'value_0':'first'if layer=='app'else'next'}]
                           for layer in ('app','landing','semantic')}
        result=self.run_claim('FIELD_WRONG',{'kind':'RECORDS','field_id':'memo'})
        self.assertEqual(result['status'],'COMPLETED')
        self.assertIn('checked Memo is first',result['outputs']['business_explanation'])
        self.assertIn('checked Memo is next',result['outputs']['business_explanation'])
        self.assertFalse(result['checks']['defect_established'])

    def test_each_key_has_its_own_first_drop_in_output(self):
        self.fixture.rows={'app':[{'count_0':1,'count_1':1}],
            'landing':[{'count_0':0,'count_1':1}], 'semantic':[{'count_0':0,'count_1':0}]}
        result=self.run_claim('LESS',examples=['22','23'])
        business=result['outputs']['business_explanation']
        self.assertIn('first observed disappearance for record 22 is between application and loaded data',business)
        self.assertIn('first observed disappearance for record 23 is between loaded data and report calculation',business)

    def test_global_decomposition_requires_no_record_example_and_renders_dimension(self):
        self.fixture.rows={layer:[{'marker':0,'group_value':1,'quantity':10 if layer=='app' else 20,'row_count':2}]
                           for layer in ('app','landing','semantic')}
        result=self.run_claim('WRONG_BREAKDOWN',{'kind':'RECORDS','dimension_id':'category'},examples=[])
        self.assertEqual(result['status'],'COMPLETED')
        self.assertIn('Category 1 totals 10 in application',result['outputs']['business_explanation'])
        self.assertIn('Category 1 totals 20 in loaded data',result['outputs']['business_explanation'])
        self.assertEqual(result['checks']['coverage'],'DECLARED_UNFILTERED_ENTITY_GROUPS')

    def test_roles_are_not_assumed_without_estate_declarations(self):
        self.agent.config.pop('_estate')
        result=self.run_claim('LESS')
        self.assertIn('UNDECLARED to UNDECLARED',result['outputs']['technical_narrative'])
        self.assertNotIn('APPLICATION to LANDING',result['outputs']['technical_narrative'])


if __name__ == '__main__':
    unittest.main()
