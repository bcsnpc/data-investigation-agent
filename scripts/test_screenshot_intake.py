import base64
from io import BytesIO
import json
from threading import Event, Thread
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

from investigator.screenshot_intake import Screenshots, inspect_image, MAX_BYTES, validate
from investigator.onboarding import Conflict
import test_question_intake as question_fixture
import test_investigator_workspace as workspace_fixture


def image_bytes(format='PNG', size=(120, 60)):
    from PIL import Image
    output = BytesIO(); Image.new('RGB', size, 'white').save(output, format=format)
    return output.getvalue()


class ScreenshotTests(unittest.TestCase):
    def setUp(self):
        self.h = workspace_fixture.WorkspaceTests(); self.h.setUp(); self.addCleanup(self.h.doCleanups)
        self.w = self.h.workspace
        self.extractor = MagicMock(return_value=({'visible_text': 'ratio 7\nCurrency USD', 'readable': True, 'uncertainties': []}, {'usage': {'output_tokens': 60}}))
        self.w.screenshots = Screenshots(self.w, self.extractor)
        self.raw = image_bytes()
        self.upload = {'name': 'report.png', 'mime': 'image/png', 'base64': base64.b64encode(self.raw).decode(), 'request_key': 'upload'}

    def attach(self): return self.w.screenshots.upload(self.upload)
    def read(self): return self.w.screenshots.read({'attachment_id': self.attach()['id'], 'request_key': 'read'})
    def review(self): return self.w.screenshots.review({'extraction_id': self.read()['id'], 'text': 'ratio 7\nCurrency USD', 'request_key': 'review'})

    def test_upload_read_review_does_not_query_business_data(self):
        image = self.attach(); self.assertEqual(image['bytes'], len(self.raw)); self.extractor.assert_not_called()
        result = self.read(); self.assertEqual(result['status'], 'EXTRACTED')
        self.assertTrue(self.extractor.call_args.args[0].startswith('data:image/png;base64,'))
        reviewed = self.review(); self.assertFalse(reviewed['edited']); self.assertFalse(reviewed['interpretation_verified'])
        self.h.native.assert_not_called(); self.h.source.assert_not_called(); self.h.planner.assert_not_called()

    def test_upload_read_review_and_history_are_idempotent(self):
        first = self.review(); self.assertEqual(first, self.review())
        self.w.screenshots.history(); self.w.screenshots.reads(first['attachment']['id'])
        self.extractor.assert_called_once()
        self.assertEqual(self.h.agent.governor.snapshot()['reserved_today']['planner_calls'], 1)

    def test_jpeg_and_png_are_accepted_without_reencoding(self):
        for mime, format in [('image/png', 'PNG'), ('image/jpeg', 'JPEG')]:
            raw = image_bytes(format); metadata = inspect_image(raw, mime)
            self.assertEqual(metadata['bytes'], len(raw)); self.assertEqual(metadata['width'], 120)
        metadata, raw = self.w.screenshots.image(self.attach()['id'], content=True)
        self.assertEqual(raw, self.raw)

    def test_bad_types_corruption_mime_mismatch_and_oversize_rejected(self):
        cases = [(b'<svg onload="alert(1)"></svg>', 'image/svg+xml'), (self.raw, 'image/jpeg'),
                 (self.raw[:35], 'image/png'), (b'x' * (MAX_BYTES + 1), 'image/png'), (b'', 'image/png')]
        for raw, mime in cases:
            with self.subTest(mime=mime, size=len(raw)):
                with self.assertRaises(ValueError): inspect_image(raw, mime)
        self.extractor.assert_not_called()

    def test_dimensions_and_animated_images_rejected(self):
        with self.assertRaises(ValueError): inspect_image(image_bytes(size=(5001, 1)), 'image/png')
        with self.assertRaises(ValueError): inspect_image(image_bytes(size=(3000, 3000)), 'image/png')
        from PIL import Image
        output = BytesIO(); one = Image.new('RGB', (4, 4), 'white'); two = Image.new('RGB', (4, 4), 'black')
        one.save(output, format='PNG', save_all=True, append_images=[two])
        with self.assertRaises(ValueError): inspect_image(output.getvalue(), 'image/png')

    def test_invalid_base64_and_path_names_rejected(self):
        for change in [{'base64': 'https://example.com/image.png'}, {'base64': '%'}, {'name': '../report.png'}, {'name': 'C:\\secret.png'}, {'url': 'http://localhost'}]:
            with self.assertRaises(ValueError): self.w.screenshots.upload(dict(self.upload, **change))

    def test_changed_upload_read_review_keys_cannot_replace_saved_content(self):
        image = self.attach()
        with self.assertRaises(Conflict): self.w.screenshots.upload(dict(self.upload, name='different.png'))
        self.read()
        with self.assertRaises(Conflict): self.w.screenshots.read({'attachment_id': 'different', 'request_key': 'read'})
        review = self.review()
        with self.assertRaises(Conflict): self.w.screenshots.review(dict(review['request'], text='changed'))

    def test_storage_limit_and_remove_preserve_review_metadata(self):
        reviewed = self.review(); identity = reviewed['attachment']['id']
        with patch('investigator.screenshot_intake.MAX_STORED_BYTES', len(self.raw)):
            with self.assertRaises(Conflict): self.w.screenshots.upload(dict(self.upload, request_key='second'))
            self.assertFalse(self.w.screenshots.remove(identity)['available'])
            self.assertEqual(self.review(), reviewed)
            with self.assertRaises(Conflict): self.w.screenshots.image(identity, content=True)
            self.assertTrue(self.w.screenshots.upload(dict(self.upload, request_key='second'))['available'])

    def test_image_hash_tampering_is_rejected(self):
        image = self.attach()
        with self.h.store.connect() as db: db.execute("UPDATE workspace_images SET content=? WHERE id=?", (b'changed', image['id']))
        with self.assertRaises(Conflict): self.w.screenshots.image(image['id'])

    def test_unreviewed_or_held_image_cannot_be_used_as_question_scope(self):
        from investigator.question_intake import Intake
        resolver = MagicMock(); self.w.intake = Intake(self.w, resolver)
        image = self.attach()
        with self.assertRaises(KeyError): self.w.intake.resolve({'text': 'Investigate', 'request_key': 'q', 'parent_id': None, 'screenshot_review_id': image['id']})
        resolver.assert_not_called()

    def test_reviewed_screenshot_to_catalog_to_runtime_preserves_input_provenance(self):
        from investigator.question_intake import Intake
        resolver = MagicMock(return_value=(question_fixture.proposal(), {})); self.w.intake = Intake(self.w, resolver)
        reviewed = self.review()
        q = self.w.intake.resolve({'text': 'This looks low.', 'request_key': 'q', 'parent_id': None, 'screenshot_review_id': reviewed['id']})
        self.assertEqual(q['status'], 'PROPOSED'); self.assertIn('Currency USD', resolver.call_args.args[0]['text'])
        p = self.w.preview(dict(self.h.request, symptom=q['text'], intake_id=q['id']))
        run = self.w.start(p['id']); self.w.run_once(); result = self.w.session(run['id'])
        self.assertEqual(result['intake']['screenshot_review']['attachment']['sha256'], reviewed['attachment']['sha256'])
        self.assertFalse(result['cause_verified']); self.assertEqual(result['facts'][0]['values'][0]['[m0]']['value'], '7')

    def test_clarification_inherits_same_review_without_reextracting(self):
        from investigator.question_intake import Intake
        resolver = MagicMock(return_value=(question_fixture.ask(), {})); self.w.intake = Intake(self.w, resolver)
        reviewed = self.review(); parent = self.w.intake.resolve({'text': 'Looks low', 'request_key': 'q', 'parent_id': None, 'screenshot_review_id': reviewed['id']})
        child = self.w.intake.resolve({'text': 'Use USD', 'request_key': 'answer', 'parent_id': parent['id']})
        self.assertEqual(child['screenshot_review'], parent['screenshot_review']); self.extractor.assert_called_once()

    def test_corrected_transcription_is_labelled_as_user_edit(self):
        r = self.read(); review = self.w.screenshots.review({'extraction_id': r['id'], 'text': 'Corrected ratio for EUR', 'request_key': 'corrected'})
        self.assertTrue(review['edited']); self.assertEqual(review['text'], 'Corrected ratio for EUR')

    def test_vision_timeout_is_not_retried_and_error_is_redacted(self):
        self.extractor.side_effect = TimeoutError('secret provider body')
        r = self.read(); self.assertEqual(r['status'], 'HELD'); self.assertNotIn('secret', json.dumps(r))
        self.assertEqual(r, self.read()); self.extractor.assert_called_once()

    def test_crash_hold_and_late_response_fencing(self):
        entered, release = Event(), Event(); results = []
        def extract(_): entered.set(); release.wait(5); return {'visible_text': 'ratio', 'readable': True, 'uncertainties': []}, {}
        self.extractor.side_effect = extract
        image = self.attach(); worker = Thread(target=lambda: results.append(self.read())); worker.start()
        self.assertTrue(entered.wait(5))
        try:
            pending = self.w.screenshots.reads(image['id'])['reads'][0]
            self.w.screenshots.hold(pending['id'])
        finally: release.set(); worker.join(5)
        self.assertEqual(results[0]['status'], 'HELD'); self.assertIsNone(results[0]['extraction'])
        self.assertEqual(self.h.agent.governor.snapshot()['reservation_states'], {'UNCERTAIN': 1})

    def test_reserved_crash_is_recoverable_from_history(self):
        self.extractor.side_effect = KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt): self.read()
        pending = self.read(); self.assertEqual(pending['status'], 'READING'); self.extractor.assert_called_once()
        self.assertEqual(self.w.screenshots.hold(pending['id'])['status'], 'HELD')

    def test_shared_budget_and_token_accounting(self):
        self.read()
        with self.h.store.connect() as db:
            r = db.execute('SELECT reserved,actual FROM adaptive_usage').fetchone()
        self.assertGreater(json.loads(r[0])['input_characters'], len(self.upload['base64']))
        self.assertEqual(json.loads(r[1])['output_tokens'], 60)
        self.h.agent.governor.policy['daily_limits']['planner_calls'] = 1
        with self.assertRaises(Conflict): self.w.screenshots.read({'attachment_id': self.attach()['id'], 'request_key': 'over-limit'})
        self.extractor.assert_called_once()

    def test_malformed_or_excessive_vision_output_held(self):
        for value in [{'visible_text': 'x'*1601, 'readable': True, 'uncertainties': []},
                      {'visible_text': 'ratio', 'readable': True, 'uncertainties': [], 'query': 'SELECT 1'}]:
            with self.assertRaises(ValueError): validate(value)
        self.extractor.return_value = {'query': 'SELECT 1'}, {}
        self.assertEqual(self.read()['status'], 'HELD')

    def test_removal_during_vision_prevents_new_review(self):
        def extract(_):
            self.w.screenshots.remove(self.attach()['id'])
            return {'visible_text': 'ratio', 'readable': True, 'uncertainties': []}, {}
        self.extractor.side_effect = extract
        self.assertEqual(self.read()['status'], 'HELD')

    def test_authenticated_upload_and_content_no_public_image_urls(self):
        url = '/api/workspace/attachments'
        self.assertEqual(self.h.http(url, self.upload, token='bad')['status'], '401 Unauthorized')
        result = self.h.http(url, self.upload); self.assertEqual(result['status'], '200 OK')
        image_url = url + '/' + result['body']['id'] + '/content'
        self.assertEqual(self.h.http(image_url, token='bad')['status'], '401 Unauthorized')
        r = self.h.http(image_url); self.assertEqual(r['body'], self.raw); self.assertEqual(r['headers']['Cache-Control'], 'no-store')
        self.assertNotIn('base64', json.dumps(self.h.http(url)['body']))

    def test_history_only_host_cannot_call_vision(self):
        self.w.execution_enabled = False
        with self.assertRaises(Conflict): self.read()
        self.extractor.assert_not_called()


class VisionTransportTests(unittest.TestCase):
    def test_sdk_receives_inline_image_and_existing_limits(self):
        from ticket_planner import azure_generate
        client = MagicMock(); client.__enter__.return_value = client
        client.responses.create.return_value = SimpleNamespace(status='completed', output=[SimpleNamespace(type='function_call', name='vision', arguments='{}')],
                                                               id='response', model='configured', usage=None)
        with patch.dict('os.environ', {'AZURE_OPENAI_ENDPOINT':'https://test.openai.azure.com','AZURE_OPENAI_DEPLOYMENT':'configured','AZURE_OPENAI_API_KEY':'fake-test-key'}), patch.dict('sys.modules', {'openai': SimpleNamespace(OpenAI=MagicMock(return_value=client))}):
            azure_generate({}, name='vision', decision_tool=True, image_data_url='data:image/png;base64,aGVsbG8=')
            options = client.responses.create.call_args.kwargs
            self.assertEqual(options['input'][0]['content'][1]['type'], 'input_image')
            self.assertFalse(options['store']); self.assertEqual(options['max_output_tokens'], 1500)
            with self.assertRaises(ValueError): azure_generate({}, image_data_url='http://localhost/private')


if __name__ == '__main__': unittest.main()
