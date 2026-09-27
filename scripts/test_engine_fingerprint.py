"""The engine fingerprint must change whenever code that shapes a run changes."""
from pathlib import Path
import shutil
import tempfile
import unittest

from investigator.runtime import FINGERPRINT_TRANSPORTS, fingerprint, fingerprint_files

ROOT = Path(__file__).resolve().parents[1]


class FingerprintTests(unittest.TestCase):
    def test_adapters_and_nested_packages_are_covered(self):
        _, files = fingerprint_files()
        names = {p.relative_to(ROOT).as_posix() for p in files}
        self.assertIn('scripts/investigator/adapters/microsoft_process.py', names)
        self.assertFalse(any('__pycache__' in n for n in names))

    def test_every_listed_transport_exists(self):
        for name in FINGERPRINT_TRANSPORTS:
            self.assertTrue((ROOT/name).is_file(), name)

    def test_an_adapter_only_change_changes_the_fingerprint(self):
        with tempfile.TemporaryDirectory() as folder:
            copy = Path(folder)
            shutil.copytree(ROOT/'scripts/investigator', copy/'scripts/investigator',
                            ignore=shutil.ignore_patterns('__pycache__'))
            for name in FINGERPRINT_TRANSPORTS:
                (copy/name).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT/name, copy/name)
            before = fingerprint(copy)
            self.assertEqual(before, fingerprint(ROOT))
            adapter = copy/'scripts/investigator/adapters/microsoft_process.py'
            adapter.write_text(adapter.read_text(encoding='utf-8') + '\n# adapter-only change\n', encoding='utf-8')
            self.assertNotEqual(fingerprint(copy), before)

    def test_a_transport_only_change_changes_the_fingerprint(self):
        with tempfile.TemporaryDirectory() as folder:
            copy = Path(folder)
            shutil.copytree(ROOT/'scripts/investigator', copy/'scripts/investigator',
                            ignore=shutil.ignore_patterns('__pycache__'))
            for name in FINGERPRINT_TRANSPORTS:
                (copy/name).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT/name, copy/name)
            before = fingerprint(copy)
            script = copy/'infra/scripts/Read-FabricSqlAggregate.ps1'
            script.write_text(script.read_text(encoding='utf-8-sig') + '\n# change\n', encoding='utf-8')
            self.assertNotEqual(fingerprint(copy), before)


if __name__ == '__main__':
    unittest.main()
