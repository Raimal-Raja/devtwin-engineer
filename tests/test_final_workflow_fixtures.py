from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class FinalWorkflowFixtureTests(unittest.TestCase):
    def test_performance_contract_and_work_reduction(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'sales'
            shutil.copytree(ROOT / 'evaluations/fixtures/performance_review', target)
            result = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-v'],
                                    cwd=target, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('Ran 3 tests', result.stderr)

    def test_documented_failures_and_corrected_command(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'docs'
            shutil.copytree(ROOT / 'evaluations/fixtures/documentation_review', target)
            missing = subprocess.run([sys.executable, '-B', 'runner.py', '--amount', '12.5'],
                                     cwd=target, capture_output=True, text=True, timeout=30)
            bad_flag = subprocess.run([sys.executable, '-B', 'cli.py', '--total', '12.5'],
                                      cwd=target, capture_output=True, text=True, timeout=30)
            unknown_flag = subprocess.run([sys.executable, '-B', 'cli.py', '--amount', '12.5', '--total', '12.5'],
                                          cwd=target, capture_output=True, text=True, timeout=30)
            corrected = subprocess.run([sys.executable, '-B', 'cli.py', '--amount', '12.5'],
                                       cwd=target, capture_output=True, text=True, timeout=30)
            self.assertEqual(missing.returncode, 2)
            self.assertIn("can't open file", missing.stderr)
            self.assertEqual(bad_flag.returncode, 2)
            self.assertIn('--amount', bad_flag.stderr)
            self.assertEqual(unknown_flag.returncode, 2)
            self.assertIn('unrecognized arguments: --total', unknown_flag.stderr)
            self.assertEqual(corrected.returncode, 0, corrected.stderr)
            self.assertEqual(corrected.stdout.strip(), '12.50')
