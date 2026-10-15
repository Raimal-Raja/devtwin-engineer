"""Start the localhost Docker app with OpenRouter Free; prompt privately, never save the key."""
import argparse
import getpass
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.providers import complete, ProviderError
from backend.runner import find_docker


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--allow-public-inputs', action='store_true',
                        help='Allow upstream storage/training; public or synthetic inputs only')
    args = parser.parse_args(argv)
    if args.allow_public_inputs:
        os.environ['DEVTWIN_OPENROUTER_DATA_POLICY'] = 'allow'
    docker = find_docker()
    if not docker or not (ROOT / '.env.docker').is_file():
        print('Start Docker and prepare .env.docker first; see docs/docker.md.')
        return 1
    key = os.environ.get('OPENROUTER_API_KEY', '').strip()
    if not key:
        key = getpass.getpass('OpenRouter API key (hidden; not saved): ').strip()
    if len(key) < 32 or not key.isascii() or any(ord(char) < 33 for char in key):
        print('A valid OpenRouter key is required; no request was sent.')
        return 1
    os.environ['DEVTWIN_PROVIDER'] = 'openrouter'
    os.environ.setdefault('DEVTWIN_OPENROUTER_MODEL', 'nvidia/nemotron-3-ultra-550b-a55b:free')
    if os.environ.get('DEVTWIN_OPENROUTER_DATA_POLICY') == 'allow':
        print('Public/synthetic inputs only: upstream providers may store inputs or use them for training.')
    os.environ['OPENROUTER_API_KEY'] = key
    try:
        result = complete('Reply with one short sentence confirming this synthetic development check.', max_tokens=2048)
    except ProviderError as exc:
        print(str(exc))
        return 1
    print('Free-provider smoke passed. Actual model: ' + result['model'])
    environment = os.environ.copy()
    environment['PATH'] = str(Path(docker).parent) + os.pathsep + environment.get('PATH', '')
    # Do not pass unrelated provider credentials to the app during this setup.
    for name in ('NVIDIA_API_KEY', 'GROQ_API_KEY', 'GEMINI_API_KEY'):
        environment.pop(name, None)
    try:
        result = subprocess.run([docker, 'compose', '--env-file', '.env.docker', '-p', 'devtwin-engineer',
                                 'up', '-d', '--build', '--wait', '--wait-timeout', '90'],
                                cwd=ROOT, env=environment, timeout=240)
    except (OSError, subprocess.SubprocessError):
        print('Docker startup failed; check the engine and preserve your configuration.')
        return 1
    if result.returncode:
        return 1
    print('Ready to test at http://127.0.0.1:8765. Use the workspace token from .env.docker, not the API key.')
    print('The API key is held in the app container environment; never share resolved Compose configuration or container environments.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
