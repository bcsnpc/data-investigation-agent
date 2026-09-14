from io import BytesIO
import unittest
from investigation_evidence_api import create_app


class UiTests(unittest.TestCase):
    def test_fixed_assets_are_public_but_api_remains_protected(self):
        app=create_app('unused.sqlite','x'*40,ui=True)
        for path in ['/', '/review.js', '/review.css', '/api/investigations', '/../docs/progress.md']:
            captured={}
            def start(status,headers):captured.update(status=status,headers=dict(headers))
            content=b''.join(app({'PATH_INFO':path,'REQUEST_METHOD':'GET','wsgi.input':BytesIO()},start))
            if path in ['/', '/review.js', '/review.css']:
                self.assertTrue(captured['status'].startswith('200'))
                self.assertIn("frame-ancestors 'none'",captured['headers']['Content-Security-Policy'])
                self.assertTrue(content)
            else:self.assertTrue(captured['status'].startswith('401'))

    def test_ui_is_opt_in(self):
        app=create_app('unused.sqlite','x'*40)
        captured=[]
        app({'PATH_INFO':'/','REQUEST_METHOD':'GET'},lambda status,headers:captured.append(status))
        self.assertTrue(captured[0].startswith('401'))


if __name__=='__main__':unittest.main()
