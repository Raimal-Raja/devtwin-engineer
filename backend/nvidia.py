"""Bounded NVIDIA trial inference; no repository access or command execution."""
import argparse
import json
import os
import socket
import sys
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

ENDPOINT = 'https://integrate.api.nvidia.com/v1/chat/completions'
MODEL = 'nvidia/nemotron-3-ultra-550b-a55b'
MAX_RESPONSE_BYTES = 1024 * 1024


class ProviderError(Exception):
    """Safe diagnostic that excludes upstream bodies, credentials and prompts."""


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Never forward the Authorization header to a redirected destination.
        return None


def complete(prompt, *, max_tokens=512, timeout=60, thinking=False):
    """One request, fixed host/model, bounded input/output, no automatic retries."""
    key = os.environ.get('NVIDIA_API_KEY', '').strip()
    if not key or '\r' in key or '\n' in key:
        raise ProviderError('Configure a valid NVIDIA_API_KEY in the backend environment')
    if not isinstance(prompt, str) or not prompt.strip() or len(prompt.encode('utf-8')) > 32000:
        raise ProviderError('Prompt must contain 1 to 32000 UTF-8 bytes')
    if type(max_tokens) is not int or not 1 <= max_tokens <= 2048:
        raise ProviderError('max_tokens must be an integer from 1 to 2048')
    if type(timeout) not in (int, float) or not 1 <= timeout <= 120:
        raise ProviderError('timeout must be between 1 and 120 seconds')
    if type(thinking) is not bool:
        raise ProviderError('thinking must be boolean')
    body = {'model': MODEL, 'messages': [{'role': 'user', 'content': prompt}],
            'temperature': 0.2, 'top_p': 0.95, 'max_tokens': max_tokens,
            'stream': False, 'chat_template_kwargs': {'enable_thinking': thinking}}
    request = Request(ENDPOINT, data=json.dumps(body).encode('utf-8'), method='POST',
                      headers={'Authorization': 'Bearer ' + key,
                               'Content-Type': 'application/json', 'Accept': 'application/json'})
    try:
        with build_opener(NoRedirect()).open(request, timeout=timeout) as response:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
    except HTTPError as exc:
        status = exc.code
        exc.close()
        messages = {401: 'NVIDIA authentication failed', 403: 'NVIDIA access denied',
                    429: 'NVIDIA quota or rate limit reached; no retry was made'}
        raise ProviderError(messages.get(status, 'NVIDIA request failed (HTTP %s)' % status)) from None
    except (URLError, TimeoutError, socket.timeout, OSError):
        raise ProviderError('NVIDIA connection failed or timed out; no retry was made') from None
    if len(raw) > MAX_RESPONSE_BYTES:
        raise ProviderError('NVIDIA response exceeded the size limit')
    try:
        payload = json.loads(raw)
        choice = payload['choices'][0]
        content = choice['message']['content']
        finish = choice['finish_reason']
        if not isinstance(content, str) or not content.strip() or finish != 'stop':
            raise ValueError()
    except (ValueError, KeyError, IndexError, TypeError, UnicodeError):
        raise ProviderError('NVIDIA returned an invalid, empty or unfinished answer') from None
    # Do not return reasoning traces or echo an accidentally reflected credential.
    return {'model': MODEL, 'content': content.replace(key, '[REDACTED]'),
            'finish_reason': finish}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--smoke', action='store_true', required=True,
                        help='Send only a fixed synthetic prompt; no repository files')
    parser.parse_args()
    try:
        result = complete('Reply with one short sentence confirming you can respond to a development test.')
    except ProviderError as exc:
        print(json.dumps({'passed': False, 'error': str(exc)}))
        return 1
    print(json.dumps({'passed': True, **result}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
