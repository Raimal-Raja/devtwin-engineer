from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class OrderFixtureTests(unittest.TestCase):
    def test_tracing_fixture_behavior_contracts(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'orders'
            shutil.copytree(ROOT / 'evaluations/fixtures/order_flow', target)
            result = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-v'],
                                    cwd=target, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('Ran 6 tests', result.stderr)
