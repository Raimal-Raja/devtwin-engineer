from decimal import Decimal

from pricing import calculate_total as total_for


def make_invoice(order_id, lines, discount=Decimal('0')):
    return {'order_id': order_id, 'total': total_for(lines, discount)}
