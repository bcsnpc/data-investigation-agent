"""Fixture-only recorded transport excerpt, distinct from private budget replay."""
import hashlib,json,unittest
from pathlib import Path
from investigator.code_sources import read
from investigator.adapters.code_definition import fetch

ROOT=Path(__file__).resolve().parents[1]

class FixtureCodeSourceTests(unittest.TestCase):
    def test_recorded_api_projections_reproduce_fetched_fixture_bytes_without_network(self):
        excerpt=json.loads((ROOT/'fixture-code/api-recorded-operation.json').read_text(encoding='utf8'))
        self.assertEqual(excerpt['provenance'],'DERIVED_TRANSPORT_EXCERPT')
        self.assertEqual(len(excerpt['requests']),3)
        pending=list(excerpt['requests']);counts=[]
        def request(method,endpoint):
            recorded=pending.pop(0)
            self.assertEqual((method,endpoint),(recorded['method'],recorded['endpoint']))
            return recorded['response']
        unit,receipt=read(excerpt['source'],excerpt['path'],meter=lambda fn:(counts.append(1),fn())[1],
            item_fetch=lambda s,p,m:fetch(s,p,m,request,wait=lambda _:None))
        self.assertEqual(pending,[]);self.assertEqual(len(counts),3)
        folder=ROOT/'fixture-code'/excerpt['source']['item_ids'][0]
        provenance=json.loads((folder/'fetch-provenance.json').read_text(encoding='utf8'))
        self.assertEqual(unit['content_hash'],provenance['parts']['notebook-content.py']['sha256'])
        self.assertEqual(unit['content_hash'],hashlib.sha256((folder/'notebook-content.py').read_bytes()).hexdigest())
        self.assertEqual(receipt['identity'],'investigator-code-reader')
        self.assertEqual(unit['item_identity']['item_id'],excerpt['source']['item_ids'][0])

if __name__=='__main__':unittest.main()
