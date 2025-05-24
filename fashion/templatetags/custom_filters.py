from django import template

register = template.Library()

@register.filter
def format_price(value):
    try:
        if isinstance(value, (int, float)):
            value_int = int(value)
            return f"{value_int:,}"
        elif isinstance(value, str):
            if '.' in value:
                return value.replace('.', ',')
            else:
                return value
        else:
            return value
    except (ValueError, TypeError):
        return value
