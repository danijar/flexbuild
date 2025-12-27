import base64
import hashlib
import io
import pathlib
import re
import tarfile
import tomllib
import zipfile


# TODO: rename to atlas?
# TODO: Look for .gitignore for excludes
# TODO: Look for pyproject.toml includes/excludes
# TODO: Look for pyproject.toml for source root
# TODO: Look for parent pyroot.toml for defaults
# TODO: Look for parent pyroot.toml to assert namespace name
# TODO: Support entry points
# TODO: Support dependency extras
# TODO: Support metadata for pypi (description, readme, etc, python version)
# TODO: Support build commands and including build artifacts into wheel
# TODO: Support build profiles


EDITABLE_FINDER = """
import importlib.abc
import sys

class EditableFinder(importlib.abc.MetaPathFinder):

    def find_spec(self, fullname, path, target=None):
        if fullname == '{name}':
            import os, importlib
            locations = [os.path.dirname('{path}')]
            return importlib.util.spec_from_file_location(
                fullname, '{path}', submodule_search_locations=locations)
        if '{name}'.startswith(fullname + '.'):  # Namespace
            import importlib.machinery
            spec = importlib.machinery.ModuleSpec(fullname, None)
            spec.submodule_search_locations = []
            return spec
        return None

sys.meta_path.insert(0, EditableFinder())
"""


def build_sdist(sdist_directory, config_settings=None):
    project = Project(root='.')
    outdir = pathlib.Path(sdist_directory).resolve()
    outfile = outdir / f'{project.stem}.tar.gz'
    with tarfile.open(outfile, 'w:gz') as f:
        for path in project.root.rglob('*'):
            if path.is_dir():
                continue
            relative = path.relative_to(project.root)
            if _should_exclude(relative):
                continue
            f.add(path, f'{project.stem}/{relative}')
        metadata = _format_key_value(project.metadata)
        info = tarfile.TarInfo(f'{project.stem}/PKG-INFO')
        info.size = len(metadata)
        f.addfile(info, io.BytesIO(metadata))
    return outfile.name


def build_wheel(
    wheel_directory, config_settings=None, metadata_directory=None,
):
    project = Project(root='.')
    with Wheel(wheel_directory, project) as wheel:
        for path in project.root.rglob('*.py'):
            relative = path.relative_to(project.root)
            if _should_exclude(relative):
                continue
            wheel.add(f'{project.scope}/{relative}', path.read_bytes())
    return wheel.name


def build_editable(
    wheel_directory, config_settings=None, metadata_directory=None,
):
    project = Project(root='.')
    path = str((project.root / '__init__.py').as_posix())
    finder = repr(EDITABLE_FINDER.format(name=project.name, path=path))
    # finder = 'import sys; exec("""' + finder + '""")'
    finder = f'import sys; exec({finder})'
    finder = finder.encode('utf-8')
    with Wheel(wheel_directory, project) as wheel:
        ident = project.name.replace('.', '_')
        wheel.add(f'_editable_impl_{ident}.pth', finder)
    return wheel.name


class Project:

    def __init__(self, root):
        self.root = pathlib.Path(root).resolve()
        assert (self.root / '__init__.py').exists()
        self.pyproject = tomllib.loads(
            (self.root / 'pyproject.toml').read_text())

        self.name = self.pyproject['project'].get('name', self.root.name)
        assert re.match(r'[A-Za-z0-9_.]+', self.name), self.name
        self.version = self.pyproject['project'].get('version', '0.0.0')
        self.deps = self.pyproject['project'].get('dependencies', [])

        self.scope = self.name.replace('.', '/')
        self.stem = f'{self.name.replace(".", "_")}-{self.version}'
        self.metadata = tuple([
            ('Metadata-Version', '2.1'),
            ('Name', self.name),
            ('Version', self.version),
            *[('Requires-Dist', x) for x in self.deps],
        ])


class Wheel:

    def __init__(self, outdir, project):
        outdir = pathlib.Path(outdir).resolve()
        self.stem = project.stem
        self.meta = project.metadata
        self.path = outdir / f'{self.stem}-py3-none-any.whl'
        self.records = []
        self.f = None

    @property
    def name(self):
        return self.path.name

    def __enter__(self):
        assert not self.f
        self.f = zipfile.ZipFile(self.path, 'w')
        self.f.__enter__()
        return self

    def __exit__(self, typ, val, tb):
        self._finish()
        self.records = []
        self.f.__exit__(typ, val, tb)
        self.f = None

    def add(self, name, content):
        assert isinstance(content, bytes), (name, content)
        name = str(name)
        digest = _get_digest(content)
        self.records.append(f'{name},{digest},{len(content)}\n')
        self.f.writestr(name, content)

    def _finish(self):
        distinfo = f'{self.stem}.dist-info'
        self.add(f'{distinfo}/METADATA', _format_key_value(self.meta))
        self.add(f'{distinfo}/WHEEL', _format_key_value([
            ('Wheel-Version', '1.0'),
            ('Generator', 'tinybuild 0.1.0'),
            ('Root-Is-Purelib', 'true'),
            ('Tag', 'py3-none-any'),
        ]))
        self.records.append('RECORD,,\n')
        self.f.writestr(f'{distinfo}/RECORD', ''.join(self.records))


def _should_exclude(path):
    parts = path.parts
    return (
        path.suffix == '.pyc' or
        any(part.startswith('.') for part in parts) or
        'dist' in parts or
        'build' in parts or
        '__pycache__' in parts
    )


def _get_digest(data):
    digest = hashlib.sha256(data).digest()
    digest = base64.urlsafe_b64encode(digest)
    digest = 'sha256=' + digest.decode('latin1').rstrip('=')
    return digest


def _format_key_value(data):
    content = ''.join(f'{k}: {v}\n' for k, v in data)
    content = content.encode('utf-8')
    return content
