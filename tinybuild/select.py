class Selector:

    def should_include(self, path):
        parts = path.parts
        if path.suffix == '.pyc':
            return False
        if any(part.startswith('.') for part in parts):
            return False
        if any(x in parts for x in ('dist', 'build', '__pycache__')):
            return False
        return True
