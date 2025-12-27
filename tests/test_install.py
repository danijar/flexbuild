import pathlib

import pytest

from . import utils


REPO = pathlib.Path(__file__).parent.parent
ROOT = pathlib.Path(__file__).parent
PROJECTS = [
    ('project_basic', 'project_basic'),
    ('project_namespace', 'virtual1.virtual2.project_namespace'),
    # ('namespace1/namespace2/project', 'namespace1.namespace2.project'),
]


class TestInstall:

    @pytest.mark.parametrize('project', PROJECTS)
    def test_sync_editable(self, project):
        root, name = utils.find_project(project)
        system = utils.System(cwd=root)
        system('rm -rf .venv')
        system('uv sync --editable')
        code = f'import {name}; print({name}.foo())'
        assert system(f'uv run python -c "{code}"') == '42\n'

    @pytest.mark.parametrize('project', PROJECTS)
    def test_sync_no_editable(self, project):
        root, name = utils.find_project(project)
        system = utils.System(cwd=root)
        system('rm -rf .venv')
        system('uv sync --no-editable')
        code = f'import {name}; print({name}.foo())'
        assert system(f'uv run python -c "{code}"') == '42\n'

    @pytest.mark.parametrize('project', PROJECTS)
    def test_build_wheel(self, tmpdir, project):
        root, name = utils.find_project(project)
        system = utils.System(cwd=root)
        system('rm -rf .venv')
        system('uv sync')
        system('uv build')
        stem = f'{name.replace(".", "_")}-0.1.0'
        wheel = root / f'dist/{stem}-py3-none-any.whl'
        assert wheel.exists()
        system = utils.System(cwd=tmpdir)
        system('uv venv')
        system(f'uv pip install {wheel}')
        code = f'import {name}; print({name}.foo())'
        assert system(f'uv run python -c "{code}"') == '42\n'

    @pytest.mark.parametrize('project', PROJECTS)
    def test_build_sdist(self, tmpdir, project):
        packages = []

        system = utils.System(cwd=REPO)
        system('uv build')
        sdist = list((REPO / 'dist').glob('*.whl'))[0]
        packages.append(str(sdist))

        root, name = utils.find_project(project)
        system = utils.System(cwd=root)
        system('rm -rf .venv')
        system('uv sync')
        system('uv build')
        stem = f'{name.replace(".", "_")}-0.1.0'
        sdist = root / f'dist/{stem}.tar.gz'
        assert sdist.exists()
        packages.append(str(sdist))

        system = utils.System(cwd=tmpdir)
        system('uv venv')
        system(f'uv pip install {" ".join(packages)} --no-build-isolation')
        code = f'import {name}; print({name}.foo())'
        assert system(f'uv run python -c "{code}"') == '42\n'
