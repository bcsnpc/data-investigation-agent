import json
from pathlib import Path
import tempfile
import unittest
from publish import generate, notebook
from publish_reports import model


class PublisherTests(unittest.TestCase):
    def test_related_rows_and_private_expectations(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);generate(root)
            data=json.loads((root/'publisher-input.json').read_text())
            truth=json.loads((root/'evaluator-private.json').read_text())
            warehouses,products,rates,movements,purchases,adjustments=[t['rows'] for t in data['tables']]
            self.assertTrue(all(r[1] in {w[0] for w in warehouses} and r[2] in {p[0] for p in products} for r in movements+purchases))
            self.assertTrue(all(r[1] in {m[0] for m in movements} for r in adjustments))
            joined=[m for m in movements for r in rates if m[2]==r[0]]
            self.assertEqual(len(joined),truth['gold_rows'])
            self.assertEqual(sum(r[3] for r in joined),truth['gold_units'])
            nb=notebook(data,'workspace',{'bronze':'b','silver':'s','gold':'g'})
            code=''.join(nb['cells'][0]['source']);compile(code,'notebook','exec')
            self.assertNotIn('evaluator-private',code)
            self.assertNotIn('gold_units',code)

    def test_native_model_references_gold_tables_and_related_dimensions(self):
        value=model({'id':'endpoint','connectionString':'endpoint.fabric.microsoft.com'})['model']
        tables={t['name']:t for t in value['tables']}
        for relation in value['relationships']:
            for prefix in ('from','to'):
                self.assertIn(relation[prefix+'Column'],{c['name'] for c in tables[relation[prefix+'Table']]['columns']})
        self.assertTrue(all(t['partitions'][0]['mode']=='directLake' for t in tables.values()))
        self.assertNotIn('expected',json.dumps(value).lower())


if __name__=='__main__':unittest.main()
