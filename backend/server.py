"""Authenticated local investigation and isolated-test workspace; not public hosting."""
import argparse
import base64
import binascii
import hmac
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import math
import os
from pathlib import Path
import time

from .investigate import WORKFLOWS, investigate
from .nvidia import ProviderError
from .providers import provider_info
from .patches import export_candidate, propose
from .github import GithubError, import_repository, list_repository
from .runner import verify_candidate, verify_dispatch
from .repair import repair, validate_repair_selection
from .workspace import WorkspaceError, ingest_zip

UI = Path(__file__).parent / 'ui'
MAX_BODY = 3 * 1024 * 1024


class WorkspaceServer(HTTPServer):
    def __init__(self, port, token, *, analyze=investigate, propose_patch=propose, import_repo=import_repository,
                 verify=verify_dispatch, list_repo=list_repository, listen='127.0.0.1', worker_only=False):
        if not isinstance(token, str) or len(token) < 32 or not token.isascii() or not token.isalnum():
            raise ValueError('DEVTWIN_SESSION_TOKEN must contain at least 32 ASCII letters/digits')
        self.token, self.analyze, self.calls = token, analyze, []
        self.propose_patch = propose_patch
        self.import_repo, self.import_calls = import_repo, []
        self.browse_calls = []
        self.list_repo = list_repo
        self.verify, self.verification_calls = verify, []
        if listen not in ('127.0.0.1', '0.0.0.0'):
            raise ValueError('Unsupported listen address')
        self.worker_only = worker_only
        super().__init__((listen, port), Handler)
        self.api_authority = ('worker:' if worker_only else '127.0.0.1:') + str(self.server_port)
        self.origin = 'http://' + self.api_authority

    def get_request(self):
        connection, address = super().get_request()
        connection.settimeout(10)
        return connection, address


