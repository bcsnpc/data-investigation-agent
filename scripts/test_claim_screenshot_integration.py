"""Real screenshot/controller integration, using a deterministic OCR response."""
import base64
import copy
import unittest
from unittest.mock import Mock, patch
import test_investigator_workspace as workspace_fixture
from test_screenshot_intake import image_bytes
from test_claim_intake import CAT
from test_claim_screenshots import ocr


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.h = workspace_fixture.WorkspaceTests(); self.h.setUp(); self.addCleanup(self.h.doCleanups)
        self.w = self.h.workspace
        with self.w.store.connect() as db:
            self.w.store.database = db.execute('PRAGMA database_list').fetchone()[2]
        self.catalog = copy.deepcopy(CAT)
        self.catalog_patch = patch('investigator.claim_intake.ClaimIntake._catalog', return_value=self.catalog)
        self.catalog_patch.start(); self.addCleanup(self.catalog_patch.stop)
        self.w.claim_screenshot_ocr = Mock(return_value=ocr('Quantity: 950'))
        self.w.claim_screenshot_catalog = lambda: [{
            'candidate_id': 'page-candidate', 'model_id': 'model', 'report_id': 'report',
            'page_id': 'page', 'label': 'Activity Report / Overview',
            'names': {'report': 'Activity Report', 'page': 'Overview'},
            'anchors': ['Quantity'], 'definition_hash': 'native-definition-hash',
            'targets': [{'target_id': 'card', 'labels': ['Quantity'], 'measure_ids': ['quantity']}]}]

    def test_screenshot_only_reaches_claim_without_fabricating_the_question(self):
        image = self.w.screenshots.upload({'name': 'question.png', 'mime': 'image/png',
            'base64': base64.b64encode(image_bytes()).decode(), 'request_key': 'upload'})
        review = self.w.claim_screenshots.identify({'image_id': image['id'], 'request_key': 'identify'})
        confirmed = self.w.claim_screenshots.confirm({'review_id': review['id'],
            'candidate_id': 'page-candidate', 'request_key': 'confirm-image'})
        result = self.w.claims.submit({'text': '', 'request_key': 'claim',
            'screenshot_evidence': {'review_id': confirmed['id']}})
        self.assertEqual(result['claim']['settled']['scope']['report_id'], 'report')
        self.assertEqual(result['claim']['settled']['scope']['page_id'], 'page')
        self.assertEqual(result['claim']['settled']['observation'][0]['figure']['value'], '950')
        self.assertNotIn('direction', result['claim']['settled'])
        self.assertEqual(result['status'], 'CLARIFYING')
        self.assertNotIn(result['questions'][0]['field'], ('report', 'page', 'metric', 'observation'))
        for fact in result['claim']['facts']:
            self.assertEqual(fact['source']['review_id'], review['id'])
            self.assertEqual(fact['source']['review_hash'], review['hash'])
        self.h.native.assert_not_called(); self.h.source.assert_not_called(); self.h.planner.assert_not_called()


if __name__ == '__main__': unittest.main()
