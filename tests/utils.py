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


def find_project(project):
    # return pathlib.Path(__file__).parent / project.replace('.', '/')
    path, name = project
    path = pathlib.Path(__file__).parent / path
    return path, name


def build_packages(project_paths, root=None, ext='whl'):
    if root is not None:
        project_paths = [root / x for x in project_paths]
    packages = []
    for path in project_paths:
        system = System(cwd=path)
        system('rm -rf dist')
        system('uv build --refresh-package flexbuild')
        package = list((path / 'dist').glob(f'*.{ext}'))
        assert len(package) == 1, package
        packages += [str(x) for x in package]
    return packages


def install_packages(system, package_paths, refresh):
    command = [
        'uv pip install',
        *package_paths,
        '--no-build-isolation',
        f'--refresh-package {refresh}',
    ]
    system(' '.join(command))
