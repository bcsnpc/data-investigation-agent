import hashlib
import tempfile
import unittest
from pathlib import Path
from prepare_retained_enrichment import sources_from_export, prepare


class RetainedExamplesTests(unittest.TestCase):
    def export(self, root):
        raw=b'{"expression":"SUM(Sales[Amount])"}';digest=hashlib.sha256(raw).hexdigest()
        (root/digest).write_bytes(raw)
        return {'source':'synthetic retained export','subjects':[{'estate':'synthetic','node':{
            'id':'measure-1','kind':'MEASURE','label':'Sales','properties':{'definition':{'sha256':digest,'bytes':len(raw)}},
            'provenance':{'definition_hash':digest,'source_id':'retained-definition'}}}]}

    def test_real_definition_bytes_not_cas_pointer_are_the_input(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);export=self.export(root)
            self.assertEqual(sources_from_export(export,root)[0]['definition'],'{"expression":"SUM(Sales[Amount])"}')
            (root/export['subjects'][0]['node']['properties']['definition']['sha256']).write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'HASH_DIFFERS'):sources_from_export(export,root)

    def test_stub_results_cannot_be_misreported_as_live_enrichment(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);export=self.export(root)
            result=prepare(export,root,root/'results','2026-10-22T17:30:00Z')
            self.assertEqual(result['live_model_calls'],0);self.assertEqual(result['live_spend_microdollars'],0)
            self.assertEqual(result['estates'][0]['recording_class'],'RECORDED_STUB')
            self.assertIn('RECORDED_STUB',result['estates'][0]['examples'][0]['business_meaning'])


if __name__=='__main__':unittest.main()
