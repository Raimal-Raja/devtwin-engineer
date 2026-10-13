import unittest

from orders import ORDERS, candidate_lookup, vulnerable_lookup


class OwnershipTests(unittest.TestCase):
    def test_original_lookup_exposes_other_owners_order(self):
        self.assertEqual(vulnerable_lookup('B1')['owner'], 'bob')

    def test_owner_access_is_preserved(self):
        self.assertEqual(candidate_lookup('alice', 'A1')['total_cents'], 2500)
        self.assertEqual(candidate_lookup('bob', 'B1')['total_cents'], 1000)

    def test_cross_owner_access_is_denied(self):
        with self.assertRaises(PermissionError):
            candidate_lookup('alice', 'B1')

    def test_absent_actor_is_denied(self):
        with self.assertRaises(PermissionError):
            candidate_lookup(None, 'A1')

    def test_missing_and_unauthorized_orders_use_same_error(self):
        errors = []
        for order_id in ('B1', 'absent'):
            with self.assertRaises(PermissionError) as error:
                candidate_lookup('alice', order_id)
            errors.append(str(error.exception))
        self.assertEqual(errors, ['Order unavailable', 'Order unavailable'])

    def test_lookup_result_does_not_mutate_stored_order(self):
        result = candidate_lookup('alice', 'A1')
        result['total_cents'] = 0
        self.assertEqual(ORDERS['A1']['total_cents'], 2500)
