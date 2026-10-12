"""Evaluator-side contract checks; run against an authorized fixture copy."""
from decimal import Decimal
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(sys.argv.pop(1)).resolve()))
from checkout import checkout_total


class CheckoutContract(unittest.TestCase):
    def test_optional_discount(self):
        self.assertEqual(checkout_total(100), 100)
        self.assertEqual(checkout_total(100, None), 100)

    def test_fixed_discounts(self):
        for discount, expected in [(0, 100), (25, 75), (100, 0), (150, 0)]:
            with self.subTest(discount=discount):
                self.assertEqual(checkout_total(100, discount), expected)

    def test_decimal_amounts(self):
        self.assertEqual(checkout_total(Decimal('10.25')), Decimal('10.25'))
        self.assertEqual(checkout_total(Decimal('10.25'), Decimal('0.10')), Decimal('10.15'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
