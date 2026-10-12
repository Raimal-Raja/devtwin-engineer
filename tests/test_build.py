import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import zipfile

from scripts import build_package

ROOT = Path(__file__).resolve().parents[1]


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)

    def test_reproducible_archive_extraction_and_integrity(self):
        first = self.directory / 'first.zip'
        second = self.directory / 'second.zip'
        build_package.build(ROOT, first)
        build_package.build(ROOT, second)
        self.assertEqual(first.read_bytes(), second.read_bytes())
        with zipfile.ZipFile(first) as archive:
            names = archive.namelist()
            self.assertTrue(all(name.startswith('devtwin-engineer/') for name in names))
            self.assertFalse(any('/evaluations/' in name or '/.workspaces/' in name or '/.git/' in name for name in names))
            manifest = json.loads(archive.read('devtwin-engineer/manifest.json'))
            for name, expected in manifest['files'].items():
                content = archive.read('devtwin-engineer/' + name)
                self.assertEqual(hashlib.sha256(content).hexdigest(), expected['sha256'])
                self.assertEqual(len(content), expected['bytes'])
            archive.extractall(self.directory / 'extracted')
        self.assertEqual(build_package.validate(self.directory / 'extracted/devtwin-engineer'), [])

    def test_existing_output_is_preserved(self):
        output = self.directory / 'existing.zip'
        output.write_bytes(b'user file')
        with self.assertRaises(ValueError):
            build_package.build(ROOT, output)
        self.assertEqual(output.read_bytes(), b'user file')

    def fixture(self):
        root = self.directory / 'source'
        root.mkdir()
        entries = json.loads((ROOT / 'package-files.json').read_text())
        for name in [*entries, 'package-files.json']:
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        return root, entries

    def test_unsafe_allowlist_is_rejected(self):
        root, entries = self.fixture()
        (root / 'package-files.json').write_text(json.dumps(entries + ['../outside']))
        with self.assertRaisesRegex(ValueError, 'Unsafe allowlist'):
            build_package.build(root, self.directory / 'bad.zip')

    def test_missing_selected_dependency_is_rejected(self):
        root, entries = self.fixture()
        (root / 'package-files.json').write_text(json.dumps([e for e in entries if e != 'scripts/inspect_changes.py']))
        with self.assertRaisesRegex(ValueError, 'Selected package validation failed'):
            build_package.build(root, self.directory / 'bad.zip')
