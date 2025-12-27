import pathlib

import pytest

from . import utils


ROOT = pathlib.Path(__file__).parent
PROJECTS = [
    'project_basic',
    'namespace1.namespace2.project',
]


class TestInstall:

    @pytest.mark.parametrize('project', PROJECTS)
    def test_sync_editable(self, project):
        root = utils.find_project(project)
        system = utils.System(cwd=root)
        system('rm -rf .venv')
        system('uv sync --editable')
        code = f'import {project}; print({project}.foo())'
        assert system(f'uv run python -c "{code}"') == '42\n'

    @pytest.mark.parametrize('project', PROJECTS)
    def test_sync_no_editable(self, project):
        root = utils.find_project(project)
        system = utils.System(cwd=root)
        system('rm -rf .venv')
        system('uv sync --no-editable')
        code = f'import {project}; print({project}.foo())'
        assert system(f'uv run python -c "{code}"') == '42\n'

    @pytest.mark.parametrize('project', PROJECTS)
    def test_build_wheel(self, tmpdir, project):
        root = utils.find_project(project)
        system = utils.System(cwd=root)
        system('rm -rf .venv')
        system('uv sync')
        system('uv build')
        stem = f'{project.replace(".", "_")}-0.1.0'
        wheel = root / f'dist/{stem}-py3-none-any.whl'
        assert wheel.exists()
        system = utils.System(cwd=tmpdir)
        system('uv venv')
        system(f'uv pip install {wheel}')
        code = f'import {project}; print({project}.foo())'
        assert system(f'uv run python -c "{code}"') == '42\n'

    @pytest.mark.parametrize('project', PROJECTS)
    def test_build_sdist(self, tmpdir, project):
        root = utils.find_project(project)
        system = utils.System(cwd=root)
        system('rm -rf .venv')
        system('uv sync')
        system('uv build')
        stem = f'{project.replace(".", "_")}-0.1.0'
        sdist = root / f'dist/{stem}.tar.gz'
        assert sdist.exists()
        system = utils.System(cwd=tmpdir)
        system('uv venv')
        system(f'uv pip install {sdist}')
        code = f'import {project}; print({project}.foo())'
        assert system(f'uv run python -c "{code}"') == '42\n'
