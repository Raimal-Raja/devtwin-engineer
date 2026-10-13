from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ReviewFixtureTests(unittest.TestCase):
    def run_fixture(self, name, count):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / name
            shutil.copytree(ROOT / 'evaluations/fixtures' / name, target)
            result = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-v'],
                                    cwd=target, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(f'Ran {count} tests', result.stderr)

    def test_migration_existing_data_and_transaction_behavior(self):
        self.run_fixture('migration_review', 5)

    def test_ownership_denial_and_legitimate_access(self):
        self.run_fixture('ownership_review', 6)
