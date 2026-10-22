import copy
import unittest
from investigator.connection_rotation import rotate, RotationIncomplete


class Adapter:
    def __init__(self):
        self.calls = []
        self.fail = None
        self.changed_scope = False
    def targets(self): return ['first', 'second']
    def observe(self): return {'roles': ['read'], 'bindings': self.targets()}
    def create_and_store(self, days):
        self.calls.append(('create-store', days))
        return {'key_id': 'new', 'store_reference': 'existing-store/new', 'expires_at_utc': '2026-11-21T00:00:00Z'}
    def update(self, target, reference): self.calls.append(('update', target))
    def verify(self, target):
        self.calls.append(('verify', target))
        return {'status': 'FAIL' if target == self.fail else 'PASS', 'evidence_id': 'receipt-' + target}
    def assert_unchanged_scope(self, before, after):
        if self.changed_scope: raise ValueError('SCOPE_CHANGED')
    def remove_old(self): self.calls.append(('remove-old',))


class Tests(unittest.TestCase):
    def test_two_live_read_proofs_precede_removal(self):
        a = Adapter(); saved = []
        result = rotate(a, {}, lambda s: saved.append(copy.deepcopy(s)))
        self.assertEqual(result['status'], 'COMPLETE')
        self.assertLess(a.calls.index(('verify', 'second')), a.calls.index(('remove-old',)))
        self.assertEqual(a.calls.count(('create-store', 30)), 1)
        self.assertNotIn('secret', repr(result))

    def test_second_failure_retains_old_and_resume_does_not_create_again(self):
        a = Adapter(); a.fail = 'second'; saved = []
        with self.assertRaises(RotationIncomplete):
            rotate(a, {}, lambda s: saved.append(copy.deepcopy(s)))
        self.assertNotIn(('remove-old',), a.calls)
        a.fail = None
        result = rotate(a, saved[-1], lambda s: saved.append(copy.deepcopy(s)))
        self.assertEqual(result['status'], 'COMPLETE')
        self.assertEqual(a.calls.count(('create-store', 30)), 1)
        self.assertEqual(a.calls.count(('update', 'first')), 1)
        self.assertEqual(a.calls.count(('verify', 'first')), 2)

    def test_scope_change_retains_old(self):
        a = Adapter(); a.changed_scope = True
        with self.assertRaisesRegex(ValueError, 'SCOPE_CHANGED'):
            rotate(a, {}, lambda _: None)
        self.assertNotIn(('remove-old',), a.calls)

    def test_completed_checkpoint_is_idempotent(self):
        a = Adapter(); state = rotate(a, {}, lambda _: None); a.calls.clear()
        self.assertEqual(rotate(a, state, lambda _: None), state)
        self.assertEqual(a.calls, [])

    def test_changed_targets_refuse_before_any_mutation(self):
        a = Adapter()
        with self.assertRaisesRegex(ValueError, 'TARGETS_CHANGED'):
            rotate(a, {'targets': ['different']}, lambda _: None)
        self.assertEqual(a.calls, [])


if __name__ == '__main__': unittest.main()
