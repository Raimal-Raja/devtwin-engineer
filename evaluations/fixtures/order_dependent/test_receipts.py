import unittest
from receipts import build_receipt


class ReceiptTests(unittest.TestCase):
    def test_first_order(self):
        self.assertEqual(build_receipt('A'), ['A'])

    def test_second_order(self):
        self.assertEqual(build_receipt('B'), ['B'])
