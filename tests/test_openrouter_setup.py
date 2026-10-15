import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from backend.providers import ProviderError
from scripts import start_openrouter


class OpenRouterSetupTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        (self.root / '.env.docker').write_text('local config\n')
        for context in (patch.object(start_openrouter, 'ROOT', self.root),
                        patch.object(start_openrouter, 'find_docker', return_value='docker'),
                        patch.dict(start_openrouter.os.environ, {'OPENROUTER_API_KEY': '',
                                   'NVIDIA_API_KEY': 'unrelated-secret', 'GROQ_API_KEY': 'unrelated-secret',
                                   'GEMINI_API_KEY': 'unrelated-secret'}),
                        patch('sys.stdout', new_callable=io.StringIO)):
            context.start()
            self.addCleanup(context.stop)

    def test_smoke_failure_does_not_change_running_containers(self):
        with patch.object(start_openrouter.getpass, 'getpass', return_value='a' * 64), \
                patch.object(start_openrouter, 'complete', side_effect=ProviderError('quota reached')), \
                patch.object(start_openrouter.subprocess, 'run') as run:
            self.assertEqual(start_openrouter.main([]), 1)
            run.assert_not_called()

    def test_setup_never_saves_key_or_forwards_unrelated_provider_keys(self):
        key = 'synthetic-hidden-key-' + 'a' * 40
        original = (self.root / '.env.docker').read_bytes()
        with patch.object(start_openrouter.getpass, 'getpass', return_value=key), \
                patch.object(start_openrouter, 'complete', return_value={'model': 'example/model:free'}), \
                patch.object(start_openrouter.subprocess, 'run', return_value=Mock(returncode=0)) as run:
            self.assertEqual(start_openrouter.main(['--allow-public-inputs']), 0)
            environment = run.call_args.kwargs['env']
            self.assertEqual(environment['OPENROUTER_API_KEY'], key)
            self.assertEqual(environment['DEVTWIN_PROVIDER'], 'openrouter')
            self.assertEqual(environment['DEVTWIN_OPENROUTER_DATA_POLICY'], 'allow')
            for name in ('NVIDIA_API_KEY', 'GROQ_API_KEY', 'GEMINI_API_KEY'):
                self.assertNotIn(name, environment)
            self.assertNotIn(key, str(run.call_args.args))
            self.assertEqual((self.root / '.env.docker').read_bytes(), original)
            self.assertEqual([p.name for p in self.root.iterdir()], ['.env.docker'])


if __name__ == '__main__':
    unittest.main()
