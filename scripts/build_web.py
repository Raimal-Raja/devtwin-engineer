"""Build the static catalog and validated development downloads. No network/model calls."""
import argparse
import json
from pathlib import Path
import shutil
import tempfile
import zipfile

try:
    from .build_package import build
    from .build_plugins import build_plugins
    from .verify_archive import verify
except ImportError:
    from build_package import build
    from build_plugins import build_plugins
    from verify_archive import verify


def build_web(root, output):
    root, output = Path(root).resolve(), Path(output).absolute()
    for path in (output, *output.parents):
        if path.is_symlink() or (path.exists() and getattr(path.stat(), 'st_file_attributes', 0) & 0x400):
            raise ValueError('Output must not contain links or junctions')
    if output.exists():
        raise ValueError('Output already exists; use a fresh directory')
    with tempfile.TemporaryDirectory() as folder:
        stage = Path(folder)
        marketplace = stage / 'marketplace'
        plugins = build_plugins(root, marketplace)
        downloads = stage / 'site/downloads'
        downloads.mkdir(parents=True)
        skill = downloads / 'devtwin-engineer-skill.zip'
        build(root, skill)
        verify(skill)
        with zipfile.ZipFile(downloads / 'devtwin-engineer-plugin.zip', 'w') as archive:
            for path in sorted(marketplace.rglob('*')):
                if path.is_file():
                    info = zipfile.ZipInfo('devtwin-engineer-marketplace/' + path.relative_to(marketplace).as_posix(),
                                           date_time=(1980, 1, 1, 0, 0, 0))
                    info.create_system = 3
                    info.external_attr = 0o100644 << 16
                    archive.writestr(info, path.read_bytes())
        for name in ('index.html', 'styles.css', 'model.mjs', 'app.mjs', 'icon.svg'):
            source = root / 'web' / name
            if source.is_symlink() or not source.is_file():
                raise ValueError('Missing or linked web source: ' + name)
            shutil.copyfile(source, stage / 'site' / name)
        output.mkdir(parents=True, exist_ok=False)
        shutil.copytree(stage / 'site', output, dirs_exist_ok=True)
    return {'directory': str(output), 'plugin_files': plugins['files'],
            'downloads': ['devtwin-engineer-skill.zip', 'devtwin-engineer-plugin.zip'],
            'runtime_activation_verified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    try:
        result = build_web(args.root, args.output)
    except (OSError, ValueError, UnicodeError, zipfile.BadZipFile) as exc:
        print(json.dumps({'error': str(exc) if isinstance(exc, ValueError) else type(exc).__name__}))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
