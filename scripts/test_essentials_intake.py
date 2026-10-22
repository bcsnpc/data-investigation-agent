from copy import deepcopy
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from investigator.essentials_intake import VERSION, admit, rank, nodes, retained_text, submit, reply

CAT={'models':[{'id':'model','reports':[{'id':'report','name':'Billing'}],
               'measures':[{'id':'mrr','name':'Monthly Recurring Revenue'},{'id':'net','name':'Net Revenue'}],
               'visuals':[{'target_id':'global-card','names':['Global MRR','Overview'],
                           'report_id':'report','page_id':'overview','page_names':['Overview'],'measure_ids':['mrr']},
                          {'target_id':'detail-card','names':['By Account'],
                           'report_id':'report','page_id':'accounts','page_names':['Accounts'],'measure_ids':['mrr']},
                          {'target_id':'net-card','names':['Net Revenue'],
                           'report_id':'report','page_id':'overview','page_names':['Overview'],'measure_ids':['net']}]}]}


def request(**overrides):
    return {'version':VERSION,'request_key':'one','report':'Billing','page':'Overview','number':'Global MRR',
            'goal':'COMPARE','comparison':{'kind':'SOURCE','reference':'Billing application'},'value':'950',**overrides}


class EssentialsTests(unittest.TestCase):
    def test_complete_essentials_admit_without_question_or_live_calls(self):
        result=admit(request(),CAT)
        self.assertEqual(result['status'],'READY');self.assertEqual(result['question_count'],0)
        self.assertEqual(result['scope']['target_id'],'global-card')
        self.assertFalse(result['investigation_executed'])
        self.assertEqual(result['reported_figure']['value'],'950')

    def test_missing_required_comparison_is_hold_not_an_invented_reference(self):
        result=admit(request(comparison=None),CAT)
        self.assertEqual(result['status'],'HELD')
        self.assertEqual(result['reason'],'ESSENTIALS_INVALID_OR_MISSING')
        self.assertEqual(result['questions'],[])

    def test_freshness_and_definition_do_not_require_fake_numeric_comparator(self):
        for kind in ('FRESHNESS','DEFINITION'):
            with self.subTest(kind=kind):
                result=admit(request(goal=kind,comparison=None),CAT)
                self.assertEqual(result['status'],'READY');self.assertIsNone(result['comparison'])

    def test_page_is_optional_but_report_is_not(self):
        data=request();data.pop('page')
        self.assertEqual(admit(data,CAT)['status'],'READY')
        data.pop('report');self.assertEqual(admit(data,CAT)['status'],'HELD')

    def test_selected_page_limits_loose_name_candidates(self):
        data=request(number='revenue')
        enrichment=[{'subject':'mrr','synonyms':['revenue'],'business_meaning':'MRR','status':'INFERRED'},
                    {'subject':'net','synonyms':['revenue'],'business_meaning':'Net','status':'INFERRED'}]
        data['page']='Accounts'
        result=admit(data,CAT,enrichment=enrichment)
        self.assertEqual(result['status'],'READY');self.assertEqual(result['scope']['node_id'],'mrr')
        self.assertIsNone(result['scope']['target_id'])
        self.assertEqual(result['selected_number']['match_source'],'ENRICHMENT_INFERRED')

    def test_measure_anchor_never_selects_a_visual_the_ticket_did_not_name(self):
        result=admit(request(number='Monthly Recurring Revenue'),CAT)
        self.assertEqual(result['status'],'READY');self.assertIsNone(result['scope']['target_id'])
        self.assertEqual(result['scope']['node_kind'],'MEASURE')
        self.assertNotIn('cell_address',result['scope'])

    def test_unknown_visual_does_not_fall_back_to_a_different_card(self):
        result=admit(request(number='Unknown Global card'),CAT)
        self.assertEqual(result['status'],'HELD')
        self.assertNotIn('scope',result)

    def test_tie_asks_once_from_real_named_candidates_then_holds(self):
        enrichment=[{'subject':'mrr','synonyms':['revenue'],'status':'INFERRED'},
                    {'subject':'net','synonyms':['revenue'],'status':'INFERRED'}]
        result=admit(request(number='revenue'),CAT,enrichment=enrichment)
        self.assertEqual(result['status'],'CLARIFYING');self.assertEqual(result['question_count'],1)
        choices=result['questions'][0]['choices']
        self.assertEqual({c['label'] for c in choices},{'Monthly Recurring Revenue','Net Revenue'})
        self.assertNotIn('model',result['questions'][0]['text'])
        second=admit(request(number='revenue'),CAT,enrichment=enrichment,questions_asked=1)
        self.assertEqual(second['reason'],'AMBIGUITY_AFTER_ONE_QUESTION');self.assertEqual(second['questions'],[])

    def test_business_correctness_is_not_an_automatic_technical_answer(self):
        result=admit(request(description='Please confirm this number is the intended value for that view.'),CAT)
        self.assertEqual(result['reason'],'BUSINESS_INTENT_REQUIRES_OWNER')

    def test_unknown_filters_are_not_dropped_to_force_a_ready_result(self):
        result=admit(request(filters=[{'column_id':'account','operator':'in','values':['North']}]),CAT)
        self.assertEqual(result['reason'],'FILTER_COLUMN_UNRESOLVED')
        self.assertEqual(result['supplied_filters'][0]['values'],['North'])

    def test_typed_user_filter_is_validated_and_preserved_without_lower_scope_claim(self):
        catalog=deepcopy(CAT);catalog['models'][0]['columns']=[{'column_id':'account','name':'Account','data_type':'string'}]
        filters=[{'column_id':'account','operator':'in','values':['North']}]
        result=admit(request(filters=filters),catalog)
        self.assertEqual(result['status'],'READY');self.assertEqual(result['filters'],filters)
        self.assertEqual(result['filters_authority'],'USER_SUPPLIED_NOT_LOWER_PATH_ATTESTATION')

    def test_code_exception_becomes_clear_held_cause(self):
        result=admit(request(),{'malformed':'catalog'})
        self.assertEqual(result['reason'],'INTAKE_INTERNAL_ERROR')
        self.assertEqual(result['cause']['type'],'KeyError')
        self.assertEqual(result['cause']['message'],"'models'")

    def test_approximate_precision_is_not_invented_to_admit_a_figure(self):
        result=admit(request(value='about 950'),CAT)
        self.assertEqual(result['status'],'HELD')

    def test_exact_page_name_is_not_misread_as_a_visual_name(self):
        projected=nodes(CAT)
        global_card=next(n for n in projected if n['id']=='global-card')
        self.assertEqual(global_card['names'],['Global MRR'])

    def test_historical_free_text_adapter_never_completes_omitted_report(self):
        result=retained_text('When was the Global MRR card last refreshed?',CAT,request_key='old')
        self.assertEqual(result['reason'],'MISSING_REPORT')
        result=retained_text('When was Billing > Overview > Global MRR last refreshed?',CAT,request_key='old')
        self.assertEqual(result['status'],'READY')
        self.assertIsNone(result['comparison'])
        self.assertEqual(result['scope']['target_id'],'global-card')

    def test_every_internal_hold_is_retained_and_shared_between_workers(self):
        from test_shared_application import store
        from investigator.shared_state import SharedState
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);state=SharedState.offline(root/'state.sqlite');state.migrate()
            first=SimpleNamespace(store=store(root/'first.sqlite',state),agent=SimpleNamespace(config={}))
            with patch('investigator.question_intake.snapshot',side_effect=RuntimeError('retained definition unavailable')):
                result=submit(first,request())
            self.assertEqual(result['reason'],'INTAKE_INTERNAL_ERROR')
            second=SimpleNamespace(store=store(root/'second.sqlite',state),agent=SimpleNamespace(config={}))
            with patch('investigator.question_intake.snapshot',return_value=CAT):
                replay=submit(second,request())
            self.assertEqual(result,replay)

    def test_unknown_synonyms_cannot_create_nodes_or_grant_scope(self):
        result=admit(request(number='secret savings'),CAT,enrichment=[{'subject':'not-a-real-node','synonyms':['secret savings'],'status':'HUMAN_CONFIRMED'}])
        self.assertEqual(result['reason'],'NUMBER_UNRESOLVED')

    def test_stale_or_recorded_stub_enrichment_cannot_admit_a_live_label(self):
        for qualification in ({'stale_definition':True},{'recording_class':'RECORDED_STUB'}):
            with self.subTest(qualification=qualification):
                rows=[{'subject':'mrr','synonyms':['special business label'],'status':'INFERRED',**qualification}]
                result=admit(request(number='special business label'),CAT,enrichment=rows)
                self.assertEqual(result['reason'],'NUMBER_UNRESOLVED')

    def test_server_persists_one_question_and_rejects_second_reply(self):
        from test_shared_application import store
        from investigator.shared_state import SharedState
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);state=SharedState.offline(root/'state.sqlite');state.migrate()
            enrichment=[{'subject':'mrr','synonyms':['revenue'],'status':'INFERRED'},
                        {'subject':'net','synonyms':['revenue'],'status':'INFERRED'}]
            workspace=SimpleNamespace(store=store(root/'first.sqlite',state),agent=SimpleNamespace(config={}),enrichment_entries=lambda:enrichment)
            with patch('investigator.question_intake.snapshot',return_value=CAT):
                first=submit(workspace,request(number='revenue'))
                choice=first['questions'][0]['choices'][0]
                answer={'choice_key':choice['key'],'request_key':'first-reply'}
                result=reply(workspace,first['intake_id'],answer)
                repeated=reply(workspace,first['intake_id'],answer)
                second=reply(workspace,first['intake_id'],{**answer,'request_key':'second-reply'})
            self.assertEqual(result['status'],'READY');self.assertEqual(result['questions_asked_total'],1)
            self.assertEqual(result,repeated);self.assertEqual(second['reason'],'CLARIFICATION_ALREADY_USED')


