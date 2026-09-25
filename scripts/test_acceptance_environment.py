"""The evaluator must read the exact environment populated by discovery."""
import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT=Path(__file__).resolve().parents[1]


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


class AcceptanceEnvironmentTests(unittest.TestCase):
    def test_live_and_replay_store_preserve_explicit_environment(self):
        live=load('acceptance_run_ticket',ROOT/'acceptance/unknown_domain/run_ticket.py')
        replay=load('acceptance_replay_planner',ROOT/'acceptance/unknown_domain/replay_planner.py')
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp);inventory=folder/'inventory.sqlite'
            config={'storage':{'database':str(inventory)}}
            for factory in (live.model_store,replay.model_store):
                store=factory(folder,config,'isolated-challenge')
                self.assertEqual(store.environment,'isolated-challenge')
                self.assertNotEqual(store.environment,'development')


if __name__=='__main__':unittest.main()
