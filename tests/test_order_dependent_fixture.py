from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class OrderDependentFixtureTests(unittest.TestCase):
    def test_individual_pass_combined_failure_and_focused_correction(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'receipts'
            shutil.copytree(ROOT / 'evaluations/fixtures/order_dependent', target,
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
            protected = {name: (target / name).read_bytes() for name in ('test_receipts.py', 'README.md', 'USER-NOTE.txt')}
            def execute(*arguments):
                return subprocess.run([sys.executable, '-B', '-m', 'unittest', *arguments], cwd=target,
                                      capture_output=True, text=True, timeout=20)
            for name in ('test_first_order', 'test_second_order'):
                self.assertEqual(execute('test_receipts.ReceiptTests.' + name).returncode, 0)
            combined = execute('test_receipts')
            self.assertNotEqual(combined.returncode, 0)
            self.assertIn("['A', 'B']", combined.stderr)
            (target / 'receipts.py').write_text('def build_receipt(order_id):\n    return [order_id]\n', encoding='utf-8')
            self.assertEqual(execute('test_receipts').returncode, 0)
            for name, raw in protected.items():
                self.assertEqual((target / name).read_bytes(), raw)
