"""Loopback-only internal trial workspace; no public hosting or command execution."""
import argparse
import base64
import binascii
import hmac
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import time

from .investigate import WORKFLOWS, investigate
from .nvidia import ProviderError
from .providers import provider_info
from .workspace import WorkspaceError, ingest_zip

UI = Path(__file__).parent / 'ui'
MAX_BODY = 3 * 1024 * 1024


class WorkspaceServer(HTTPServer):
    def __init__(self, port, token, *, analyze=investigate):
        if not isinstance(token, str) or len(token) < 32 or not token.isascii() or not token.isalnum():
            raise ValueError('DEVTWIN_SESSION_TOKEN must contain at least 32 ASCII letters/digits')
        self.token, self.analyze, self.calls = token, analyze, []
        super().__init__(('127.0.0.1', port), Handler)
        self.origin = 'http://127.0.0.1:' + str(self.server_port)

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
        self.send_header('Content-Security-Policy', "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
        self.end_headers()
        self.wfile.write(raw)

    def allowed_host(self):
        return self.headers.get('Host') == '127.0.0.1:' + str(self.server.server_port)

    def do_GET(self):
        if not self.allowed_host():
            return self.reply(403, {'error': 'Host rejected'})
        assets = {'/': ('index.html', 'text/html; charset=utf-8'),
                  '/app.mjs': ('app.mjs', 'text/javascript; charset=utf-8'),
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
        if self.path not in ('/api/preview', '/api/investigate'):
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
            if not isinstance(data, dict) or not isinstance(data.get('archive'), str):
                raise ValueError()
            archive = base64.b64decode(data['archive'], validate=True)
            files = ingest_zip(archive, data.get('selected'))
            if self.path == '/api/preview':
                return self.reply(200, {'files': files, 'workflows': sorted(WORKFLOWS),
                                        'provider': provider_info(), 'submitted_to_model': False})
            if data.get('consent') is not True:
                return self.reply(400, {'error': 'Approve submission of nonconfidential selected files first'})
            if data.get('provider') != provider_info()['id']:
                return self.reply(400, {'error': 'Preview and approve the current provider before submission'})
            now = time.monotonic()
            self.server.calls = [stamp for stamp in self.server.calls if now - stamp < 60]
            if len(self.server.calls) >= 5:
                return self.reply(429, {'error': 'Workspace limit reached; wait before another investigation'})
            self.server.calls.append(now)
            result = self.server.analyze(archive, data['selected'], data.get('task'), data.get('workflow'))
            self.reply(200, result)
        except (ValueError, TypeError, KeyError, binascii.Error, WorkspaceError):
            self.reply(400, {'error': 'Invalid archive, selection or task; check the input limits'})
        except ProviderError as exc:
            self.reply(502, {'error': str(exc)})
        except Exception:
            self.reply(500, {'error': 'Workspace request failed'})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error('Port must be between 1 and 65535')
    try:
        server = WorkspaceServer(args.port, os.environ.get('DEVTWIN_SESSION_TOKEN', ''))
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
