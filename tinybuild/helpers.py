def format_key_value(data):
    content = ''.join(f'{k}: {v}\n' for k, v in data)
    content = content.encode('utf-8')
    return content


def merge_dicts(first, second):
    if not isinstance(first, dict):
        return first
    if not isinstance(second, dict):
        return merge_dicts(first, {})
    merged = {}
    keys = sorted(set(first.keys()) | set(second.keys()))
    for key in keys:
        if key in first and key in second:
            merged[key] = merge_dicts(first[key], second[key])
        elif key in first:
            merged[key] = merge_dicts(first[key], {})
        else:
            merged[key] = merge_dicts(second[key], {})
    return merged
