import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ContractFixtureTests(unittest.TestCase):
    def test_api_contract_examples(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'api'
            shutil.copytree(ROOT / 'evaluations/fixtures/api_contract', target)
            result = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-v'],
                                    cwd=target, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('Ran 4 tests', result.stderr)

    def test_offline_dependency_conflict_and_candidate_resolution(self):
        if importlib.util.find_spec('pip') is None:
            self.skipTest('pip unavailable; offline resolver not exercised')
        fixture = ROOT / 'evaluations/fixtures/dependency_conflict'
        spec = importlib.util.spec_from_file_location('synthetic_wheels', fixture / 'wheelhouse.py')
        wheels = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(wheels)
        environment = {key: value for key, value in os.environ.items() if not key.startswith('PIP_')}
        environment['PIP_CONFIG_FILE'] = os.devnull
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            wheels.create(root / 'wheels')
            base = [sys.executable, '-m', 'pip', '--disable-pip-version-check', '--no-input',
                    'install', '--dry-run', '--ignore-installed', '--no-index', '--no-cache-dir',
                    '--find-links', str(root / 'wheels')]
            before = subprocess.run(base + ['-r', str(fixture / 'requirements.txt')], env=environment,
                                    capture_output=True, text=True, timeout=30)
            self.assertNotEqual(before.returncode, 0)
            self.assertIn('ResolutionImpossible', before.stderr)
            candidate = root / 'candidate.txt'
            candidate.write_text('devtwin-demo-core==1.0\ndevtwin-demo-addon==1.0\n')
            report = root / 'report.json'
            after = subprocess.run(base + ['--report', str(report), '-r', str(candidate)], env=environment,
                                   capture_output=True, text=True, timeout=30)
            self.assertEqual(after.returncode, 0, after.stderr)
            selected = {entry['metadata']['name']: entry['metadata']['version']
                        for entry in json.loads(report.read_text())['install']}
            self.assertEqual(selected, {'devtwin-demo-core': '1.0', 'devtwin-demo-addon': '1.0'})
