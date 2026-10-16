"""Check archive paths, manifest integrity and extracted package links without running code."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import tempfile
import zipfile

try:
    from .validate_package import validate
except ImportError:
    from validate_package import validate

PREFIX = 'devtwin-engineer/'
MAX_FILE = 1048576
MAX_TOTAL = 33554432


def verify(path):
    with zipfile.ZipFile(path) as archive:
        entries = archive.infolist()
        if not entries or len(entries) > 1000 or sum(e.file_size for e in entries) > MAX_TOTAL:
            raise ValueError('Archive size or entry limit exceeded')
        names = set()
        payloads = {}
        for entry in entries:
            name = entry.filename
            parts = PurePosixPath(name)
            if not name.startswith(PREFIX) or parts.as_posix() != name or '..' in parts.parts or '\\' in name:
                raise ValueError('Unsafe archive path')
            for part in parts.parts:
                if re.search(r'[<>:"|?*]', part) or part.endswith(('.', ' ')) or re.fullmatch(r'(?i)(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?', part):
                    raise ValueError('Unsafe portable filename')
            if name.casefold() in names or entry.is_dir() or stat.S_ISLNK(entry.external_attr >> 16):
                raise ValueError('Duplicate, directory or symlink archive entry')
            names.add(name.casefold())
            if entry.file_size > MAX_FILE:
                raise ValueError('Archive file size limit exceeded')
            with archive.open(entry) as stream:
                payload = stream.read(MAX_FILE + 1)
            if len(payload) > MAX_FILE:
                raise ValueError('Archive file size limit exceeded')
            payloads[name[len(PREFIX):]] = payload
    if 'manifest.json' not in payloads:
        raise ValueError('Missing archive manifest')
    manifest = json.loads(payloads.pop('manifest.json'))
    if not isinstance(manifest, dict) or manifest.get('schema') != 1 or not isinstance(manifest.get('files'), dict):
        raise ValueError('Invalid archive manifest')
    if set(manifest['files']) != set(payloads):
        raise ValueError('Manifest file list mismatch')
    for name, payload in payloads.items():
        expected = manifest['files'][name]
        if not isinstance(expected, dict) or expected.get('bytes') != len(payload) or expected.get('sha256') != hashlib.sha256(payload).hexdigest():
            raise ValueError('Manifest integrity mismatch: ' + name)
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        for name, payload in payloads.items():
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
        errors = validate(root)
        if errors:
            raise ValueError('Extracted package invalid: ' + '; '.join(errors))
    return {'valid': True, 'files': len(payloads), 'signature_verified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.archive)
    except (OSError, ValueError, zipfile.BadZipFile, RuntimeError) as exc:
        print(json.dumps({'valid': False, 'error': str(exc) if isinstance(exc, ValueError) else type(exc).__name__}))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
