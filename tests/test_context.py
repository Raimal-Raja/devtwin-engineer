import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('context', ROOT / 'scripts/collect_context.py')
context = importlib.util.module_from_spec(spec)
spec.loader.exec_module(context)


class ContextTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_exclusions_and_size_limit(self):
        (self.root / '.git').mkdir()
        (self.root / '.git/private').write_text('private')
        (self.root / '.env').write_text('SECRET=example')
        (self.root / 'large.py').write_bytes(b'x' * 20)
        (self.root / 'small.py').write_text('pass')
        result = context.collect(self.root, max_file_bytes=10)
        self.assertEqual([e['path'] for e in result['entries']], ['small.py'])

    def test_entry_scan_and_depth_bounds(self):
        for name in ('a', 'b', 'c'):
            (self.root / name).mkdir()
            (self.root / name / 'file.py').write_text('pass')
        result = context.collect(self.root, max_entries=2)
        self.assertEqual(len(result['entries']), 2)
        self.assertTrue(result['truncated'])
        result = context.collect(self.root, max_scan=2)
        self.assertEqual(result['scanned'], 2)
        self.assertTrue(result['truncated'])
        result = context.collect(self.root, max_depth=0)
        self.assertTrue(result['truncated'])
        self.assertTrue(all(e['kind'] == 'directory' for e in result['entries']))

    def test_missing_root_and_invalid_limits(self):
        with self.assertRaises(ValueError):
            context.collect(self.root / 'missing')
        with self.assertRaises(ValueError):
            context.collect(self.root, max_entries=0)

    def test_permission_error_is_reported(self):
        with patch.object(context.os, 'scandir', side_effect=PermissionError()):
            result = context.collect(self.root)
        self.assertEqual(result['errors'], [{'path': '.', 'error': 'PermissionError'}])

    def test_symlink_is_skipped_when_supported(self):
        (self.root / 'source.py').write_text('pass')
        try:
            (self.root / 'link.py').symlink_to(self.root / 'source.py')
        except OSError as exc:
            self.skipTest(f'Symlink creation unavailable: {type(exc).__name__}')
        self.assertEqual([e['path'] for e in context.collect(self.root)['entries']], ['source.py'])
