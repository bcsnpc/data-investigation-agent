import copy
import json
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from investigator.claim_glossary import EstateGlossary, relationship
from investigator.onboarding import Conflict, digest
from investigator.privacy_storage import connect


def catalog():
    return [{'id': 'model', 'name': 'Clinic',
             'measures': [{'id': 'seen', 'name': 'Patients Seen', 'expression': 'COUNT(visits)'},
                          {'id': 'booked', 'name': 'Appointments Booked'}],
             'columns': [{'column_id': 'status', 'name': 'Visit status'}],
             'source_columns': [{'column_id': 'source.status', 'name': 'visit_state'}],
             'visuals': [{'target_id': 'card', 'report_id': 'report', 'page_id': 'today',
                          'names': ['Completed Visits'], 'measure_ids': ['seen']}]}]


def phrase(label):
    return {'kind': 'PHRASE', 'label': label}


def measure(identity='seen'):
    return {'kind': 'MODEL_MEASURE', 'model_id': 'model', 'id': identity}


class GlossaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'catalog.sqlite'
        self.evidence = {}
        self.store = EstateGlossary(self.path, 'clinic-a', evidence_lookup=self.evidence.get)
        self.catalog = catalog()

    def proof(self, identity, source, target, kind='MODEL_INFERRED', actor=None):
        value = {'id': identity, 'kind': kind, 'sha256': digest({'record': identity}),
                 'supports': [relationship(source, target)]}
        if actor:
            value['actor'] = actor
        self.evidence[identity] = value
        return identity

    def add(self, source, target, identity='proposal', kind='MODEL_INFERRED', actor=None):
        evidence_id = self.proof(identity, source, target, kind, actor)
        return self.store.add_link(source, target, evidence_id=evidence_id,
                                   catalog=self.catalog, expected_revision=self.store.get()['revision'])

    def test_model_inference_needs_separate_retained_human_confirmation(self):
        source, target = phrase('patients treated'), measure()
        link = self.add(source, target)
        self.assertEqual(self.store.resolve('PATIENTS  TREATED', self.catalog)[0]['status'], 'INFERRED')
        with self.assertRaisesRegex(ValueError, 'HUMAN_CONFIRMATION'):
            self.store.confirm(link['id'], evidence_id='proposal', catalog=self.catalog, expected_revision=1)
        proof = self.proof('ticket-17-answer', source, target, 'CONFIRMED_CLARIFICATION',
                           {'kind': 'USER', 'id': 'owner'})
        self.store.confirm(link['id'], evidence_id=proof, catalog=self.catalog, expected_revision=1)
        result = self.store.resolve('patients treated', self.catalog)[0]
        self.assertEqual(result['status'], 'CONFIRMED')
        self.assertEqual(result['label'], 'Patients Seen')
        self.assertEqual(set(result['evidence_ids']), {'proposal', 'ticket-17-answer'})
        history = self.store.get()['history']
        self.assertEqual(history[0]['link']['status'], 'INFERRED')
        self.assertEqual(history[1]['event'], 'LINK_CONFIRMED')

    def test_many_to_many_returns_both_meanings_instead_of_first_match(self):
        self.add(phrase('patients'), measure(), identity='seen')
        self.add(phrase('patients'), measure('booked'), identity='booked')
        self.assertEqual({x['measure_id'] for x in self.store.resolve('patients', self.catalog)}, {'seen', 'booked'})

    def test_multihop_graph_keeps_weakest_link_and_catalog_visual_scope(self):
        self.store.seed_catalog(self.catalog)
        concept = {'kind': 'CONCEPT', 'label': 'Completed care'}
        visual = {'kind': 'REPORT_LABEL', 'model_id': 'model', 'id': 'card'}
        self.add(phrase('treated'), concept, 'phrase')
        self.add(concept, visual, 'concept')
        result = self.store.resolve('treated', self.catalog)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['status'], 'INFERRED')
        self.assertEqual(result[0]['target_ids'], ['card'])
        self.assertEqual(result[0]['report_id'], 'report')
        self.assertEqual(result[0]['page_id'], 'today')
        self.assertEqual(result[0]['measure_id'], 'seen')

    def test_confirmed_definitions_seed_once_without_inventing_synonyms(self):
        self.store.seed_catalog(self.catalog)
        before = self.store.get()
        self.assertEqual(self.store.seed_catalog(self.catalog), [])
        self.assertEqual(before, self.store.get())
        self.assertEqual(self.store.resolve('Patients Seen', self.catalog)[0]['status'], 'CONFIRMED')
        self.assertEqual(self.store.resolve('treated', self.catalog), [])

    def test_unknown_catalog_reference_refuses_at_creation(self):
        with self.assertRaisesRegex(ValueError, 'UNKNOWN_REFERENCE'):
            self.add(phrase('patients'), measure('fabricated'))

    def test_external_evidence_cannot_impersonate_definition_seed(self):
        with self.assertRaisesRegex(ValueError, 'NAMESPACE_RESERVED'):
            self.add(phrase('treated'), measure(), identity='catalog:invented')

    def test_changed_definition_invalidates_link_even_when_id_stays_same(self):
        self.store.seed_catalog(self.catalog)
        changed = copy.deepcopy(self.catalog)
        changed[0]['measures'][0]['expression'] = 'COUNT(all appointments)'
        self.assertEqual(self.store.resolve('Patients Seen', changed), [])
        self.assertEqual(self.store.resolve('Completed Visits', changed), [])

    def test_compact_catalog_context_change_invalidates_unchanged_measure_name(self):
        self.catalog[0]['context_id'] = 'before'
        self.store.seed_catalog(self.catalog)
        self.catalog[0]['context_id'] = 'after'
        self.assertEqual(self.store.resolve('Patients Seen', self.catalog), [])
        self.store.seed_catalog(self.catalog)
        self.assertEqual(self.store.resolve('Patients Seen', self.catalog)[0]['status'], 'CONFIRMED')

    def test_changed_retained_evidence_cannot_keep_authority(self):
        self.add(phrase('treated'), measure())
        self.evidence['proposal']['sha256'] = 'f' * 64
        self.assertEqual(self.store.resolve('treated', self.catalog), [])

    def test_confirmation_cannot_be_model_actor_or_unrelated_evidence(self):
        source, target = phrase('treated'), measure()
        link = self.add(source, target)
        bad = self.proof('bad-actor', source, target, 'CONFIRMED_CLARIFICATION', {'kind': 'MODEL', 'id': 'model'})
        with self.assertRaisesRegex(ValueError, 'HUMAN_AUTHORITY'):
            self.store.confirm(link['id'], evidence_id=bad, catalog=self.catalog, expected_revision=1)
        wrong = self.proof('other-target', source, measure('booked'), 'STEWARD_ENTRY', {'kind': 'STEWARD', 'id': 'owner'})
        with self.assertRaisesRegex(ValueError, 'DOES_NOT_SUPPORT'):
            self.store.confirm(link['id'], evidence_id=wrong, catalog=self.catalog, expected_revision=1)

    def test_estate_isolation_and_durable_reopen(self):
        self.store.seed_catalog(self.catalog)
        other = EstateGlossary(self.path, 'clinic-b')
        self.assertEqual(other.get()['links'], [])
        self.assertEqual(other.resolve('Patients Seen', self.catalog), [])
        reopened = EstateGlossary(self.path, 'clinic-a')
        self.assertEqual(reopened.resolve('Patients Seen', self.catalog), self.store.resolve('Patients Seen', self.catalog))

    def test_optimistic_revision_protects_concurrent_editor(self):
        source, target = phrase('treated'), measure()
        proof = self.proof('proposal', source, target)
        self.store.seed_catalog(self.catalog)
        with self.assertRaises(Conflict):
            self.store.add_link(source, target, evidence_id=proof, catalog=self.catalog, expected_revision=0)

    def test_tampered_history_is_not_loaded(self):
        self.store.seed_catalog(self.catalog)
        with closing(connect(self.path)) as db:
            revision, body = db.execute('SELECT revision,body FROM claim_glossary_events LIMIT 1').fetchone()
            value = json.loads(body)
            value['link']['status'] = 'INFERRED'
            db.execute('UPDATE claim_glossary_events SET body=? WHERE revision=?', (json.dumps(value), revision))
            db.commit()
        with self.assertRaisesRegex(ValueError, 'HISTORY_INVALID'):
            self.store.get()

    def test_cycles_do_not_loop_or_create_an_authoritative_path(self):
        a, b = {'kind': 'CONCEPT', 'label': 'A'}, {'kind': 'CONCEPT', 'label': 'B'}
        self.add(phrase('treated'), a, 'start')
        self.add(a, b, 'forward')
        self.add(b, a, 'back')
        self.add(b, measure(), 'finish')
        self.assertEqual(len(self.store.resolve('treated', self.catalog)), 1)

    def test_native_identifier_is_not_used_as_a_display_label(self):
        self.catalog[0]['measures'][0]['name'] = 'seen'
        self.store.seed_catalog(self.catalog)
        self.assertEqual(self.store.resolve('seen', self.catalog), [])

    def test_source_columns_must_exist_in_retained_catalog(self):
        target = {'kind': 'SOURCE_COLUMN', 'model_id': 'model', 'id': 'source.status'}
        self.add({'kind': 'MODEL_COLUMN', 'model_id': 'model', 'id': 'status'}, target)
        self.assertEqual(len(self.store.get()['links']), 1)
        with self.assertRaisesRegex(ValueError, 'UNKNOWN_REFERENCE'):
            self.add(phrase('unknown'), {**target, 'id': 'missing'})

    def test_projected_installation_never_writes_raw_glossary_pages(self):
        from investigator.privacy_storage import EvidenceStore
        from investigator.privacy_projection import Projection
        from investigator.privacy_identities import Identities, active
        raw = 'PRIVATE_SENSITIVE_PERSON'
        column = 'column://person/name'
        policy = {'tape_class': 'PRIVACY_PROJECTED', 'version': 'estate-privacy-projection-v1',
                  'estate_id': 'clinic-a', 'key_reference': 'secret-store/estate', 'columns': [column]}
        projection = Projection(policy, lambda _: b'synthetic-test-key-with-32-bytes!')
        projection.bind(column, raw)
        vault = EvidenceStore(self.path, projection)
        self.addCleanup(vault.close)
        identities = Identities(projection)
        with active(identities):
            self.add(phrase(raw), measure())
            self.assertEqual(list(Path(self.temp.name).iterdir()), [])
        image = vault.prepare()
        identities.prepare()
        identities.rekey()
        vault.persist(image)
        for file in Path(self.temp.name).rglob('*'):
            if file.is_file():
                self.assertNotIn(raw.encode(), file.read_bytes())
                self.assertNotIn(raw.lower().encode(), file.read_bytes())
        vault.close()
        fresh = Projection(policy, lambda _: b'synthetic-test-key-with-32-bytes!')
        reopened = EvidenceStore(self.path, fresh)
        self.addCleanup(reopened.close)
        restored = EstateGlossary(self.path, 'clinic-a').get()
        self.assertEqual(restored['revision'], 1)
        self.assertNotEqual(restored['links'][0]['source']['label'], raw)


if __name__ == '__main__':
    unittest.main()
