from pathlib import Path
import tempfile
import unittest
import zipfile

from scripts.build_package import build
from scripts.verify_archive import verify

ROOT = Path(__file__).resolve().parents[1]


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.original = self.directory / 'source.zip'
        build(ROOT, self.original)

    def rewrite(self, extra=None, changed=None):
        target = self.directory / 'changed.zip'
        with zipfile.ZipFile(self.original) as source, zipfile.ZipFile(target, 'w') as output:
            for entry in source.infolist():
                data = source.read(entry)
                if changed and entry.filename == changed:
                    data += b'tampered'
                output.writestr(entry, data)
            if extra:
                output.writestr(extra, b'extra')
        return target

    def test_valid_archive(self):
        self.assertTrue(verify(self.original)['valid'])
        self.assertFalse(verify(self.original)['signature_verified'])

    def test_tampering_is_detected(self):
        with self.assertRaisesRegex(ValueError, 'integrity mismatch'):
            verify(self.rewrite(changed='devtwin-engineer/SKILL.md'))

    def test_unlisted_file_is_detected(self):
        with self.assertRaisesRegex(ValueError, 'file list mismatch'):
            verify(self.rewrite(extra='devtwin-engineer/extra.txt'))

    def test_traversal_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unsafe archive path'):
            verify(self.rewrite(extra='devtwin-engineer/../../escape.txt'))
        self.assertFalse((self.directory / 'escape.txt').exists())

    def test_case_collision_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            verify(self.rewrite(extra='devtwin-engineer/skill.md'))

    def test_portable_reserved_filename_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unsafe portable filename'):
            verify(self.rewrite(extra='devtwin-engineer/CON.txt'))

    def test_symlink_archive_entry_is_rejected(self):
        target = self.directory / 'link.zip'
        with zipfile.ZipFile(target, 'w') as archive:
            entry = zipfile.ZipInfo('devtwin-engineer/link')
            entry.create_system = 3
            entry.external_attr = 0o120777 << 16
            archive.writestr(entry, '../../outside')
        with self.assertRaisesRegex(ValueError, 'symlink archive entry'):
            verify(target)
