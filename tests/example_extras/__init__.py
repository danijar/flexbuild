try:
    from dependency import foo  # noqa
except ImportError:

    def foo():
        return 'fallback'
