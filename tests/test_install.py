from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

from scripts.install_skill import install
from scripts.validate_package import validate

ROOT = Path(__file__).resolve().parents[1]


class InstallTests(unittest.TestCase):
    def test_both_runtime_layouts_validate_and_preserve_project_files(self):
        for runtime, layout in [('codex', '.agents/skills'), ('claude-code', '.claude/skills')]:
            with self.subTest(runtime=runtime), tempfile.TemporaryDirectory() as folder:
                project = Path(folder)
                note = project / 'user.txt'
                note.write_bytes(b'Unrelated user work\r\n')
                result = install(ROOT, project, runtime)
                destination = project / layout / 'devtwin-engineer'
                self.assertEqual(Path(result['installed']), destination.resolve())
                self.assertFalse(result['activation_verified'])
                self.assertEqual(validate(destination), [])
                self.assertTrue((destination / 'scripts/install_skill.py').is_file())
                self.assertEqual(note.read_bytes(), b'Unrelated user work\r\n')
                consumer = project / 'consumer'
                consumer.mkdir()
                copied = subprocess.run([sys.executable, '-B', str(destination / 'scripts/install_skill.py'),
                                         str(destination), str(consumer), '--runtime', runtime],
                                        capture_output=True, text=True, timeout=30)
                self.assertEqual(copied.returncode, 0, copied.stderr)
                self.assertFalse(json.loads(copied.stdout)['activation_verified'])
                self.assertEqual(validate(consumer / layout / 'devtwin-engineer'), [])

    def test_existing_installation_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder)
            destination = project / '.agents/skills/devtwin-engineer'
            destination.mkdir(parents=True)
            (destination / 'SKILL.md').write_bytes(b'user-owned skill')
            with self.assertRaisesRegex(ValueError, 'already exists'):
                install(ROOT, project, 'codex')
            self.assertEqual((destination / 'SKILL.md').read_bytes(), b'user-owned skill')

    def test_invalid_runtime_or_missing_project_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError, 'Unknown runtime'):
                install(ROOT, folder, 'other')
            with self.assertRaisesRegex(ValueError, 'existing directory'):
                install(ROOT, Path(folder) / 'missing', 'codex')
