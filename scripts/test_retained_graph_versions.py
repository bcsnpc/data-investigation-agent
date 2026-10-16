import json
from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import unittest

from investigator.onboarding import digest
from validate_retained_graph_versions import retained


class RetainedVersionsTests(unittest.TestCase):
    def test_hash_checked_parts_are_unchanged_and_children_use_collector_expansion(self):
        report='fabric://workspace/report';raw='{ "name": "p", "displayName": "Page" }'
        part={'id':report+'/part/p','kind':'DefinitionPart','name':'definition/pages/p/page.json',
              'parent_id':report,'metadata':{'path':'definition/pages/p/page.json','content':raw}}
        value={'scan_ended':'2026-01-01T00:00:00Z','reports':[{'report':{'id':report,'kind':'Report',
            'name':'Report','source':'retained'},'report_definitions':[part]}]}
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'context.sqlite'
            with closing(sqlite3.connect(path)) as db:
                db.execute('CREATE TABLE model_contexts(id TEXT,body TEXT,hash TEXT)')
                db.execute('INSERT INTO model_contexts VALUES(?,?,?)',('c',json.dumps(value),digest(value)))
                db.commit()
            before=path.read_bytes()
            context,assets,proof=retained(path,'c',report)
            self.assertEqual(next(a for a in assets if a['kind']=='DefinitionPart'),part)
            self.assertEqual(next(a for a in assets if a['kind']=='ReportPage')['metadata'],json.loads(raw))
            self.assertEqual(proof['context_hash'],digest(context));self.assertEqual(before,path.read_bytes())
            with self.assertRaisesRegex(ValueError,'MISSING'):retained(path,'missing',report)
            with self.assertRaisesRegex(ValueError,'AMBIGUOUS_OR_MISSING'):retained(path,'c','another-report')
            with closing(sqlite3.connect(path)) as db:
                db.execute("UPDATE model_contexts SET hash='wrong'");db.commit()
            with self.assertRaisesRegex(ValueError,'HASH_DIFFERS'):retained(path,'c',report)


if __name__=='__main__':unittest.main()
