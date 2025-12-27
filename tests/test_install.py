import pathlib

import pytest

from . import utils


ROOT = pathlib.Path(__file__).parent
PROJECTS = [
    'project_basic',
]


class TestInstall:

    @pytest.mark.parametrize('project', PROJECTS)
    def test_sync_editable(self, project):
        print(ROOT / project)
        system = utils.System(cwd=ROOT / project)
        system('rm -rf .venv')
        system('uv sync --editable')
        code = f'import {project}; print({project}.foo())'
        assert system(f'uv run python -c "{code}"') == '42\n'

    @pytest.mark.parametrize('project', PROJECTS)
    def test_sync_no_editable(self, project):
        system = utils.System(cwd=ROOT / project)
        system('rm -rf .venv')
        system('uv sync --no-editable')
        code = f'import {project}; print({project}.foo())'
        assert system(f'uv run python -c "{code}"') == '42\n'

    @pytest.mark.parametrize('project', PROJECTS)
    def test_build_wheel(self, tmpdir, project):
        system = utils.System(cwd=ROOT / project)
        system('rm -rf .venv')
        system('uv sync')
        system('uv build')
        wheel = ROOT / project / f'dist/{project}-0.1.0-py3-none-any.whl'
        assert wheel.exists()
        system = utils.System(cwd=tmpdir)
        system('uv venv')
        system(f'uv pip install {wheel}')
        code = f'import {project}; print({project}.foo())'
        assert system(f'uv run python -c "{code}"') == '42\n'

    @pytest.mark.parametrize('project', PROJECTS)
    def test_build_sdist(self, tmpdir, project):
        system = utils.System(cwd=ROOT / project)
        system('rm -rf .venv')
        system('uv sync')
        system('uv build')
        sdist = ROOT / project / f'dist/{project}-0.1.0.tar.gz'
        assert sdist.exists()
        system = utils.System(cwd=tmpdir)
        system('uv venv')
        system(f'uv pip install {sdist}')
        code = f'import {project}; print({project}.foo())'
        assert system(f'uv run python -c "{code}"') == '42\n'
