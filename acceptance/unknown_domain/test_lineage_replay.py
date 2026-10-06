"""Sealed installation inputs are required; recorded answers are never injected."""
import copy
import sys
import unittest
import tempfile
import importlib.util
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

ROOT=Path(__file__).resolve().parents[2].resolve()
sys.path[:0]=[str(ROOT/'scripts'),str(Path(__file__).parent)]
import metadata_config
from investigator.process_tape import TapeError
from lineage_replay import install


class InstallationReplayTests(unittest.TestCase):
    def setUp(self):
        self.manifest={'adapters':[{'options':{'fabric':{'auth':{'python':'.local/python.exe'}}}}]}
        self.config={'_estate':{'manifest_hash':'sealed','lineage':{'code_locations':[{'may_infer_from_code':True}]}},
                     'fabric':{'auth':{'python':str((ROOT/'.local/python.exe').resolve())}}}
        self.tape=SimpleNamespace(bootstrap={'config':self.config})
        self.installation_root=Path(self.config['fabric']['auth']['python']).parents[1]
        self.original=Mock()
        self.module=SimpleNamespace(ROOT=Path('/temporary/archive'),AdaptiveRuntime=self.original)

    def patches(self):
        return (patch('investigator.estate_manifest.load',return_value=self.manifest),
                patch('investigator.onboarding.digest',return_value='sealed'),
                patch('investigator.adapters.estate_installation.configuration',return_value=self.config),
                patch('investigator.adapters.code_lineage.Installation'))

    def test_missing_manifest_refuses_before_installation(self):
        with self.assertRaisesRegex(TapeError,'MISSING_SEALED_ESTATE_MANIFEST'):
            with install(self.module,self.tape,None):self.fail('accepted')
        self.assertIs(self.module.AdaptiveRuntime,self.original)

    def test_disabled_legacy_producer_needs_no_new_input(self):
        self.config['_estate']['lineage']['code_locations']=[]
        with install(self.module,self.tape,None):
            self.assertIs(self.module.AdaptiveRuntime,self.original)

    def test_manifest_content_change_refuses(self):
        a,b,c,d=self.patches()
        with a,b as digest,c,d as service:
            digest.return_value='changed'
            with self.assertRaisesRegex(TapeError,'MANIFEST_HASH_DIFFERS'):
                with install(self.module,self.tape,'sealed.json'):self.fail('accepted')
            service.assert_not_called()

    def test_projection_change_refuses_and_restores_path_resolver(self):
        a,b,c,d=self.patches();original_root=metadata_config.ROOT
        with a,b,c as projection,d as service:
            projection.return_value={'changed':'content'}
            with self.assertRaisesRegex(TapeError,'CONFIGURATION_DIFFERS'):
                with install(self.module,self.tape,'sealed.json'):self.fail('accepted')
            service.assert_not_called()
        self.assertEqual(metadata_config.ROOT,original_root)

    def test_exact_input_supplies_service_not_saved_results_and_restores_factory(self):
        a,b,c,d=self.patches();original_root=metadata_config.ROOT
        with a,b,c as projection,d as service:
            def project(manifest):
                self.assertEqual(metadata_config.ROOT,self.installation_root)
                return self.config
            projection.side_effect=project
            with install(self.module,self.tape,'sealed.json'):
                self.module.AdaptiveRuntime('runtime')
                self.original.assert_called_once_with('runtime',process_lineage=service.return_value)
                with self.assertRaisesRegex(TapeError,'DUPLICATE_REPLAY_LINEAGE_INSTALLATION'):
                    self.module.AdaptiveRuntime(process_lineage=object())
            service.assert_called_once_with(self.manifest,Path('sealed.json'),self.installation_root)
        self.assertIs(self.module.AdaptiveRuntime,self.original)
        self.assertEqual(metadata_config.ROOT,original_root)

    def test_unbound_root_cannot_be_guessed(self):
        self.config['fabric']['auth']['python']=str((ROOT/'unrelated.exe').resolve())
        a,b,c,d=self.patches()
        with a,b,c,d as service:
            with self.assertRaisesRegex(TapeError,'ROOT_NOT_ESTABLISHED'):
                with install(self.module,self.tape,'sealed.json'):self.fail('accepted')
            service.assert_not_called()


class ManifestLocatorTests(unittest.TestCase):
    def test_only_sealed_digest_selects_sidecar_and_disabled_needs_none(self):
        spec=importlib.util.spec_from_file_location('lineage_private_bundle',ROOT/'acceptance/known_domain/private_bundle.py')
        bundle=importlib.util.module_from_spec(spec);spec.loader.exec_module(bundle)
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);estate={'manifest_hash':'a'*64,'lineage':{'code_locations':[{'may_infer_from_code':True}]}}
            tape=SimpleNamespace(bootstrap={'config':{'_estate':estate}})
            with self.assertRaisesRegex(ValueError,'MISSING_SEALED_ESTATE_MANIFEST'):bundle.estate_manifest(tape,root)
            folder=root/'estate-manifests';folder.mkdir();path=folder/('a'*64+'.json');path.write_text('{}')
            self.assertEqual(bundle.estate_manifest(tape,root),path)
            estate['manifest_hash']='../escape'
            with self.assertRaisesRegex(ValueError,'HASH_INVALID'):bundle.estate_manifest(tape,root)
            estate['lineage']['code_locations']=[]
            self.assertIsNone(bundle.estate_manifest(tape,root))


if __name__=='__main__':unittest.main()
