"""Audit the thirteen workflow prerequisite resources; do not execute target code."""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil


def check(root):
    root = Path(root).resolve()
    from backend.investigate import WORKFLOWS
    from backend.runner import find_docker
    items = json.loads((root / 'evaluations/capabilities.json').read_text(encoding='utf-8'))
    if not isinstance(items, list) or {item['id'] for item in items} != WORKFLOWS or len(items) != 13:
        raise ValueError('Capability registry must contain each supported workflow exactly once')
    rows = []
    for item in items:
        paths = ['references/' + item['id'] + '.md', 'evaluations/tasks/' + item['task'] + '.md',
                 'evaluations/rubrics/' + item['rubric'] + '.md']
        paths += ['evaluations/fixtures/' + name for name in item['fixtures']]
        missing = []
        for relative in paths:
            target = root / relative
            if not target.resolve().is_relative_to(root) or target.is_symlink() or not target.exists():
                missing.append(relative)
        complete = all(isinstance(item.get(key), list) and item[key]
                       and all(isinstance(value, str) and value.strip() for value in item[key])
                       for key in ('requires', 'checks', 'fixtures'))
        complete = complete and isinstance(item.get('failure'), str) and bool(item['failure'].strip())
        rows.append({'id': item['id'], 'resources_ready': not missing and complete,
                     'missing': missing, 'requires': item.get('requires'), 'checks': item.get('checks'),
                     'failure': item.get('failure')})
    return {'resources_ready': all(row['resources_ready'] for row in rows), 'capabilities': rows,
            'environment': {'codex_cli_available': shutil.which('codex') is not None,
                            'docker_available': find_docker() is not None,
                            'fastapi_available': importlib.util.find_spec('fastapi') is not None},
            'limitations': 'Resource presence is not runtime success. Claude execution, independent comparisons and web sandbox gates are separate.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    try:
        result = check(args.root)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({'resources_ready': False, 'error': type(exc).__name__}))
        return 1
    print(json.dumps(result, indent=2))
    return 0 if result['resources_ready'] else 1


if __name__ == '__main__':
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    raise SystemExit(main())
