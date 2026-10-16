import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from investigator.shared_state import SharedState,StateConflict
from investigator.shared_catalog import SharedCatalog,import_catalog,publish_readiness
from investigator.onboarding import digest,Conflict,ModelStore


class SharedCatalogTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.state=SharedState.offline(Path(self.tmp.name)/'shared.sqlite');self.state.migrate()
        context={'id':'context-one','model_id':'model-one','measures':[]}
        self.source={'version':'shared-catalog-import-v1','environment':'test',
          'models':[{'environment':'test','id':'model-one','name':'Synthetic model','enabled':True,'context_id':'context-one','context':context}],
          'contexts':[{'model_id':'model-one','context_id':'context-one','body':context,'hash':digest(context)}]}

    def test_import_and_current_context_hash_pin(self):
        proof=import_catalog(self.state,'one',self.source)
        catalog=SharedCatalog(self.state,'test')
        self.assertEqual(catalog.get('model-one'),self.source['models'][0])
        self.assertEqual(catalog.list(True),self.source['models'])
        self.assertEqual(import_catalog(self.state,'one',self.source),proof)
        with self.assertRaisesRegex(Conflict,'Pinned context hash differs'):
            catalog.get('model-one',{'context_id':'context-one','hash':'0'*64})

    def test_bad_context_never_enters_publication(self):
        source=copy.deepcopy(self.source);source['contexts'][0]['hash']='0'*64
        with self.assertRaisesRegex(Conflict,'context identity or hash'):import_catalog(self.state,'one',source)
        with self.assertRaises(KeyError):SharedCatalog(self.state,'test').list()

    def test_live_model_store_get_context_and_list_use_shared_state(self):
        import_catalog(self.state,'one',self.source)
        with patch('investigator.shared_state.configured_state',return_value=self.state):
            store=ModelStore(Path(self.tmp.name)/'private.sqlite',Path(self.tmp.name)/'inventory.sqlite','test')
        self.assertEqual(store.get('model-one'),self.source['models'][0])
        self.assertEqual(store.context('model-one','context-one'),self.source['contexts'][0]['body'])
        self.assertEqual(store.list(),self.source['models'])
        with self.assertRaisesRegex(Conflict,'OPERATOR_PUBLICATION'):store.enable('model-one',0,False,'worker')

    def test_readiness_is_immutable_evidence_not_a_ready_verdict(self):
        certificate={'version':'route-readiness-v1','unverified':'synthetic only'}
        key=publish_readiness(self.state,certificate)
        self.assertEqual(publish_readiness(self.state,certificate),key)
        self.assertEqual(self.state.get('readiness_certificate',key)['body'],certificate)
        self.assertNotIn('status',self.state.get('readiness_certificate',key)['body'])


if __name__=='__main__':unittest.main()
