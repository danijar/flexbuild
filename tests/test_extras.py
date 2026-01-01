import pathlib

from . import utils


ROOT = pathlib.Path(__file__).parent


class TestExtras:
    def test_with_extra(self, tmpdir):
        project = 'example_extras'
        dependency = 'example_extras/dependency'
        package = utils.build_package(ROOT / project)
        links = [utils.build_package(ROOT / dependency).parent]
        system = utils.System(cwd=tmpdir)
        system('uv venv')
        utils.install_package(system, f'{package}[dep]', links)
        code = 'import project; print(project.foo())'
        assert system(f'uv run python -c "{code}"') == 'dependency\n'

    def test_without_extra(self, tmpdir):
        project = 'example_extras'
        dependency = 'example_extras/dependency'
        package = utils.build_package(ROOT / project)
        links = [utils.build_package(ROOT / dependency).parent]
        system = utils.System(cwd=tmpdir)
        system('uv venv')
        utils.install_package(system, f'{package}', links)
        code = 'import project; print(project.foo())'
        assert system(f'uv run python -c "{code}"') == 'fallback\n'
