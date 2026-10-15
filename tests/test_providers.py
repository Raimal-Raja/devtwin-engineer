import io
import json
import os
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from backend import providers


class ProviderTests(unittest.TestCase):
    def setUp(self):
        env = patch.dict(os.environ, {'DEVTWIN_PROVIDER': 'groq', 'GROQ_API_KEY': 'test-secret',
                                      'GEMINI_API_KEY': 'test-secret', 'OPENROUTER_API_KEY': 'test-secret'})
        env.start()
        self.addCleanup(env.stop)

    def groq(self, finish='stop'):
        return {'choices': [{'message': {'content': 'test-secret answer'}, 'finish_reason': finish}]}

    def gemini(self, finish='STOP'):
        return {'candidates': [{'finishReason': finish, 'content': {'parts': [
            {'text': 'hidden reasoning', 'thought': True}, {'text': 'test-secret answer'}]}}]}

    def test_groq_contract_and_no_redirects(self):
        with patch.object(providers, 'build_opener') as factory:
            factory.return_value.open.return_value = io.BytesIO(json.dumps(self.groq()).encode())
            result = providers.complete('Synthetic test')
            request = factory.return_value.open.call_args.args[0]
            self.assertEqual(request.full_url, 'https://api.groq.com/openai/v1/chat/completions')
            self.assertEqual(json.loads(request.data)['max_completion_tokens'], 512)
            self.assertEqual(result['content'], '[REDACTED] answer')
            self.assertEqual(result['provider'], 'groq')
            self.assertIsInstance(factory.call_args.args[0], providers.NoRedirect)

    def test_gemini_contract_and_thought_exclusion(self):
        with patch.dict(os.environ, {'DEVTWIN_PROVIDER': 'gemini'}), patch.object(providers, 'build_opener') as factory:
            factory.return_value.open.return_value = io.BytesIO(json.dumps(self.gemini()).encode())
            result = providers.complete('Synthetic test')
            request = factory.return_value.open.call_args.args[0]
            self.assertNotIn('test-secret', request.full_url)
            self.assertEqual(request.get_header('X-goog-api-key'), 'test-secret')
            self.assertEqual(json.loads(request.data)['generationConfig']['maxOutputTokens'], 512)
            self.assertEqual(result['content'], '[REDACTED] answer')
            self.assertNotIn('hidden reasoning', str(result))

    def test_bad_configuration_and_limits_never_call_network(self):
        with patch.object(providers, 'build_opener') as factory:
            with patch.dict(os.environ, {'GROQ_API_KEY': ''}):
                with self.assertRaises(providers.ProviderError):
                    providers.complete('test')
            with patch.dict(os.environ, {'DEVTWIN_PROVIDER': 'https://evil.example'}):
                with self.assertRaises(providers.ProviderError):
                    providers.complete('test')
            for prompt, kwargs in (('', {}), ('x' * 32001, {}), ('test', {'max_tokens': 9999}),
                                   ('test', {'timeout': float('nan')}), ('test', {'json_mode': 'yes'})):
                with self.assertRaises(providers.ProviderError):
                    providers.complete(prompt, **kwargs)
            factory.assert_not_called()

    def test_provider_structured_output_modes(self):
        for provider, answer in (('groq', self.groq()), ('gemini', self.gemini())):
            with patch.dict(os.environ, {'DEVTWIN_PROVIDER': provider}), patch.object(providers, 'build_opener') as factory:
                factory.return_value.open.return_value = io.BytesIO(json.dumps(answer).encode())
                providers.complete('Return JSON', json_mode=True)
                body = json.loads(factory.return_value.open.call_args.args[0].data)
                if provider == 'groq':
                    self.assertEqual(body['response_format'], {'type': 'json_object'})
                else:
                    self.assertEqual(body['generationConfig']['responseMimeType'], 'application/json')

    def test_http_quota_stops_without_fallback(self):
        with patch.object(providers, 'build_opener') as factory, patch.object(providers.nvidia, 'complete') as fallback:
            factory.return_value.open.side_effect = HTTPError('url', 429, 'test-secret', {}, io.BytesIO(b'private body'))
            with self.assertRaisesRegex(providers.ProviderError, 'no retry or fallback') as caught:
                providers.complete('test')
            self.assertNotIn('test-secret', str(caught.exception))
            self.assertEqual(factory.return_value.open.call_count, 1)
            fallback.assert_not_called()

    def test_invalid_incomplete_and_blocked_responses(self):
        for provider, payload in (('groq', self.groq('length')), ('gemini', self.gemini('SAFETY')),
                                  ('groq', {}), ('gemini', {'candidates': []})):
            with patch.dict(os.environ, {'DEVTWIN_PROVIDER': provider}), patch.object(providers, 'build_opener') as factory:
                factory.return_value.open.return_value = io.BytesIO(json.dumps(payload).encode())
                with self.assertRaises(providers.ProviderError):
                    providers.complete('test')

    def test_response_limit(self):
        with patch.object(providers, 'build_opener') as factory:
            factory.return_value.open.return_value = io.BytesIO(b'x' * (providers.MAX_RESPONSE_BYTES + 1))
            with self.assertRaisesRegex(providers.ProviderError, 'size limit'):
                providers.complete('test')

    def test_openrouter_free_only_request_and_actual_model(self):
        answer = {**self.groq(), 'model': 'example/free-model:free', 'usage': {'cost': 0}}
        with patch.dict(os.environ, {'DEVTWIN_PROVIDER': 'openrouter'}), patch.object(providers, 'build_opener') as factory:
            factory.return_value.open.return_value = io.BytesIO(json.dumps(answer).encode())
            result = providers.complete('Return JSON', json_mode=True)
            request = factory.return_value.open.call_args.args[0]
            body = json.loads(request.data)
            self.assertEqual(request.full_url, 'https://openrouter.ai/api/v1/chat/completions')
            self.assertEqual(request.get_header('Authorization'), 'Bearer test-secret')
            self.assertEqual(body['model'], 'openrouter/free')
            self.assertEqual(body['provider']['max_price'], {'prompt': 0, 'completion': 0, 'request': 0})
            self.assertTrue(body['provider']['require_parameters'])
            self.assertFalse(body['provider']['allow_fallbacks'])
            self.assertEqual(body['provider']['data_collection'], 'deny')
            self.assertEqual(body['response_format'], {'type': 'json_object'})
            self.assertNotIn('plugins', body)
            self.assertNotIn('models', body)
            self.assertNotIn('test-secret', json.dumps(result))
            self.assertEqual(result['model'], 'example/free-model:free')

    def test_openrouter_error_quota_and_nonzero_cost_stop(self):
        with patch.dict(os.environ, {'DEVTWIN_PROVIDER': 'openrouter'}), patch.object(providers, 'build_opener') as factory:
            for code in (401, 402, 429, 503):
                factory.return_value.open.reset_mock()
                factory.return_value.open.side_effect = HTTPError('url', code, 'private', {}, io.BytesIO(b'test-secret'))
                with self.assertRaises(providers.ProviderError) as caught:
                    providers.complete('test')
                self.assertNotIn('test-secret', str(caught.exception))
                self.assertEqual(factory.return_value.open.call_count, 1)
            factory.return_value.open.side_effect = None
            for answer in ({**self.groq(), 'model': 'example/model:free', 'usage': {'cost': .01}},
                           self.groq(), {**self.groq('length'), 'model': 'example/model:free'}):
                factory.return_value.open.return_value = io.BytesIO(json.dumps(answer).encode())
                with self.assertRaises(providers.ProviderError):
                    providers.complete('test')

    def test_paid_model_is_rejected_and_free_nemotron_uses_supported_controls(self):
        with patch.dict(os.environ, {'DEVTWIN_PROVIDER': 'openrouter',
                                    'DEVTWIN_OPENROUTER_MODEL': 'nvidia/nemotron-3-ultra-550b-a55b'}), patch.object(providers, 'build_opener') as factory:
            with self.assertRaises(providers.ProviderError):
                providers.complete('Return JSON', json_mode=True)
            factory.assert_not_called()
        with patch.dict(os.environ, {'DEVTWIN_PROVIDER': 'openrouter',
                                    'DEVTWIN_OPENROUTER_MODEL': 'nvidia/nemotron-3-ultra-550b-a55b:free'}), patch.object(providers, 'build_opener') as factory:
            factory.return_value.open.return_value = io.BytesIO(json.dumps({**self.groq(), 'model': 'nvidia/nemotron-3-ultra-550b-a55b:free'}).encode())
            result = providers.complete('Return JSON', json_mode=True)
            body = json.loads(factory.return_value.open.call_args.args[0].data)
            self.assertNotIn('response_format', body)
            self.assertEqual(body['model'], result['requested_model'])
            self.assertFalse(body['reasoning']['enabled'])

    def test_missing_openrouter_key_blocks_before_network(self):
        with patch.dict(os.environ, {'DEVTWIN_PROVIDER': 'openrouter', 'OPENROUTER_API_KEY': ''}), patch.object(providers, 'build_opener') as factory:
            self.assertFalse(providers.provider_info()['configured'])
            with self.assertRaises(providers.ProviderError):
                providers.complete('test')
            factory.assert_not_called()

    def test_collection_requires_explicit_policy_and_disclosure(self):
        with patch.dict(os.environ, {'DEVTWIN_PROVIDER': 'openrouter', 'DEVTWIN_OPENROUTER_DATA_POLICY': 'allow'}), patch.object(providers, 'build_opener') as factory:
            info = providers.provider_info()
            self.assertTrue(info['public_input_required'])
            self.assertIn('training', info['notice'])
            factory.return_value.open.return_value = io.BytesIO(json.dumps({**self.groq(), 'model': 'example/model:free'}).encode())
            providers.complete('Synthetic example')
            body = json.loads(factory.return_value.open.call_args.args[0].data)
            self.assertEqual(body['provider']['data_collection'], 'allow')
            self.assertEqual(body['provider']['max_price']['prompt'], 0)

    def test_metadata_excludes_secrets_and_nvidia_stays_explicit(self):
        self.assertNotIn('test-secret', json.dumps(providers.provider_info()))
        with patch.dict(os.environ, {'DEVTWIN_PROVIDER': 'nvidia'}), patch.object(providers.nvidia, 'complete') as selected:
            selected.return_value = {'content': 'ok'}
            self.assertEqual(providers.complete('test')['provider'], 'nvidia')
            selected.assert_called_once()
