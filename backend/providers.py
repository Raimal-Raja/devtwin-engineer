"""Explicit free-tier-capable provider selection; no retries or fallback."""
import argparse
from http.client import HTTPException
import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener

from . import nvidia
from .nvidia import NoRedirect, ProviderError, MAX_RESPONSE_BYTES

PROVIDERS = {
    'nvidia': {'name': 'NVIDIA', 'model': nvidia.MODEL, 'key': 'NVIDIA_API_KEY',
               'notice': 'Trial service: internal evaluation only; nonconfidential inputs only.'},
    'groq': {'name': 'Groq', 'model': 'openai/gpt-oss-120b', 'key': 'GROQ_API_KEY',
             'notice': 'Use a Groq Free Plan account. Quotas apply; this app cannot verify billing status.'},
    'gemini': {'name': 'Google Gemini', 'model': 'gemini-3.8-flash', 'key': 'GEMINI_API_KEY',
               'notice': 'Use an unpaid Gemini project. Inputs may be used for improvement; no confidential or personal information.'},
    'openrouter': {'name': 'OpenRouter Free', 'model': 'openrouter/free', 'key': 'OPENROUTER_API_KEY',
                   'notice': 'Free models only; OpenRouter chooses an upstream model/provider per request. '
                             'Nonconfidential inputs only. Zero-price routing and data-collection denial are requested; quotas and availability apply.'},
}
OPENROUTER_FREE_MODELS = ('openrouter/free', 'nvidia/nemotron-3-ultra-550b-a55b:free')


def provider_config(provider):
    config = dict(PROVIDERS[provider])
    if provider == 'openrouter':
        model = os.environ.get('DEVTWIN_OPENROUTER_MODEL', 'openrouter/free')
        if model not in OPENROUTER_FREE_MODELS:
            raise ProviderError('Select only an allowlisted OpenRouter free model')
        config['model'] = model
        policy = os.environ.get('DEVTWIN_OPENROUTER_DATA_POLICY', 'deny')
        if policy not in ('deny', 'allow'):
            raise ProviderError('OpenRouter data policy must be deny or allow')
        config['data_policy'] = policy
        if policy == 'allow':
            config['notice'] = ('Public or synthetic inputs only. OpenRouter forwards to an upstream provider '
                                'that may store inputs or use them for training. Free-only routing; quotas apply.')
    return config


def selected_provider():
    provider = os.environ.get('DEVTWIN_PROVIDER', 'nvidia')
    if provider not in PROVIDERS:
        raise ProviderError('DEVTWIN_PROVIDER must be nvidia, groq, gemini or openrouter')
    return provider


def provider_info():
    provider = selected_provider()
    config = provider_config(provider)
    return {'id': provider, 'name': config['name'], 'model': config['model'],
            'notice': config['notice'], 'configured': bool(os.environ.get(config['key'], '').strip()),
            'public_input_required': config.get('data_policy') == 'allow'}


