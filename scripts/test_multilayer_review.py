from pathlib import Path
import tempfile
import unittest
import json
from multilayer_lab import run_case
from investigation_evidence_api import EvidenceStore,create_app
from evidence_summary import summarize


class MultiReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.folder=Path(cls.temp.name)/'case'
        cls.report=run_case(cls.folder);cls.identity=cls.report['result']['id']
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def test_summary_keeps_all_layers_boundaries_and_scope(self):
        item=EvidenceStore(self.folder/'evidence.sqlite').get(self.identity)
        result=summarize(item)
        self.assertEqual({r['layer'] for r in result['observations']},{'bronze','silver','gold'})
        self.assertEqual(len(result['observations']),9)
        self.assertEqual([b['status'] for b in result['boundaries']],['MISMATCH','MATCH'])
        self.assertEqual(result['classification'],'UNRESOLVED');self.assertFalse(result['automatic_defect_routing'])
        self.assertIn('does not establish a root cause',result['text'])

    def test_authenticated_detail_exposes_saved_impact(self):
        app=create_app(self.folder/'evidence.sqlite','x'*32);status=[]
        result=json.loads(b''.join(app({'PATH_INFO':'/api/investigations/'+self.identity,'REQUEST_METHOD':'GET','QUERY_STRING':'',
                                      'HTTP_AUTHORIZATION':'Bearer '+'x'*32},lambda s,h:status.append(s))))
        self.assertTrue(status[0].startswith('200'))
        self.assertEqual(result['investigation']['result']['boundaries'][0]['impact_by_currency']['USD']['downstream_minus_upstream'],'10.0000')
        self.assertEqual(result['summary']['boundaries'][1]['status'],'MATCH')

    def test_legacy_summary_remains_supported(self):
        result=summarize({'id':'fixture','classification':'UNRESOLVED','request':{'observations':{}},'result':{}})
        self.assertEqual(result['observations'],[]);self.assertEqual(result['boundaries'],[])


if __name__=='__main__':unittest.main()
