import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from scripts.build_workspace import FILES, build

ROOT = Path(__file__).resolve().parents[1]


class WorkspaceBuildTests(unittest.TestCase):
    def test_reproducible_manifest_and_private_file_exclusion(self):
        with tempfile.TemporaryDirectory() as folder:
            first, second = Path(folder) / 'first.zip', Path(folder) / 'second.zip'
            build(ROOT, first)
            build(ROOT, second)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            with zipfile.ZipFile(first) as archive:
                prefix = 'devtwin-workspace/'
                names = {name.removeprefix(prefix) for name in archive.namelist()}
                self.assertEqual(names, set(FILES) | {'manifest.json'})
                self.assertNotIn('.env.docker', names)
                self.assertFalse(any('.workspaces' in name or '__pycache__' in name for name in names))
                manifest = json.loads(archive.read(prefix + 'manifest.json'))['files']
                for name in FILES:
                    content = archive.read(prefix + name)
                    self.assertEqual(manifest[name]['bytes'], len(content))
                    self.assertEqual(manifest[name]['sha256'], hashlib.sha256(content).hexdigest())

    def test_existing_output_and_incomplete_source_are_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'keep.zip'
            output.write_bytes(b'user data')
            with self.assertRaises(ValueError):
                build(ROOT, output)
            self.assertEqual(output.read_bytes(), b'user data')
            fresh = Path(folder) / 'missing.zip'
            with self.assertRaises(ValueError):
                build(folder, fresh)
            self.assertFalse(fresh.exists())


if __name__ == '__main__':
    unittest.main()
