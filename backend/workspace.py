"""In-memory ingestion of explicitly selected ZIP files; never extract or execute."""
import hashlib
import io
from pathlib import PurePosixPath
import re
import stat
import zipfile

MAX_ARCHIVE = 2 * 1024 * 1024
MAX_TOTAL = 16000
MAX_FILES = 30
MAX_ENTRIES = 200
EXTENSIONS = {'.py', '.md', '.toml', '.json', '.txt', '.sql', '.yaml', '.yml'}
EXCLUDED = {'.git', '.env', '.ssh', '.aws', '.codex', '.claude', '.agents',
            'node_modules', 'venv', '.venv', '__pycache__', 'credentials'}
SECRET = re.compile(r'nvapi-[A-Za-z0-9_-]{20,}|-----BEGIN .*PRIVATE KEY-----|'
                    r'(?i:api[_-]?key|password|secret|token)\s*[:=]\s*[\"\']?[^\s\"\']{16,}')


class WorkspaceError(ValueError):
    pass


def ingest_zip(data, selected):
    """Reject unsafe archives and return exact selected text with content hashes."""
    if not isinstance(data, bytes) or len(data) > MAX_ARCHIVE:
        raise WorkspaceError('ZIP must be at most 2 MiB')
    if (not isinstance(selected, list) or not 1 <= len(selected) <= MAX_FILES
            or any(not isinstance(path, str) for path in selected)):
        raise WorkspaceError('Select 1 to 30 text files')
    if len({path.casefold() for path in selected}) != len(selected):
        raise WorkspaceError('Duplicate selected paths')
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            entries = archive.infolist()
            if len(entries) > MAX_ENTRIES:
                raise WorkspaceError('ZIP has too many entries')
            members = {}
            folded = set()
            for info in entries:
                name = info.filename
                parts = name.rstrip('/').split('/')
                if (not name or '\\' in name or ':' in name or '\x00' in name
                        or any(part in ('', '.', '..') for part in parts)
                        or any(any(ord(char) < 32 for char in part) for part in parts)):
                    raise WorkspaceError('ZIP contains an unsafe path')
                if name.casefold() in folded:
                    raise WorkspaceError('ZIP contains colliding paths')
                folded.add(name.casefold())
                mode = info.external_attr >> 16
                if stat.S_IFMT(mode) not in (0, stat.S_IFREG, stat.S_IFDIR):
                    raise WorkspaceError('ZIP contains a link or special entry')
                if info.flag_bits & 1:
                    raise WorkspaceError('Encrypted ZIP entries are unsupported')
                members[name] = info
            files = []
            total = 0
            for path in selected:
                info = members.get(path)
                parts = PurePosixPath(path).parts
                if (info is None or info.is_dir() or PurePosixPath(path).suffix.lower() not in EXTENSIONS
                        or any(part.lower() in EXCLUDED or part.lower().startswith('.env') for part in parts)
                        or PurePosixPath(path).name.lower().endswith(('.key', '.pem', '.log'))):
                    raise WorkspaceError('Selection contains a missing or excluded file')
                if info.file_size > MAX_TOTAL - total:
                    raise WorkspaceError('Selected text exceeds 16000 bytes')
                with archive.open(info) as stream:
                    raw = stream.read(MAX_TOTAL - total + 1)
                total += len(raw)
                if total > MAX_TOTAL:
                    raise WorkspaceError('Selected text exceeds 16000 bytes')
                try:
                    text = raw.decode('utf-8')
                except UnicodeError:
                    raise WorkspaceError('Selected files must be UTF-8') from None
                if '\x00' in text or SECRET.search(text):
                    raise WorkspaceError('Selected file contains binary data or a possible secret')
                files.append({'path': path, 'content': text, 'sha256': hashlib.sha256(raw).hexdigest()})
            return files
    except (zipfile.BadZipFile, RuntimeError, OSError, NotImplementedError):
        raise WorkspaceError('ZIP could not be read') from None
