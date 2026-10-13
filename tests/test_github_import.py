import base64
import hashlib
import io
import json
import os
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError
import zipfile

from backend import github
from backend.workspace import WorkspaceError


class GithubImportTests(unittest.TestCase):
    def setUp(self):
        self.raw = b'def total(x):\n    return x\n'
        self.sha = hashlib.sha1(b'blob ' + str(len(self.raw)).encode() + b'\x00' + self.raw).hexdigest()
        self.commit = 'a' * 40
        self.tree = 'b' * 40
        self.entry = {'path': 'app.py', 'type': 'blob', 'mode': '100644', 'size': len(self.raw), 'sha': self.sha}

    def fetch(self, entry=None, truncated=False, raw=None):
        return Mock(side_effect=[{'private': False}, {'sha': self.commit, 'commit': {'tree': {'sha': self.tree}}},
                                 {'truncated': truncated, 'tree': [entry or self.entry]},
                                 {'encoding': 'base64', 'content': base64.b64encode(self.raw if raw is None else raw).decode()}])

    def test_pinned_commit_and_blob_integrity(self):
        fetch = self.fetch()
        result = github.import_repository('https://github.com/example/project', 'feature/test', ['app.py'], fetch=fetch)
        self.assertEqual(result['commit'], self.commit)
        self.assertFalse(result['submitted_to_model'])
        self.assertFalse(result['github_writes'])
        routes = [call.args[0] for call in fetch.call_args_list]
        self.assertIn('/commits/feature%2Ftest', routes[1])
        self.assertIn('/git/trees/' + self.tree, routes[2])
        self.assertIn('/git/blobs/' + self.sha, routes[3])
        with zipfile.ZipFile(io.BytesIO(base64.b64decode(result['archive']))) as archive:
            self.assertEqual(archive.read('app.py'), self.raw)

    def test_invalid_repo_paths_and_ref_never_fetch(self):
        fetch = Mock()
        for repository in ('https://evil.example/x/y', 'https://github.com/x/y/tree/main', 'x/../y', 'https://github.com/x/y?token=secret'):
            with self.assertRaises(WorkspaceError):
                github.import_repository(repository, 'main', ['app.py'], fetch=fetch)
        for selected in (['../app.py'], ['.env'], ['a.exe'], []):
            with self.assertRaises(WorkspaceError):
                github.import_repository('x/y', 'main', selected, fetch=fetch)
        with self.assertRaises(WorkspaceError):
            github.import_repository('x/y', '', ['app.py'], fetch=fetch)
        fetch.assert_not_called()

    def test_links_submodules_missing_and_size_rejected(self):
        for update in ({'mode': '120000'}, {'type': 'commit', 'mode': '160000'}, {'size': 16001}, {'path': 'other.py'}):
            fetch = self.fetch(entry={**self.entry, **update})
            with self.assertRaises(WorkspaceError):
                github.import_repository('x/y', 'main', ['app.py'], fetch=fetch)
            self.assertEqual(fetch.call_count, 3)

    def test_incomplete_tree_or_corrupt_blob_rejected(self):
        for fetch in (self.fetch(truncated=True), self.fetch(raw=b'corrupt')):
            with self.assertRaises(github.GithubError):
                github.import_repository('x/y', 'main', ['app.py'], fetch=fetch)

    def test_private_metadata_is_preserved(self):
        fetch = self.fetch()
        responses = list(fetch.side_effect)
        responses[0] = {'private': True}
        self.assertTrue(github.import_repository('x/y', 'main', ['app.py'], fetch=Mock(side_effect=responses))['private'])

    def test_backend_token_only_goes_to_fixed_github_host(self):
        with patch.dict(os.environ, {'DEVTWIN_GITHUB_TOKEN': 'fake-private-token'}), patch.object(github, 'build_opener') as factory:
            factory.return_value.open.return_value = io.BytesIO(b'{"private":true}')
            github.get_json('/repos/x/y')
            request = factory.return_value.open.call_args.args[0]
            self.assertEqual(request.full_url, 'https://api.github.com/repos/x/y')
            self.assertEqual(request.method, 'GET')
            self.assertNotIn('fake-private-token', request.full_url)
            self.assertEqual(request.get_header('Authorization'), 'Bearer fake-private-token')

    def test_error_body_and_token_never_returned(self):
        with patch.object(github, 'build_opener') as factory:
            factory.return_value.open.side_effect = HTTPError('url', 403, 'private-token', {}, io.BytesIO(b'private body'))
            with self.assertRaises(github.GithubError) as caught:
                github.get_json('/repos/x/y')
            self.assertNotIn('private-token', str(caught.exception))
            self.assertNotIn('private body', str(caught.exception))
