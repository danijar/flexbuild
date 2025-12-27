def should_exclude(path):
    parts = path.parts
    return (
        path.suffix == '.pyc'
        or any(part.startswith('.') for part in parts)
        or 'dist' in parts
        or 'build' in parts
        or '__pycache__' in parts
    )
