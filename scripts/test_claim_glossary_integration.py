import copy
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from investigator.claim_glossary import EstateGlossary, relationship
from investigator.claim_clarification import candidates
from investigator.onboarding import digest
from test_claim_glossary import catalog, phrase, measure


class GlossaryIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'catalog.sqlite'
        self.catalog = {'models': catalog()}
        other = copy.deepcopy(self.catalog['models'][0]['visuals'][0])
        other.update(target_id='other-card', report_id='other-report', names=['All Visits'])
        self.catalog['models'][0]['visuals'].append(other)
        self.glossary = EstateGlossary(self.path, 'clinic')
        self.glossary.seed_catalog(self.catalog)

    def test_specific_visual_glossary_link_never_expands_to_another_cell(self):
        settled = {'metric': [{'phrase': 'Completed Visits'}], 'scope': {'kind': 'VISUALS'}}
        result = candidates(settled, self.catalog, self.glossary)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['target_ids'], ['card'])
        self.assertEqual(result[0]['report_id'], 'report')

    def test_specific_visual_glossary_link_cannot_jump_to_selected_other_report(self):
        settled = {'metric': [{'phrase': 'Completed Visits'}],
                   'scope': {'kind': 'VISUALS', 'report_id': 'other-report'}}
        self.assertEqual(candidates(settled, self.catalog, self.glossary), [])

    def test_measure_only_confirmed_link_narrows_to_selected_report_and_stays_confirmed(self):
        settled = {'metric': [{'phrase': 'Patients Seen'}],
                   'scope': {'kind': 'VISUALS', 'report_id': 'other-report'}}
        result = candidates(settled, self.catalog, self.glossary)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['target_ids'], ['other-card'])
        self.assertEqual(result[0]['status'], 'CONFIRMED')

    def test_workspace_callback_is_late_bound_after_first_glossary_access(self):
        from investigator.workspace import Workspace
        workspace = object.__new__(Workspace)
        workspace.store = SimpleNamespace(database=self.path, environment='new-estate')
        glossary = workspace.claim_glossary
        source, target = phrase('treated'), measure()
        proof = {'id': 'retained-proposal', 'kind': 'MODEL_INFERRED',
                 'sha256': digest('retained proposal'), 'supports': [relationship(source, target)]}
        workspace.claim_glossary_evidence = lambda identity: proof if identity == proof['id'] else None
        glossary.add_link(source, target, evidence_id=proof['id'], catalog=self.catalog, expected_revision=0)
        self.assertEqual(glossary.resolve('treated', self.catalog)[0]['status'], 'INFERRED')


if __name__ == '__main__':
    unittest.main()
