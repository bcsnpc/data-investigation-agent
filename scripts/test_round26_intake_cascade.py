from unittest.mock import Mock
import unittest
from investigator.intake_cascade import Cascade
from investigator.model_spend import SpendHold


class CascadeTests(unittest.TestCase):
    def setup_cascade(self, results):
        factory=Mock()
        resolvers=[]
        for value in results:
            resolver=Mock()
            if isinstance(value,Exception):resolver.resolve.side_effect=value
            else:resolver.resolve.return_value=value
            resolvers.append(resolver)
        factory.side_effect=resolvers
        first=Mock();first.model='terra';second=Mock();second.model='astra'
        fallback=Mock(return_value=second)
        cascade=Cascade(catalog=Mock(),first_model=first,fallback_model=fallback,record=Mock(),resolver_factory=factory)
        return cascade,factory,fallback

    def test_ready_high_confidence_uses_cheap_model_only(self):
        cascade,factory,fallback=self.setup_cascade([{'status':'READY','resolution_confidence':'NAMED'}])
        result=cascade.resolve('ticket')
        fallback.assert_not_called();self.assertEqual(factory.call_count,1)
        self.assertEqual(result['intake_cascade']['resolved_by_model'],'terra')

    def test_hold_rejection_and_low_confidence_each_get_exactly_one_fallback(self):
        for first in ({'status':'NEEDS_INPUT'},{'status':'REJECTED'},
                      {'status':'READY','resolution_confidence':'FUZZY'}):
            cascade,factory,fallback=self.setup_cascade([first,{'status':'READY','resolution_confidence':'NAMED'}])
            result=cascade.resolve('ticket')
            fallback.assert_called_once();self.assertEqual(factory.call_count,2)
            self.assertEqual(result['intake_cascade']['resolved_by_model'],'astra')

    def test_second_hold_stays_held_without_a_third_pass(self):
        cascade,factory,fallback=self.setup_cascade([{'status':'NEEDS_INPUT'},{'status':'NEEDS_INPUT'}])
        result=cascade.resolve('ticket')
        self.assertEqual(result['status'],'NEEDS_INPUT');self.assertEqual(factory.call_count,2)
        self.assertIsNone(result['intake_cascade']['resolved_by_model'])

    def test_budget_hard_stop_is_not_a_reason_to_spend_on_fallback(self):
        cascade,factory,fallback=self.setup_cascade([SpendHold('cap')])
        with self.assertRaises(SpendHold):cascade.resolve('ticket')
        fallback.assert_not_called()
