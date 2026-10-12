import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('evaluation', ROOT / 'scripts/evaluate_checkout.py')
evaluation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluation)


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.run = Path(self.temp.name) / 'run'
        evaluation.prepare(self.run)
        self.source = self.run / 'target/checkout.py'

    def correct(self):
        self.source.write_text(self.source.read_text().replace(
            'subtotal - discount', 'subtotal - (0 if discount is None else discount)'), encoding='utf-8')

    def test_failure_then_success(self):
        failed = evaluation.check(self.run)
        self.assertEqual(failed['status'], 'failed')
        self.assertIn('TypeError', failed['checks'][0]['stderr'])
        self.correct()
        passed = evaluation.check(self.run)
        self.assertEqual(passed['status'], 'passed')
        self.assertEqual(len(passed['checks']), 2)

    def test_incorrect_candidate_is_rejected(self):
        self.source.write_text('def checkout_total(subtotal, discount=None):\n    return subtotal\n', encoding='utf-8')
        result = evaluation.check(self.run)
        self.assertEqual(result['status'], 'failed')
        self.assertNotEqual(result['checks'][1]['exit_code'], 0)

    def test_modified_user_work_is_rejected(self):
        self.correct()
        (self.run / 'target/user-note.txt').write_text('lost original', encoding='utf-8')
        result = evaluation.check(self.run)
        self.assertEqual(result['status'], 'failed')
        self.assertIn('user-note.txt', result['changed_protected_files'])

    def test_missing_interpreter_is_blocked(self):
        result = evaluation.check(self.run, Path(self.temp.name) / 'absent-python')
        self.assertEqual(result['status'], 'blocked')
        self.assertEqual(result['checks'], [])

    def test_prepare_does_not_overwrite(self):
        before = self.source.read_bytes()
        with self.assertRaises(FileExistsError):
            evaluation.prepare(self.run)
        self.assertEqual(self.source.read_bytes(), before)
