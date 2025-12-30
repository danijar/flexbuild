import pathlib
import re
import tomllib

from . import helpers


# TODO: Support entry points
# TODO: Support dependency extras
# TODO: Support metadata for pypi (description, readme, python version, etc)
# TODO: Support build commands and including build artifacts into wheel
# TODO: Support build profiles


INCLUDE = [
    '*.py',
    'pyproject.toml',
]

EXCLUDE = [
    'dist',
    'build',
    '__pycache__',
    '.*',
    '*/.*',
    '*.pyc',
]


class Project:
    """Holds project information and metadata."""

    def __init__(self, project_folder):
        self._project_folder = pathlib.Path(project_folder)
        self._pyproject, self._module_folder, self._root_folder = read_project(
            project_folder
        )
        self._metadata = create_metadata(self._pyproject)

    @property
    def stem(self):
        name = self._pyproject['project']['name']
        version = self._pyproject['project']['version']
        stem = f'{name.replace(".", "_")}-{version}'
        return stem

    @property
    def name(self):
        return self._pyproject['project']['name']

    @property
    def scope(self):
        return self._pyproject['project']['name'].replace('.', '/')

    @property
    def project_folder(self):
        return self._project_folder

    @property
    def module_folder(self):
        return self._module_folder

    @property
    def root_folder(self):
        return self._root_folder

    @property
    def metadata(self):
        return self._metadata

    @property
    def include(self):
        return self._pyproject['build-system'].get('include', INCLUDE)

    @property
    def exclude(self):
        additional = self._pyproject['build-system'].get('exclude', [])
        return EXCLUDE + additional


def read_project(project_folder):
    project_folder = pathlib.Path(project_folder).resolve()
    pyproject = tomllib.loads((project_folder / 'pyproject.toml').read_text())

    root_folder = find_root(project_folder)
    if root_folder:
        pyroot = tomllib.loads((root_folder / 'pyroot.toml').read_text())
        pyproject['build-system'] = helpers.merge_dicts(
            pyproject.get('build-system', {}),
            pyroot.get('build-system', {}),
        )

    module_folder = pyproject['build-system'].get('module-folder', '.')
    module_folder = (project_folder / module_folder).resolve()
    if not (module_folder / '__init__.py').exists():
        raise ValueError(
            f'Missing __init__.py in module folder ({module_folder})'
        )

    pyproject['project'].setdefault('name', module_folder.name)
    pyproject['project'].setdefault('version', '0.0.0')
    validate_name(pyproject['project']['name'], module_folder, root_folder)

    return pyproject, module_folder, root_folder


def validate_name(name, module_folder, root_folder):
    if not re.match(r'[A-Za-z0-9_.]+', name):
        raise ValueError(f'Invalid chars in project name: {name}')

    if root_folder:
        scope = str(module_folder.relative_to(root_folder)).replace('/', '.')
        if scope != name:
            raise ValueError(
                f'When using pyroot.toml, the module name ({name}) must match '
                f'the parent folder structure ({scope})'
            )


def create_metadata(pyproject):
    name = pyproject['project']['name']
    version = pyproject['project'].get('version', '0.0.0')
    deps = pyproject['project'].get('dependencies', [])
    metadata = [
        ('Metadata-Version', '2.1'),
        ('Name', name),
        ('Version', version),
        *[('Requires-Dist', x) for x in deps],
    ]
    metadata = helpers.format_key_value(metadata)
    return metadata


def find_root(folder):
    while True:
        if (folder / 'pyroot.toml').exists():
            return folder
        if folder.parent == folder:  # Filesystem root
            break
        folder = folder.parent
    return None
