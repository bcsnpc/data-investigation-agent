"""Claim HTTP boundaries remain additive, authenticated and identity preserving."""
import unittest
from unittest.mock import MagicMock
import test_investigator_workspace as workspace_fixture


class ClaimApiTests(unittest.TestCase):
    def setUp(self):
        self.h = workspace_fixture.WorkspaceTests(); self.h.setUp(); self.addCleanup(self.h.doCleanups)
        self.claims = self.h.workspace._claims = MagicMock()
        self.images = self.h.workspace._claim_screenshots = MagicMock()
        self.checks = self.h.workspace._claim_investigations = MagicMock()
        self.checks.run.return_value={'status':'HELD','outputs':{'business_explanation':'The check could not start.','technical_narrative':'Context is unavailable.'}}
        self.checks.get.return_value=self.checks.run.return_value
        for controller in (self.claims, self.images):
            for name in ('catalog', 'submit', 'get', 'reply', 'confirm', 'identify'):
                getattr(controller, name).return_value = {'status': 'saved'}

    def test_claim_routes_require_auth_before_controller(self):
        result = self.h.http('/api/workspace/claims', {'text': 'Revenue differs'}, token='wrong')
        self.assertTrue(result['status'].startswith('401'))
        self.claims.submit.assert_not_called()

    def test_claim_body_and_plural_scope_arrive_without_projection(self):
        body = {'text': 'Both cards show 600', 'request_key': 'one',
                'claim': {'scope': {'kind': 'VISUALS', 'visual_ids': ['first', 'second']}}}
        result = self.h.http('/api/workspace/claims', body)
        self.assertTrue(result['status'].startswith('200'))
        self.claims.submit.assert_called_once_with(body)

    def test_reply_and_confirmation_bind_path_identity(self):
        for suffix, method in [('replies', 'reply'), ('confirm', 'confirm')]:
            body = {'revision': 1, 'request_key': suffix}
            result = self.h.http('/api/workspace/claims/retained/' + suffix, body)
            self.assertTrue(result['status'].startswith('200'))
            getattr(self.claims, method).assert_called_once_with({'id': 'retained', **body})
            result = self.h.http('/api/workspace/claims/retained/' + suffix, {**body, 'id': 'other'})
            self.assertTrue(result['status'].startswith('400'))

    def test_investigation_binds_path_identity_and_preserves_outputs(self):
        body={'revision':2,'request_key':'once'}
        result=self.h.http('/api/workspace/claims/saved/run',body)
        self.assertTrue(result['status'].startswith('200'))
        self.checks.run.assert_called_once_with({'id':'saved',**body})
        self.assertEqual(result['body']['outputs']['business_explanation'],'The check could not start.')
        result=self.h.http('/api/workspace/claims/saved/investigation')
        self.assertTrue(result['status'].startswith('200'));self.checks.get.assert_called_once_with('saved')
        self.assertTrue(self.h.http('/api/workspace/claims/saved/run',{**body,'id':'other'})['status'].startswith('400'))
        self.assertTrue(self.h.http('/api/workspace/claims/saved/run',body,token='wrong')['status'].startswith('401'))
        self.assertEqual(self.checks.run.call_count,1)

    def test_screenshot_confirmation_cannot_substitute_review(self):
        body = {'candidate_id': 'choice', 'request_key': 'confirm'}
        result = self.h.http('/api/workspace/claim-screenshots/saved/confirm', body)
        self.assertTrue(result['status'].startswith('200'))
        self.images.confirm.assert_called_once_with({'review_id': 'saved', **body})
        result = self.h.http('/api/workspace/claim-screenshots/saved/confirm', {**body, 'review_id': 'other'})
        self.assertTrue(result['status'].startswith('400'))

    def test_unknown_subroute_is_not_a_claim_operation(self):
        result = self.h.http('/api/workspace/claims/saved/execute', {'request_key': 'bad'})
        self.assertTrue(result['status'].startswith('404'))
        self.h.native.assert_not_called(); self.h.planner.assert_not_called()

    def test_claim_assets_are_served_without_exposing_credentials(self):
        result = self.h.http('/claims.js', token='')
        self.assertTrue(result['status'].startswith('200'))
        self.assertIn(b'Yes, that is my question', result['body'])
        self.assertNotIn(self.h.token.encode(), result['body'])

    def test_native_ocr_program_is_part_of_the_recorded_engine(self):
        from investigator.runtime import fingerprint_files
        root, paths = fingerprint_files()
        self.assertIn(root / 'scripts/investigator/windows_ocr.ps1', paths)


if __name__ == '__main__': unittest.main()
