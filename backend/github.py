"""Read selected GitHub blobs at one pinned commit; no clone, extraction or writes."""
import base64
import hashlib
from http.client import HTTPException
import io
import json
import os
import re
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import Request, build_opener
import zipfile

from .nvidia import NoRedirect
from .workspace import MAX_TOTAL, WorkspaceError, ingest_zip

SHA = re.compile(r'[0-9a-f]{40}')


class GithubError(Exception):
    pass


def repository_name(value):
    if not isinstance(value, str):
        raise WorkspaceError('Use owner/repository or an https://github.com repository URL')
    if value.startswith('https://'):
        url = urlsplit(value)
        if url.netloc != 'github.com' or url.query or url.fragment:
            raise WorkspaceError('Only plain github.com repository URLs are supported')
        value = url.path.strip('/')
    if value.endswith('.git'):
        value = value[:-4]
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,100}/[A-Za-z0-9_.-]{1,100}', value) or value.split('/')[1] in ('.', '..'):
        raise WorkspaceError('Use owner/repository, without a branch or file URL')
    return value


def get_json(path):
    # Callers construct only fixed GitHub REST routes; never follow response URLs.
    if not path.startswith('/repos/') or '://' in path:
        raise GithubError('Invalid GitHub route')
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'DevTwin-Engineer',
               'X-GitHub-Api-Version': '2022-11-28'}
    token = os.environ.get('DEVTWIN_GITHUB_TOKEN', '').strip()
    if token:
        if not token.isascii() or any(ord(char) < 33 for char in token):
            raise GithubError('Invalid backend GitHub token')
        headers['Authorization'] = 'Bearer ' + token
    request = Request('https://api.github.com' + path, headers=headers, method='GET')
    try:
        with build_opener(NoRedirect()).open(request, timeout=20) as response:
            raw = response.read(1024 * 1024 + 1)
    except HTTPError as exc:
        status = exc.code
        exc.close()
        raise GithubError('GitHub request failed (HTTP %s); check repository access or API limits' % status) from None
    except (URLError, OSError, TimeoutError, HTTPException):
        raise GithubError('GitHub connection failed; no retry was made') from None
    if len(raw) > 1024 * 1024:
        raise GithubError('GitHub response exceeded the size limit')
    try:
        return json.loads(raw)
    except (ValueError, UnicodeError):
        raise GithubError('GitHub returned invalid JSON') from None


def import_repository(repository, ref, selected, *, fetch=get_json):
    name = repository_name(repository)
    if not isinstance(ref, str) or not ref.strip() or len(ref) > 200 or any(ord(c) < 32 for c in ref):
        raise WorkspaceError('Choose an explicit branch, tag or commit (at most 200 characters)')
    # Validate requested paths before touching the network.
    dummy = io.BytesIO()
    if not isinstance(selected, list) or not selected or len(selected) > 30 or any(not isinstance(p, str) for p in selected):
        raise WorkspaceError('Select 1 to 30 text files')
    with zipfile.ZipFile(dummy, 'w') as archive:
        for path in selected:
            archive.writestr(path, '')
    ingest_zip(dummy.getvalue(), selected)
    route = '/repos/' + name
    try:
        metadata = fetch(route)
        private = metadata['private']
        if type(private) is not bool:
            raise ValueError()
        commit = fetch(route + '/commits/' + quote(ref, safe=''))
        commit_sha, tree_sha = commit['sha'], commit['commit']['tree']['sha']
        if not isinstance(commit_sha, str) or not SHA.fullmatch(commit_sha) or not isinstance(tree_sha, str) or not SHA.fullmatch(tree_sha):
            raise ValueError()
        tree = fetch(route + '/git/trees/' + tree_sha + '?recursive=1')
        if tree.get('truncated') is not False or not isinstance(tree['tree'], list) or len(tree['tree']) > 5000:
            raise GithubError('Repository tree is incomplete or too large for this importer')
        entries = {entry['path']: entry for entry in tree['tree']}
        output = io.BytesIO()
        total = 0
        with zipfile.ZipFile(output, 'w') as archive:
            for path in selected:
                entry = entries.get(path)
                if (not entry or entry.get('type') != 'blob' or entry.get('mode') not in ('100644', '100755')
                        or type(entry.get('size')) is not int or not 0 <= entry['size'] <= MAX_TOTAL - total
                        or not isinstance(entry.get('sha'), str) or not SHA.fullmatch(entry['sha'])):
                    raise WorkspaceError('Selected file is missing, linked, a submodule or exceeds limits')
                blob = fetch(route + '/git/blobs/' + entry['sha'])
                if blob.get('encoding') != 'base64' or not isinstance(blob.get('content'), str):
                    raise ValueError()
                raw = base64.b64decode(''.join(blob['content'].split()), validate=True)
                if len(raw) != entry['size'] or len(raw) > MAX_TOTAL - total:
                    raise ValueError()
                digest = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\x00' + raw).hexdigest()
                if digest != entry['sha']:
                    raise ValueError()
                total += len(raw)
                archive.writestr(path, raw)
        data = output.getvalue()
        files = ingest_zip(data, selected)
    except (KeyError, TypeError, ValueError) as exc:
        if isinstance(exc, WorkspaceError):
            raise
        raise GithubError('GitHub metadata or blob integrity validation failed') from None
    return {'archive': base64.b64encode(data).decode(), 'repository': name, 'ref': ref,
            'commit': commit_sha, 'private': private,
            'files': [{'path': file['path'], 'sha256': file['sha256']} for file in files],
            'submitted_to_model': False, 'github_writes': False}
