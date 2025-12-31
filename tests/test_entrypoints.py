import pathlib

from . import utils


REPO = pathlib.Path(__file__).parent.parent
ROOT = pathlib.Path(__file__).parent


class TestEntrypoints:
    def test_sync_editable(self):
        project = 'example_entrypoints'
        system = utils.System(cwd=ROOT / project)
        system('rm -rf .venv')
        system('uv sync --editable --refresh-package flexbuild')
        assert system('uv run -qq entrypoint_foo') == '42\n'

    def test_sync_no_editable(self):
        project = 'example_entrypoints'
        system = utils.System(cwd=ROOT / project)
        system('rm -rf .venv')
        system('uv sync --no-editable --refresh-package flexbuild')
        assert system('uv run -qq entrypoint_foo') == '42\n'

    def test_build_wheel(self, tmpdir):
        package = utils.build_package(ROOT / 'example_entrypoints')
        system = utils.System(cwd=tmpdir)
        system('uv venv')
        utils.install_package(system, package)
        assert system('uv run -qq entrypoint_foo') == '42\n'

    def test_build_sdist(self, tmpdir):
        backend = utils.build_package(REPO)
        package = utils.build_package(ROOT / 'example_entrypoints')
        system = utils.System(cwd=tmpdir)
        system('uv venv')
        system(f'uv pip install {backend}')
        utils.install_package(system, package)
        assert system('uv run -qq entrypoint_foo') == '42\n'