def complete(prompt, *, max_tokens=512, timeout=60, json_mode=False):
    provider = selected_provider()
    if provider == 'nvidia':
        return {'provider': provider, **nvidia.complete(prompt, max_tokens=max_tokens, timeout=timeout, json_mode=json_mode)}
    config = provider_config(provider)
    key = os.environ.get(config['key'], '').strip()
    if not key or not key.isascii() or any(ord(char) < 33 for char in key):
        raise ProviderError('Configure a valid ' + config['key'] + ' in the backend environment')
    if (not isinstance(prompt, str) or not prompt.strip() or len(prompt.encode('utf-8')) > 32000
            or type(max_tokens) is not int or not 1 <= max_tokens <= 2048
            or type(timeout) not in (int, float) or not 1 <= timeout <= 120 or type(json_mode) is not bool):
        raise ProviderError('Invalid provider prompt, token limit or timeout')
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    if provider in ('groq', 'openrouter'):
        endpoint = ('https://openrouter.ai/api/v1/chat/completions' if provider == 'openrouter'
                    else 'https://api.groq.com/openai/v1/chat/completions')
        headers['Authorization'] = 'Bearer ' + key
        body = {'model': config['model'], 'messages': [{'role': 'user', 'content': prompt}],
                'temperature': 0.2, 'stream': False}
        if provider == 'openrouter':
            body['max_tokens'] = max_tokens
            body['provider'] = {'max_price': {'prompt': 0, 'completion': 0, 'request': 0},
                                'require_parameters': True, 'data_collection': config['data_policy'], 'allow_fallbacks': False}
            if config['model'] != 'openrouter/free':
                body['reasoning'] = {'enabled': False}
        else:
            body['max_completion_tokens'] = max_tokens
        if json_mode and (provider != 'openrouter' or config['model'] == 'openrouter/free'):
            body['response_format'] = {'type': 'json_object'}
    else:
        endpoint = 'https://generativelanguage.googleapis.com/v1beta/models/' + config['model'] + ':generateContent'
        headers['x-goog-api-key'] = key
        body = {'contents': [{'role': 'user', 'parts': [{'text': prompt}]}],
                'generationConfig': {'temperature': 0.2, 'maxOutputTokens': max_tokens}}
        if json_mode:
            body['generationConfig']['responseMimeType'] = 'application/json'
    request = Request(endpoint, data=json.dumps(body).encode(), headers=headers, method='POST')
    try:
        with build_opener(NoRedirect()).open(request, timeout=timeout) as response:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
    except HTTPError as exc:
        status = exc.code
        exc.close()
        suffix = 'quota or rate limit reached' if status == 429 else 'request failed (HTTP %s)' % status
        raise ProviderError(config['name'] + ' ' + suffix + '; no retry or fallback was made') from None
    except (URLError, TimeoutError, OSError, HTTPException):
        raise ProviderError(config['name'] + ' connection failed; no retry or fallback was made') from None
    if len(raw) > MAX_RESPONSE_BYTES:
        raise ProviderError('Provider response exceeded the size limit')
    try:
        payload = json.loads(raw)
        if provider == 'openrouter' and isinstance(payload, dict) and 'error' in payload:
            raise ProviderError('OpenRouter returned an upstream generation error; no retry or fallback was made')
        actual_model = config['model']
        if provider in ('groq', 'openrouter'):
            choice = payload['choices'][0]
            content, finish = choice['message']['content'], choice['finish_reason']
            if finish != 'stop':
                raise ProviderError('Provider returned an unfinished answer within the configured output budget')
            if provider == 'openrouter':
                actual_model = payload.get('model')
                if (not isinstance(actual_model, str) or not actual_model.strip()
                        or len(actual_model) > 200 or not actual_model.isascii()
                        or any(ord(char) < 33 for char in actual_model)):
                    raise ProviderError('OpenRouter response did not identify a valid model')
                cost = payload.get('usage', {}).get('cost') if isinstance(payload.get('usage'), dict) else None
                if cost is not None and (type(cost) not in (int, float) or cost != 0):
                    raise ProviderError('OpenRouter reported an invalid or nonzero cost; result rejected')
        else:
            candidate = payload['candidates'][0]
            if candidate['finishReason'] != 'STOP':
                raise ValueError()
            parts = candidate['content']['parts']
            if not isinstance(parts, list) or any(not isinstance(part, dict) for part in parts):
                raise ValueError()
            content = ''.join(part['text'] for part in parts if 'text' in part and not part.get('thought'))
            finish = 'stop'
        if not isinstance(content, str) or not content.strip():
            raise ValueError()
    except (ValueError, KeyError, IndexError, TypeError, UnicodeError):
        raise ProviderError('Provider returned an invalid, empty or unfinished answer') from None
    return {'provider': provider, 'model': actual_model.replace(key, '[REDACTED]'),
            'requested_model': config['model'], 'content': content.replace(key, '[REDACTED]'), 'finish_reason': finish}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--smoke', required=True, action='store_true')
    parser.parse_args()
    try:
        result = complete('Reply with one short sentence confirming you can respond to a development test.')
    except ProviderError as exc:
        print(json.dumps({'passed': False, 'error': str(exc)}))
        return 1
    print(json.dumps({'passed': True, **result}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
