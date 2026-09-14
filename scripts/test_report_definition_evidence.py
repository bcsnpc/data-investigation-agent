from contextlib import closing,redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from metadata_inventory import Inventory,expand_definition
from report_definition_evidence import bundle

class DefinitionEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'inventory.sqlite'
        store=Inventory(self.path);self.scan=store.scan
        self.root='fabric://workspace';self.report=self.root+'/report'
        self.model=self.root+'/22222222-2222-4222-8222-222222222222'
        store.asset(self.report,'Report','Report','endpoint',{},self.root)
        store.asset(self.model,'SemanticModel','Model','endpoint',{},self.root)
        expand_definition(store,self.report,'Report',{
            'definition.pbir':json.dumps({'datasetReference':{'byConnection':{'connectionString':'semanticmodelid=22222222-2222-4222-8222-222222222222'}}}),
            'definition/report.json':json.dumps({'filterConfig':{'filters':[{'name':'test'}]}}),
            'definition/pages/p1/page.json':json.dumps({'name':'p1'})},'endpoint')
        expand_definition(store,self.model,'SemanticModel',{'model.bim':json.dumps({'model':{'tables':[{'name':'Sales','measures':[{'name':'Cash','expression':'SUM(Sales[Cash])'}]}]}})},'endpoint')
        store.finish();store.db.close()
    def test_binding_filters_and_dax_are_retained(self):
        result=bundle(self.path,self.scan,self.report)
        self.assertEqual(result['binding_status'],'RESOLVED_EXPLICIT_ID')
        self.assertEqual(result['model_id'],self.model)
        self.assertEqual(result['gaps'],[])
        self.assertTrue(any(x['filter_config_present'] for x in result['filter_context']))
        self.assertTrue(any(x['kind']=='Measure' and x['metadata']['expression']=='SUM(Sales[Cash])' for x in result['model_assets']))
        self.assertFalse(result['root_cause_verified'])
        self.assertEqual(result['bundle_hash'],bundle(self.path,self.scan,self.report)['bundle_hash'])
    def test_missing_binding_never_falls_back_to_name(self):
        with closing(sqlite3.connect(self.path)) as db:
            db.execute("DELETE FROM assets WHERE name='definition.pbir'");db.commit()
        result=bundle(self.path,self.scan,self.report)
        self.assertEqual(result['binding_status'],'UNRESOLVED')
        self.assertEqual(result['model_assets'],[])
    def test_tampering_rejected(self):
        with closing(sqlite3.connect(self.path)) as db:
            db.execute("UPDATE assets SET metadata='{}' WHERE kind='Measure'");db.commit()
        with self.assertRaises(ValueError):bundle(self.path,self.scan,self.report)
    def test_unfinished_scan_and_missing_model_definition(self):
        with closing(sqlite3.connect(self.path)) as db:
            db.execute("DELETE FROM assets WHERE name='model.bim'");db.commit()
        self.assertIn('Native model.bim missing',bundle(self.path,self.scan,self.report)['gaps'])
        with closing(sqlite3.connect(self.path)) as db:
            db.execute("UPDATE scans SET status='RUNNING'");db.commit()
        with self.assertRaises(ValueError):bundle(self.path,self.scan,self.report)

    def test_duplicate_model_id_is_unresolved_even_with_valid_hash(self):
        import hashlib
        with closing(sqlite3.connect(self.path)) as db:
            aid,raw=db.execute("SELECT id,metadata FROM assets WHERE name='definition.pbir'").fetchone()
            value=json.loads(raw);content=json.loads(value['content'])
            content['datasetReference']['byConnection']['connectionString']+=';semanticmodelid=22222222-2222-4222-8222-222222222222'
            value['content']=json.dumps(content);encoded=json.dumps(value,sort_keys=True)
            db.execute('UPDATE assets SET metadata=?,content_hash=? WHERE id=?',(encoded,hashlib.sha256(encoded.encode()).hexdigest(),aid));db.commit()
        self.assertEqual(bundle(self.path,self.scan,self.report)['binding_status'],'UNRESOLVED')
