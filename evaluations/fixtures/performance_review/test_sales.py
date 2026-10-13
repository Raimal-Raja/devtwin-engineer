import unittest

from sales import baseline, candidate


class SalesTests(unittest.TestCase):
    def test_contract_cases(self):
        rows = [{'product': 'A', 'quantity': 3}, {'product': 'B', 'quantity': 4},
                {'product': 'A', 'quantity': -1}]
        for requests in ([], ['A'], ['A', 'B', 'missing'], ['A', 'A']):
            with self.subTest(requests=requests):
                self.assertEqual(candidate(rows, requests), baseline(rows, requests))
        self.assertEqual(candidate(rows, ['A', 'B', 'missing']), {'A': 2, 'B': 4, 'missing': 0})

    def test_empty_rows(self):
        self.assertEqual(candidate([], ['A']), baseline([], ['A']))

    def test_one_pass_row_work(self):
        rows = [{'product': 'A', 'quantity': 1}] * 10
        before, after = {}, {}
        self.assertEqual(baseline(rows, ['A', 'B', 'A'], before), candidate(rows, ['A', 'B', 'A'], after))
        self.assertEqual(before['rows_examined'], 30)
        self.assertEqual(after['rows_examined'], 10)
