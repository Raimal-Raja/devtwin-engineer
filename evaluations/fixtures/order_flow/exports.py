def export_row(invoice):
    return [invoice['order_id'], str(invoice['total'])]
