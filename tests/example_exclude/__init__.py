import pathlib


PROJECT = pathlib.Path(__file__).parent


def foo():
    ensure_include()
    ensure_exclude()
    return 42


def ensure_include():
    from . import include  # noqa

    content = (PROJECT / 'include.txt').read_text()
    assert content == '123\n'


def ensure_exclude():
    try:
        from . import exclude  # noqa

        assert False
    except ImportError:
        pass
    assert not (PROJECT / 'exclude.txt').exists()
