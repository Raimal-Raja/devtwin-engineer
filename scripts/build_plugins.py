"""Build private Codex/Claude plugin marketplaces from the canonical skill bundle."""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import zipfile

try:
    from .build_package import build
    from .verify_archive import verify
except ImportError:
    from build_package import build
    from verify_archive import verify


def build_plugins(root, output):
    output = Path(output).absolute()
    # No overwrite or writes through junctions, including a linked ancestor.
    for path in (output, *output.parents):
        if path.is_symlink() or (path.exists() and getattr(path.stat(), 'st_file_attributes', 0) & 0x400):
            raise ValueError('Output must not contain links or junctions')
    if output.exists():
        raise ValueError('Output already exists; choose a fresh directory')
    with tempfile.TemporaryDirectory() as folder:
        archive = Path(folder) / 'skill.zip'
        built = build(root, archive)
        verify(archive)
        payloads = {}
        with zipfile.ZipFile(archive) as bundle:
            for entry in bundle.infolist():
                relative = entry.filename.removeprefix('devtwin-engineer/')
                payloads['plugins/devtwin-engineer/skills/devtwin-engineer/' + relative] = bundle.read(entry)
        identity = {'name': 'devtwin-engineer', 'version': '0.0.1',
                    'description': 'Evidence-based Python investigation, focused repairs and regression verification.'}
        portable = dict(identity, **{'$schema': 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json'})
        codex = dict(identity, skills='./skills/', interface={
            'displayName': 'DevTwin Engineer', 'shortDescription': 'Investigate code and verify repairs',
            'longDescription': identity['description'], 'developerName': 'DevTwin Engineer',
            'category': 'Developer Tools'})
        claude = dict(identity)  # Default skills/ scan; no duplicate custom paths.
        documents = {
            'plugins/devtwin-engineer/plugin.json': portable,
            'plugins/devtwin-engineer/.codex-plugin/plugin.json': codex,
            'plugins/devtwin-engineer/.claude-plugin/plugin.json': claude,
            '.agents/plugins/marketplace.json': {
                'name': 'devtwin-engineer-local', 'interface': {'displayName': 'DevTwin Engineer'},
                'plugins': [{'name': identity['name'], 'source': {
                    'source': 'local', 'path': './plugins/devtwin-engineer'}}]},
            '.claude-plugin/marketplace.json': {
                'name': 'devtwin-engineer-local', 'owner': {'name': 'DevTwin Engineer'},
                'plugins': [{'name': identity['name'], 'source': './plugins/devtwin-engineer'}]},
        }
        for name, data in documents.items():
            payloads[name] = (json.dumps(data, indent=2, sort_keys=True) + '\n').encode()
        hashes = {name: hashlib.sha256(data).hexdigest() for name, data in sorted(payloads.items())}
        payloads['build-manifest.json'] = (json.dumps({
            'schema': 1, 'skill_archive_sha256': built['sha256'], 'files': hashes,
            'runtime_activation_verified': False}, indent=2, sort_keys=True) + '\n').encode()
        output.mkdir(parents=True, exist_ok=False)
        for name, data in sorted(payloads.items()):
            target = output / name
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as stream:
                stream.write(data)
    return {'directory': str(output), 'files': len(payloads), 'skill_archive_sha256': built['sha256'],
            'runtime_activation_verified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    try:
        result = build_plugins(args.root, args.output)
    except (OSError, ValueError, UnicodeError, zipfile.BadZipFile) as exc:
        print(json.dumps({'error': str(exc) if isinstance(exc, ValueError) else type(exc).__name__}))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
