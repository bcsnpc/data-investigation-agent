"""Pins the full offline production route run to unchanged dev inputs and code."""
import unittest,json,hashlib
from pathlib import Path
class BacktrackRouteTests(unittest.TestCase):
 @unittest.skipUnless((Path(__file__).resolve().parents[1]/'docs/runs/round-twenty-four-dev-route-check.json').exists(),'Code-only image excludes acceptance evidence; repository CI executes this regression.')
 def test_all_target_failures_and_five_walkthroughs_have_query_routes(self):
  root=Path(__file__).resolve().parents[1]
  prior=json.loads((root/'docs/runs/round-twenty-three-failure-backtrack.json').read_bytes())
  proof=json.loads((root/'docs/runs/round-twenty-four-dev-route-check.json').read_bytes())
  self.assertEqual(proof['estate_reads'],0);self.assertEqual(proof['model_calls'],0)
  self.assertEqual(hashlib.sha256(json.dumps(json.loads((root/'acceptance/tickets/guided-v2/dev.json').read_bytes()),sort_keys=True,separators=(',',':')).encode()).hexdigest(),proof['ticket_canonical_sha256'])
  for path,digest in proof['route_sources'].items():self.assertEqual(hashlib.sha256((root/path).read_bytes().replace(b'\r\n',b'\n')).hexdigest(),digest,path)
  rows={r['id']:r for r in proof['results']};targets=[c for c in prior['cases']if c['first_wrong_step']=='target'and c['official_zero']]
  self.assertEqual(len(targets),28)
  walkthroughs=['v2-screenshot-record-01-v1','v2-failed-application-load-v1','v2-fixture-quantity-v1','v2-before-temporal-retention-v1','v2-application-baseline-v1']
  for ident in [c['ticket']for c in targets]+walkthroughs:
   with self.subTest(ticket=ident):
    row=rows[ident]
    if ident=='v2-warehouse-scope-v2':
     self.assertEqual((row['status'],row['reason']),('INTAKE_REFUSED','UNKNOWN_REPORT'));continue
    self.assertEqual(row['status'],'ASSEMBLED')
    self.assertGreaterEqual(row['actual_wire']['layers'],3)
    self.assertEqual(row['actual_wire']['layer_ids'],row['without_bookkeeping']['layer_ids'])
if __name__=='__main__':unittest.main()
