"""Docker-based, standard-library Python test checks; no host execution fallback."""
import json
import os
import re
import shutil
import subprocess
import tempfile
import threading
import uuid
import base64
import inspect
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, build_opener

from .nvidia import NoRedirect

from .patches import validate_patch
from .workspace import WorkspaceError, ingest_zip
from .discovery import discover_selected_tests

OUTPUT_LIMIT = 32768


def find_docker():
    found = shutil.which('docker')
    if found:
        return found
    if os.name == 'nt':
        candidates = [Path(os.environ.get('LOCALAPPDATA', '')) / 'Programs/DockerDesktop/resources/bin/docker.exe',
                      Path(os.environ.get('ProgramFiles', 'C:/Program Files')) / 'Docker/Docker/resources/bin/docker.exe']
        for path in candidates:
            if path.is_file():
                return str(path)
    return None


HARNESS = inspect.getsource(discover_selected_tests) + r'''
import contextlib, json, os, pathlib, sys, unittest
payload = json.load(sys.stdin)
root = pathlib.Path('/tmp/project')
root.mkdir()
for item in payload:
    path = root / item['path']
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(item['content'], encoding='utf-8')
os.chdir(root)
sys.path.insert(0, str(root))
class Log:
    def __init__(self): self.text = ''
    def write(self, text):
        self.text += text[:max(0, 8000-len(self.text))]
        return len(text)
    def flush(self): pass
log = Log()
with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
    suite = discover_selected_tests(root, [item['path'] for item in payload])
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
passed = result.wasSuccessful() and result.testsRun > len(result.skipped)
print(json.dumps({'passed': passed, 'tests_run': result.testsRun, 'skipped': len(result.skipped),
                  'failures': len(result.failures), 'errors': len(result.errors), 'log': log.text}))
sys.exit(0 if passed else 1)
'''


def _bounded(command, env, data=b'', timeout=30):
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, env=env)
    chunks, size, exceeded = [], [0], threading.Event()
    def read():
        while True:
            chunk = process.stdout.read(4096)
            if not chunk:
                break
            size[0] += len(chunk)
            if size[0] > OUTPUT_LIMIT:
                exceeded.set()
                process.kill()
                break
            chunks.append(chunk)
    def write():
        try:
            process.stdin.write(data)
        except (BrokenPipeError, OSError, ValueError):
            pass
        finally:
            try:
                process.stdin.close()
            except (BrokenPipeError, OSError, ValueError):
                pass
    reader = threading.Thread(target=read, daemon=True)
    writer = threading.Thread(target=write, daemon=True)
    reader.start()
    writer.start()
    timed_out = False
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        process.kill()
        process.wait(timeout=5)
    reader.join(timeout=5)
    writer.join(timeout=5)
    process.stdout.close()
    return {'returncode': process.returncode, 'output': b''.join(chunks).decode('utf-8', errors='replace'),
            'timed_out': timed_out, 'output_exceeded': exceeded.is_set()}


def _run_files(files, docker, image, config, *, execute=_bounded):
    # Do not propagate provider/session/GitHub credentials, Docker contexts or registry credentials.
    env = {key: value for key, value in os.environ.items()
           if key.upper() in {'PATH', 'SYSTEMROOT', 'WINDIR', 'TEMP', 'TMP'}}
    host = 'npipe:////./pipe/docker_engine' if os.name == 'nt' else 'unix:///var/run/docker.sock'
    prefix = [docker, '--config', config, '--host', host]
    name = 'devtwin-' + uuid.uuid4().hex
    command = prefix + ['run', '--rm', '--pull=never', '--name', name, '--network=none',
                        '--read-only', '--cap-drop=ALL', '--security-opt=no-new-privileges',
                        '--pids-limit=64', '--memory=256m', '--memory-swap=256m', '--cpus=1',
                        '--user=65534:65534', '--tmpfs', '/tmp:rw,noexec,nosuid,size=16m,mode=1777',
                        '--log-driver=none', '--interactive', '--entrypoint', 'python', image,
                        '-I', '-S', '-B', '-c', HARNESS]
    cleanup = None
    try:
        result = execute(command, env, json.dumps(files).encode(), timeout=30)
    except (OSError, subprocess.SubprocessError):
        return {'status': 'blocked', 'reason': 'Docker execution could not start'}
    finally:
        try:
            cleanup = execute(prefix + ['rm', '-f', name], env, timeout=5)
        except (OSError, subprocess.SubprocessError):
            pass
    if cleanup is None or cleanup['timed_out'] or (cleanup['returncode'] != 0 and 'No such container' not in cleanup['output']):
        return {'status': 'blocked', 'reason': 'Container cleanup could not be confirmed'}
    if result['timed_out'] or result['output_exceeded']:
        return {'status': 'blocked', 'reason': 'Container time or output limit exceeded'}
    try:
        report = json.loads(result['output'])
        if not isinstance(report, dict) or set(report) != {'passed', 'tests_run', 'skipped', 'failures', 'errors', 'log'}:
            raise ValueError()
        counts = [report[key] for key in ('tests_run', 'skipped', 'failures', 'errors')]
        if (any(type(value) is not int or value < 0 for value in counts)
                or not isinstance(report.get('log'), str) or len(report['log']) > 8000
                or type(report['passed']) is not bool or report['skipped'] > report['tests_run']
                or report['failures'] + report['errors'] > report['tests_run']):
            raise ValueError()
        passed = (result['returncode'] == 0 and report['tests_run'] > report['skipped']
                  and report['failures'] == 0 and report['errors'] == 0 and report.get('passed') is True)
        if result['returncode'] not in (0, 1):
            return {'status': 'blocked', 'reason': 'Container runtime did not complete a supported test run'}
        if report['tests_run'] == 0:
            return {'status': 'blocked', 'reason': 'No unittest cases discovered; select test*.py modules containing unittest tests'}
        if report['tests_run'] <= report['skipped']:
            return {'status': 'blocked', 'reason': 'All selected tests were skipped; no test executed'}
    except (ValueError, KeyError, TypeError):
        return {'status': 'blocked', 'reason': 'Container returned no valid test report'}
    report['passed'] = passed
    return {'status': 'passed' if passed else 'failed', 'exit_code': result['returncode'], **report}


