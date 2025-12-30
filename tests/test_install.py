import dataclasses
import pathlib

import pytest

from . import utils


REPO = pathlib.Path(__file__).parent.parent
ROOT = pathlib.Path(__file__).parent


@dataclasses.dataclass
class Project:
    name: str
    path: str
    deps: list


PROJECTS = [
    Project(
        name='project',
        path='example_basic',
        deps=[],
    ),
    Project(
        name='project',
        path='example_exclude',
        deps=[],
    ),
    Project(
        name='project',
        path='example_folder',
        deps=[],
    ),
    Project(
        name='namespace1.namespace2.project',
        path='example_namespace',
        deps=[],
    ),
    Project(
        name='namespace1.project1',
        path='example_monorepo/namespace1/project1',
        deps=[],
    ),
    Project(
        name='namespace1.project2',
        path='example_monorepo/namespace1/project2',
        deps=['example_monorepo/namespace1/project1'],
    ),
]


PROJECTS_NO_EXCLUDE = [x for x in PROJECTS if x.path != 'example_exclude']


class TestInstall:
    @pytest.mark.parametrize('project', PROJECTS_NO_EXCLUDE)
    def test_sync_editable(self, project):
        path = ROOT / project.path
        system = utils.System(cwd=path)
        system('rm -rf .venv')
        system('uv sync --editable --refresh-package flexbuild')
        code = f'import {project.name}; print({project.name}.foo())'
        assert system(f'uv run -qq python -c "{code}"') == '42\n'

    @pytest.mark.parametrize('project', PROJECTS_NO_EXCLUDE)
    def test_sync_no_editable(self, project):
        path = ROOT / project.path
        system = utils.System(cwd=path)
        system('rm -rf .venv')
        system('uv sync --no-editable --refresh-package flexbuild')
        code = f'import {project.name}; print({project.name}.foo())'
        assert system(f'uv run -qq python -c "{code}"') == '42\n'

    @pytest.mark.parametrize('project', PROJECTS)
    def test_build_wheel(self, tmpdir, project):
        packages = []

        for folder in [project.path, *(project.deps or [])]:
            path = ROOT / folder
            system = utils.System(cwd=path)
            system('rm -rf dist')
            system('uv build --refresh-package flexbuild')
            wheels = list((path / 'dist').glob('*.whl'))
            assert len(wheels) == 1, wheels
            packages += [str(x) for x in wheels]

        stem = f'{project.name.replace(".", "_")}-0.1.0'
        wheel = ROOT / project.path / f'dist/{stem}-py3-none-any.whl'
        assert wheel.exists()

        system = utils.System(cwd=tmpdir)
        system('uv venv')

        with pytest.raises(RuntimeError) as e:
            system(f'uv run -qq python -c "import {project.name}"')
        assert 'ModuleNotFoundError' in e.value.args[0]

        command = [
            'uv pip install',
            *packages,
            '--no-build-isolation',
            f'--refresh-package {project.name}',
        ]
        system(' '.join(command))
        code = f'import {project.name}; print({project.name}.foo())'
        assert system(f'uv run -qq python -c "{code}"') == '42\n'

    @pytest.mark.parametrize('project', PROJECTS)
    def test_build_sdist(self, tmpdir, project):
        packages = []

        system = utils.System(cwd=REPO)
        system('rm -rf dist')
        system('uv build')
        sdist = list((REPO / 'dist').glob('*.whl'))[0]
        backend = str(sdist)

        for folder in [project.path, *(project.deps or [])]:
            path = ROOT / folder
            system = utils.System(cwd=path)
            system('rm -rf dist')
            system('uv build --refresh-package flexbuild')
            sdists = list((path / 'dist').glob('*.tar.gz'))
            assert len(sdists) == 1, sdists
            packages += [str(x) for x in sdists]

        system = utils.System(cwd=tmpdir)
        system('uv venv')

        with pytest.raises(RuntimeError) as e:
            system(f'uv run -qq python -c "import {project.name}"')
        assert 'ModuleNotFoundError' in e.value.args[0]

        system(f'uv pip install {backend}')
        command = [
            'uv pip install',
            *packages,
            '--no-build-isolation',
            f'--refresh-package {project.name}',
        ]
        system(' '.join(command))
        code = f'import {project.name}; print({project.name}.foo())'
        assert system(f'uv run -qq python -c "{code}"') == '42\n'
