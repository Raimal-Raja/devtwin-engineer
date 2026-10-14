"""Synthetic order contamination; each receipt should describe only its current order."""
_history = []


def build_receipt(order_id):
    _history.append(order_id)
    return list(_history)
