import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from scripts.check_project import check, web_tests

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


class WebGateTests(unittest.TestCase):
    def run_web(self, source):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'web').mkdir()
            if source is not None:
                (root / 'web/check.test.mjs').write_text(source, encoding='utf-8')
            return web_tests(root)

    def test_web_failure_fails_combined_project_gate(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'web').mkdir()
            (root / 'web/failure.test.mjs').write_text(
                "import {test} from 'node:test'; import assert from 'node:assert/strict'; "
                "test('regression',()=>assert.equal(1,2));", encoding='utf-8')
            worker = subprocess.CompletedProcess([], 0, json.dumps({'passed': True, 'tests_run': 1}))
            # Isolate the gate aggregation from package/Python checks; execute real Node tests.
            import scripts.check_project as checker
            real_run = subprocess.run
            def run(command, **kwargs):
                return worker if '--test-worker' in command else real_run(command, **kwargs)
            with patch.object(checker, 'validate', return_value=[]), patch.object(checker.subprocess, 'run', side_effect=run):
                result = check(root)
            self.assertFalse(result['passed'])
            self.assertEqual(result['gates'][-1]['gate'], 'web_tests')
            self.assertEqual(result['gates'][-1]['failures'], 1)

    def test_passing_web_tests_count_executed_cases(self):
        result = self.run_web("import {test} from 'node:test'; test('works',()=>{});")
        self.assertTrue(result['passed'], result)
        self.assertEqual(result['tests_run'], 1)
        self.assertEqual(result['passed_tests'], 1)

    def test_empty_and_all_skipped_web_suites_fail(self):
        self.assertFalse(self.run_web(None)['passed'])
        self.assertFalse(self.run_web('')['passed'])
        self.assertFalse(self.run_web('// only a comment')['passed'])
        result = self.run_web("import {test} from 'node:test'; test.skip('missing tool',()=>{});")
        self.assertFalse(result['passed'])
        self.assertEqual(result['skipped'], 1)

    def test_missing_node_is_an_explicit_failure(self):
        with patch('scripts.check_project.shutil.which', return_value=None):
            result = self.run_web("import {test} from 'node:test'; test('works',()=>{});")
        self.assertFalse(result['passed'])
        self.assertEqual(result['error'], 'Node.js is unavailable')

    def test_empty_file_cannot_hide_beside_passing_tests(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'web').mkdir()
            (root / 'web/empty.test.mjs').write_text('// no tests', encoding='utf-8')
            (root / 'web/real.test.mjs').write_text(
                "import {test} from 'node:test'; test('works',()=>{});", encoding='utf-8')
            result = web_tests(root)
            self.assertFalse(result['passed'])
            self.assertEqual(len(result['empty_suites']), 1)
