from decimal import Decimal
import unittest

from billing import make_invoice
from delivery import RENDERERS, register_renderer
from exports import export_row
from service import submit_order


class OrderTests(unittest.TestCase):
    def setUp(self):
        self.lines = [{'price': Decimal('10.25'), 'quantity': 2}]

    def test_default_receipt(self):
        self.assertEqual(submit_order('A1', self.lines), 'Order A1 — Total: 20.50')

    def test_discount(self):
        self.assertEqual(submit_order('A1', self.lines, Decimal('0.50')), 'Order A1 — Total: 20.00')

    def test_invoice_export_contract(self):
        self.assertEqual(export_row(make_invoice('A1', self.lines)), ['A1', '20.50'])

    def test_empty_order(self):
        self.assertEqual(submit_order('A1', []), 'Order A1 — Total: 0.00')

    def test_discount_floor(self):
        self.assertEqual(submit_order('A1', self.lines, Decimal('100')), 'Order A1 — Total: 0.00')

    def test_custom_renderer(self):
        register_renderer('custom-test', lambda invoice: invoice['order_id'])
        self.addCleanup(RENDERERS.pop, 'custom-test', None)
        self.assertEqual(submit_order('A1', self.lines, renderer='custom-test'), 'A1')
