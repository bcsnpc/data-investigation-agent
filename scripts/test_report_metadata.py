from contextlib import closing, redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from collect_report_metadata import collect

REPORT='11111111-1111-4111-8111-111111111111'
MODEL='22222222-2222-4222-8222-222222222222'
OTHER='33333333-3333-4333-8333-333333333333'

class Reader:
    workspace='44444444-4444-4444-8444-444444444444'
    def __init__(self): self.calls=[]; self.fail=False
    def discover_assets(self):
        return [{'id':i,'type':t,'displayName':t} for i,t in [(REPORT,'Report'),(MODEL,'SemanticModel'),(OTHER,'Notebook')]]
    def get_definition(self, asset):
        self.calls.append(('definition',asset['id']))
        if self.fail and asset['id']==REPORT: raise RuntimeError('private provider detail')
        if asset['type']=='Report':
            return {'definition/pages/p1/page.json':json.dumps({'name':'p1','displayName':'Page'})}
        return {'model.bim':json.dumps({'model':{'tables':[{'name':'Sales','measures':[{'name':'Cash','expression':'SUM(Sales[Cash])'}]}]}})}
    def get_refresh_history(self, asset):
        self.calls.append(('history',asset['id']));return []

class ReportMetadataTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'inventory.sqlite';self.reader=Reader()
    def collect(self,ids):
        with redirect_stdout(StringIO()): return collect(self.path,self.reader,ids)
    def test_selected_definitions_and_measure_retained(self):
        result=self.collect([REPORT,MODEL])
        self.assertEqual(result['status'],'COMPLETE')
        self.assertEqual(result['assets']['Measure'],1)
        self.assertFalse(result['snapshot_comparable'])
        self.assertFalse(result['report_model_association_verified'])
        self.assertEqual(self.reader.calls,[('definition',REPORT),('definition',MODEL),('history',MODEL)])
        with closing(sqlite3.connect(self.path)) as db:
            value=db.execute("SELECT metadata FROM assets WHERE kind='Measure'").fetchone()[0]
        self.assertEqual(json.loads(value)['expression'],'SUM(Sales[Cash])')
    def test_failure_is_partial_and_redacted(self):
        self.reader.fail=True;result=self.collect([REPORT,MODEL])
        self.assertEqual(result['status'],'PARTIAL')
        self.assertEqual(result['unavailable_capabilities'],1)
        with closing(sqlite3.connect(self.path)) as db:
            details=str(db.execute('SELECT detail FROM observations').fetchall())
        self.assertNotIn('private provider detail',details)
        self.assertEqual(result['assets']['Measure'],1)
    def test_invalid_selection_creates_no_scan(self):
        for ids in [[],[REPORT,REPORT],[OTHER],['invalid'],['55555555-5555-4555-8555-555555555555']]:
            with self.assertRaises(ValueError): self.collect(ids)
            self.assertFalse(self.path.exists())
    def test_repeated_collection_keeps_prior_scan(self):
        first=self.collect([REPORT]);second=self.collect([MODEL])
        self.assertNotEqual(first['scan_id'],second['scan_id'])
        with closing(sqlite3.connect(self.path)) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM scans').fetchone()[0],2)
            self.assertEqual(db.execute('SELECT count(*) FROM assets WHERE scan_id=? AND kind=?',(first['scan_id'],'ReportPage')).fetchone()[0],1)
