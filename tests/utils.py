import os
import pathlib
import shlex
import subprocess


class System:
    def __init__(self, cwd='.', env=None):
        self.cwd = pathlib.Path(cwd).resolve()
        assert self.cwd.is_dir()
        env = {**os.environ, **(env or {})}
        env.pop('VIRTUAL_ENV', None)
        self.env = env

    def __call__(self, *command):
        return run_command(' '.join(command), self.cwd, self.env)


def run_command(command, cwd='.', env=None):
    args = shlex.split(command)
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        cwd=cwd,
        env=env,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f'Command failed with return code {result.returncode}.\n'
            f'--- COMMAND ---\n{command}\n'
            f'--- STDERR ---\n{result.stderr}\n'
            f'--- STDOUT ---\n{result.stdout}'
        )
    return result.stdout


def find_project(project):
    # return pathlib.Path(__file__).parent / project.replace('.', '/')
    path, name = project
    path = pathlib.Path(__file__).parent / path
    return path, name
