def parse_int(value, default, *, minv=None, maxv=None):
    if value is None:
        return default

    try:
        value = int(value)
    except (TypeError, ValueError):
        return default

    if minv is not None:
        value = max(minv, value)
    if maxv is not None:
        value = min(maxv, value)

    return value
