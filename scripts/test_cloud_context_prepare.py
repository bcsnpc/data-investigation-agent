import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from cloud_context_prepare import prepare,publish
from investigator.onboarding import digest
from investigator.shared_state import SharedState,StateConflict
from investigator.shared_catalog import SharedCatalog

class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.state=SharedState.offline(Path(self.tmp.name)/'state.sqlite');self.state.migrate()
        self.before={'id':'m','environment':'e','workspace':'w','native_id':'n','enabled':False,'context_id':'old'}
        self.after={**self.before,'enabled':True,'context_id':'new','context':{'id':'new'}}
        self.c={'version':'cloud-selected-model-publication-v1','environment':'e','model_before':self.before,
            'model_after':self.after,'context':self.after['context'],'context_hash':digest(self.after['context']),
            'approval':{'owner':'owner','reason':'explicit retained-context migration'}}
        self.key=SharedCatalog(self.state,'e')._key('m')
        self.state.put('catalog_model',self.key,self.before)
        self.state.put('catalog_model','unrelated',{'enabled':False})
    def test_one_model_cas_preserves_prior_and_does_not_claim_readiness(self):
        proof=publish(self.state,self.c)
        self.assertEqual(proof['readiness'],'NOT_EARNED_BY_PUBLICATION')
        self.assertEqual(self.state.get('catalog_model',self.key)['body'],self.after)
        self.assertEqual(self.state.get('catalog_model_history',self.key+':0')['body'],self.before)
        self.assertEqual(self.state.get('catalog_model','unrelated')['body'],{'enabled':False})
    def test_stale_or_changed_target_refuses_atomically(self):
        self.c['model_before']['enabled']=True
        with self.assertRaises(StateConflict):publish(self.state,self.c)
        self.assertFalse(self.state.get('catalog_model',self.key)['body']['enabled'])
        self.c['model_before']['enabled']=False;self.c['model_after']['native_id']='different'
        with self.assertRaisesRegex(ValueError,'TARGET'):publish(self.state,self.c)

class ReadoptionTests(unittest.TestCase):
    def test_retained_assets_unchanged_sources_untouched(self):
        from test_enterprise_discovery import DiscoveryTests
        f=DiscoveryTests();f.setUp();self.addCleanup(f.tearDown)
        original=f.scan();model=f.store.list()[0]
        source_hash=hashlib.sha256(f.store.database.read_bytes()).hexdigest()
        destination=f.root/'cloud-candidate';manifest=f.root/'manifest.json';manifest.write_text('{}')
        config=copy.deepcopy(f.config);config['fabric']['auth']={'python':'cloud-python'}
        with patch('cloud_context_prepare.load',return_value={'environment':'test'}),patch('cloud_context_prepare.configuration',return_value=config):
            result=prepare(manifest,f.store.database,f.store.inventory,destination,model_id=model['id'],
                context_id=original['id'],context_hash=original['hash'],actor='owner',decision='retained metadata reapproval')
        self.assertEqual(hashlib.sha256(f.store.database.read_bytes()).hexdigest(),source_hash)
        self.assertEqual(result['model_before'],model)
        self.assertEqual(result['approval']['physical_requests'],0)
        self.assertNotEqual(result['model_after']['context_id'],model['context_id'])
        self.assertTrue(result['model_after']['enabled'])

