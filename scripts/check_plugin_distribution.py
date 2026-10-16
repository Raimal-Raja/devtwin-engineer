"""Verify the checked-in marketplace matches a fresh canonical plugin build."""
import argparse
import json
from pathlib import Path
import tempfile

try:
    from .build_plugins import build_plugins
except ImportError:
    from build_plugins import build_plugins


def check(root):
    root = Path(root).resolve()
    errors = []
    with tempfile.TemporaryDirectory() as folder:
        output = Path(folder) / 'marketplace'
        build_plugins(root, output)
        for source in sorted(output.rglob('*')):
            if not source.is_file():
                continue
            relative = source.relative_to(output)
            if relative.as_posix() == 'build-manifest.json':
                relative = Path('plugin-build-manifest.json')
            target = root / relative
            if target.is_symlink() or not target.is_file():
                errors.append('Missing or linked: ' + relative.as_posix())
            elif target.read_bytes() != source.read_bytes():
                errors.append('Outdated: ' + relative.as_posix())
        expected = {p.relative_to(output).as_posix() for p in output.rglob('*') if p.is_file()}
        plugin = root / 'plugins/devtwin-engineer'
        if plugin.is_dir():
            for path in plugin.rglob('*'):
                if path.is_file() and path.relative_to(root).as_posix() not in expected:
                    errors.append('Unexpected plugin file: ' + path.relative_to(root).as_posix())
    return {'passed': not errors, 'errors': errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    result = check(args.root)
    print(json.dumps(result, indent=2))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
