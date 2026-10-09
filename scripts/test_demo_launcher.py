"""One start command creates only ephemeral local browser authentication."""
import os
import unittest
from unittest.mock import MagicMock,patch
import serve_investigator_workspace as launcher


class LauncherTests(unittest.TestCase):
    def test_open_browser_uses_ephemeral_key_without_environment_or_secret_write(self):
        workspace=MagicMock();manifest={'model':{'credential':{},'endpoint':'https://example.invalid','deployment':'test'}}
        server=MagicMock();server.__enter__.return_value=server
        server.serve_forever.side_effect=KeyboardInterrupt
        with patch.dict(os.environ,{},clear=True),patch('sys.argv',['demo','--manifest','estate.json','--open-browser']),\
             patch('investigator.estate_installation.build',return_value=(manifest,workspace)),\
             patch.object(launcher,'create_app') as app,patch.object(launcher,'make_server',return_value=server),\
             patch.object(launcher,'local_azure_key'),patch.object(launcher.webbrowser,'open') as browser,\
             patch('builtins.print') as output:
            with self.assertRaises(KeyboardInterrupt):launcher.main()
            key=app.call_args.args[1]
            self.assertGreaterEqual(len(key),32)
            browser.assert_called_once_with('http://127.0.0.1:8776/#access='+key)
            self.assertNotIn('INVESTIGATOR_WORKSPACE_TOKEN',os.environ)
            self.assertNotIn(key,str(output.call_args_list))
            workspace.work.assert_not_called()
            workspace.stopping.set.assert_called_once()

if __name__=='__main__':unittest.main()
