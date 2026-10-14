"""Prepare private local Compose tokens using already downloaded official images."""
import argparse
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.runner import find_docker


def image_digest(docker, tag, repository):
    result = subprocess.run([docker, 'image', 'inspect', tag, '--format', '{{json .RepoDigests}}'],
                            capture_output=True, text=True, timeout=15)
    if result.returncode:
        raise ValueError('Preload the official ' + tag + ' image first')
    values = json.loads(result.stdout)
    for value in values:
        if re.fullmatch(repository + r'@sha256:[0-9a-f]{64}', value):
            return value
    raise ValueError('Official image digest could not be verified')


def prepare(root):
    root = Path(root).resolve()
    docker = find_docker()
    if not docker or not (root / 'compose.yaml').is_file():
        raise ValueError('Docker and the project Compose configuration are required')
    runner = image_digest(docker, 'python:3.12-slim', 'python')
    cli = image_digest(docker, 'docker:cli', 'docker')
    destination = root / '.env.docker'
    if destination.exists() or destination.is_symlink():
        raise ValueError('Preserve existing .env.docker; preparation refuses to overwrite it')
    descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'w', encoding='utf-8') as stream:
        stream.write('DEVTWIN_SESSION_TOKEN=' + secrets.token_hex(32) + '\n')
        stream.write('DEVTWIN_WORKER_TOKEN=' + secrets.token_hex(32) + '\n')
        stream.write('DEVTWIN_RUNNER_IMAGE=' + runner + '\n')
        stream.write('DEVTWIN_DOCKER_CLI_IMAGE=' + cli + '\n')
    return {'env_file': str(destination), 'runner_image': runner, 'docker_cli_image': cli,
            'provider_keys_saved': False, 'tokens_displayed': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    try:
        result = prepare(args.root)
    except (OSError, ValueError, subprocess.SubprocessError):
        print(json.dumps({'prepared': False, 'error': 'Check installed/preloaded Docker images and preserve any existing environment file'}))
        return 1
    print(json.dumps({'prepared': True, **result}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
