"""Synthetic validated rows: product strings and integer quantities, including returns."""


def baseline(rows, requested, metrics=None):
    result = {}
    for product in requested:
        total = 0
        for row in rows:
            if metrics is not None:
                metrics['rows_examined'] = metrics.get('rows_examined', 0) + 1
            if row['product'] == product:
                total += row['quantity']
        result[product] = total
    return result


def candidate(rows, requested, metrics=None):
    totals = {}
    for row in rows:
        if metrics is not None:
            metrics['rows_examined'] = metrics.get('rows_examined', 0) + 1
        totals[row['product']] = totals.get(row['product'], 0) + row['quantity']
    return {product: totals.get(product, 0) for product in requested}
