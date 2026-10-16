"""Bounded metadata-only inventory; never read source contents or follow links."""
import argparse
import fnmatch
import json
import os
from pathlib import Path
import stat

EXCLUDED = {'.git', '.venv', 'venv', 'node_modules', '__pycache__', '.pytest_cache',
            '.workspaces', '.aws', '.ssh', 'dist', 'build'}
SENSITIVE = ('.env', '.env.*', '*.pem', '*.key', 'credentials', '*.log')


def collect(root, max_entries=1000, max_scan=5000, max_depth=8, max_file_bytes=1048576):
    if min(max_entries, max_scan, max_file_bytes) < 1 or max_depth < 0:
        raise ValueError('Limits must be positive; depth may be zero')
    root = Path(root)
    if root.is_symlink() or not root.is_dir() or getattr(root.stat(), 'st_file_attributes', 0) & 0x400:
        raise ValueError('Root must be an existing directory, not a symlink')
    root = root.resolve()
    result = {'root': str(root), 'entries': [], 'errors': [], 'truncated': False, 'scanned': 0}
    pending = [(root, 0)]
    while pending:
        directory, depth = pending.pop()
        entries = []
        try:
            with os.scandir(directory) as iterator:
                for entry in iterator:
                    if result['scanned'] >= max_scan:
                        result['truncated'] = True
                        break
                    result['scanned'] += 1
                    entries.append(entry)
        except OSError as exc:
            result['errors'].append({'path': directory.relative_to(root).as_posix(),
                                     'error': type(exc).__name__})
            continue
        children = []
        for entry in sorted(entries, key=lambda item: item.name):
            if entry.name.lower() in EXCLUDED or any(fnmatch.fnmatch(entry.name.lower(), pattern) for pattern in SENSITIVE):
                continue
            try:
                metadata = entry.stat(follow_symlinks=False)
                # Windows directory junctions are reparse points, too.
                if entry.is_symlink() or getattr(metadata, 'st_file_attributes', 0) & 0x400:
                    continue
                relative = Path(entry.path).relative_to(root).as_posix()
                if stat.S_ISDIR(metadata.st_mode):
                    if depth < max_depth:
                        children.append((Path(entry.path), depth + 1))
                    else:
                        result['truncated'] = True
                    item = {'path': relative, 'kind': 'directory'}
                elif stat.S_ISREG(metadata.st_mode):
                    if metadata.st_size > max_file_bytes:
                        continue
                    item = {'path': relative, 'kind': 'file', 'bytes': metadata.st_size}
                else:
                    continue
                if len(result['entries']) >= max_entries:
                    result['truncated'] = True
                    return result
                result['entries'].append(item)
            except OSError as exc:
                result['errors'].append({'path': Path(entry.path).relative_to(root).as_posix(),
                                         'error': type(exc).__name__})
        pending.extend(reversed(children))
        if result['scanned'] >= max_scan and pending:
            result['truncated'] = True
            break
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--max-entries', type=int, default=1000)
    parser.add_argument('--max-scan', type=int, default=5000)
    parser.add_argument('--max-depth', type=int, default=8)
    parser.add_argument('--max-file-bytes', type=int, default=1048576)
    args = parser.parse_args()
    try:
        result = collect(args.root, args.max_entries, args.max_scan, args.max_depth, args.max_file_bytes)
    except (OSError, ValueError) as exc:
        print(json.dumps({'error': str(exc)}))
        return 2
    print(json.dumps(result, indent=2))
    return 1 if result['errors'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
