import pathlib
import re
import tomllib


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


class Project:
    """Holds project information and metadata."""

    def __init__(self, root):
        self.root = pathlib.Path(root).resolve()
        assert (self.root / '__init__.py').exists()
        content = (self.root / 'pyproject.toml').read_text()
        self.pyproject = tomllib.loads(content)

        self.name = self.pyproject['project'].get('name', self.root.name)
        assert re.match(r'[A-Za-z0-9_.]+', self.name), self.name
        self.version = self.pyproject['project'].get('version', '0.0.0')
        self.deps = self.pyproject['project'].get('dependencies', [])

        self.scope = self.name.replace('.', '/')
        self.stem = f'{self.name.replace(".", "_")}-{self.version}'
        metadata = [
            ('Metadata-Version', '2.1'),
            ('Name', self.name),
            ('Version', self.version),
            *[('Requires-Dist', x) for x in self.deps],
        ]
        self.metadata = tuple(metadata)
