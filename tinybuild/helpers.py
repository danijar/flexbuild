def format_key_value(data):
    content = ''.join(f'{k}: {v}\n' for k, v in data)
    content = content.encode('utf-8')
    return content
