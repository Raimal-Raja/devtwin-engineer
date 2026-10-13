import hashlib
import io
import json
import unittest
from unittest.mock import Mock
import zipfile

from backend.patches import export_candidate, propose
from backend.workspace import WorkspaceError
from backend.nvidia import ProviderError


def fixture(source='def total(x):\n    return x - None\n'):
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w') as archive:
        archive.writestr('app.py', source)
        archive.writestr('test_app.py', '# protected original test\n')
        archive.writestr('unselected.md', 'not exported')
    return output.getvalue()


class PatchTests(unittest.TestCase):
    def setUp(self):
        self.source = 'def total(x):\n    return x - None\n'
        self.archive = fixture(self.source)
        self.selected = ['app.py', 'test_app.py']
        self.patch = {'path': 'app.py', 'base_sha256': hashlib.sha256(self.source.encode()).hexdigest(),
                      'replacement': 'def total(x):\n    return x\n'}

    def test_proposal_is_unverified_and_hash_bound(self):
        send = Mock(return_value={'content': json.dumps({'path': 'app.py',
                    'replacement': self.patch['replacement'], 'explanation': 'Proposed optional discount repair'}),
                    'provider': 'groq', 'model': 'synthetic'})
        result = propose(self.archive, self.selected, 'Repair the function', send=send)
        self.assertEqual(result['patch'], self.patch)
        self.assertIn('-    return x - None', result['diff'])
        self.assertIn('+    return x', result['diff'])
        self.assertEqual(result['executed_commands'], [])
        self.assertEqual(result['applied_changes'], [])
        self.assertEqual(send.call_count, 1)

    def test_approved_export_preserves_other_selected_files(self):
        before = hashlib.sha256(self.archive).hexdigest()
        candidate, hashes = export_candidate(self.archive, self.selected, self.patch, approved=True)
        with zipfile.ZipFile(io.BytesIO(candidate)) as archive:
            self.assertEqual(archive.namelist(), self.selected)
            self.assertEqual(archive.read('app.py').decode(), self.patch['replacement'])
            self.assertEqual(archive.read('test_app.py'), b'# protected original test\n')
        self.assertEqual(hashlib.sha256(self.archive).hexdigest(), before)
        self.assertEqual(len(hashes), 2)

    def test_approval_conflict_and_unselected_paths_reject(self):
        with self.assertRaises(WorkspaceError):
            export_candidate(self.archive, self.selected, self.patch)
        for change in ({'base_sha256': 'stale'}, {'path': '../app.py'}, {'path': 'unselected.md'},
                       {'path': 'test_app.py'},
                       {'replacement': self.source}, {'replacement': ''}):
            with self.assertRaises(WorkspaceError):
                export_candidate(self.archive, self.selected, {**self.patch, **change}, approved=True)
        with self.assertRaises(WorkspaceError):
            export_candidate(fixture('changed\n'), self.selected, self.patch, approved=True)

    def test_secret_binary_and_size_limits_reject(self):
        for text in ('nvapi-' + 'a' * 30, 'a\x00b', 'a' * 8001):
            with self.assertRaises(WorkspaceError):
                export_candidate(self.archive, self.selected, {**self.patch, 'replacement': text}, approved=True)

    def test_model_invalid_output_does_not_apply(self):
        for payload in ({}, {'path': 'other.py', 'replacement': 'pass', 'explanation': 'bad path'},
                        {'path': 'app.py', 'replacement': self.source, 'explanation': 'no change'}):
            with self.assertRaises(ProviderError):
                propose(self.archive, self.selected, 'Repair', send=Mock(return_value={'content': json.dumps(payload)}))

    def test_invalid_task_never_calls_provider(self):
        send = Mock()
        for task in ('', 'x' * 2001, 'nvapi-' + 'a' * 30):
            with self.assertRaises(WorkspaceError):
                propose(self.archive, self.selected, task, send=send)
        send.assert_not_called()