def verify_candidate(archive, selected, patch, *, approved=False, execution_approved=False, execute=_bounded):
    if approved is not True or execution_approved is not True:
        raise WorkspaceError('Patch review and isolated execution approval are required')
    original = ingest_zip(archive, selected)
    validate_patch(original, patch)
    docker = find_docker()
    image = os.environ.get('DEVTWIN_RUNNER_IMAGE', '')
    if not docker:
        return {'status': 'blocked', 'reason': 'Docker is unavailable; no project code executed', 'executed_checks': []}
    if not re.fullmatch(r'python@sha256:[0-9a-f]{64}', image):
        return {'status': 'blocked', 'reason': 'Configure a preloaded official Python image by digest', 'executed_checks': []}
    candidate = [{**file, 'content': patch['replacement'] if file['path'] == patch['path'] else file['content']}
                 for file in original]
    with tempfile.TemporaryDirectory(prefix='devtwin-docker-config-') as config:
        baseline = _run_files(original, docker, image, config, execute=execute)
        if baseline['status'] == 'blocked':
            return {'status': 'blocked', 'baseline': baseline, 'executed_checks': ['baseline attempted']}
        after = _run_files(candidate, docker, image, config, execute=execute)
    status = after['status']
    return {'status': status, 'baseline': baseline, 'candidate': after, 'image': image,
            'executed_checks': ['baseline unittest discovery', 'candidate unittest discovery'],
            'observed_failure_resolved': baseline['status'] == 'failed' and status == 'passed',
            'limitations': ['Selected-file standard-library unittest scope only; no dependency installation.',
                            'Basic container execution has been exercised; broader containment and production security auditing remain pending.',
                            'Project tests and their reported claims remain untrusted; passing checks are not proof of correctness.']}


def verify_dispatch(archive, selected, patch, *, approved=False, execution_approved=False):
    endpoint = os.environ.get('DEVTWIN_WORKER_URL', '')
    if not endpoint:
        return verify_candidate(archive, selected, patch, approved=approved, execution_approved=execution_approved)
    if approved is not True or execution_approved is not True:
        raise WorkspaceError('Patch review and isolated execution approval are required')
    validate_patch(ingest_zip(archive, selected), patch)
    if endpoint not in ('http://worker:8766/api/verify', 'http://127.0.0.1:8766/api/verify'):
        raise WorkspaceError('Only the configured local verification worker is supported')
    token = os.environ.get('DEVTWIN_WORKER_TOKEN', '')
    if len(token) < 32 or not token.isascii() or not token.isalnum():
        raise WorkspaceError('Configure a valid backend worker token')
    authority = urlsplit(endpoint).netloc
    data = {'archive': base64.b64encode(archive).decode(), 'selected': selected, 'patch': patch,
            'approved': True, 'execution_approved': True}
    request = Request(endpoint, data=json.dumps(data).encode(), method='POST',
                      headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json',
                               'Host': authority, 'Origin': 'http://' + authority})
    try:
        with build_opener(NoRedirect()).open(request, timeout=120) as response:
            raw = response.read(65537)
        if len(raw) > 65536:
            raise ValueError()
        result = json.loads(raw)
        if not isinstance(result, dict) or result.get('status') not in ('passed', 'failed', 'blocked'):
            raise ValueError()
        if result['status'] != 'blocked':
            # A transport success or bare status is not evidence of test execution.
            for key in ('baseline', 'candidate'):
                report = result.get(key)
                if not isinstance(report, dict) or report.get('status') not in ('passed', 'failed'):
                    raise ValueError()
                counts = [report.get(name) for name in ('tests_run', 'skipped', 'failures', 'errors')]
                if (any(type(value) is not int or value < 0 for value in counts)
                        or counts[0] <= counts[1] or counts[2] + counts[3] > counts[0]
                        or type(report.get('passed')) is not bool
                        or type(report.get('exit_code')) is not int or report['exit_code'] not in (0, 1)
                        or not isinstance(report.get('log'), str) or len(report['log']) > 8000):
                    raise ValueError()
                passed = report['exit_code'] == 0 and counts[2] == counts[3] == 0 and report['passed']
                if (report['status'] == 'passed') != passed:
                    raise ValueError()
            if result['status'] != result['candidate']['status']:
                raise ValueError()
            resolved = result['baseline']['status'] == 'failed' and result['candidate']['status'] == 'passed'
            if type(result.get('observed_failure_resolved')) is not bool or result['observed_failure_resolved'] != resolved:
                raise ValueError()
        return result
    except (HTTPError, URLError, OSError, TimeoutError, ValueError, UnicodeError):
        return {'status': 'blocked', 'reason': 'Local worker unavailable or returned an invalid report', 'executed_checks': []}
