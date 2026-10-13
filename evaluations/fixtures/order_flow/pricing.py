from decimal import Decimal


def calculate_total(lines, discount=Decimal('0')):
    """Synthetic fixed-amount pricing; tax and currencies are out of scope."""
    subtotal = sum((line['price'] * line['quantity'] for line in lines), Decimal('0'))
    return max(Decimal('0'), subtotal - discount)
