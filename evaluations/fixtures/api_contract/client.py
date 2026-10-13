from decimal import Decimal


def read_total(response):
    return Decimal(response['total'])


def strict_read_total(response):
    if set(response) != {'id', 'total'}:
        raise ValueError('Unexpected response fields')
    return read_total(response)
