import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from scripts.check_capabilities import check

ROOT = Path(__file__).resolve().parents[1]


class CapabilityPrerequisiteTests(unittest.TestCase):
    def copy_resources(self, destination):
        for directory in ('references', 'evaluations/tasks', 'evaluations/rubrics', 'evaluations/fixtures'):
            shutil.copytree(ROOT / directory, destination / directory,
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        shutil.copyfile(ROOT / 'evaluations/capabilities.json', destination / 'evaluations/capabilities.json')

    def test_complete_registry_is_not_runtime_success(self):
        result = check(ROOT)
        self.assertTrue(result['resources_ready'])
        self.assertEqual(len(result['capabilities']), 13)
        self.assertIn('not runtime success', result['limitations'])

    def test_missing_fixture_and_duplicate_workflow_fail(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.copy_resources(root)
            shutil.rmtree(root / 'evaluations/fixtures/order_flow')
            result = check(root)
            self.assertFalse(result['resources_ready'])
            self.assertTrue(next(row for row in result['capabilities'] if row['id'] == 'feature-tracing')['missing'])
            manifest = json.loads((root / 'evaluations/capabilities.json').read_text())
            manifest[-1] = manifest[0]
            (root / 'evaluations/capabilities.json').write_text(json.dumps(manifest))
            with self.assertRaises(ValueError):
                check(root)

    def test_external_resource_path_cannot_satisfy_prerequisite(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.copy_resources(root)
            manifest = json.loads((root / 'evaluations/capabilities.json').read_text())
            manifest[0]['fixtures'] = ['../../../outside']
            (root / 'evaluations/capabilities.json').write_text(json.dumps(manifest))
            self.assertFalse(check(root)['resources_ready'])
