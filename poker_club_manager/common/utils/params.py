def parse_int(value, default, *, min_value=None, max_value=None):
    if value is None:
        return default

    try:
        value = int(value)
    except (TypeError, ValueError):
        return default

    if min_value is not None:
        value = max(min_value, value)
    if max_value is not None:
        value = min(max_value, value)

    return value
