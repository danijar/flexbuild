import os
import pathlib

from flexbuild import helpers


class System:
    def __init__(self, cwd='.', env=None):
        self.cwd = pathlib.Path(cwd).resolve()
        assert self.cwd.is_dir()
        env = {**os.environ, **(env or {})}
        env.pop('VIRTUAL_ENV', None)
        self.env = env

    def __call__(self, *command):
        return helpers.run_command(' '.join(command), self.cwd, self.env)


def build_package(project_path, typ='wheel'):
    system = System(cwd=project_path)
    system('rm -rf dist')
    system('uv build --refresh-package flexbuild')
    return find_package(project_path, typ)


def find_package(project_path, typ='wheel'):
    ext = dict(wheel='whl', sdist='tar.gz')[typ]
    packages = list((project_path / 'dist').glob(f'*.{ext}'))
    assert len(packages) == 1, packages
    return packages[0]


def install_package(system, package, links=None):
    links = links or []
    assert isinstance(links, list)
    name = str(package).rsplit('/')[-1]
    name = name.split('-', 0)[0]
    name = name.split('[')[0]
    command = [
        f'uv pip install {package}',
        *[f'--find-links {x}' for x in links],
        f'--refresh-package {name}',
    ]
    system(' '.join(command))
