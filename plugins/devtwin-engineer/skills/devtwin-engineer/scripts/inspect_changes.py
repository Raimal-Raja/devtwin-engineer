"""Read-only Git status summary; no diffs, file contents, hooks or index refresh."""
import argparse
import json
import os
from pathlib import Path
import subprocess


def parse_status(output):
    fields = output.split('\0')
    changes = []
    position = 0
    while position < len(fields) and fields[position]:
        record = fields[position]
        position += 1
        if len(record) < 4 or record[2] != ' ':
            raise ValueError('Malformed Git status output')
        index, working = record[:2]
        item = {'path': record[3:], 'index': index, 'working_tree': working,
                'untracked': record[:2] == '??'}
        if index in 'RC' or working in 'RC':
            if position >= len(fields) or not fields[position]:
                raise ValueError('Missing rename source')
            item['original_path'] = fields[position]
            position += 1
        changes.append(item)
    return changes


def inspect(root, git='git', max_entries=1000):
    if max_entries < 1:
        raise ValueError('max_entries must be positive')
    root = Path(root).resolve()
    if not root.is_dir():
        raise ValueError('Root must be an existing directory')
    environment = os.environ.copy()
    # Prevent inherited Git variables from redirecting inspection to another repository.
    for key in list(environment):
        if key.startswith('GIT_'):
            del environment[key]
    environment['GIT_OPTIONAL_LOCKS'] = '0'
    prefix = [str(git), '-c', 'core.fsmonitor=false', '-c', 'core.untrackedCache=false', '-C', str(root)]

    # Status may run clean/process filters while comparing working-tree content.
    # Read driver names without executing their command values, then disable them.
    configured = subprocess.run(prefix + ['config', '--null', '--get-regexp',
                                         r'^filter\..*\.(clean|process|required)$'],
                                env=environment, capture_output=True, timeout=30)
    if configured.returncode not in (0, 1):
        raise ValueError('Unable to inspect Git filter configuration')
    drivers = set()
    for record in configured.stdout.decode('utf-8', errors='surrogateescape').split('\0'):
        if record:
            key = record.split('\n', 1)[0]
            drivers.add(key.rsplit('.', 1)[0])
    for driver in sorted(drivers):
        prefix.extend(['-c', driver + '.clean=', '-c', driver + '.process=',
                       '-c', driver + '.required=false'])

    def run(arguments):
        result = subprocess.run(prefix + arguments, env=environment, capture_output=True,
                                timeout=30)
        if result.returncode:
            # Avoid emitting repository-controlled error text or sensitive local paths.
            raise ValueError('Git inspection failed: directory may not be an accessible working tree')
        return result.stdout.decode('utf-8', errors='surrogateescape')

    top = run(['rev-parse', '--show-toplevel']).rstrip('\r\n')
    output = run(['status', '--porcelain=v1', '-z', '--untracked-files=normal', '--ignore-submodules=all'])
    changes = parse_status(output)
    return {'root': top, 'changes': changes[:max_entries], 'total_changes': len(changes),
            'truncated': len(changes) > max_entries,
            'scope': 'whole working tree; untracked directories grouped; submodule contents excluded'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--git', default='git')
    parser.add_argument('--max-entries', type=int, default=1000)
    args = parser.parse_args()
    try:
        result = inspect(args.root, args.git, args.max_entries)
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        # OSError can contain private paths, so report only its type.
        message = str(exc) if isinstance(exc, ValueError) else type(exc).__name__
        print(json.dumps({'error': message}))
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
