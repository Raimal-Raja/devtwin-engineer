import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('package_validator', ROOT / 'scripts/validate_package.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'package'
        self.root.mkdir()
        for name in ('references', 'templates', 'scripts'):
            shutil.copytree(ROOT / name, self.root / name)
        shutil.copyfile(ROOT / 'SKILL.md', self.root / 'SKILL.md')
        (self.root / 'docs').mkdir()

    def test_duplicate_empty_and_structured_metadata_rejected(self):
        for metadata in ('name: good\nname: other\ndescription: test',
                         'name: good\ndescription:   ',
                         'name: good\ndescription: |\n  test',
                         'name: good\ndescription: "unterminated',
                         'name: good\ndescription: null',
                         'name: good\ndescription: 123',
                         'name: good\ndescription: "bad\\q"'):
            with self.subTest(metadata=metadata):
                (self.root / 'SKILL.md').write_text(f'---\n{metadata}\n---\n', encoding='utf-8')
                self.assertTrue(validator.validate(self.root))

    def test_missing_document_reference_detected(self):
        (self.root / 'docs/guide.md').write_text('[missing](not-there.md)')
        errors = validator.validate(self.root)
        self.assertTrue(any('docs/guide.md: missing reference' in e for e in errors))

    def test_encoded_escape_and_unsupported_scheme_rejected(self):
        (self.root / 'README.md').write_text('[escape](%2e%2e/outside.md)\n[script](javascript:alert)')
        errors = validator.validate(self.root)
        self.assertTrue(any('reference escapes' in e for e in errors))
        self.assertTrue(any('unsupported reference scheme' in e for e in errors))

    def test_document_size_and_encoding_errors(self):
        (self.root / 'docs/large.md').write_bytes(b'x' * (validator.MAX_BYTES + 1))
        (self.root / 'docs/invalid.md').write_bytes(b'\xff')
        errors = validator.validate(self.root)
        self.assertTrue(any('size limit exceeded' in e for e in errors))
        self.assertTrue(any('UnicodeDecodeError' in e for e in errors))

    def test_quoted_metadata_spaces_and_fenced_examples(self):
        (self.root / 'SKILL.md').write_text('---\nname: "good-name"\ndescription: "Useful workflow"\n---\n')
        (self.root / 'docs/a b.md').write_text('A guide')
        (self.root / 'README.md').write_text('[guide](<docs/a b.md>)\n```md\n[example](missing.md)\n```\n')
        self.assertEqual(validator.validate(self.root), [])

    def test_missing_linked_helper_detected(self):
        (self.root / 'scripts/inspect_changes.py').unlink()
        self.assertTrue(any('inspect_changes.py' in e for e in validator.validate(self.root)))

    def test_document_limit_is_not_reported_as_success(self):
        with patch.object(validator, 'MAX_DOCUMENTS', 1):
            self.assertTrue(any('validation incomplete' in e for e in validator.validate(self.root)))

    def test_symlink_document_rejected_when_available(self):
        outside = self.root.parent / 'outside.md'
        outside.write_text('private')
        try:
            (self.root / 'docs/link.md').symlink_to(outside)
        except OSError as exc:
            self.skipTest(f'Symlink creation unavailable: {type(exc).__name__}')
        self.assertTrue(any('unsafe document path' in e for e in validator.validate(self.root)))
