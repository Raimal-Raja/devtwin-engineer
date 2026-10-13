"""Install the private skill into an explicitly selected project's runtime layout."""
import argparse
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

LAYOUTS = {'codex': '.agents/skills', 'claude-code': '.claude/skills'}


def install(source, project, runtime):
    if runtime not in LAYOUTS:
        raise ValueError('Unknown runtime')
    project = Path(project)
    if not project.is_dir() or project.is_symlink() or getattr(project.stat(), 'st_file_attributes', 0) & 0x400:
        raise ValueError('Project must be an existing directory, not a link or junction')
    project = project.resolve()
    destination = project / LAYOUTS[runtime] / 'devtwin-engineer'
    for path in (destination, *destination.parents):
        if path == project:
            break
        if path.is_symlink() or (path.exists() and getattr(path.stat(), 'st_file_attributes', 0) & 0x400):
            raise ValueError('Runtime destination must not contain links or junctions')
    if destination.exists():
        raise ValueError('Skill destination already exists; installation refuses to overwrite it')
    with tempfile.TemporaryDirectory() as folder:
        archive = Path(folder) / 'skill.zip'
        built = build(source, archive)
        verified = verify(archive)
        # All payload names, sizes and hashes are verified before writing to the project.
        destination.mkdir(parents=True, exist_ok=False)
        with zipfile.ZipFile(archive) as contents:
            for entry in contents.infolist():
                relative = entry.filename.removeprefix('devtwin-engineer/')
                target = destination / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open('xb') as stream:
                    stream.write(contents.read(entry))
    return {'installed': str(destination), 'runtime': runtime, 'files': verified['files'],
            'archive_sha256': built['sha256'], 'activation_verified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('project', type=Path)
    parser.add_argument('--runtime', choices=LAYOUTS, required=True)
    args = parser.parse_args()
    try:
        result = install(args.source, args.project, args.runtime)
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(json.dumps({'installed': False, 'error': str(exc) if isinstance(exc, ValueError) else type(exc).__name__}))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
