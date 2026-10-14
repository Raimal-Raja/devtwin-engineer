"""Build a private development workspace ZIP; explicit files only, no credentials."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

BACKEND = ('__init__.py', 'github.py', 'investigate.py', 'nvidia.py', 'patches.py',
           'providers.py', 'repair.py', 'runner.py', 'server.py', 'workspace.py',
           'ui/app.mjs', 'ui/index.html', 'ui/style.css')
REFERENCES = ('api-compatibility', 'bug-reproduction', 'change-impact', 'database-review',
              'delivery-preparation', 'dependency-diagnosis', 'documentation-verification',
              'feature-tracing', 'implementation', 'performance-investigation',
              'regression-testing', 'repository-understanding', 'routing', 'security-review')
FILES = (('Dockerfile', 'compose.yaml', '.dockerignore', 'scripts/prepare_docker.py',
          'docs/docker.md', 'docs/repair-loop.md', 'docs/isolated-runner.md', 'docs/free-hosting.md')
         + tuple('backend/' + name for name in BACKEND)
         + tuple('references/' + name + '.md' for name in REFERENCES))


def build(root, output):
    root, output = Path(root).resolve(), Path(output).absolute()
    if output.exists():
        raise ValueError('Preserve existing output; select a new filename')
    for path in (output, *output.parents):
        if path.is_symlink() or (path.exists() and getattr(path.stat(), 'st_file_attributes', 0) & 0x400):
            raise ValueError('Output must not contain links or junctions')
    payloads = {}
    for name in FILES:
        path = root / name
        for component in (path, *path.parents):
            if component == root:
                break
            if component.is_symlink() or (component.exists() and getattr(component.stat(), 'st_file_attributes', 0) & 0x400):
                raise ValueError('Source files must not contain links or junctions')
        if not path.resolve().is_relative_to(root) or not path.is_file():
            raise ValueError('Missing workspace resource: ' + name)
        with path.open('rb') as stream:
            data = stream.read(1048577)
        if len(data) > 1048576:
            raise ValueError('Workspace resource exceeds size limit')
        payloads[name] = data.decode('utf-8').replace('\r\n', '\n').encode()
    manifest = {name: {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
                for name, data in sorted(payloads.items())}
    payloads['manifest.json'] = json.dumps({'schema': 1, 'files': manifest,
        'distribution': 'Private development candidate; license undecided; not a public production service'},
        sort_keys=True, indent=2).encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('xb') as stream, zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_STORED) as archive:
        for name, data in sorted(payloads.items()):
            info = zipfile.ZipInfo('devtwin-workspace/' + name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    return {'archive': str(output), 'files': len(manifest),
            'sha256': hashlib.sha256(output.read_bytes()).hexdigest(), 'credentials_included': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(build(args.root, args.output), indent=2))
    except (OSError, ValueError, UnicodeError) as exc:
        print(json.dumps({'error': str(exc) if isinstance(exc, ValueError) else type(exc).__name__}))
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
