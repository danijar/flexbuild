from . import project
from . import wheel


def build_editable(
    wheel_directory,
    config_settings=None,
    metadata_directory=None,
):
    proj = project.Project('.')
    path = str((proj.module_folder / '__init__.py').as_posix())
    finder = make_finder(proj.name, path)
    with wheel.Wheel(wheel_directory, proj) as whl:
        ident = proj.name.replace('.', '_')
        whl.add(f'_editable_impl_{ident}.pth', finder)
    return whl.name


def make_finder(name, path):
    finder = repr(EDITABLE_FINDER.format(name=name, path=path))
    finder = f'import sys; exec({finder})'
    finder = finder.encode('utf-8')
    return finder


EDITABLE_FINDER = """
import importlib.abc
import sys

class EditableFinder(importlib.abc.MetaPathFinder):

    def find_spec(self, fullname, path, target=None):
        if fullname == '{name}':
            import os, importlib.util
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
