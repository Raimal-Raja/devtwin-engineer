import hashlib
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('changes', ROOT / 'scripts/inspect_changes.py')
changes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(changes)


@unittest.skipUnless(shutil.which('git'), 'Git unavailable')
class GitChangesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git('init', '-q')
        self.git('config', 'user.name', 'Synthetic Tester')
        self.git('config', 'user.email', 'tester@example.invalid')
        for name in ('tracked.txt', 'old name.txt'):
            (self.root / name).write_text('original\n', encoding='utf-8')
        self.git('add', '.')
        self.git('-c', 'core.hooksPath=', 'commit', '-qm', 'fixture')

    def git(self, *arguments):
        return subprocess.run(['git', '-C', str(self.root), *arguments], check=True,
                              capture_output=True, timeout=30)

    def test_clean_and_non_git(self):
        self.assertEqual(changes.inspect(self.root)['changes'], [])
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                changes.inspect(directory)

    def test_staged_unstaged_rename_untracked_and_preservation(self):
        source = self.root / 'tracked.txt'
        source.write_text('staged\n', encoding='utf-8')
        self.git('add', 'tracked.txt')
        source.write_text('staged and unstaged\n', encoding='utf-8')
        self.git('mv', 'old name.txt', 'new name.txt')
        (self.root / 'untracked ü.txt').write_text('private contents', encoding='utf-8')
        index = self.root / '.git/index'
        before_index = hashlib.sha256(index.read_bytes()).hexdigest()
        before_source = source.read_bytes()
        result = changes.inspect(self.root)
        records = {item['path']: item for item in result['changes']}
        self.assertEqual((records['tracked.txt']['index'], records['tracked.txt']['working_tree']), ('M', 'M'))
        self.assertEqual(records['new name.txt']['original_path'], 'old name.txt')
        self.assertTrue(records['untracked ü.txt']['untracked'])
        self.assertEqual(hashlib.sha256(index.read_bytes()).hexdigest(), before_index)
        self.assertEqual(source.read_bytes(), before_source)
        self.assertNotIn('private contents', str(result))

    def test_limits_and_inherited_git_environment(self):
        (self.root / 'one').write_text('one')
        (self.root / 'two').write_text('two')
        with patch.dict(os.environ, {'GIT_DIR': str(self.root / 'absent')}):
            result = changes.inspect(self.root, max_entries=1)
        self.assertEqual(len(result['changes']), 1)
        self.assertEqual(result['total_changes'], 2)
        self.assertTrue(result['truncated'])

    def test_subdirectory_reports_whole_tree(self):
        directory = self.root / 'subdir'
        directory.mkdir()
        (self.root / 'tracked.txt').write_text('changed')
        self.assertEqual(changes.inspect(directory)['changes'][0]['path'], 'tracked.txt')

    def test_repository_content_filter_is_not_executed(self):
        (self.root / '.gitattributes').write_text('*.txt filter=probe\n')
        self.git('config', 'filter.probe.clean', 'echo invoked >> filter-ran.txt; cat')
        self.git('config', 'filter.probe.required', 'true')
        (self.root / 'tracked.txt').write_text('changed contents\n')
        result = changes.inspect(self.root)
        self.assertTrue(any(item['path'] == 'tracked.txt' for item in result['changes']))
        self.assertFalse((self.root / 'filter-ran.txt').exists())


class StatusParsingTests(unittest.TestCase):
    def test_path_with_newline_and_rename(self):
        result = changes.parse_status('?? line\nbreak.txt\0R  new name\0old name\0')
        self.assertEqual(result[0]['path'], 'line\nbreak.txt')
        self.assertEqual(result[1]['original_path'], 'old name')

    def test_malformed_output(self):
        for output in ('bad\0', 'R  new\0'):
            with self.assertRaises(ValueError):
                changes.parse_status(output)

    def test_missing_git(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(OSError):
                changes.inspect(directory, git=str(Path(directory) / 'missing-git'))