class EssentialsApiTests(unittest.TestCase):
    def setUp(self):
        from test_investigator_workspace import WorkspaceTests
        self.h=WorkspaceTests();self.h.setUp();self.addCleanup(self.h.doCleanups)

    def test_schema_exposes_required_essentials_and_submit_is_authenticated(self):
        result=self.h.http('/api/workspace/essentials/schema')
        self.assertTrue(result['status'].startswith('200'))
        self.assertTrue({'report','number','comparison'}<=set(result['body']['required']))
        denied=self.h.http('/api/workspace/essentials',request(),token='wrong')
        self.assertTrue(denied['status'].startswith('401'))
        with patch('investigator.question_intake.snapshot',return_value=CAT):
            submitted=self.h.http('/api/workspace/essentials',request())
        self.assertTrue(submitted['status'].startswith('200'))
        self.assertEqual(submitted['body']['status'],'READY')

    def test_additive_form_requires_report_number_and_comparison_reference(self):
        result=self.h.http('/essentials')
        self.assertTrue(result['status'].startswith('200'))
        self.assertIn(b'name="report" required',result['body'])
        self.assertIn(b'name="number" required',result['body'])
        self.assertIn(b'id="comparison-reference" required',result['body'])
        script=self.h.http('/essentials.js')['body']
        self.assertIn(b'button.textContent=choice.label',script)
        self.assertNotIn(b'localStorage',script)


if __name__=='__main__':unittest.main()
