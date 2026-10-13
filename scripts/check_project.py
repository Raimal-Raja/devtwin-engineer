"""Run local development gates against trusted project source; no network or Git writes."""
import argparse
import contextlib
import io
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

try:
    from .build_package import build
    from .verify_archive import verify
    from .validate_package import validate
except ImportError:
    from build_package import build
    from verify_archive import verify
    from validate_package import validate


def test_worker(root):
    root = Path(root).resolve()
    if not (root / 'tests').is_dir():
        return {'passed': False, 'error': 'Missing test directory', 'tests_run': 0}
    sys.path.insert(0, str(root))
    output = io.StringIO()
    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
        suite = unittest.defaultTestLoader.discover(str(root / 'tests'))
        result = unittest.TextTestRunner(stream=output, verbosity=2).run(suite)
    return {'passed': result.wasSuccessful() and result.testsRun > len(result.skipped),
            'tests_run': result.testsRun, 'skipped': len(result.skipped),
            'skip_reasons': [{'test': str(test), 'reason': reason} for test, reason in result.skipped],
            'failures': len(result.failures), 'errors': len(result.errors), 'log': output.getvalue()}


def web_tests(root):
    """Run every declared web suite; missing Node/tests and all-skipped suites fail."""
    root = Path(root).resolve()
    suites = sorted((root / 'web').rglob('*.test.mjs'))
    if not suites:
        return {'passed': False, 'error': 'No web test suites found', 'tests_run': 0}
    node = shutil.which('node')
    if not node:
        return {'passed': False, 'error': 'Node.js is unavailable', 'tests_run': 0}
    try:
        result = subprocess.run([node, '--test', '--test-reporter=tap', *map(str, suites)],
                                cwd=root, capture_output=True, text=True, encoding='utf-8',
                                errors='replace', timeout=60)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {'passed': False, 'error': type(exc).__name__, 'tests_run': 0}
    counts = {key: int(value) for key, value in re.findall(
        r'^# (tests|pass|fail|skipped|cancelled) (\d+)\s*$', result.stdout, re.MULTILINE)}
    # Node reports an otherwise empty test file as a passing file-level case.
    # Conservatively reject those named file results instead of counting them as tests.
    def normalized(name):
        return re.sub(r'/+', '/', name.replace('\\', '/')).casefold()
    suite_names = {normalized(str(name)) for suite in suites
                   for name in (suite, suite.relative_to(root))}
    empty_suites = [name for name in re.findall(r'^# Subtest: (.+)$', result.stdout, re.MULTILINE)
                    if normalized(name) in suite_names]
    return {'passed': result.returncode == 0 and counts.get('pass', 0) > 0 and not empty_suites,
            'exit_code': result.returncode, 'tests_run': counts.get('tests', 0),
            'passed_tests': counts.get('pass', 0), 'failures': counts.get('fail', 0),
            'skipped': counts.get('skipped', 0), 'cancelled': counts.get('cancelled', 0),
            'empty_suites': empty_suites,
            'log': result.stdout + result.stderr}


def check(root):
    root = Path(root).resolve()
    gates = []
    errors = validate(root)
    gates.append({'gate': 'package', 'passed': not errors, 'errors': errors})
    if errors:
        return {'passed': False, 'gates': gates}
    command = [sys.executable, '-B', str(Path(__file__).resolve()), str(root), '--test-worker']
    worker = subprocess.run(command, cwd=root, capture_output=True, text=True,
                            encoding='utf-8', errors='replace', timeout=120)
    if worker.returncode not in (0, 1):
        raise ValueError('Test worker could not complete')
    tests = json.loads(worker.stdout)
    gates.append({'gate': 'tests', **tests})
    if (root / 'web').is_dir():
        gates.append({'gate': 'web_tests', **web_tests(root)})
    if any(not gate['passed'] for gate in gates):
        return {'passed': False, 'gates': gates}
    with tempfile.TemporaryDirectory() as folder:
        archive = Path(folder) / 'skill.zip'
        built = build(root, archive)
        verified = verify(archive)
        gates.append({'gate': 'archive', 'passed': verified['valid'],
                      'files': verified['files'], 'sha256': built['sha256']})
    return {'passed': True, 'gates': gates,
            'limitations': 'Local development gates only; skipped tests and runtime/release gates remain separate'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--test-worker', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    try:
        result = test_worker(args.root) if args.test_worker else check(args.root)
    except (OSError, ValueError, subprocess.TimeoutExpired, zipfile.BadZipFile) as exc:
        result = {'passed': False, 'error': type(exc).__name__}
    print(json.dumps(result, indent=2))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
