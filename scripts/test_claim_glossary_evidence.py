import copy
import json
import unittest

from investigator.claim_glossary import EstateGlossary, relationship
from investigator.claim_glossary_evidence import RetainedClaimEvidence, confirmed_relationships, record_confirmation
from investigator.onboarding import digest
import test_claim_intake as claim_fixture


class RetainedGlossaryEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.fixture = claim_fixture.ClaimTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.fixture.workspace.owner = 'synthetic-local-session'
        self.catalog = copy.deepcopy(claim_fixture.CAT)
        self.controller = self.fixture.controller
        self.store = self.fixture.workspace.store
        self.lookup = RetainedClaimEvidence(self.store, lambda: self.catalog)
        self.glossary = EstateGlossary(self.store.database, 'fixture', evidence_lookup=self.lookup)

    def confirmed(self):
        submitted = self.controller.submit(self.fixture.request())
        return self.controller.confirm({'id': submitted['id'], 'revision': submitted['revision'],
                                        'request_key': 'confirm', 'accepted': True})

    def alter(self, identity, change):
        with self.store.connect() as db:
            body = json.loads(db.execute('SELECT body FROM claim_intakes WHERE id=?', (identity,)).fetchone()[0])
            change(body)
            db.execute('UPDATE claim_intakes SET body=?,body_hash=? WHERE id=?',
                       (json.dumps(body), digest(body), identity))

    def test_real_controller_confirmation_creates_durable_glossary_authority(self):
        done = self.confirmed()
        learned = record_confirmation(self.glossary, self.store, done['id'], self.catalog)
        self.assertEqual(len(learned), 1)
        found = self.glossary.resolve('Quantity', self.catalog)
        self.assertEqual(found[0]['status'], 'CONFIRMED')
        self.assertEqual(found[0]['measure_id'], 'quantity')
        proof = self.lookup(learned[0]['evidence_id'])
        self.assertEqual(proof['actor'], {'kind': 'USER', 'id': 'local-operator@synthetic-local-session'})
        self.assertEqual(record_confirmation(self.glossary, self.store, done['id'], self.catalog), [])

    def test_model_candidate_confirmed_status_does_not_replace_user_acceptance(self):
        submitted = self.controller.submit(self.fixture.request())
        self.alter(submitted['id'], lambda b: b['claim']['selected_binding'].update(status='CONFIRMED'))
        self.assertEqual(confirmed_relationships(self.store, submitted['id'], self.catalog), [])

    def test_missing_exact_accepted_request_does_not_establish_confirmation(self):
        done = self.confirmed()
        self.alter(done['id'], lambda b: b.update(documents=[]))
        self.assertEqual(confirmed_relationships(self.store, done['id'], self.catalog), [])

    def test_changed_displayed_interpretation_cannot_authorise_another_mapping(self):
        done = self.confirmed()
        self.alter(done['id'], lambda b: b['interpretation'].update(text='Something unrelated was shown.'))
        self.assertEqual(confirmed_relationships(self.store, done['id'], self.catalog), [])

    def test_changed_catalog_does_not_reuse_historical_user_authority(self):
        done = self.confirmed()
        learned = record_confirmation(self.glossary, self.store, done['id'], self.catalog)
        self.catalog['models'][0]['revision'] = 2
        self.assertIsNone(self.lookup(learned[0]['evidence_id']))
        self.assertEqual(self.glossary.resolve('Quantity', self.catalog), [])


    def test_current_confirmation_does_not_promote_stale_inferred_link(self):
        source = {'kind': 'PHRASE', 'label': 'Quantity'}
        target = {'kind': 'MODEL_MEASURE', 'model_id': self.catalog['models'][0]['id'], 'id': 'quantity'}
        proof = {'id': 'old-inference', 'kind': 'MODEL_INFERRED', 'sha256': digest('old'),
                 'supports': [relationship(source, target)]}
        self.lookup.fallback = lambda identity: proof if identity == proof['id'] else None
        stale_catalog = copy.deepcopy(self.catalog)
        stale_catalog['models'][0]['revision'] = -1
        old = self.glossary.add_link(source, target, evidence_id=proof['id'], catalog=stale_catalog,
                                     expected_revision=0)
        done = self.confirmed()
        learned = record_confirmation(self.glossary, self.store, done['id'], self.catalog)
        self.assertEqual(learned[0]['event'], 'LINK_ADDED')
        self.assertNotEqual(learned[0]['link_id'], old['id'])
        self.assertEqual(self.glossary.get()['links'][0]['status'], 'INFERRED')
        self.assertEqual(self.glossary.resolve('Quantity', self.catalog)[0]['status'], 'CONFIRMED')

    def test_actual_workspace_lazy_callback_learns_after_controller_commit(self):
        from investigator.workspace import Workspace
        workspace = object.__new__(Workspace)
        workspace.store = self.store
        workspace.store.environment = 'actual-workspace-estate'
        workspace.agent = self.fixture.workspace.agent
        workspace.owner = 'actual-session'
        controller = workspace.claims
        glossary = workspace.claim_glossary
        submitted = controller.submit(self.fixture.request())
        done = controller.confirm({'id': submitted['id'], 'revision': submitted['revision'],
                                   'request_key': 'actual-confirm', 'accepted': True})
        learned = [link for link in glossary.get()['links']
                   if link['proof']['id'].startswith('claim-confirmation/')]
        self.assertEqual(len(learned), 1)
        self.assertEqual(learned[0]['status'], 'CONFIRMED')
        self.assertEqual(learned[0]['proof']['actor']['id'], 'local-operator@actual-session')
        self.assertEqual(done['status'], 'CONFIRMED')
        reused = glossary.resolve('Quantity', self.catalog)
        self.assertTrue(any(x['status'] == 'CONFIRMED' for x in reused))
        self.assertEqual(controller.get(done['id'])['status'], 'CONFIRMED')

if __name__ == '__main__':
    unittest.main()
