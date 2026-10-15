import hashlib
import io
import json
import os
import sys
import unittest
from unittest.mock import Mock, patch
import zipfile

from backend.runner import _bounded, verify_candidate, verify_dispatch
from backend.workspace import WorkspaceError


class RunnerTests(unittest.TestCase):
    def setUp(self):
        data = io.BytesIO()
        with zipfile.ZipFile(data, 'w') as archive:
            archive.writestr('app.py', 'value = 0\n')
            archive.writestr('test_app.py', 'import unittest\n')
        self.archive = data.getvalue()
        self.selected = ['app.py', 'test_app.py']
        self.patch = {'path': 'app.py', 'base_sha256': hashlib.sha256(b'value = 0\n').hexdigest(),
                      'replacement': 'value = 1\n'}
        env = patch.dict(os.environ, {'DEVTWIN_RUNNER_IMAGE': 'python@sha256:' + 'a' * 64,
                                      'NVIDIA_API_KEY': 'should-never-reach-runner',
                                      'OPENROUTER_API_KEY': 'should-never-reach-runner',
                                      'DEVTWIN_SESSION_TOKEN': 'should-never-reach-runner',
                                      'DEVTWIN_GITHUB_TOKEN': 'should-never-reach-runner'})
        env.start()
        self.addCleanup(env.stop)

    def report(self, passed=True, count=2, skipped=0):
        return {'returncode': 0 if passed else 1, 'timed_out': False, 'output_exceeded': False,
                'output': json.dumps({'passed': passed, 'tests_run': count, 'skipped': skipped,
                                      'failures': 0 if passed else 1, 'errors': 0, 'log': 'synthetic results'})}

    def cleanup(self):
        return {'returncode': 0, 'timed_out': False, 'output_exceeded': False, 'output': ''}

    def verify(self, execute):
        with patch('backend.runner.shutil.which', return_value='docker'):
            return verify_candidate(self.archive, self.selected, self.patch, approved=True,
                                    execution_approved=True, execute=execute)

    def test_missing_docker_blocks_without_execution(self):
        execute = Mock()
        with patch('backend.runner.find_docker', return_value=None):
            result = verify_candidate(self.archive, self.selected, self.patch, approved=True,
                                      execution_approved=True, execute=execute)
        self.assertEqual(result['status'], 'blocked')
        self.assertEqual(result['executed_checks'], [])
        execute.assert_not_called()

    def test_approval_and_image_are_required(self):
        execute = Mock()
        with self.assertRaises(WorkspaceError):
            verify_candidate(self.archive, self.selected, self.patch, execute=execute)
        with patch.dict(os.environ, {'DEVTWIN_RUNNER_IMAGE': 'python:latest'}):
            self.assertEqual(self.verify(execute)['status'], 'blocked')
        execute.assert_not_called()

    def test_original_candidate_and_container_controls(self):
        execute = Mock(side_effect=[self.report(False), self.cleanup(), self.report(), self.cleanup()])
        result = self.verify(execute)
        self.assertEqual(result['status'], 'passed')
        self.assertTrue(result['observed_failure_resolved'])
        before, after = execute.call_args_list[0], execute.call_args_list[2]
        command, env, payload = before.args
        for flag in ('--network=none', '--read-only', '--cap-drop=ALL', '--security-opt=no-new-privileges',
                     '--pids-limit=64', '--memory=256m', '--pull=never', '--log-driver=none'):
            self.assertIn(flag, command)
        self.assertNotIn('--mount', command)
        self.assertNotIn('should-never-reach-runner', str(env))
        self.assertIn('value = 0', payload.decode())
        self.assertIn('value = 1', after.args[2].decode())
        self.assertEqual(json.loads(payload)[1]['content'], json.loads(after.args[2])[1]['content'])
        self.assertIn('rm', execute.call_args_list[1].args[0])

    def test_timeout_output_limit_empty_suite_and_bad_protocol_block(self):
        for report in ({**self.report(), 'timed_out': True}, {**self.report(), 'output_exceeded': True},
                       self.report(count=0), self.report(count=2, skipped=2),
                       {**self.report(), 'output': '{"status":"passed"}'}):
            execute = Mock(side_effect=[report, self.cleanup()])
            self.assertEqual(self.verify(execute)['status'], 'blocked')
            self.assertEqual(execute.call_count, 2)

    def test_cleanup_failure_blocks_result(self):
        execute = Mock(side_effect=[self.report(), {**self.cleanup(), 'returncode': 1, 'output': 'daemon unavailable'}])
        self.assertEqual(self.verify(execute)['status'], 'blocked')

    def test_candidate_failure_is_not_reported_as_repair(self):
        execute = Mock(side_effect=[self.report(), self.cleanup(), self.report(False), self.cleanup()])
        result = self.verify(execute)
        self.assertEqual(result['status'], 'failed')
        self.assertFalse(result['observed_failure_resolved'])

    def test_bounded_process_stops_excess_output_and_timeout(self):
        normal = _bounded([sys.executable, '-c', 'print("ok")'], {}, timeout=5)
        self.assertEqual(normal['output'].strip(), 'ok')
        excessive = _bounded([sys.executable, '-c', 'print("x"*100000)'], {}, timeout=5)
        self.assertTrue(excessive['output_exceeded'])
        timed = _bounded([sys.executable, '-c', 'import time; time.sleep(10)'], {}, timeout=0.1)
        self.assertTrue(timed['timed_out'])

    def test_private_worker_request_uses_separate_token_and_no_redirects(self):
        with patch.dict(os.environ, {'DEVTWIN_WORKER_URL': 'http://worker:8766/api/verify',
                                    'DEVTWIN_WORKER_TOKEN': 'b' * 64}), patch('backend.runner.build_opener') as factory:
            factory.return_value.open.return_value = io.BytesIO(b'{"status":"blocked","reason":"synthetic"}')
            result = verify_dispatch(self.archive, self.selected, self.patch, approved=True, execution_approved=True)
            self.assertEqual(result['status'], 'blocked')
            request = factory.return_value.open.call_args.args[0]
            self.assertEqual(request.full_url, 'http://worker:8766/api/verify')
            self.assertEqual(request.get_header('Authorization'), 'Bearer ' + 'b' * 64)
            self.assertNotIn('should-never-reach-runner', request.data.decode())

    def test_worker_destination_and_execution_approval_cannot_be_bypassed(self):
        with patch.dict(os.environ, {'DEVTWIN_WORKER_URL': 'https://evil.example/verify'}), patch('backend.runner.build_opener') as factory:
            with self.assertRaises(WorkspaceError):
                verify_dispatch(self.archive, self.selected, self.patch, approved=True, execution_approved=True)
            factory.assert_not_called()

        with patch.dict(os.environ, {'DEVTWIN_WORKER_URL': 'http://worker:8766/api/verify'}):
            with self.assertRaises(WorkspaceError):
                verify_dispatch(self.archive, self.selected, self.patch)

    def test_worker_cannot_claim_pass_without_executed_test_evidence(self):
        env = {'DEVTWIN_WORKER_URL': 'http://worker:8766/api/verify', 'DEVTWIN_WORKER_TOKEN': 'b' * 64}
        report = {'status': 'passed', 'tests_run': 1, 'skipped': 0, 'failures': 0,
                  'errors': 0, 'passed': True, 'exit_code': 0, 'log': 'synthetic'}
        valid = {'status': 'passed', 'baseline': report, 'candidate': report,
                 'observed_failure_resolved': False}
        for answer, expected in (({'status': 'passed'}, 'blocked'),
                                 ({**valid, 'observed_failure_resolved': True}, 'blocked'),
                                 ({**valid, 'candidate': {**report, 'skipped': 1}}, 'blocked'),
                                 (valid, 'passed')):
            with patch.dict(os.environ, env), patch('backend.runner.build_opener') as factory:
                factory.return_value.open.return_value = io.BytesIO(json.dumps(answer).encode())
                result = verify_dispatch(self.archive, self.selected, self.patch, approved=True, execution_approved=True)
                self.assertEqual(result['status'], expected)
