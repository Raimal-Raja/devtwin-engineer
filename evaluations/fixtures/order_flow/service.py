from decimal import Decimal

from billing import make_invoice
from delivery import dispatch


def submit_order(order_id, lines, discount=Decimal('0'), renderer='receipt'):
    invoice = make_invoice(order_id, lines, discount)
    return dispatch(renderer, invoice)
