import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from installation_secrets import root
from investigator.admission_deadline import require_open


class ExistingSecretLocationTests(unittest.TestCase):
    def test_secret_locator_bytes_are_frozen_with_transports(self):
        from investigator.runtime import FINGERPRINT_TRANSPORTS
        self.assertIn('scripts/installation_secrets.py',FINGERPRINT_TRANSPORTS)
    def test_existing_location_only_no_creation(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder=Path(temporary)
            with patch.dict(os.environ,{'INVESTIGATOR_EXISTING_SECRET_ROOT':str(folder)}):
                with self.assertRaisesRegex(ValueError,'EXISTING_SECRET_ROOT_REQUIRED'):root(Path('default'))
                self.assertEqual(list(folder.iterdir()),[])
                (folder/'.local').mkdir()
                self.assertEqual(root(Path('default')),folder.resolve())
                self.assertEqual(list(folder.iterdir()),[folder/'.local'])
    def test_default_and_closed_admission(self):
        with patch.dict(os.environ,{},clear=True):
            self.assertEqual(root(Path('default')),Path('default'))
            require_open()
        with patch.dict(os.environ,{'INVESTIGATOR_LIVE_ADMISSION_DEADLINE':'2000-01-01T23:30:00-05:00'}):
            with self.assertRaisesRegex(ValueError,'LIVE_ADMISSION_DEADLINE_REACHED'):require_open()
    def test_expired_portal_refuses_live_catalog_before_any_reader(self):
        from investigator.workspace_api import create_app
        from unittest.mock import MagicMock
        from io import BytesIO
        workspace=MagicMock();token='synthetic-local-token-of-at-least-32-characters'
        app=create_app(workspace,token,8791)
        for path in ('/api/workspace/forms/catalog','/api/workspace/questionnaire/catalog'):
            statuses=[]
            with patch.dict(os.environ,{'INVESTIGATOR_LIVE_ADMISSION_DEADLINE':'2000-01-01T23:30:00-05:00'}):
                result=b''.join(app({'HTTP_HOST':'127.0.0.1:8791','HTTP_AUTHORIZATION':'Bearer '+token,'REQUEST_METHOD':'GET','PATH_INFO':path,'wsgi.input':BytesIO()},lambda status,headers:statuses.append(status)))
            self.assertIn('409',statuses[0]);self.assertIn(b'LIVE_ADMISSION_DEADLINE_REACHED',result)
        workspace.forms.catalog.assert_not_called()
