import base64
import hashlib
import http.client
import io
import json
import os
import threading
import unittest
from unittest.mock import Mock, patch
import zipfile

from backend.server import MAX_BODY, WorkspaceServer
from backend.nvidia import ProviderError


class ServerTests(unittest.TestCase):
    def setUp(self):
        env = patch.dict(os.environ, {'DEVTWIN_PROVIDER': 'nvidia'})
        env.start()
        self.addCleanup(env.stop)
        self.analyze = Mock(return_value={'status': 'unverified_source_analysis',
                                         'executed_commands': [], 'applied_changes': []})
        self.propose = Mock(return_value={'status': 'unverified_patch_proposal'})
        self.import_repo = Mock(return_value={'repository': 'x/y', 'commit': 'a' * 40,
                                              'submitted_to_model': False, 'github_writes': False})
        self.verify = Mock(return_value={'status': 'blocked', 'reason': 'Synthetic missing runner'})
        self.server = WorkspaceServer(0, 'a' * 32, analyze=self.analyze, propose_patch=self.propose,
                                      import_repo=self.import_repo, verify=self.verify)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.close)
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, 'w') as archive:
            archive.writestr('a.py', 'pass\n')
        self.data = {'archive': base64.b64encode(stream.getvalue()).decode(),
                     'selected': ['a.py'], 'task': 'Explain',
                     'workflow': 'repository-understanding', 'consent': True, 'provider': 'nvidia'}

    def close(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)

    def call(self, path='/api/preview', data=None, headers=None, method='POST', headers_only=False):
        connection = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=3)
        try:
            supplied = {'Origin': self.server.origin, 'Authorization': 'Bearer ' + 'a' * 32,
                        'Content-Type': 'application/json'}
            supplied.update(headers or {})
            body = None if headers_only or method == 'GET' else json.dumps(self.data if data is None else data)
            connection.request(method, path, body, supplied)
            response = connection.getresponse()
            raw = response.read()
            return response.status, raw, dict(response.getheaders())
        finally:
            connection.close()

    def test_preview_is_authenticated_and_never_infers(self):
        status, raw, headers = self.call()
        self.assertEqual(status, 200)
        self.assertFalse(json.loads(raw)['submitted_to_model'])
        self.assertEqual(json.loads(raw)['files'][0]['content'], 'pass\n')
        self.assertEqual(headers['Cache-Control'], 'no-store')
        self.analyze.assert_not_called()

    def test_repair_requires_consent_and_reserves_bounded_budgets(self):
        self.assertEqual(self.call('/api/repair', self.data)[0], 400)
        self.analyze.assert_not_called()
        self.propose.return_value = {'patch': {'path': 'a.py',
            'base_sha256': hashlib.sha256(b'pass\n').hexdigest(), 'replacement': 'value = 1\n'}}
        status, raw, _ = self.call('/api/repair', {**self.data, 'loop_approved': True})
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(raw)['status'], 'blocked')
        self.assertEqual(len(self.server.calls), 3)
        self.assertEqual(len(self.server.verification_calls), 2)
        self.assertEqual(self.call('/api/repair', {**self.data, 'loop_approved': True})[0], 429)
        self.analyze.assert_called_once()

    def test_openrouter_collection_requires_public_input_confirmation(self):
        with patch.dict(os.environ, {'DEVTWIN_PROVIDER': 'openrouter', 'DEVTWIN_OPENROUTER_DATA_POLICY': 'allow'}):
            data = {**self.data, 'provider': 'openrouter'}
            self.assertEqual(self.call('/api/investigate', data)[0], 400)
            self.analyze.assert_not_called()
            self.assertEqual(self.call('/api/investigate', {**data, 'public_input_confirmed': True})[0], 200)
            self.analyze.assert_called_once()

    def test_auth_origin_and_host_reject_before_provider(self):
        for headers, expected in (({'Authorization': 'Bearer invalid'}, 401),
                                  ({'Origin': 'https://evil.example'}, 403),
                                  ({'Host': 'evil.example'}, 403)):
            self.assertEqual(self.call('/api/investigate', headers=headers)[0], expected)
        self.analyze.assert_not_called()

    def test_consent_and_input_validation(self):
        for update in ({'consent': False}, {'provider': 'groq'}, {'archive': 'bad base64'}, {'selected': ['absent']}):
            self.assertEqual(self.call('/api/investigate', {**self.data, **update})[0], 400)
        self.assertEqual(self.call(headers={'Content-Type': 'text/plain'})[0], 415)
        self.assertEqual(self.call(headers={'Content-Length': str(MAX_BODY + 1)}, headers_only=True)[0], 413)
        self.analyze.assert_not_called()

    def test_inference_and_rate_limit(self):
        for _ in range(5):
            self.assertEqual(self.call('/api/investigate')[0], 200)
        self.assertEqual(self.call('/api/investigate')[0], 429)
        self.assertEqual(self.analyze.call_count, 5)

    def test_provider_and_unexpected_errors(self):
        self.analyze.side_effect = ProviderError('NVIDIA quota reached')
        self.assertEqual(self.call('/api/investigate')[0], 502)
        self.analyze.side_effect = RuntimeError('private token')
        status, raw, _ = self.call('/api/investigate')
        self.assertEqual(status, 500)
        self.assertNotIn(b'private token', raw)

    def test_static_assets_and_path_allowlist(self):
        for path in ('/', '/app.mjs', '/style.css'):
            status, _, headers = self.call(path, method='GET')
            self.assertEqual(status, 200)
            self.assertIn("connect-src 'self'", headers['Content-Security-Policy'])
        self.assertEqual(self.call('/../server.py', method='GET')[0], 404)

    def test_token_configuration(self):
        for token in ('', 'short', 'x' * 31 + '\n'):
            with self.assertRaises(ValueError):
                WorkspaceServer(0, token)

    def test_patch_proposal_uses_consent_and_shared_rate_limit(self):
        self.assertEqual(self.call('/api/propose', {**self.data, 'consent': False})[0], 400)
        self.propose.assert_not_called()
        self.assertEqual(self.call('/api/propose')[0], 200)
        self.propose.assert_called_once()
        for _ in range(4):
            self.assertEqual(self.call('/api/investigate')[0], 200)
        self.assertEqual(self.call('/api/propose')[0], 429)

    def test_patch_export_requires_approval_and_source_hash(self):
        patch = {'path': 'a.py', 'base_sha256': hashlib.sha256(b'pass\n').hexdigest(),
                 'replacement': '# reviewed candidate\npass\n'}
        data = {**self.data, 'patch': patch}
        self.assertEqual(self.call('/api/export', data)[0], 400)
        status, raw, _ = self.call('/api/export', {**data, 'approved': True})
        self.assertEqual(status, 200)
        self.assertFalse(json.loads(raw)['tests_executed'])
        self.assertEqual(self.call('/api/export', {**data, 'approved': True,
                                                 'patch': {**patch, 'base_sha256': 'stale'}})[0], 400)
        self.analyze.assert_not_called()
        self.propose.assert_not_called()

    def test_github_import_is_authenticated_read_only_and_limited(self):
        data = {'repository': 'x/y', 'ref': 'main', 'selected': ['a.py']}
        self.assertEqual(self.call('/api/github', data, headers={'Authorization': 'bad'})[0], 401)
        self.import_repo.assert_not_called()
        for _ in range(2):
            status, raw, _ = self.call('/api/github', data)
            self.assertEqual(status, 200)
            self.assertFalse(json.loads(raw)['submitted_to_model'])
        self.assertEqual(self.call('/api/github', data)[0], 429)
        self.analyze.assert_not_called()
        self.propose.assert_not_called()

    def test_verification_route_does_not_call_a_model(self):
        data = {**self.data, 'patch': {}, 'approved': True, 'execution_approved': True}
        for _ in range(2):
            status, raw, _ = self.call('/api/verify', data)
            self.assertEqual(status, 200)
            self.assertEqual(json.loads(raw)['status'], 'blocked')
        self.assertEqual(self.call('/api/verify', data)[0], 429)
        self.assertEqual(self.verify.call_args.kwargs['execution_approved'], True)
        self.analyze.assert_not_called()
        self.propose.assert_not_called()

    def test_private_worker_only_exposes_health_and_verification(self):
        worker = WorkspaceServer(0, 'b' * 64, worker_only=True, verify=Mock(return_value={'status': 'blocked'}))
        thread = threading.Thread(target=worker.serve_forever, daemon=True)
        thread.start()
        try:
            connection = http.client.HTTPConnection('127.0.0.1', worker.server_port, timeout=3)
            connection.request('GET', '/health', headers={'Host': worker.api_authority})
            response = connection.getresponse()
            self.assertEqual(response.status, 200)
            response.read()
            connection.close()
            connection = http.client.HTTPConnection('127.0.0.1', worker.server_port, timeout=3)
            connection.request('POST', '/api/propose', '{}', headers={
                'Host': worker.api_authority, 'Origin': worker.origin, 'Authorization': 'Bearer ' + 'b' * 64,
                'Content-Type': 'application/json'})
            response = connection.getresponse()
            self.assertEqual(response.status, 404)
            response.read()
            connection.close()
        finally:
            worker.shutdown()
            worker.server_close()
            thread.join(timeout=3)
