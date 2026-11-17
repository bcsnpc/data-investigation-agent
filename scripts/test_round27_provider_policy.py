import unittest
from unittest.mock import Mock, patch
from investigator.anthropic_credit import admit
from investigator.provider_budget import policy
from investigator.model_spend import SpendHold


class ProviderPolicyTests(unittest.TestCase):
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


if __name__ == '__main__':
    unittest.main()
