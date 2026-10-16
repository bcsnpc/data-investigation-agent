import json
from contextlib import closing
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import owner_demo


class OwnerDemoTests(unittest.TestCase):
    def test_preparation_cannot_consume_admission_disk_floor(self):
        from types import SimpleNamespace
        with patch('sys.argv',['owner_demo','--source-manifest','synthetic.json']),\
             patch.object(owner_demo,'prepare',return_value=Path('isolated.json')),\
             patch.object(owner_demo.shutil,'disk_usage',side_effect=[SimpleNamespace(free=15*1024**3),SimpleNamespace(free=9*1024**3)]):
            with self.assertRaisesRegex(ValueError,'OWNER_STORAGE_STOP_AFTER_PREPARATION'):owner_demo.main()
    def test_live_refuses_after_owner_deadline(self):
        from datetime import datetime
        with patch.object(owner_demo,'datetime') as clock:
            clock.now.return_value.astimezone.return_value.timestamp.return_value=9999999999
            clock.fromisoformat.side_effect=datetime.fromisoformat
            with self.assertRaisesRegex(ValueError, 'ROUND_FIFTEEN_DEADLINE'):
                owner_demo.live_admission()

    def test_storage_clone_does_not_copy_secrets_or_share_catalog(self):
        import sqlite3
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / '.local/round-fourteen/control/estate.json'
            source.parent.mkdir(parents=True)
            source.write_text('{}')
            for name in ('catalog', 'inventory'):
                with closing(sqlite3.connect(root / (name + '.sqlite'))) as db:
                    with db:
                        db.execute('CREATE TABLE marker(value TEXT)')
                        db.execute("INSERT INTO marker VALUES('unchanged')")
            original = {'storage': {'catalog': 'catalog.sqlite', 'inventory': 'inventory.sqlite'},
                        'budgets': {'diagnostic_reads_per_run': 12},
                        'secret': {'credential_file': '.local/existing.xml'}}
            with patch('investigator.estate_manifest.load', return_value=original):
                result = owner_demo.prepare(source, root / 'isolated')
            manifest = json.loads(result.read_text())
            self.assertEqual(original['storage']['catalog'], 'catalog.sqlite')
            self.assertNotEqual(manifest['storage']['catalog'], str(root / 'catalog.sqlite'))
            self.assertEqual(manifest['secret']['credential_file'], str(root / '.local/existing.xml'))
            self.assertFalse((root / 'isolated/existing.xml').exists())
            isolation = json.loads((root / 'isolated/isolation.json').read_text())
            self.assertEqual(isolation['dollar_guard_microdollars'], 190000000)
            self.assertEqual(isolation['source_budget_policy']['diagnostic_reads_per_run'], 12)
            self.assertFalse(isolation['copied_secrets'])


if __name__ == '__main__':
    unittest.main()
