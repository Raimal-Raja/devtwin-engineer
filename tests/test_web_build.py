from pathlib import Path
import tempfile
import unittest
import zipfile
from scripts.build_web import build_web
from scripts.verify_archive import verify

ROOT = Path(__file__).resolve().parents[1]


class WebBuildTests(unittest.TestCase):
    def test_downloads_are_complete_and_output_is_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'web'
            build_web(ROOT, output)
            self.assertTrue(verify(output / 'downloads/devtwin-engineer-skill.zip')['valid'])
            with zipfile.ZipFile(output / 'downloads/devtwin-engineer-plugin.zip') as archive:
                for name in ['.agents/plugins/marketplace.json', '.claude-plugin/marketplace.json',
                             'plugins/devtwin-engineer/.codex-plugin/plugin.json',
                             'plugins/devtwin-engineer/.claude-plugin/plugin.json',
                             'plugins/devtwin-engineer/skills/devtwin-engineer/SKILL.md']:
                    self.assertIn('devtwin-engineer-marketplace/' + name, archive.namelist())
            page = (output / 'index.html').read_bytes()
            with self.assertRaises(ValueError):
                build_web(ROOT, output)
            self.assertEqual((output / 'index.html').read_bytes(), page)
