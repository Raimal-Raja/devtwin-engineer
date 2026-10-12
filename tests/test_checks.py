import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class TestWorkerTests(unittest.TestCase):
    def run_worker(self, source):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'tests').mkdir()
            if source:
                (root / 'tests/test_synthetic.py').write_text(source, encoding='utf-8')
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/check_project.py'),
                                     str(root), '--test-worker'], capture_output=True, text=True, timeout=30)
            return result.returncode, json.loads(result.stdout)

    def test_failed_test_is_not_success(self):
        status, result = self.run_worker('import unittest\nclass T(unittest.TestCase):\n def test_failure(self): self.assertEqual(1, 2)\n')
        self.assertEqual(status, 1)
        self.assertFalse(result['passed'])
        self.assertEqual(result['failures'], 1)

    def test_empty_or_all_skipped_suite_is_not_success(self):
        status, result = self.run_worker('')
        self.assertEqual(status, 1)
        self.assertEqual(result['tests_run'], 0)
        status, result = self.run_worker('import unittest\n@unittest.skip("missing tool")\nclass T(unittest.TestCase):\n def test_skip(self): pass\n')
        self.assertEqual(status, 1)
        self.assertEqual(result['skipped'], 1)

    def test_test_output_is_captured_in_json_log(self):
        status, result = self.run_worker('import unittest\nprint("import output")\nclass T(unittest.TestCase):\n def test_print(self): print("test output")\n')
        self.assertEqual(status, 0)
        self.assertIn('import output', result['log'])
        self.assertIn('test output', result['log'])
