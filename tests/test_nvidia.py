import io
import json
import os
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from backend import nvidia


class NvidiaTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {'NVIDIA_API_KEY': 'test-only-secret'})
        self.env.start()
        self.addCleanup(self.env.stop)

    def response(self, content='Verified answer', finish='stop'):
        return io.BytesIO(json.dumps({'choices': [{'message': {
            'content': content, 'reasoning_content': 'not user-facing'},
            'finish_reason': finish}]}).encode())

    def test_request_contract_and_redaction(self):
        with patch.object(nvidia, 'build_opener') as factory:
            factory.return_value.open.return_value = self.response('test-only-secret answer')
            result = nvidia.complete('Synthetic task')
            request = factory.return_value.open.call_args.args[0]
            self.assertEqual(request.full_url, nvidia.ENDPOINT)
            body = json.loads(request.data)
            self.assertEqual(body['model'], nvidia.MODEL)
            self.assertFalse(body['stream'])
            self.assertFalse(body['chat_template_kwargs']['enable_thinking'])
            self.assertEqual(result['content'], '[REDACTED] answer')
            self.assertNotIn('reasoning_content', result)

    def test_invalid_configuration_never_calls_network(self):
        with patch.object(nvidia, 'build_opener') as factory:
            for kwargs in ({'max_tokens': 9000}, {'timeout': 0}, {'thinking': 'yes'}):
                with self.assertRaises(nvidia.ProviderError):
                    nvidia.complete('task', **kwargs)
            for prompt in ('', 'x' * 32001):
                with self.assertRaises(nvidia.ProviderError):
                    nvidia.complete(prompt)
            with patch.dict(os.environ, {'NVIDIA_API_KEY': ''}):
                with self.assertRaises(nvidia.ProviderError):
                    nvidia.complete('task')
            factory.assert_not_called()

    def test_http_errors_do_not_echo_bodies_or_retry(self):
        for status in (302, 401, 403, 429, 500):
            with self.subTest(status=status), patch.object(nvidia, 'build_opener') as factory:
                factory.return_value.open.side_effect = HTTPError(
                    nvidia.ENDPOINT, status, 'test-only-secret', {}, io.BytesIO(b'private body'))
                with self.assertRaises(nvidia.ProviderError) as caught:
                    nvidia.complete('private prompt')
                self.assertNotIn('test-only-secret', str(caught.exception))
                self.assertNotIn('private', str(caught.exception))
                self.assertEqual(factory.return_value.open.call_count, 1)

    def test_network_error_is_redacted(self):
        with patch.object(nvidia, 'build_opener') as factory:
            factory.return_value.open.side_effect = URLError('test-only-secret')
            with self.assertRaisesRegex(nvidia.ProviderError, 'connection failed'):
                nvidia.complete('task')

    def test_invalid_and_truncated_answers_fail(self):
        for response in (self.response(finish='length'), self.response(content=''),
                         io.BytesIO(b'not json'), io.BytesIO(b'{}'),
                         io.BytesIO(b'x' * (nvidia.MAX_RESPONSE_BYTES + 1))):
            with patch.object(nvidia, 'build_opener') as factory:
                factory.return_value.open.return_value = response
                with self.assertRaises(nvidia.ProviderError):
                    nvidia.complete('task')

    def test_redirects_are_refused(self):
        self.assertIsNone(nvidia.NoRedirect().redirect_request(None, None, 302, '', {},
                                                             'https://example.com'))
