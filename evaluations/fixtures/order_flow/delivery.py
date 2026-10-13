def render_receipt(invoice):
    return f"Order {invoice['order_id']} — Total: {invoice['total']:.2f}"


RENDERERS = {'receipt': render_receipt}


def register_renderer(name, renderer):
    RENDERERS[name] = renderer


def dispatch(name, invoice):
    return RENDERERS[name](invoice)
