"""Self-authored metadata fixtures for offline resolver exercises."""
from pathlib import Path
import zipfile


def create(root):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    for name, version, requirement in [('devtwin_demo_core', '1.0', None),
                                       ('devtwin_demo_core', '2.0', None),
                                       ('devtwin_demo_addon', '1.0', 'devtwin-demo-core<2')]:
        dist = f'{name}-{version}.dist-info'
        metadata = f'Metadata-Version: 2.1\nName: {name.replace("_", "-")}\nVersion: {version}\n'
        if requirement:
            metadata += f'Requires-Dist: {requirement}\n'
        files = {f'{dist}/METADATA': metadata,
                 f'{dist}/WHEEL': 'Wheel-Version: 1.0\nGenerator: synthetic-fixture\nRoot-Is-Purelib: true\nTag: py3-none-any\n',
                 f'{name}/__init__.py': f'__version__ = "{version}"\n'}
        files[f'{dist}/RECORD'] = ''.join(f'{path},,\n' for path in [*files, f'{dist}/RECORD'])
        with zipfile.ZipFile(root / f'{name}-{version}-py3-none-any.whl', 'w') as archive:
            for path, content in files.items():
                archive.writestr(path, content)
