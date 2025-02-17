from django import template

register = template.Library()

@register.filter
def format_gas_amount(value):
    if value is None:
        return "-"
    return f"{float(value):.2f}"