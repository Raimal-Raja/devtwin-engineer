"""Validate the foundation package without running target repository code."""
import argparse
import json
import re
from pathlib import Path


def validate(root):
    root = Path(root).resolve()
    errors = []
    required = ['SKILL.md', 'references/routing.md',
                'references/repository-understanding.md', 'references/bug-reproduction.md',
                'references/implementation.md', 'references/regression-testing.md',
                'templates/evidence-ledger.md', 'templates/verification-report.md']
    for relative in required:
        if not (root / relative).is_file():
            errors.append(f'Missing required file: {relative}')
    skill = root / 'SKILL.md'
    if skill.is_file():
        text = skill.read_text(encoding='utf-8')
        match = re.match(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)', text, re.S)
        if not match:
            errors.append('SKILL.md: missing frontmatter')
        else:
            fields = dict(re.findall(r'^([a-z]+):\s*(.+)$', match[1], re.M))
            if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', fields.get('name', '')) or len(fields.get('name', '')) > 64:
                errors.append('SKILL.md: invalid name')
            if not fields.get('description', '').strip():
                errors.append('SKILL.md: missing description')
    for relative in required:
        path = root / relative
        if not path.is_file():
            continue
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
            if '://' in target or target.startswith('#'):
                continue
            resolved = (path.parent / target.split('#')[0]).resolve()
            if not resolved.is_relative_to(root):
                errors.append(f'{relative}: reference escapes package: {target}')
            elif not resolved.is_file():
                errors.append(f'{relative}: missing reference: {target}')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    try:
        errors = validate(args.root)
    except (OSError, UnicodeError) as exc:
        errors = [str(exc)]
    print(json.dumps({'valid': not errors, 'errors': errors}, indent=2))
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
