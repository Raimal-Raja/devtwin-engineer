import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from scripts.build_plugins import build_plugins
from scripts.validate_package import validate

ROOT = Path(__file__).resolve().parents[1]


class PluginBuildTests(unittest.TestCase):
    def test_marketplace_and_shared_skill_integrity(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'marketplace'
            result = build_plugins(ROOT, output)
            self.assertFalse(result['runtime_activation_verified'])
            plugin = output / 'plugins/devtwin-engineer'
            skill = plugin / 'skills/devtwin-engineer'
            self.assertEqual(validate(skill), [])
            self.assertEqual((skill / 'SKILL.md').read_text(), (ROOT / 'SKILL.md').read_text())
            for relative in ['plugin.json', '.codex-plugin/plugin.json', '.claude-plugin/plugin.json']:
                data = json.loads((plugin / relative).read_text())
                self.assertEqual(data['name'], 'devtwin-engineer')
                self.assertNotIn('hooks', data)
                self.assertNotIn('mcpServers', data)
            for relative in ['.agents/plugins/marketplace.json', '.claude-plugin/marketplace.json']:
                entry = json.loads((output / relative).read_text())['plugins'][0]
                source = entry['source']
                path = source['path'] if isinstance(source, dict) else source
                self.assertEqual((output / path).resolve(), plugin.resolve())
            manifest = json.loads((output / 'build-manifest.json').read_text())
            for relative, expected in manifest['files'].items():
                self.assertEqual(hashlib.sha256((output / relative).read_bytes()).hexdigest(), expected)
            before = (plugin / 'plugin.json').read_bytes()
            with self.assertRaises(ValueError):
                build_plugins(ROOT, output)
            self.assertEqual((plugin / 'plugin.json').read_bytes(), before)
