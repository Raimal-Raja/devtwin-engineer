import json
import unittest
from decimal import Decimal

from client import read_total, strict_read_total
from provider import alias_response, original_response, proposed_response


class ContractTests(unittest.TestCase):
    def test_original_round_trip(self):
        response = json.loads(json.dumps(original_response()))
        self.assertEqual(read_total(response), Decimal('20.50'))
        self.assertEqual(strict_read_total(response), Decimal('20.50'))

    def test_rename_breaks_known_client(self):
        with self.assertRaises(KeyError):
            read_total(proposed_response())

    def test_alias_preserves_permissive_client(self):
        self.assertEqual(read_total(alias_response()), Decimal('20.50'))

    def test_alias_breaks_strict_client(self):
        with self.assertRaises(ValueError):
            strict_read_total(alias_response())
