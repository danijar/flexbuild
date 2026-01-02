import pathlib
import re
import tomllib

from . import helpers


INCLUDE = [
    '*.py',
    'pyproject.toml',
    'README.md',
    'README.rst',
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
        self._metadata = create_metadata(self._pyproject, self._project_folder)
        self._entrypoints = create_entrypoints(self._pyproject)

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
    def entrypoints(self):
        return self._entrypoints

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
        relative = module_folder.relative_to(root_folder.parent)
        scope = str(relative).replace('/', '.')
        if scope != name:
            raise ValueError(
                f'When using pyroot.toml, the module name ({name}) must match '
                f'the parent folder structure ({scope})'
            )


def create_entrypoints(pyproject):
    sections = []
    if scripts := pyproject['project'].get('scripts', {}):
        entries = helpers.format_key_value(scripts.items(), sep=' = ')
        sections.append(f'[console_scripts]\n{entries}')
    if scripts := pyproject['project'].get('gui-scripts', {}):
        entries = helpers.format_key_value(scripts.items(), sep=' = ')
        sections.append(f'[gui_scripts]\n{entries}')
    if not sections:
        return None
    return '\n'.join(sections).encode('utf-8')


def find_root(folder):
    while True:
        if (folder / 'pyroot.toml').exists():
            return folder
        if folder.parent == folder:  # Filesystem root
            break
        folder = folder.parent
    return None


def create_metadata(pyproject, project_folder):
    proj = pyproject['project']
    entries = [
        ('Metadata-Version', '2.1'),
        ('Name', proj['name']),
        ('Version', proj.get('version', '0.0.0')),
    ]

    if x := proj.get('description'):
        entries.append(('Summary', x))
    if x := proj.get('requires-python'):
        entries.append(('Requires-Python', x))
    if x := proj.get('license'):
        if isinstance(x, str):
            entries.append(('License-Expression', x))
        else:
            entries.append(('License', x['text']))
    for x in proj.get('keywords', []):
        entries.append(('Keyword', x))
    for x in proj.get('classifiers', []):
        entries.append(('Classifier', x))
    for label, url in proj.get('urls', {}).items():
        entries.append(('Project-URL', f'{label}, {url}'))
    entries += format_people('Author', proj.get('authors', []))
    entries += format_people('Maintainer', proj.get('maintainers', []))

    for x in proj.get('dependencies', []):
        entries.append(('Requires-Dist', x))
    for extra, deps in proj.get('optional-dependencies', {}).items():
        entries.append(('Provides-Extra', extra))
        for dep in deps:
            entries.append(('Requires-Dist', f'{dep}; extra == "{extra}"'))

    if x := proj.get('readme'):
        extension = x.rsplit('.', 1)[1].lower()
        content_type = dict(
            md='text/markdown',
            rst='text/x-rst',
        ).get(extension, 'text/plain')
        entries.append(('Description-Content-Type', content_type))

    result = helpers.format_key_value(entries, sep=': ')

    if x := proj.get('readme'):
        result += '\n' + (project_folder / x).read_text()

    return result.encode('utf-8')


def format_people(field, people):
    names, emails = [], []
    for person in people:
        if 'name' in person and 'email' in person:
            emails.append(f'"{person["name"]}" <{person["email"]}>')
        elif 'name' in person:
            names.append(person['name'])
        elif 'email' in person:
            emails.append(person['email'])
        else:
            raise ValueError('Person needs name or email or both')
    entries = []
    if names:
        entries.append((field, ', '.join(names)))
    if emails:
        entries.append((f'{field}-email', ', '.join(emails)))
    return entries
