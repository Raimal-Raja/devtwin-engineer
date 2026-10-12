import unittest

from checkout import checkout_total


class CheckoutTests(unittest.TestCase):
    def test_missing_discount(self):
        self.assertEqual(checkout_total(100), 100)

    def test_explicit_none(self):
        self.assertEqual(checkout_total(100, None), 100)

    def test_discount(self):
        self.assertEqual(checkout_total(100, 20), 80)

    def test_zero_discount(self):
        self.assertEqual(checkout_total(100, 0), 100)

    def test_floor(self):
        self.assertEqual(checkout_total(100, 150), 0)
