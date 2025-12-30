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
