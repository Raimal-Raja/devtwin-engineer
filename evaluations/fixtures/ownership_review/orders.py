ORDERS = {'A1': {'owner': 'alice', 'total_cents': 2500},
          'B1': {'owner': 'bob', 'total_cents': 1000}}


def vulnerable_lookup(order_id):
    """Deliberately flawed development example, without an authorization check."""
    return dict(ORDERS[order_id])


def candidate_lookup(authenticated_actor, order_id):
    """Actor is synthetic trusted input here, not a real authentication implementation."""
    order = ORDERS.get(order_id)
    if order is None or authenticated_actor != order['owner']:
        raise PermissionError('Order unavailable')
    return dict(order)
