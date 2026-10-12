import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('validator', ROOT / 'scripts/validate_package.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class FoundationTests(unittest.TestCase):
    def test_package(self):
        self.assertEqual(validator.validate(ROOT), [])

    def test_missing_package(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertTrue(validator.validate(folder))

    def test_broken_reference_and_metadata(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name in ('references', 'templates'):
                shutil.copytree(ROOT / name, root / name)
            (root / 'SKILL.md').write_text('---\nname: Bad Name\n---\n[x](missing.md)\n', encoding='utf-8')
            errors = validator.validate(root)
            self.assertTrue(any('invalid name' in e for e in errors))
            self.assertTrue(any('missing description' in e for e in errors))
            self.assertTrue(any('missing reference' in e for e in errors))

    def test_reference_correction_and_preserved_user_work(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'checkout'
            shutil.copytree(ROOT / 'evaluations/fixtures/checkout', target)
            note = target / 'user-note.txt'
            original = b'Unrelated user work\r\n'
            note.write_bytes(original)
            command = [sys.executable, '-m', 'unittest', 'discover', '-v']
            before = subprocess.run(command, cwd=target, capture_output=True, text=True, timeout=30)
            self.assertNotEqual(before.returncode, 0)
            self.assertIn('TypeError', before.stderr)
            source = target / 'checkout.py'
            source.write_text(source.read_text().replace('subtotal - discount', 'subtotal - (0 if discount is None else discount)'), encoding='utf-8')
            after = subprocess.run(command, cwd=target, capture_output=True, text=True, timeout=30)
            self.assertEqual(after.returncode, 0, after.stderr)
            self.assertIn('Ran 5 tests', after.stderr)
            self.assertEqual(note.read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
