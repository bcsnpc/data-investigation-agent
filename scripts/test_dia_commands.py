"""Demo must pin before serving, default to no execution and never invent a key."""
import os
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
import dia


class DiaCommandsTests(unittest.TestCase):
    def test_demo_requires_existing_key_before_installation(self):
        with patch.dict(os.environ, {}, clear=True), patch('investigator.estate_installation.build') as build:
            with self.assertRaisesRegex(ValueError, 'never creates a key'): dia.demo('m','case',8776)
            build.assert_not_called()

    def test_read_only_demo_pins_before_serving_and_fetches_no_provider_key(self):
        workspace = Mock(); workspace.stopping = Mock()
        manifest = {'model':{'credential':{},'endpoint':'https://offline.example','deployment':'fixture'}}
        selected = SimpleNamespace(context_pins={'model':{'context_id':'pinned'}},acceptance_fixture_state={'name':'baseline'})
        order = []
        server = Mock(); server.__enter__ = Mock(return_value=server); server.__exit__ = Mock(return_value=False)
        server.serve_forever.side_effect = lambda: order.append('serve')
        with patch.dict(os.environ, {'INVESTIGATOR_WORKSPACE_TOKEN':'existing-offline-fixture-key-32-characters'}), \
             patch('investigator.estate_installation.build',return_value=(manifest,workspace)) as build, \
             patch('investigator.acceptance_context.pin_run_context',side_effect=lambda *a,**k:(order.append('pin') or selected)) as pin, \
             patch('investigator.workspace_api.create_app') as app, \
             patch('wsgiref.simple_server.make_server',return_value=server), \
             patch('run_adaptive_investigation.local_azure_key') as key, \
             patch('threading.Thread') as thread:
            dia.demo('m','case',8776)
            build.assert_called_once_with('m',execution_enabled=False)
            pin.assert_called_once_with(workspace,'case',fixture=manifest)
            key.assert_called_once_with(None); thread.assert_not_called()
            self.assertEqual(order,['pin','serve']); workspace.stopping.set.assert_called_once()

    def test_pin_refusal_never_starts_server(self):
        with patch.dict(os.environ, {'INVESTIGATOR_WORKSPACE_TOKEN':'existing-offline-fixture-key-32-characters'}), \
             patch('investigator.estate_installation.build',return_value=({'model':{}},Mock())), \
             patch('investigator.acceptance_context.pin_run_context',side_effect=ValueError('unapproved context')), \
             patch('wsgiref.simple_server.make_server') as serve:
            with self.assertRaisesRegex(ValueError,'unapproved context'): dia.demo('m','case',8776)
            serve.assert_not_called()

    def test_demo_cli_requires_case_and_defaults_read_only(self):
        with patch.object(dia,'demo') as call:
            dia.main(['demo','--manifest','fixture.json','--case','case.json'])
            self.assertFalse(call.call_args.args[-1])
        with self.assertRaises(SystemExit): dia.main(['demo','--manifest','fixture.json'])


if __name__ == '__main__': unittest.main()