class Handler(BaseHTTPRequestHandler):
    server_version = 'DevTwin'

    def log_message(self, *args):
        pass  # No credentials, request paths or project data in HTTP logs.

    def reply(self, status, payload, content_type='application/json'):
        # Closing with an unread, already-sent POST body can reset a Windows
        # connection before the client receives the rejection. Drain only
        # length-delimited bodies within the normal limit; never interpret them.
        if self.command == 'POST' and status >= 400 and not getattr(self, '_body_consumed', False):
            try:
                remaining = int(self.headers.get('Content-Length', '0'))
                if 0 < remaining <= MAX_BODY and not self.headers.get('Transfer-Encoding'):
                    self.rfile.read(remaining)
            except (ValueError, OSError):
                pass
            self._body_consumed = True
        raw = json.dumps(payload).encode() if content_type == 'application/json' else payload
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(raw)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Content-Security-Policy', "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
        self.end_headers()
        self.wfile.write(raw)

    def allowed_host(self):
        return self.headers.get('Host') == self.server.api_authority

    def do_GET(self):
        if not self.allowed_host():
            return self.reply(403, {'error': 'Host rejected'})
        if self.server.worker_only:
            return self.reply(200, {'ready': True}) if self.path == '/health' else self.reply(404, {'error': 'Not found'})
        assets = {'/': ('index.html', 'text/html; charset=utf-8'),
                  '/app.mjs': ('app.mjs', 'text/javascript; charset=utf-8'),
                  '/github.mjs': ('github.mjs', 'text/javascript; charset=utf-8'),
                  '/shell.mjs': ('shell.mjs', 'text/javascript; charset=utf-8'),
                  '/batch.mjs': ('batch.mjs', 'text/javascript; charset=utf-8'),
                  '/portrait.jpg': ('portrait.jpg', 'image/jpeg'),
                  '/style.css': ('style.css', 'text/css; charset=utf-8')}
        if self.path not in assets:
            return self.reply(404, {'error': 'Not found'})
        name, mime = assets[self.path]
        self.reply(200, (UI / name).read_bytes(), mime)

    def do_POST(self):
        if not self.allowed_host() or self.headers.get('Origin') != self.server.origin:
            return self.reply(403, {'error': 'Origin or Host rejected'})
        supplied = self.headers.get('Authorization', '')
        if not hmac.compare_digest(supplied.encode(), ('Bearer ' + self.server.token).encode()):
            return self.reply(401, {'error': 'Workspace authentication required'})
        routes = ('/api/verify',) if self.server.worker_only else ('/api/preview', '/api/investigate', '/api/propose', '/api/export', '/api/github', '/api/github/tree', '/api/verify', '/api/repair')
        if self.path not in routes:
            return self.reply(404, {'error': 'Not found'})
        if self.headers.get('Content-Type') != 'application/json' or self.headers.get('Transfer-Encoding'):
            return self.reply(415, {'error': 'Use a length-delimited JSON request'})
        try:
            length = int(self.headers.get('Content-Length', '0'))
        except ValueError:
            length = 0
        if not 1 <= length <= MAX_BODY:
            return self.reply(413, {'error': 'Request size rejected'})
        try:
            body = self.rfile.read(length)
            self._body_consumed = True
            if len(body) != length:
                raise ValueError()
            data = json.loads(body)
            if self.path in ('/api/github', '/api/github/tree'):
                if not isinstance(data, dict):
                    raise ValueError()
                now = time.monotonic()
                browsing = self.path.endswith('/tree')
                bucket = 'browse_calls' if browsing else 'import_calls'
                limit = 6 if browsing else 4
                calls = [stamp for stamp in getattr(self.server, bucket) if now - stamp < 60]
                setattr(self.server, bucket, calls)
                if len(calls) >= limit:
                    seconds = max(1, math.ceil(60 - (now - calls[0])))
                    action = 'browse' if browsing else 'import'
                    return self.reply(429, {'error': f'GitHub {action} limit reached; try again in {seconds} seconds',
                                            'retry_after_seconds': seconds})
                calls.append(now)
                try:
                    result = (self.server.list_repo(data.get('repository'), data.get('ref')) if self.path.endswith('/tree')
                              else self.server.import_repo(data.get('repository'), data.get('ref'), data.get('selected')))
                except WorkspaceError as exc:
                    return self.reply(400, {'error': str(exc)})
                return self.reply(200, result)
            if not isinstance(data, dict) or not isinstance(data.get('archive'), str):
                raise ValueError()
            archive = base64.b64decode(data['archive'], validate=True)
            files = ingest_zip(archive, data.get('selected'))
            if self.path == '/api/repair':
                validate_repair_selection(files)
            if self.path == '/api/preview':
                return self.reply(200, {'files': files, 'workflows': sorted(WORKFLOWS),
                                        'provider': provider_info(), 'submitted_to_model': False})
            if self.path == '/api/export':
                candidate, hashes = export_candidate(archive, data['selected'], data.get('patch'),
                                                      approved=data.get('approved'))
                return self.reply(200, {'archive': base64.b64encode(candidate).decode(), 'files': hashes,
                                       'scope': 'selected files only', 'tests_executed': False})
            if self.path == '/api/verify':
                now = time.monotonic()
                self.server.verification_calls = [stamp for stamp in self.server.verification_calls if now - stamp < 60]
                if len(self.server.verification_calls) >= 2:
                    return self.reply(429, {'error': 'Verification limit reached; wait before retrying'})
                self.server.verification_calls.append(now)
                return self.reply(200, self.server.verify(archive, data['selected'], data.get('patch'),
                                  approved=data.get('approved'), execution_approved=data.get('execution_approved')))
            if data.get('consent') is not True:
                return self.reply(400, {'error': 'Approve submission of nonconfidential selected files first'})
            if data.get('provider') != provider_info()['id']:
                return self.reply(400, {'error': 'Preview and approve the current provider before submission'})
            if provider_info()['public_input_required'] and data.get('public_input_confirmed') is not True:
                return self.reply(400, {'error': 'Confirm public or synthetic inputs and upstream data collection before submission'})
            now = time.monotonic()
            self.server.calls = [stamp for stamp in self.server.calls if now - stamp < 60]
            budget = 3 if self.path == '/api/repair' else 1
            if len(self.server.calls) + budget > 5:
                return self.reply(429, {'error': 'Workspace limit reached; wait before another investigation'})
            if self.path == '/api/repair':
                if data.get('loop_approved') is not True:
                    raise WorkspaceError('Approve the bounded repair loop first')
                self.server.verification_calls = [stamp for stamp in self.server.verification_calls if now - stamp < 60]
                if self.server.verification_calls:
                    return self.reply(429, {'error': 'Wait before reserving two isolated verification attempts'})
                self.server.verification_calls.extend([now, now])
            self.server.calls.extend([now] * budget)
            if self.path == '/api/repair':
                return self.reply(200, repair(archive, data['selected'], data.get('task'), data.get('workflow'),
                                  loop_approved=True, analyze=self.server.analyze,
                                  propose_patch=self.server.propose_patch, verify=self.server.verify))
            if self.path == '/api/propose':
                result = self.server.propose_patch(archive, data['selected'], data.get('task'))
            else:
                result = self.server.analyze(archive, data['selected'], data.get('task'), data.get('workflow'))
            self.reply(200, result)
        except WorkspaceError as exc:
            self.reply(400, {'error': str(exc)})
        except (ValueError, TypeError, KeyError, binascii.Error):
            self.reply(400, {'error': 'Invalid archive, selection or task; check the input limits'})
        except ProviderError as exc:
            self.reply(502, {'error': str(exc)})
        except GithubError as exc:
            self.reply(502, {'error': str(exc)})
        except Exception:
            self.reply(500, {'error': 'Workspace request failed'})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--listen', choices=('127.0.0.1', '0.0.0.0'), default='127.0.0.1')
    parser.add_argument('--worker', action='store_true', help='Private verification-only worker; no model routes or UI')
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error('Port must be between 1 and 65535')
    try:
        token_name = 'DEVTWIN_WORKER_TOKEN' if args.worker else 'DEVTWIN_SESSION_TOKEN'
        server = WorkspaceServer(args.port, os.environ.get(token_name, ''), listen=args.listen,
                                 worker_only=args.worker, verify=verify_candidate if args.worker else verify_dispatch)
    except (ValueError, OSError):
        parser.error('Configure a valid DEVTWIN_SESSION_TOKEN and an available port')
    print('Internal workspace: ' + server.origin, flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
