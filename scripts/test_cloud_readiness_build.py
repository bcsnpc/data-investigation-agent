import unittest
from cloud_readiness_build import unchanged_declarations
class CloudReadinessTests(unittest.TestCase):
 def test_hashes_not_status_establish_retained_definition_compatibility(self):
  before={'assets':[{'id':'a','content_hash':'one','availability':'CURRENT'}]}
  unchanged_declarations(before,{'assets':[{'id':'a','content_hash':'one','availability':'CURRENT','last_seen_scan':'new'}]})
  for current in [{'assets':[{'id':'a','content_hash':'different'}]},{'assets':[]},{'assets':[{'id':'a','content_hash':'one'},{'id':'b','content_hash':'two'}]}]:
   with self.assertRaisesRegex(ValueError,'CONTENT_CHANGED'):unchanged_declarations(before,current)
if __name__=='__main__':unittest.main()
