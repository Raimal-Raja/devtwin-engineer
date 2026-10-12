"""Validate the foundation package without running target repository code."""
import argparse
import json
import os
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

MAX_BYTES = 1048576
MAX_DOCUMENTS = 1000


def metadata_errors(text):
    errors = []
    match = re.match(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)', text, re.S)
    if not match:
        return ['SKILL.md: missing frontmatter']
    fields = {}
    for line in match[1].splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        pair = re.fullmatch(r'([a-z][a-z-]*):[ \t]*(.*)', line)
        if not pair:
            errors.append('SKILL.md: unsupported metadata structure; use flat scalar fields')
            continue
        key, value = pair.groups()
        if key in fields:
            errors.append(f'SKILL.md: duplicate metadata field: {key}')
        if value.startswith(('"', "'")):
            if len(value) < 2 or value[-1] != value[0]:
                errors.append(f'SKILL.md: invalid quoted scalar: {key}')
            elif value.startswith('"'):
                try:
                    value = json.loads(value)
                except ValueError:
                    errors.append(f'SKILL.md: unsupported quoted scalar: {key}')
            elif not re.fullmatch(r"'(?:[^']|'')*'", value):
                errors.append(f'SKILL.md: invalid quoted scalar: {key}')
            else:
                value = value[1:-1].replace("''", "'")
        elif value.startswith(('[', '{', '|', '>')) or ': ' in value:
            errors.append(f'SKILL.md: unsupported scalar: {key}')
        elif value.lower() in ('null', '~', 'true', 'false') or re.fullmatch(r'[+-]?\d+(?:\.\d+)?', value):
            errors.append(f'SKILL.md: metadata must be strings: {key}')
        fields[key] = value
    name = fields.get('name', '')
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name) or len(name) > 64:
        errors.append('SKILL.md: invalid name')
    if not fields.get('description', '').strip():
        errors.append('SKILL.md: missing description')
    if len(fields.get('description', '')) > 1024:
        errors.append('SKILL.md: description exceeds 1024 characters')
    return errors


def linked_targets(text):
    # Ignore fenced code examples. This covers inline links, not all Markdown syntax.
    text = re.sub(r'(?m)^([ \t]*)(`{3,}|~{3,})[^\n]*\n.*?^\1\2[^\n]*$', '', text, flags=re.S)
    return re.findall(r'\[[^\]]*\]\((<[^>]+>|[^\s)]+)(?:\s+"[^"]*")?\)', text)


def validate(root):
    root = Path(root)
    errors = []
    if not root.is_dir() or root.is_symlink() or getattr(root.stat(), 'st_file_attributes', 0) & 0x400:
        return ['Package root must be a real directory, not a link or junction']
    root = root.resolve()
    required = ['SKILL.md', 'references/routing.md',
                'references/repository-understanding.md', 'references/bug-reproduction.md',
                'references/implementation.md', 'references/regression-testing.md',
                'templates/evidence-ledger.md', 'templates/verification-report.md']
    def safe_file(path):
        for part in (path, *path.parents):
            if part == root:
                break
            if part.is_symlink() or (part.exists() and getattr(part.stat(), 'st_file_attributes', 0) & 0x400):
                return False
        return path.resolve().is_relative_to(root) and path.is_file()

    for relative in required:
        if not safe_file(root / relative):
            errors.append(f'Missing required file: {relative}')
    documents = [root / name for name in ('SKILL.md', 'README.md') if (root / name).exists()]
    for folder in ('references', 'templates', 'docs', 'integrations', 'evaluations'):
        base = root / folder
        if base.is_symlink() or (base.exists() and getattr(base.stat(), 'st_file_attributes', 0) & 0x400):
            errors.append(f'Unsafe document directory: {folder}')
            continue
        if not base.exists():
            continue
        if not base.is_dir():
            errors.append(f'Expected document directory: {folder}')
            continue
        def traversal_error(exc):
            errors.append(f'{folder}: document traversal failed ({type(exc).__name__})')

        for directory, subdirs, files in os.walk(base, followlinks=False, onerror=traversal_error):
            for name in list(subdirs):
                child = Path(directory) / name
                if child.is_symlink() or getattr(child.stat(), 'st_file_attributes', 0) & 0x400:
                    errors.append(f'Unsafe document directory: {child.relative_to(root).as_posix()}')
                    subdirs.remove(name)
                elif name in ('private', '__pycache__'):
                    subdirs.remove(name)
            documents.extend(Path(directory) / name for name in sorted(files) if name.endswith('.md'))
            if len(documents) > MAX_DOCUMENTS:
                return errors + ['Document limit exceeded; validation incomplete']
    for path in sorted(documents):
        relative = path.relative_to(root).as_posix()
        if not safe_file(path):
            errors.append(f'{relative}: unsafe document path')
            continue
        try:
            with path.open('rb') as stream:
                content = stream.read(MAX_BYTES + 1)
            if len(content) > MAX_BYTES:
                errors.append(f'{relative}: document size limit exceeded')
                continue
            text = content.decode('utf-8')
        except (OSError, UnicodeError) as exc:
            errors.append(f'{relative}: cannot read document ({type(exc).__name__})')
            continue
        if relative == 'SKILL.md':
            errors.extend(metadata_errors(text))
        for target in linked_targets(text):
            target = target.strip('<>')
            parts = urlsplit(target)
            if parts.scheme in ('https', 'http', 'mailto'):
                continue
            if parts.scheme or parts.netloc:
                errors.append(f'{relative}: unsupported reference scheme: {target}')
                continue
            if not parts.path:
                continue
            resolved = (path.parent / unquote(parts.path)).resolve()
            if not resolved.is_relative_to(root):
                errors.append(f'{relative}: reference escapes package: {target}')
            elif not safe_file(path.parent / unquote(parts.path)):
                errors.append(f'{relative}: missing reference: {target}')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    try:
        errors = validate(args.root)
    except (OSError, UnicodeError) as exc:
        errors = [f'Package validation failed ({type(exc).__name__})']
    print(json.dumps({'valid': not errors, 'errors': errors}, indent=2))
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
