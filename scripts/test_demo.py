from pathlib import Path
import tempfile
import unittest
from demo import prepare, rehearsal


class DemoTests(unittest.TestCase):
    def test_complete_rehearsal_and_reset(self):
        with tempfile.TemporaryDirectory() as root:
            folder = Path(root) / 'demo'
            result = rehearsal(folder)
            self.assertEqual(result['status'], 'PASSED')
            self.assertEqual(result['reset']['status'], 'READY')
            self.assertFalse(result['external_delivery'])
            self.assertTrue((folder / 'rehearsal.json').is_file())
            self.assertIsNone(result['routing']['approval'])

    def test_existing_folder_is_preserved(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(FileExistsError):
                prepare(Path(root))


if __name__ == '__main__': unittest.main()
