"""Discover explicitly selected unittest modules, including namespace test directories."""


def discover_selected_tests(root, paths):
    import sys
    import unittest
    from pathlib import Path, PurePosixPath

    root = Path(root)
    sys.path.insert(0, str(root))
    modules = []
    for name in sorted(paths):
        path = PurePosixPath(name)
        if path.suffix != '.py' or not path.name.startswith('test'):
            continue
        parts = (*path.parts[:-1], path.stem)
        if not all(part.isidentifier() for part in parts):
            raise ValueError('Selected tests must have importable Python module paths')
        modules.append('.'.join(parts))
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for module in modules:
        suite.addTests(loader.loadTestsFromName(module))
    return suite
