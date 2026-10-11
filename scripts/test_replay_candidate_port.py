import unittest
from types import SimpleNamespace
from unittest.mock import patch
from investigator.estate_installation import install_candidate_reader


class ReplayCandidatePortTests(unittest.TestCase):
    def test_live_candidate_port_exists_and_still_refuses_before_native_read_at_cap(self):
        from investigator.form_candidates import NotMeasurable
        workspace=SimpleNamespace(agent=SimpleNamespace(config={'_estate':{}}),
            store=SimpleNamespace(get=lambda identity:{}),dynamic_read_limit=0)
        install_candidate_reader(workspace)
        with patch('investigator.adapters.form_candidate_values.plan',return_value={}), \
             patch('investigator.flexible_tools.run',side_effect=AssertionError('No read allowed')):
            with self.assertRaisesRegex(NotMeasurable,'Per-form diagnostic cap'):
                workspace.form_candidate_reader({'model_id':'model'})

    def test_local_replay_keeps_local_port_and_never_installs_live_reader(self):
        workspace=SimpleNamespace(agent=SimpleNamespace(config={'_estate':{'execution':{'mode':'LOCAL_EXPORTED'}}}))
        with patch('investigator.adapters.local_installation.install') as local, \
             patch('investigator.adapters.form_candidate_values.install') as live:
            install_candidate_reader(workspace)
        local.assert_called_once_with(workspace);live.assert_not_called()
