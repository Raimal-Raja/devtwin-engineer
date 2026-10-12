"""Deliberately broken development fixture; do not fix this source copy."""


def checkout_total(subtotal, discount=None):
    """Return subtotal minus an optional fixed discount, floored at zero."""
    return max(0, subtotal - discount)
