import unittest
from unittest.mock import Mock, patch
from investigator.anthropic_credit import admit
from investigator.provider_budget import policy
from investigator.model_spend import SpendHold


class ProviderPolicyTests(unittest.TestCase):
    def test_november_model_override_matches_confirmed_anthropic_account_cap(self):
        from investigator.build_phase import model_ceiling
        from datetime import datetime,timezone
        now=datetime(2026,11,22,tzinfo=timezone.utc).timestamp()
        self.assertEqual(model_ceiling(now),policy('anthropic')['ceiling_microdollars'])
        self.assertEqual(model_ceiling(now),220284651)

    def test_approved_topup_allows_first_call_above_superseded_monthly_override(self):
        import tempfile
        from pathlib import Path
        from datetime import datetime,timezone
        from investigator.shared_state import SharedState
        from investigator.reasoning_budget import TicketBudget,RateCard
        now=datetime(2026,11,22,tzinfo=timezone.utc).timestamp()
        with tempfile.TemporaryDirectory()as folder:
            state=SharedState.offline(Path(folder)/'budget.sqlite');state.migrate()
            with state.transaction()as db:
                db.execute('INSERT INTO state_accounts VALUES(?,?,?,?,?,?)',
                    ('model-microdollars:2026-11','MICRODOLLARS',220284651,0,0,0))
                db.execute('INSERT INTO state_reservations VALUES(?,?,?,?,?,?,?)',
                    ('model-microdollars:2026-11','historical','old-worker',120100000,120100000,'SETTLED',
                     '{"case_id":"historical-other-ticket","purpose":"INVESTIGATOR"}'))
            rate=RateCard(model='opus-test',input_rate='5',output_rate='20',
                source='https://platform.claude.com/docs/en/about-claude/pricing',observed_at='2026-11-21')
            budget=TicketBudget(state,case_id='new-ticket',owner='round27-proof-test',rate=rate,
                clock=lambda:now,actual_usage_limit=3000000,purpose='INVESTIGATOR')
            self.assertEqual(budget.output_limit(100000,4000),4000)
            budget.reserve({'model':'opus-test','max_tokens':4000},input_tokens_upper_bound=100000)
            historical=next(x for x in state.snapshot('model-microdollars:2026-11')['reservations']if x['identity']=='historical')
            self.assertEqual(historical['charged'],'120100000')

    def test_active_anthropic_policy_admits_owner_approved_investigation_steps(self):
        from investigator.provider_budget import check_credit
        from datetime import datetime,timezone
        now=datetime(2026,11,22,tzinfo=timezone.utc).timestamp()
        for purpose in ('INTAKE','INVESTIGATOR','EVALUATOR','SCREENSHOT'):
            with self.subTest(purpose=purpose):
                check_credit('anthropic',now,owner='round27-proof-opus',purpose=purpose)
        for purpose in ('GRADING','REVIEWER','WRITER','ENRICHMENT','SMOKE'):
            with self.subTest(purpose=purpose),self.assertRaisesRegex(SpendHold,'PURPOSE_NOT_APPROVED'):
                check_credit('anthropic',now,owner='round27-proof-opus',purpose=purpose)

    def test_anthropic_grading_rejected_before_any_reservation(self):
        state = Mock()
        approved = {'model_account': 'model', 'grading_account': 'grading',
                    'allowed_owner_prefixes': ['round27-'],
                    'allowed_purposes': ['INTAKE', 'INVESTIGATOR']}
        with patch('investigator.anthropic_credit.policy_for', return_value=approved):
            for purpose in ('GRADING', 'SECONDARY_GRADING', 'REVIEWER', 'SMOKE', 'WRITER'):
                with self.subTest(purpose=purpose), self.assertRaisesRegex(SpendHold, 'PURPOSE_NOT_APPROVED'):
                    admit(state, 'db', 'model', 1, purpose=purpose, owner='round27-dev')
        state._totals.assert_not_called()
        state.sql.assert_not_called()

    def test_active_bedrock_policy_is_amazon_only_and_twenty_dollars(self):
        approved = policy('bedrock')
        self.assertEqual(approved['ceiling_microdollars'], 20000000)
        self.assertEqual(approved['allowed_vendor'], 'amazon-nova-only')
        self.assertIs(approved['allow_claude'], False)

    def test_round27_read_tools_and_evaluator_pass_gateway_without_write_tools(self):
        from investigator.adapters.reasoning_anthropic import authorize_body,BASE
        body={'model':'opus-test','max_tokens':20,'system':[{'type':'text','text':'Native evidence only.',
              'cache_control':{'type':'ephemeral'}}],'messages':[], 'tools':[]}
        for name in ('get_target_candidates','check_target_candidates','contribution_analysis','row_layer_diff','evaluate_delivery','repair_delivery'):
            body['tools']=[{'name':name,'description':'Approved bounded read or local evaluation.',
                            'input_schema':{'type':'object','properties':{}}}]
            authorize_body({'reasoning_models':['opus-test']},'POST',BASE+'/messages',body)
        body['tools'][0]['name']='execute_sql_write'
        with self.assertRaisesRegex(ValueError,'UNKNOWN_TOOL_REFUSED'):
            authorize_body({'reasoning_models':['opus-test']},'POST',BASE+'/messages',body)

    def test_openai_credit_expiry_and_round_purposes(self):
        from datetime import datetime,timezone
        from investigator.provider_budget import check_credit
        before=datetime(2026,11,28,tzinfo=timezone.utc).timestamp()
        expired=datetime(2026,11,29,tzinfo=timezone.utc).timestamp()
        check_credit('openai',before,owner='round27-secondary',purpose='GRADING')
        with self.assertRaisesRegex(SpendHold,'PURPOSE_NOT_APPROVED'):
            check_credit('openai',before,owner='round27-dev',purpose='INTAKE')
        with self.assertRaisesRegex(SpendHold,'CREDIT_EXPIRED'):
            check_credit('openai',expired,owner='round27-secondary',purpose='GRADING')


if __name__ == '__main__':
    unittest.main()
