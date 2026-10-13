import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(all(importlib.util.find_spec(name) for name in ('fastapi', 'httpx')),
                     'Optional HTTP fixture requires its isolated FastAPI/httpx environment')
class FastApiFixtureTests(unittest.TestCase):
    def test_http_failure_candidate_and_preservation(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'target'
            shutil.copytree(ROOT / 'evaluations/fixtures/fastapi_checkout', target)
            protected = (target / 'test_http.py').read_bytes()
            note = target / 'user-note.txt'
            note.write_bytes(b'Keep unrelated user work\r\n')
            def run():
                return subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-v'],
                                      cwd=target, capture_output=True, text=True, timeout=30)
            broken = run()
            self.assertNotEqual(broken.returncode, 0)
            self.assertIn('500 != 200', broken.stderr)
            self.assertIn('FAILED (failures=2)', broken.stderr)
            source = target / 'app.py'
            original = source.read_text()
            source.write_text(original.replace('request.subtotal - request.discount',
                                              'request.subtotal'), encoding='utf-8')
            regression = run()
            self.assertNotEqual(regression.returncode, 0)
            self.assertIn('test_explicit_discounts_and_floor', regression.stderr)
            source.write_text(original.replace(
                'request.subtotal - request.discount',
                'request.subtotal - (0 if request.discount is None else request.discount)'),
                encoding='utf-8')
            candidate = run()
            self.assertEqual(candidate.returncode, 0, candidate.stderr)
            self.assertIn('Ran 5 tests', candidate.stderr)
            self.assertEqual((target / 'test_http.py').read_bytes(), protected)
            self.assertEqual(note.read_bytes(), b'Keep unrelated user work\r\n')
