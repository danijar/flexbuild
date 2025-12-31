import pathlib

from . import utils


ROOT = pathlib.Path(__file__).parent


class TestExtras:

    def test_with_extra(self, tmpdir):
        path = 'example_extras'
        path_extra = 'example_extras/dependency'
        package = utils.build_packages([path], ROOT, ext='whl')[0]
        utils.build_packages([path_extra], ROOT, ext='whl')
        dependencies = ROOT / path_extra / 'dist'
        system = utils.System(cwd=tmpdir)
        system('uv venv')
        system(
            f'uv pip install {package}[dev]',
            f'--find-links {dependencies}',
            '--no-build-isolation',
            '--refresh-package project',
        )
        code = 'import project; print(project.foo())'
        assert system(f'uv run python -c "{code}"') == 'dependency\n'

    def test_without_extra(self, tmpdir):
        path = 'example_extras'
        path_extra = 'example_extras/dependency'
        package = utils.build_packages([path], ROOT, ext='whl')[0]
        utils.build_packages([path_extra], ROOT, ext='whl')
        dependencies = ROOT / path_extra / 'dist'
        system = utils.System(cwd=tmpdir)
        system('uv venv')
        system(
            f'uv pip install {package}',
            f'--find-links {dependencies}',
            '--no-build-isolation',
            '--refresh-package project',
        )
        code = 'import project; print(project.foo())'
        assert system(f'uv run python -c "{code}"') == 'fallback\n'
