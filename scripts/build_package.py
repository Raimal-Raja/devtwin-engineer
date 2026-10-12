"""Build a private-use skill ZIP from an explicit file allowlist."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import tempfile
import zipfile

try:
    from .validate_package import validate
except ImportError:
    from validate_package import validate

PREFIX = 'devtwin-engineer'


def build(root, output):
    root = Path(root)
    output = Path(output)
    if output.exists():
        raise ValueError('Output already exists; use a new filename')
    errors = validate(root)
    if errors:
        raise ValueError('Source package validation failed: ' + '; '.join(errors))
    root = root.resolve()
    entries = json.loads((root / 'package-files.json').read_text(encoding='utf-8'))
    if not isinstance(entries, list) or not entries or any(not isinstance(item, str) for item in entries):
        raise ValueError('Package allowlist must be a non-empty list of paths')
    if len(entries) != len(set(entries)):
        raise ValueError('Duplicate allowlist paths')
    payloads = {}
    for relative in entries:
        parts = PurePosixPath(relative)
        if parts.is_absolute() or '..' in parts.parts or '\\' in relative or ':' in relative or parts.as_posix() != relative or relative == 'manifest.json':
            raise ValueError('Unsafe allowlist path')
        path = root / relative
        for component in (path, *path.parents):
            if component == root:
                break
            if component.is_symlink() or (component.exists() and getattr(component.stat(), 'st_file_attributes', 0) & 0x400):
                raise ValueError('Allowlist paths must not contain links or junctions')
        if not path.resolve().is_relative_to(root) or not path.is_file():
            raise ValueError('Missing or unsafe allowlist file: ' + relative)
        with path.open('rb') as stream:
            content = stream.read(1048577)
        if len(content) > 1048576:
            raise ValueError('Allowlist file exceeds size limit')
        payloads[relative] = content.decode('utf-8').replace('\r\n', '\n').encode('utf-8')
    # Validate the selected resources in isolation, not only the development tree.
    with tempfile.TemporaryDirectory() as folder:
        extracted = Path(folder)
        for relative, content in payloads.items():
            path = extracted / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        errors = validate(extracted)
        if errors:
            raise ValueError('Selected package validation failed: ' + '; '.join(errors))
    manifest = {name: {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
                for name, data in sorted(payloads.items())}
    payloads['manifest.json'] = (json.dumps({'schema': 1, 'files': manifest}, indent=2, sort_keys=True) + '\n').encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive file creation refuses to overwrite another build or user file.
    with output.open('xb') as stream:
        with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_STORED) as archive:
            for relative, content in sorted(payloads.items()):
                info = zipfile.ZipInfo(PREFIX + '/' + relative, date_time=(1980, 1, 1, 0, 0, 0))
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                archive.writestr(info, content)
    return {'archive': str(output.resolve()), 'files': len(manifest),
            'sha256': hashlib.sha256(output.read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    try:
        result = build(args.root, args.output)
    except (OSError, ValueError, UnicodeError) as exc:
        print(json.dumps({'error': str(exc) if isinstance(exc, ValueError) else type(exc).__name__}))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
