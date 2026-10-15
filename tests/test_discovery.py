import importlib
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from backend.discovery import discover_selected_tests


class DiscoveryTests(unittest.TestCase):
    def test_namespace_directories_and_duplicate_basenames_run_once(self):
        before = set(sys.modules)
        try:
            with tempfile.TemporaryDirectory() as folder, patch.object(sys, 'path', sys.path.copy()):
                root = Path(folder)
                paths = ['fixture_a/test_shared.py', 'fixture_b/test_shared.py']
                for name in paths:
                    path = root / name
                    path.parent.mkdir(parents=True)
                    path.write_text('import unittest\nclass Contract(unittest.TestCase):\n def test_contract(self): self.assertEqual(2 + 2, 4)\n')
                (root / 'unselected_test.py').write_text('raise RuntimeError("must not import")\n')
                importlib.invalidate_caches()
                suite = discover_selected_tests(root, paths + ['notes.md'])
                result = unittest.TestResult()
                suite.run(result)
                self.assertEqual(result.testsRun, 2)
                self.assertTrue(result.wasSuccessful())
        finally:
            for name in set(sys.modules) - before:
                if name.startswith(('fixture_a', 'fixture_b')):
                    sys.modules.pop(name, None)

    def test_import_failure_is_evidence_not_an_empty_pass(self):
        before = set(sys.modules)
        try:
            with tempfile.TemporaryDirectory() as folder, patch.object(sys, 'path', sys.path.copy()):
                root = Path(folder)
                (root / 'fixture_failure').mkdir()
                (root / 'fixture_failure/test_import.py').write_text('import devtwin_missing_dependency\n')
                result = unittest.TestResult()
                discover_selected_tests(root, ['fixture_failure/test_import.py']).run(result)
                self.assertEqual(result.testsRun, 1)
                self.assertEqual(len(result.errors), 1)
        finally:
            for name in set(sys.modules) - before:
                if name.startswith('fixture_failure'):
                    sys.modules.pop(name, None)
