import hashlib
import io
import unittest
from unittest.mock import Mock
import zipfile

from backend.repair import repair
from backend.providers import ProviderError
from backend.workspace import WorkspaceError


class RepairTests(unittest.TestCase):
    def setUp(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as archive:
            archive.writestr('app.py', 'value = 0\n')
            archive.writestr('test_app.py', 'import unittest\n')
        self.archive = buffer.getvalue()
        self.selected = ['app.py', 'test_app.py']
        self.patch = {'path': 'app.py', 'base_sha256': hashlib.sha256(b'value = 0\n').hexdigest(),
                      'replacement': 'value = 1\n'}
        self.analyze = Mock(return_value={'status': 'unverified_source_analysis'})
        self.propose = Mock(return_value={'patch': self.patch})
        self.verify = Mock(return_value={'status': 'passed'})

    def run_loop(self, **kwargs):
        return repair(self.archive, self.selected, 'Fix the value', 'implementation',
                      analyze=self.analyze, propose_patch=self.propose, verify=self.verify, **kwargs)

    def test_consent_and_attempt_limit_before_model_calls(self):
        for kwargs in ({}, {'loop_approved': True, 'max_attempts': 3},
                       {'loop_approved': True, 'max_attempts': True}):
            with self.assertRaises(WorkspaceError):
                self.run_loop(**kwargs)
        self.analyze.assert_not_called()

    def test_no_selected_tests_rejected_before_provider_calls(self):
        self.selected = ['app.py']
        with self.assertRaisesRegex(WorkspaceError, 'test\\*'):
            self.run_loop(loop_approved=True)
        self.analyze.assert_not_called()
        self.propose.assert_not_called()

    def test_investigation_provider_failure_returns_structured_block_without_execution(self):
        self.analyze.side_effect = ProviderError('upstream private detail')
        result = self.run_loop(loop_approved=True)
        self.assertEqual(result['status'], 'blocked')
        self.assertEqual(result['stage'], 'investigation')
        self.assertEqual(result['error_code'], 'provider_failure')
        self.assertEqual(result['attempts'], [])
        self.assertIsNone(result['patch'])
        self.assertNotIn('private detail', str(result))
        self.propose.assert_not_called()
        self.verify.assert_not_called()

    def test_pass_stops_and_keeps_host_changes_empty(self):
        result = self.run_loop(loop_approved=True)
        self.assertEqual(result['status'], 'checks_passed_no_demonstrated_fix')
        self.assertEqual(result['applied_changes'], [])
        self.assertEqual(len(result['attempts']), 1)
        self.verify.assert_called_once_with(self.archive, self.selected, self.patch,
                                            approved=True, execution_approved=True)

    def test_failed_candidate_retries_against_original_source(self):
        self.verify.side_effect = [{'status': 'failed', 'candidate': {'log': 'value mismatch'}}, {'status': 'passed'}]
        result = self.run_loop(loop_approved=True)
        self.assertEqual(result['status'], 'checks_passed_no_demonstrated_fix')
        self.assertEqual(len(result['attempts']), 2)
        self.assertEqual(self.propose.call_args_list[1].args[:2], (self.archive, self.selected))
        self.assertIn('untrusted evidence', self.propose.call_args_list[1].args[2])
        self.analyze.assert_called_once()

    def test_only_baseline_failure_resolved_demonstrates_repair(self):
        self.verify.return_value = {'status': 'passed', 'observed_failure_resolved': True,
                                   'baseline': {'status': 'passed'}, 'candidate': {'status': 'passed'}}
        self.assertEqual(self.run_loop(loop_approved=True)['status'], 'checks_passed_no_demonstrated_fix')
        self.verify.return_value['baseline']['status'] = 'failed'
        self.assertEqual(self.run_loop(loop_approved=True)['status'], 'repair_demonstrated')

    def test_blocked_runtime_and_provider_failure_stop(self):
        self.verify.return_value = {'status': 'blocked'}
        self.assertEqual(self.run_loop(loop_approved=True)['status'], 'blocked')
        self.propose.assert_called_once()
        self.propose.reset_mock()
        self.propose.side_effect = ProviderError('quota')
        self.assertEqual(self.run_loop(loop_approved=True)['status'], 'blocked')
        self.propose.assert_called_once()

    def test_repeated_failures_stop_at_budget(self):
        self.verify.return_value = {'status': 'failed'}
        result = self.run_loop(loop_approved=True)
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(len(result['attempts']), 2)
        self.assertEqual(result['reason'], 'Attempt limit reached')

    def test_invalid_candidate_never_executes(self):
        self.propose.return_value = {'patch': {**self.patch, 'path': 'test_app.py'}}
        result = self.run_loop(loop_approved=True)
        self.assertEqual(result['status'], 'blocked')
        self.assertEqual(result['error_code'], 'invalid_candidate')
        self.assertNotIn('Provider request failed', result['reason'])
        self.verify.assert_not_called()

    def test_retry_provider_failure_keeps_prior_evidence(self):
        self.verify.return_value = {'status': 'failed'}
        self.propose.side_effect = [{'patch': self.patch}, ProviderError('quota')]
        result = self.run_loop(loop_approved=True)
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(len(result['attempts']), 1)
        self.assertEqual(result['patch'], self.patch)


if __name__ == '__main__':
    unittest.main()
